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
    metrics: RegistryMetricOut | None = None
