"""Trained model registry and evaluation metrics.

Only one row should have status=ACTIVE at a time. That rule is enforced
in the model-administration service, not with a fragile database enum.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.enums import ModelStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.assessment import PredictionResult


class MLModel(TimestampMixin, Base):
    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    algorithm: Mapped[str] = mapped_column(String(32), index=True)
    version: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(
        String(16),
        default=ModelStatus.TRAINED.value,
        index=True,
    )
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    dataset_name: Mapped[str] = mapped_column(String(120))
    dataset_size: Mapped[int] = mapped_column(Integer)
    train_size: Mapped[int] = mapped_column(Integer)
    test_size: Mapped[int] = mapped_column(Integer)
    is_synthetic_dataset: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    trained_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    metrics: Mapped[list[ModelMetric]] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
    )
    predictions: Mapped[list[PredictionResult]] = relationship(back_populates="model")


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        ForeignKey("ml_models.id", ondelete="CASCADE"),
        index=True,
    )
    accuracy: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    precision_macro: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    recall_macro: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    f1_macro: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    precision_weighted: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    recall_weighted: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    f1_weighted: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    confusion_matrix: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    cv_folds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cv_mean_accuracy: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    model: Mapped[MLModel] = relationship(back_populates="metrics")
