"""Questionnaire reads. Mutations belong to admin question management later."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Question, QuestionnaireVersion
from app.models.enums import QuestionStatus


def list_active_versions(session: Session) -> list[QuestionnaireVersion]:
    statement = (
        select(QuestionnaireVersion)
        .where(QuestionnaireVersion.is_active.is_(True))
        .order_by(QuestionnaireVersion.id)
    )
    return list(session.scalars(statement).all())


def list_questions_for_version(
    session: Session,
    version_id: int,
    *,
    active_only: bool,
) -> list[Question]:
    statement = (
        select(Question)
        .options(
            selectinload(Question.category),
            selectinload(Question.personality_trait),
            selectinload(Question.version),
        )
        .where(Question.questionnaire_version_id == version_id)
        .order_by(Question.display_order)
    )
    if active_only:
        statement = statement.where(Question.status == QuestionStatus.ACTIVE.value)
    return list(session.scalars(statement).all())


def get_questions_by_ids(session: Session, question_ids: list[int]) -> list[Question]:
    if not question_ids:
        return []
    statement = select(Question).where(Question.id.in_(question_ids))
    return list(session.scalars(statement).all())
