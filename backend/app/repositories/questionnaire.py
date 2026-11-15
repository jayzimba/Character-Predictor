"""Questionnaire persistence. Historical answers stay attached to the question row."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import AssessmentAnswer, Question, QuestionCategory, QuestionnaireVersion
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


def get_question_by_id(session: Session, question_id: int) -> Question | None:
    statement = (
        select(Question)
        .options(
            selectinload(Question.category),
            selectinload(Question.personality_trait),
            selectinload(Question.version),
        )
        .where(Question.id == question_id)
    )
    return session.scalar(statement)


def list_categories(session: Session) -> list[QuestionCategory]:
    statement = select(QuestionCategory).order_by(QuestionCategory.display_order)
    return list(session.scalars(statement).all())


def get_category_by_code(session: Session, code: str) -> QuestionCategory | None:
    return session.scalar(select(QuestionCategory).where(QuestionCategory.code == code))


def next_display_order(session: Session, version_id: int) -> int:
    current = session.scalar(
        select(func.max(Question.display_order)).where(
            Question.questionnaire_version_id == version_id
        )
    )
    return int(current or 0) + 1


def display_order_taken(
    session: Session,
    version_id: int,
    display_order: int,
    *,
    exclude_id: int | None = None,
) -> bool:
    statement = select(func.count(Question.id)).where(
        Question.questionnaire_version_id == version_id,
        Question.display_order == display_order,
    )
    if exclude_id is not None:
        statement = statement.where(Question.id != exclude_id)
    return int(session.scalar(statement) or 0) > 0


def answer_counts_by_question(session: Session, question_ids: list[int]) -> dict[int, int]:
    if not question_ids:
        return {}
    rows = session.execute(
        select(AssessmentAnswer.question_id, func.count(AssessmentAnswer.id))
        .where(AssessmentAnswer.question_id.in_(question_ids))
        .group_by(AssessmentAnswer.question_id)
    ).all()
    return {int(question_id): int(count) for question_id, count in rows}


def create_question(
    session: Session,
    *,
    version_id: int,
    category_id: int,
    personality_type_id: int | None,
    question_text: str,
    weight,
    reverse_scored: bool,
    display_order: int,
    status: str,
) -> Question:
    question = Question(
        questionnaire_version_id=version_id,
        category_id=category_id,
        personality_type_id=personality_type_id,
        question_text=question_text,
        weight=weight,
        reverse_scored=reverse_scored,
        display_order=display_order,
        status=status,
    )
    session.add(question)
    session.flush()
    return question
