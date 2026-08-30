"""Versioned questionnaire stored in the database, not in React."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import QuestionStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.assessment import Assessment, AssessmentAnswer
    from app.models.personality import PersonalityType


class QuestionCategory(TimestampMixin, Base):
    __tablename__ = "question_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    questions: Mapped[list[Question]] = relationship(back_populates="category")


class QuestionnaireVersion(TimestampMixin, Base):
    __tablename__ = "questionnaire_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version_code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    questions: Mapped[list[Question]] = relationship(back_populates="version")
    assessments: Mapped[list[Assessment]] = relationship(back_populates="questionnaire_version")


class Question(TimestampMixin, Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint(
            "questionnaire_version_id",
            "display_order",
            name="uq_questions_version_display_order",
        ),
        CheckConstraint("weight > 0", name="weight_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    questionnaire_version_id: Mapped[int] = mapped_column(
        ForeignKey("questionnaire_versions.id"),
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("question_categories.id"),
        index=True,
    )
    personality_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("personality_types.id"),
        nullable=True,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("1.00"))
    status: Mapped[str] = mapped_column(
        String(16),
        default=QuestionStatus.ACTIVE.value,
        index=True,
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    reverse_scored: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    version: Mapped[QuestionnaireVersion] = relationship(back_populates="questions")
    category: Mapped[QuestionCategory] = relationship(back_populates="questions")
    personality_trait: Mapped[PersonalityType | None] = relationship(
        back_populates="questions"
    )
    answers: Mapped[list[AssessmentAnswer]] = relationship(back_populates="question")
