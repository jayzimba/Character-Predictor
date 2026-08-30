"""Reference copy for the four temperament classes.

This is educational content, not a clinical profile.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.assessment import PredictionResult
    from app.models.questionnaire import Question


class PersonalityType(TimestampMixin, Base):
    __tablename__ = "personality_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    tagline: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    characteristics: Mapped[list[str]] = mapped_column(JSON)
    strengths: Mapped[list[str]] = mapped_column(JSON)
    development_areas: Mapped[list[str]] = mapped_column(JSON)
    communication_style: Mapped[str] = mapped_column(Text)
    work_style: Mapped[str] = mapped_column(Text)
    career_environments: Mapped[str] = mapped_column(Text)
    development_suggestions: Mapped[str] = mapped_column(Text)
    disclaimer: Mapped[str] = mapped_column(Text)

    questions: Mapped[list[Question]] = relationship(back_populates="personality_trait")
    prediction_results: Mapped[list[PredictionResult]] = relationship(
        back_populates="personality_type"
    )

    def as_public_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "characteristics": self.characteristics,
            "strengths": self.strengths,
            "development_areas": self.development_areas,
            "communication_style": self.communication_style,
            "work_style": self.work_style,
            "career_environments": self.career_environments,
            "development_suggestions": self.development_suggestions,
            "disclaimer": self.disclaimer,
        }
