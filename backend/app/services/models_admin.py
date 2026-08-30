"""Activate one registered model for live prediction."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.enums import ModelStatus
from app.repositories import ml_models as model_repository
from app.schemas.evaluation import RegistryMetricOut, RegistryModelOut
from app.services import evaluation as evaluation_service


def _to_out(model, *, selected: bool) -> RegistryModelOut:
    metric = model.metrics[0] if model.metrics else None
    return RegistryModelOut(
        id=model.id,
        algorithm=model.algorithm,
        version=model.version,
        status=model.status,
        dataset_name=model.dataset_name,
        dataset_size=model.dataset_size,
        train_size=model.train_size,
        test_size=model.test_size,
        is_synthetic_dataset=model.is_synthetic_dataset,
        file_path=model.file_path,
        trained_at=model.trained_at,
        notes=model.notes,
        selected=selected,
        metrics=(
            RegistryMetricOut(
                accuracy=float(metric.accuracy),
                precision_macro=float(metric.precision_macro),
                recall_macro=float(metric.recall_macro),
                f1_macro=float(metric.f1_macro),
                precision_weighted=float(metric.precision_weighted),
                recall_weighted=float(metric.recall_weighted),
                f1_weighted=float(metric.f1_weighted),
                confusion_matrix=metric.confusion_matrix,
                cv_folds=metric.cv_folds,
                cv_mean_accuracy=(
                    float(metric.cv_mean_accuracy)
                    if metric.cv_mean_accuracy is not None
                    else None
                ),
            )
            if metric
            else None
        ),
    )


def activate_model(session: Session, model_id: int) -> RegistryModelOut:
    model = model_repository.get_by_id(session, model_id)
    if model is None:
        raise AppError("Model not found", status_code=404)
    model_repository.activate(session, model)
    session.commit()
    loaded = model_repository.get_by_id(session, model.id)
    return _to_out(loaded, selected=True)


def activate_selected(session: Session) -> RegistryModelOut:
    latest = evaluation_service.last_evaluation()
    if latest is None or latest.selected_model_id is None:
        raise AppError("Evaluate a training run before activating the selected model.", status_code=400)
    return activate_model(session, latest.selected_model_id)
