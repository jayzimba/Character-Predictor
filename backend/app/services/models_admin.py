"""Administer the trained-model registry.

Only one row may be ACTIVE. Previous active models are archived, never deleted,
so stored predictions keep a stable model_id.
"""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import User
from app.models.enums import ModelStatus
from app.repositories import audit as audit_repository
from app.repositories import ml_models as model_repository
from app.schemas.evaluation import RegistryModelOut
from app.services import evaluation as evaluation_service


def _to_out(session: Session, model, *, selected: bool | None = None) -> RegistryModelOut:
    if selected is None:
        latest = evaluation_service.last_evaluation()
        selected = bool(latest and latest.selected_model_id == model.id)
    return RegistryModelOut.from_model(
        model,
        selected=selected,
        prediction_count=model_repository.count_predictions(session, model.id),
        artifact_present=model_repository.artifact_is_present(model),
    )


def list_models(session: Session) -> list[RegistryModelOut]:
    selected_id = None
    latest = evaluation_service.last_evaluation()
    if latest:
        selected_id = latest.selected_model_id
    counts = model_repository.prediction_counts(session)
    return [
        RegistryModelOut.from_model(
            model,
            selected=model.id == selected_id,
            prediction_count=counts.get(model.id, 0),
            artifact_present=model_repository.artifact_is_present(model),
        )
        for model in model_repository.list_registered(session)
    ]


def get_model(session: Session, model_id: int) -> RegistryModelOut:
    model = model_repository.get_by_id(session, model_id)
    if model is None:
        raise AppError("Model not found", status_code=404)
    return _to_out(session, model)


def activate_model(session: Session, model_id: int, actor: User | None = None) -> RegistryModelOut:
    model = model_repository.get_by_id(session, model_id)
    if model is None:
        raise AppError("Model not found", status_code=404)
    if not model_repository.artifact_is_present(model):
        raise AppError(
            "This model has no joblib artefact on disk, so it cannot be activated.",
            status_code=400,
        )
    previous = model_repository.get_active(session)
    previous_id = previous.id if previous and previous.id != model.id else None
    model_repository.activate(session, model)
    audit_repository.record(
        session,
        actor_id=actor.id if actor else None,
        action="MODEL_ACTIVATED",
        entity_type="ml_model",
        entity_id=str(model.id),
        details={
            "algorithm": model.algorithm,
            "version": model.version,
            "archived_model_id": previous_id,
            "is_synthetic_dataset": model.is_synthetic_dataset,
        },
    )
    session.commit()
    loaded = model_repository.get_by_id(session, model.id)
    return _to_out(session, loaded, selected=True)


def activate_selected(session: Session, actor: User | None = None) -> RegistryModelOut:
    latest = evaluation_service.last_evaluation()
    if latest is None or latest.selected_model_id is None:
        raise AppError(
            "Evaluate a training run before activating the selected model.",
            status_code=400,
        )
    return activate_model(session, latest.selected_model_id, actor=actor)


def archive_model(session: Session, model_id: int, actor: User | None = None) -> RegistryModelOut:
    model = model_repository.get_by_id(session, model_id)
    if model is None:
        raise AppError("Model not found", status_code=404)
    if model.status == ModelStatus.ARCHIVED.value:
        raise AppError("This model is already archived.", status_code=400)
    was_active = model.status == ModelStatus.ACTIVE.value
    model_repository.archive(session, model)
    audit_repository.record(
        session,
        actor_id=actor.id if actor else None,
        action="MODEL_ARCHIVED",
        entity_type="ml_model",
        entity_id=str(model.id),
        details={
            "algorithm": model.algorithm,
            "version": model.version,
            "was_active": was_active,
        },
    )
    session.commit()
    loaded = model_repository.get_by_id(session, model.id)
    return _to_out(session, loaded)


def update_notes(
    session: Session,
    model_id: int,
    notes: str,
    actor: User | None = None,
) -> RegistryModelOut:
    model = model_repository.get_by_id(session, model_id)
    if model is None:
        raise AppError("Model not found", status_code=404)
    model_repository.set_notes(session, model, notes)
    audit_repository.record(
        session,
        actor_id=actor.id if actor else None,
        action="MODEL_NOTES_UPDATED",
        entity_type="ml_model",
        entity_id=str(model.id),
        details={"algorithm": model.algorithm, "version": model.version},
    )
    session.commit()
    loaded = model_repository.get_by_id(session, model.id)
    return _to_out(session, loaded)
