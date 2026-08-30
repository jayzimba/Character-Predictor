"""User dashboard summary. Mix percentages are stored values, never invented."""

from datetime import datetime

from pydantic import BaseModel, Field


class DashboardPersonality(BaseModel):
    code: str
    name: str
    tagline: str


class PersonalityMix(BaseModel):
    choleric: float = Field(ge=0, le=100)
    melancholic: float = Field(ge=0, le=100)
    phlegmatic: float = Field(ge=0, le=100)
    sanguine: float = Field(ge=0, le=100)


class AssessmentCompletion(BaseModel):
    answered: int
    total: int
    percent: int
    status: str


class DashboardOut(BaseModel):
    assessments_completed: int
    assessments_in_progress: int
    latest_personality: DashboardPersonality | None = None
    latest_assessment_id: int | None = None
    latest_assessment_at: datetime | None = None
    latest_confidence: float | None = None
    latest_mix: PersonalityMix | None = None
    is_demo_mode: bool = False
    completion: AssessmentCompletion | None = None
