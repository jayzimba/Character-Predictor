"""Admin analytics payloads. Counts come from stored rows, never invented."""

from pydantic import BaseModel, Field


class NamedCount(BaseModel):
    key: str
    label: str
    count: int


class PersonalityCounts(BaseModel):
    choleric: int = 0
    melancholic: int = 0
    phlegmatic: int = 0
    sanguine: int = 0


class AnalyticsTotals(BaseModel):
    users_regular: int
    assessments_started: int
    assessments_completed: int
    assessments_in_progress: int
    classifications_stored: int
    demo_classifications: int
    model_classifications: int
    completion_rate: float | None = None
    mean_confidence: float | None = None


class TimePoint(BaseModel):
    date: str
    started: int = 0
    completed: int = 0
    classified: int = 0
    demo: int = 0


class AnalyticsOut(BaseModel):
    disclaimer: str
    window_days: int
    totals: AnalyticsTotals
    personality_counts: PersonalityCounts
    source_counts: list[NamedCount] = Field(default_factory=list)
    algorithm_counts: list[NamedCount] = Field(default_factory=list)
    age_group_counts: list[NamedCount] = Field(default_factory=list)
    gender_counts: list[NamedCount] = Field(default_factory=list)
    series: list[TimePoint] = Field(default_factory=list)
