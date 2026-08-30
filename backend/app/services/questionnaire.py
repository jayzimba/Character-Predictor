"""Load the active questionnaire. Scoring stays server-side."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Question
from app.repositories import questionnaire as questionnaire_repository
from app.schemas.questionnaire import (
    ActiveQuestionnaireOut,
    AdminQuestionOut,
    CategoryOut,
    LikertOption,
    ParticipantQuestionOut,
    TraitOut,
)

DISCLAIMER = (
    "This assessment is intended for educational, research and "
    "personal-development purposes and should not be considered a "
    "clinical psychological diagnosis."
)

LIKERT_SCALE = [
    LikertOption(value=1, label="Strongly Disagree"),
    LikertOption(value=2, label="Disagree"),
    LikertOption(value=3, label="Neutral"),
    LikertOption(value=4, label="Agree"),
    LikertOption(value=5, label="Strongly Agree"),
]


def require_single_active_version(session: Session):
    versions = questionnaire_repository.list_active_versions(session)
    if not versions:
        raise AppError("No active questionnaire is available.", status_code=404)
    if len(versions) > 1:
        raise AppError(
            "More than one questionnaire version is marked active.",
            status_code=409,
        )
    return versions[0]


def _category_out(question: Question) -> CategoryOut:
    return CategoryOut.model_validate(question.category)


def get_active_questionnaire(session: Session) -> ActiveQuestionnaireOut:
    version = require_single_active_version(session)
    questions = questionnaire_repository.list_questions_for_version(
        session, version.id, active_only=True
    )
    return ActiveQuestionnaireOut(
        version_id=version.id,
        version_code=version.version_code,
        name=version.name,
        description=version.description,
        disclaimer=DISCLAIMER,
        likert_scale=LIKERT_SCALE,
        question_count=len(questions),
        questions=[
            ParticipantQuestionOut(
                id=item.id,
                question_text=item.question_text,
                display_order=item.display_order,
                category=_category_out(item),
            )
            for item in questions
        ],
    )


def list_admin_questions(session: Session) -> list[AdminQuestionOut]:
    version = require_single_active_version(session)
    questions = questionnaire_repository.list_questions_for_version(
        session, version.id, active_only=False
    )
    payload: list[AdminQuestionOut] = []
    for item in questions:
        trait = None
        if item.personality_trait is not None:
            trait = TraitOut(
                code=item.personality_trait.code,
                name=item.personality_trait.name,
            )
        payload.append(
            AdminQuestionOut(
                id=item.id,
                question_text=item.question_text,
                display_order=item.display_order,
                status=item.status,
                weight=float(item.weight),
                reverse_scored=item.reverse_scored,
                category=_category_out(item),
                personality_trait=trait,
                version_code=item.version.version_code,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
        )
    return payload
