"""Classify a completed assessment. Mix values come from the model or DEMO MODE."""

from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.ml.instrument import instrument_from_session
from app.ml.predict import (
    PredictionError,
    demo_inference,
    features_from_assessment,
    load_estimator,
    model_inference,
)
from app.models import User
from app.models.enums import AssessmentStatus, RoleCode
from app.repositories import assessment as assessment_repository
from app.repositories import ml_models as model_repository
from app.repositories import personality as personality_repository
from app.schemas.prediction import ClassifyRequest, PersonalityMixOut, PredictionOut
from app.services.training import models_directory

DISCLAIMER = (
    "Your assessment indicates a pattern in this educational model. "
    "It is not a clinical psychological diagnosis."
)


def _dec(value: float, places: str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal(places))


def _can_access(user: User, assessment_user_id: int) -> bool:
    if assessment_user_id == user.id:
        return True
    return user.role.code == RoleCode.ADMIN.value


def _resolve_model_path(file_path: str | None) -> Path | None:
    if not file_path:
        return None
    path = Path(file_path)
    if path.exists():
        return path
    candidate = models_directory() / path.name
    if candidate.exists():
        return candidate
    return None


def _to_out(assessment_id: int, inference, type_row) -> PredictionOut:
    return PredictionOut(
        assessment_id=assessment_id,
        predicted_personality=inference.predicted_code,
        personality_name=type_row.name,
        confidence=inference.confidence,
        personality_mix=PersonalityMixOut(
            choleric=inference.mix["CHOLERIC"],
            melancholic=inference.mix["MELANCHOLIC"],
            phlegmatic=inference.mix["PHLEGMATIC"],
            sanguine=inference.mix["SANGUINE"],
        ),
        is_demo_mode=inference.is_demo_mode,
        demo_reason=inference.demo_reason,
        model_id=inference.model_id,
        algorithm=inference.algorithm,
        mix_source=inference.mix_source,
        disclaimer=DISCLAIMER,
    )


def _persist(session: Session, assessment_id: int, inference, type_row) -> None:
    assessment_repository.create_prediction(
        session,
        assessment_id=assessment_id,
        model_id=inference.model_id,
        personality_type_id=type_row.id,
        predicted_personality=inference.predicted_code,
        confidence_score=_dec(inference.confidence, "0.0001"),
        choleric_percentage=_dec(inference.mix["CHOLERIC"], "0.01"),
        melancholic_percentage=_dec(inference.mix["MELANCHOLIC"], "0.01"),
        phlegmatic_percentage=_dec(inference.mix["PHLEGMATIC"], "0.01"),
        sanguine_percentage=_dec(inference.mix["SANGUINE"], "0.01"),
        is_demo_mode=inference.is_demo_mode,
    )
    session.commit()


def _stored_out(assessment) -> PredictionOut:
    prediction = assessment.prediction
    type_row = prediction.personality_type
    algorithm = prediction.model.algorithm if prediction.model else None
    return PredictionOut(
        assessment_id=assessment.id,
        predicted_personality=prediction.predicted_personality,
        personality_name=type_row.name,
        confidence=float(prediction.confidence_score),
        personality_mix=PersonalityMixOut(
            choleric=float(prediction.choleric_percentage),
            melancholic=float(prediction.melancholic_percentage),
            phlegmatic=float(prediction.phlegmatic_percentage),
            sanguine=float(prediction.sanguine_percentage),
        ),
        is_demo_mode=bool(prediction.is_demo_mode),
        demo_reason=(
            "Stored DEMO MODE result."
            if prediction.is_demo_mode
            else None
        ),
        model_id=prediction.model_id,
        algorithm=algorithm,
        mix_source="stored",
        disclaimer=DISCLAIMER,
    )


def classify(session: Session, user: User, payload: ClassifyRequest) -> PredictionOut:
    assessment = assessment_repository.get_by_id(session, payload.assessment_id)
    if assessment is None or not _can_access(user, assessment.user_id):
        raise AppError("Assessment not found", status_code=404)
    if assessment.status != AssessmentStatus.COMPLETED.value:
        raise AppError("Submit the assessment before classification.", status_code=400)
    if assessment.prediction is not None:
        raise AppError("This assessment already has a stored prediction.", status_code=409)

    instrument = instrument_from_session(session)
    active = model_repository.get_active(session)
    if active is None:
        inference = demo_inference(assessment, instrument)
    else:
        path = _resolve_model_path(active.file_path)
        if path is None:
            raise AppError("The active model file is missing. Activate another model.", status_code=503)
        try:
            features = features_from_assessment(assessment, instrument)
            estimator = load_estimator(path)
            inference = model_inference(
                estimator=estimator,
                features=features,
                model_id=active.id,
                algorithm=active.algorithm,
                is_synthetic=bool(active.is_synthetic_dataset),
            )
        except PredictionError as exc:
            raise AppError(str(exc), status_code=400) from exc

    type_row = personality_repository.get_by_code(session, inference.predicted_code)
    if type_row is None:
        raise AppError("Predicted personality type is not in the catalogue.", status_code=500)
    _persist(session, assessment.id, inference, type_row)
    return _to_out(assessment.id, inference, type_row)


def get_prediction(session: Session, user: User, assessment_id: int) -> PredictionOut:
    assessment = assessment_repository.get_by_id(session, assessment_id)
    if assessment is None or not _can_access(user, assessment.user_id):
        raise AppError("Assessment not found", status_code=404)
    if assessment.prediction is None:
        raise AppError("This assessment has not been classified yet.", status_code=404)
    return _stored_out(assessment)
