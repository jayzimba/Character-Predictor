"""Assessment attempts, Likert answers, and stored predictions."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import AssessmentStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.ml import MLModel
    from app.models.personality import PersonalityType
    from app.models.questionnaire import Question, QuestionnaireVersion
    from app.models.user import User


class Assessment(TimestampMixin, Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    questionnaire_version_id: Mapped[int] = mapped_column(
        ForeignKey("questionnaire_versions.id"),
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default=AssessmentStatus.IN_PROGRESS.value,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    consent_accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="assessments")
    questionnaire_version: Mapped[QuestionnaireVersion] = relationship(
        back_populates="assessments"
    )
    answers: Mapped[list[AssessmentAnswer]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    prediction: Mapped[PredictionResult | None] = relationship(
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "question_id",
            name="uq_assessment_answers_assessment_question",
        ),
        CheckConstraint(
            "response_value >= 1 AND response_value <= 5",
            name="likert_range",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
        index=True,
    )
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    response_value: Mapped[int] = mapped_column(Integer, nullable=False)
    weighted_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    assessment: Mapped[Assessment] = relationship(back_populates="answers")
    question: Mapped[Question] = relationship(back_populates="answers")


class PredictionResult(Base):
    __tablename__ = "prediction_results"
    __table_args__ = (
        UniqueConstraint("assessment_id", name="uq_prediction_results_assessment_id"),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="confidence_unit_interval",
        ),
        CheckConstraint(
            "choleric_percentage >= 0 AND choleric_percentage <= 100",
            name="choleric_pct_range",
        ),
        CheckConstraint(
            "melancholic_percentage >= 0 AND melancholic_percentage <= 100",
            name="melancholic_pct_range",
        ),
        CheckConstraint(
            "phlegmatic_percentage >= 0 AND phlegmatic_percentage <= 100",
            name="phlegmatic_pct_range",
        ),
        CheckConstraint(
            "sanguine_percentage >= 0 AND sanguine_percentage <= 100",
            name="sanguine_pct_range",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"),
    )
    model_id: Mapped[int | None] = mapped_column(
        ForeignKey("ml_models.id"),
        nullable=True,
        index=True,
    )
    personality_type_id: Mapped[int] = mapped_column(
        ForeignKey("personality_types.id"),
        index=True,
    )
    predicted_personality: Mapped[str] = mapped_column(String(32), index=True)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    choleric_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    melancholic_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    phlegmatic_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    sanguine_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    is_demo_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    assessment: Mapped[Assessment] = relationship(back_populates="prediction")
    model: Mapped[MLModel | None] = relationship(back_populates="predictions")
    personality_type: Mapped[PersonalityType] = relationship(
        back_populates="prediction_results"
    )
