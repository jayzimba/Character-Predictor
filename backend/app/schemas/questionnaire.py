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
    answer_count: int
    scoring_locked: bool
    created_at: datetime
    updated_at: datetime


class QuestionWrite(BaseModel):
    question_text: str = Field(min_length=8, max_length=2000)
    category_code: str = Field(min_length=1, max_length=64)
    personality_code: str = Field(min_length=1, max_length=32)
    weight: float = Field(gt=0, le=10)
    reverse_scored: bool = False
    display_order: int | None = Field(default=None, ge=1)


class QuestionPatch(BaseModel):
    question_text: str | None = Field(default=None, min_length=8, max_length=2000)
    category_code: str | None = Field(default=None, min_length=1, max_length=64)
    personality_code: str | None = Field(default=None, min_length=1, max_length=32)
    weight: float | None = Field(default=None, gt=0, le=10)
    reverse_scored: bool | None = None
    display_order: int | None = Field(default=None, ge=1)
    status: str | None = None


class QuestionOptionOut(BaseModel):
    code: str
    name: str


class QuestionOptionsOut(BaseModel):
    version_code: str
    categories: list[QuestionOptionOut]
    personality_types: list[QuestionOptionOut]
