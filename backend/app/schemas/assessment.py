"""Assessment taking payloads. Participant views never include weighted scores."""

from datetime import datetime

from pydantic import BaseModel, Field


class ConsentRequest(BaseModel):
    consent_accepted: bool


class AnswerIn(BaseModel):
    question_id: int
    response_value: int = Field(ge=1, le=5)


class AnswersRequest(BaseModel):
    answers: list[AnswerIn] = Field(min_length=1, max_length=200)


class AnswerOut(BaseModel):
    question_id: int
    response_value: int


class AssessmentSummaryOut(BaseModel):
    id: int
    status: str
    questionnaire_version_id: int
    started_at: datetime
    completed_at: datetime | None
    consent_accepted_at: datetime | None
    answered: int
    total: int


class AssessmentDetailOut(AssessmentSummaryOut):
    answers: list[AnswerOut]
