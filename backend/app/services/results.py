"""Assemble a stored classification plus the educational type write-up."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Assessment, User
from app.models.enums import RoleCode
from app.repositories import assessment as assessment_repository
from app.schemas.personality import PersonalityTypeOut
from app.schemas.prediction import PersonalityMixOut
from app.schemas.results import ResultOut
from app.services.predictions import DISCLAIMER


def _can_access(user: User, assessment_user_id: int) -> bool:
    if assessment_user_id == user.id:
        return True
    return user.role.code == RoleCode.ADMIN.value


def _to_out(assessment: Assessment) -> ResultOut:
    prediction = assessment.prediction
    type_row = prediction.personality_type
    algorithm = prediction.model.algorithm if prediction.model else None
    return ResultOut(
        assessment_id=assessment.id,
        completed_at=assessment.completed_at or assessment.started_at,
        headline=f"Your assessment indicates {type_row.name}.",
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
            "Stored DEMO MODE result. Percentages come from the saved "
            "prediction, not from a new estimate."
            if prediction.is_demo_mode
            else None
        ),
        model_id=prediction.model_id,
        algorithm=algorithm,
        mix_source="stored",
        disclaimer=DISCLAIMER,
        personality=PersonalityTypeOut.model_validate(type_row),
    )


def get_latest_result(session: Session, user: User) -> ResultOut:
    assessment = assessment_repository.get_latest_classified_for_user(session, user.id)
    if assessment is None or assessment.prediction is None:
        raise AppError(
            "No classified assessment yet. Complete a questionnaire and classify it first.",
            status_code=404,
        )
    return _to_out(assessment)


def get_result(session: Session, user: User, assessment_id: int) -> ResultOut:
    assessment = assessment_repository.get_by_id(session, assessment_id)
    if assessment is None or not _can_access(user, assessment.user_id):
        raise AppError("Assessment not found", status_code=404)
    if assessment.prediction is None:
        raise AppError("This assessment has not been classified yet.", status_code=404)
    return _to_out(assessment)
