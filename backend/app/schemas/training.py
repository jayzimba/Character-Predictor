"""Training-run payloads. No invented test metrics."""

from typing import Any

from pydantic import BaseModel, Field


class FittedModelOut(BaseModel):
    algorithm: str
    sklearn_class: str
    file_name: str
    file_path: str | None = None
    uses_scaler: bool
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    cv: dict[str, Any] | None = None


class TrainingRunOut(BaseModel):
    trained_at: str
    dataset_name: str
    is_synthetic: bool
    feature_names: list[str]
    label_order: list[str]
    random_state: int
    n_train: int
    n_test: int
    class_counts_train: dict[str, int]
    held_out_evaluated: bool
    registered: bool
    cv_note: str
    warnings: list[str] = Field(default_factory=list)
    models: list[FittedModelOut] = Field(default_factory=list)
    disclaimer: str
