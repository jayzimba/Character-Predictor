"""Prediction API payloads."""

from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    assessment_id: int = Field(ge=1)


class PersonalityMixOut(BaseModel):
    choleric: float
    melancholic: float
    phlegmatic: float
    sanguine: float


class PredictionOut(BaseModel):
    assessment_id: int
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
