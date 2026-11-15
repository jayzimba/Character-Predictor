"""Personality results payload. Mix percentages are stored values, never invented."""

from datetime import datetime

from pydantic import BaseModel

from app.schemas.personality import PersonalityTypeOut
from app.schemas.prediction import PersonalityMixOut


class ResultOut(BaseModel):
    assessment_id: int
    completed_at: datetime | None
    headline: str
    predicted_personality: str
    personality_name: str
    confidence: float
    personality_mix: PersonalityMixOut
    is_demo_mode: bool
    demo_reason: str | None = None
    model_id: int | None = None
    algorithm: str | None = None
    mix_source: str
    disclaimer: str
    personality: PersonalityTypeOut
