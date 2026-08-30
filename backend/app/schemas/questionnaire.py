"""Questionnaire payloads.

The participant view omits weight, reverse scoring and trait so a test-taker
cannot infer how an item is scored. Administrators see the full row.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LikertOption(BaseModel):
    value: int = Field(ge=1, le=5)
    label: str


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    display_order: int


class TraitOut(BaseModel):
    code: str
    name: str


class ParticipantQuestionOut(BaseModel):
    id: int
    question_text: str
    display_order: int
    category: CategoryOut


class ActiveQuestionnaireOut(BaseModel):
    version_id: int
    version_code: str
    name: str
    description: str
    disclaimer: str
    likert_scale: list[LikertOption]
    question_count: int
    questions: list[ParticipantQuestionOut]


class AdminQuestionOut(BaseModel):
    id: int
    question_text: str
    display_order: int
    status: str
    weight: float
    reverse_scored: bool
    category: CategoryOut
    personality_trait: TraitOut | None = None
    version_code: str
    created_at: datetime
    updated_at: datetime
