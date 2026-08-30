"""Registry persistence for trained models and their evaluation metrics."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import MLModel, ModelMetric
from app.models.enums import ModelStatus


def _dec(value: float | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(round(float(value), 4)))


def next_run_version(session: Session) -> str:
    versions = list(session.scalars(select(MLModel.version).distinct()).all())
    return f"run-{len(versions) + 1}"


def create_registered_model(
    session: Session,
    *,
    algorithm: str,
    version: str,
    file_path: str | None,
    dataset_name: str,
    dataset_size: int,
    train_size: int,
    test_size: int,
    is_synthetic_dataset: bool,
    trained_at: datetime | None,
    notes: str | None,
    scores: dict,
) -> MLModel:
    model = MLModel(
        algorithm=algorithm,
        version=version,
        status=ModelStatus.TRAINED.value,
        file_path=file_path,
        dataset_name=dataset_name,
        dataset_size=dataset_size,
        train_size=train_size,
        test_size=test_size,
        is_synthetic_dataset=is_synthetic_dataset,
        trained_at=trained_at,
        notes=notes,
    )
    session.add(model)
    session.flush()
    session.add(
        ModelMetric(
            model_id=model.id,
            accuracy=_dec(scores["accuracy"]),
            precision_macro=_dec(scores["precision_macro"]),
            recall_macro=_dec(scores["recall_macro"]),
            f1_macro=_dec(scores["f1_macro"]),
            precision_weighted=_dec(scores["precision_weighted"]),
            recall_weighted=_dec(scores["recall_weighted"]),
            f1_weighted=_dec(scores["f1_weighted"]),
            confusion_matrix=scores["confusion_matrix"],
            cv_folds=scores.get("cv_folds"),
            cv_mean_accuracy=_dec(scores.get("cv_mean_accuracy")),
        )
    )
    session.flush()
    return model


def list_registered(session: Session) -> list[MLModel]:
    statement = (
        select(MLModel)
        .options(selectinload(MLModel.metrics))
        .order_by(MLModel.id.desc())
    )
    return list(session.scalars(statement).all())


def count_models(session: Session) -> int:
    return int(session.scalar(select(func.count(MLModel.id))) or 0)


def get_by_id(session: Session, model_id: int) -> MLModel | None:
    statement = (
        select(MLModel)
        .options(selectinload(MLModel.metrics))
        .where(MLModel.id == model_id)
    )
    return session.scalar(statement)


def get_active(session: Session) -> MLModel | None:
    statement = (
        select(MLModel)
        .options(selectinload(MLModel.metrics))
        .where(MLModel.status == ModelStatus.ACTIVE.value)
        .order_by(MLModel.id.desc())
    )
    return session.scalar(statement)


def activate(session: Session, model: MLModel) -> MLModel:
    current = list(
        session.scalars(
            select(MLModel).where(MLModel.status == ModelStatus.ACTIVE.value)
        ).all()
    )
    for row in current:
        if row.id != model.id:
            row.status = ModelStatus.ARCHIVED.value
    model.status = ModelStatus.ACTIVE.value
    session.flush()
    return model
