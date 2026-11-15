"""Admin overview and assessment list. No Likert answers on these payloads."""

from datetime import datetime

from pydantic import BaseModel


class PersonalityCounts(BaseModel):
    choleric: int = 0
    melancholic: int = 0
    phlegmatic: int = 0
    sanguine: int = 0


class ActiveModelSummary(BaseModel):
    id: int
    algorithm: str
    version: str
    status: str
    dataset_name: str
    is_synthetic_dataset: bool


class AdminOverviewOut(BaseModel):
    users_total: int
    users_admin: int
    users_regular: int
    assessments_completed: int
    assessments_in_progress: int
    classifications_stored: int
    demo_classifications: int
    personality_counts: PersonalityCounts
    active_model: ActiveModelSummary | None = None


class AdminAssessmentOut(BaseModel):
    assessment_id: int
    user_id: int
    user_email: str
    user_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    answered: int
    total: int
    has_prediction: bool
    predicted_personality: str | None = None
    personality_name: str | None = None
    confidence: float | None = None
    is_demo_mode: bool = False
