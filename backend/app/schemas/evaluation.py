"""Held-out evaluation and registry payloads. Metrics are never invented."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ConfusionMatrixOut(BaseModel):
    labels: list[str]
    matrix: list[list[int]]


class ModelScoresOut(BaseModel):
    algorithm: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float
    confusion_matrix: dict[str, Any]
    cv_folds: int | None = None
    cv_mean_accuracy: float | None = None
    selected: bool = False
    model_id: int | None = None


class EvaluationOut(BaseModel):
    disclaimer: str
    dataset_name: str
    is_synthetic: bool
    n_test: int
    selection_rule: str
    selected_algorithm: str
    selected_model_id: int | None = None
    version: str | None = None
    registered: bool
    scores: list[ModelScoresOut]
    warnings: list[str] = Field(default_factory=list)


class RegistryMetricOut(BaseModel):
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float
    confusion_matrix: dict[str, Any]
    cv_folds: int | None = None
    cv_mean_accuracy: float | None = None

    @classmethod
    def from_metric(cls, metric) -> "RegistryMetricOut":
        return cls(
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


class RegistryModelOut(BaseModel):
    id: int
    algorithm: str
    version: str
    status: str
    dataset_name: str
    dataset_size: int
    train_size: int
    test_size: int
    is_synthetic_dataset: bool
    file_path: str | None = None
    trained_at: datetime | None = None
    notes: str | None = None
    selected: bool = False
    prediction_count: int = 0
    artifact_present: bool = False
    metrics: RegistryMetricOut | None = None

    @classmethod
    def from_model(
        cls,
        model,
        *,
        selected: bool,
        prediction_count: int = 0,
        artifact_present: bool = False,
    ) -> "RegistryModelOut":
        metric = model.metrics[0] if model.metrics else None
        return cls(
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
            prediction_count=prediction_count,
            artifact_present=artifact_present,
            metrics=RegistryMetricOut.from_metric(metric) if metric else None,
        )


class ModelNotesPatch(BaseModel):
    notes: str = Field(min_length=0, max_length=2000)
