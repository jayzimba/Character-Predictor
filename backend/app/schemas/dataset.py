"""Admin dataset validation payloads. No invented metrics."""

from typing import Any

from pydantic import BaseModel, Field


class DatasetReportOut(BaseModel):
    source: str
    disclaimer: str
    format: str
    is_synthetic: bool
    origin_counts: dict[str, int]
    rows_in: int
    rows_kept: int
    duplicates_removed: int
    missing_dropped: int
    invalid_range_dropped: int
    invalid_label_dropped: int
    unlabelled_collected: int = 0
    class_counts: dict[str, int]
    feature_names: list[str]
    preview: list[dict[str, Any]] = Field(default_factory=list)
    split: dict[str, Any] | None = None
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    scaling_applied: bool
    scaling_note: str
    ready_for_training: bool
    trained: bool = False


class DemoDatasetOut(BaseModel):
    filename: str
    path: str
    disclaimer: str
    is_synthetic: bool = True
