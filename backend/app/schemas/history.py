"""Assessment history rows. Type and confidence are stored values, never invented."""

from datetime import datetime

from pydantic import BaseModel


class HistoryItemOut(BaseModel):
    assessment_id: int
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
