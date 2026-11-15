"""Load and administer the active questionnaire. Scoring stays server-side."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Question, User
from app.models.enums import QuestionStatus
from app.repositories import audit as audit_repository
from app.repositories import personality as personality_repository
from app.repositories import questionnaire as questionnaire_repository
from app.schemas.questionnaire import (
    ActiveQuestionnaireOut,
    AdminQuestionOut,
    CategoryOut,
    LikertOption,
    ParticipantQuestionOut,
    QuestionOptionOut,
    QuestionOptionsOut,
    QuestionPatch,
    QuestionWrite,
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


def _admin_out(question: Question, answer_count: int) -> AdminQuestionOut:
    trait = None
    if question.personality_trait is not None:
        trait = TraitOut(
            code=question.personality_trait.code,
            name=question.personality_trait.name,
        )
    return AdminQuestionOut(
        id=question.id,
        question_text=question.question_text,
        display_order=question.display_order,
        status=question.status,
        weight=float(question.weight),
        reverse_scored=question.reverse_scored,
        category=_category_out(question),
        personality_trait=trait,
        version_code=question.version.version_code,
        answer_count=answer_count,
        scoring_locked=answer_count > 0,
        created_at=question.created_at,
        updated_at=question.updated_at,
    )


def _loaded(session: Session, question_id: int) -> Question:
    question = questionnaire_repository.get_question_by_id(session, question_id)
    if question is None:
        raise AppError("Question not found", status_code=404)
    return question


def _resolve_category(session: Session, code: str):
    category = questionnaire_repository.get_category_by_code(session, code)
    if category is None:
        raise AppError("Unknown question category.", status_code=400)
    return category


def _resolve_trait(session: Session, code: str):
    trait = personality_repository.get_by_code(session, code)
    if trait is None:
        raise AppError("Unknown personality type.", status_code=400)
    return trait


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
    counts = questionnaire_repository.answer_counts_by_question(
        session, [item.id for item in questions]
    )
    return [_admin_out(item, counts.get(item.id, 0)) for item in questions]


def question_options(session: Session) -> QuestionOptionsOut:
    version = require_single_active_version(session)
    return QuestionOptionsOut(
        version_code=version.version_code,
        categories=[
            QuestionOptionOut(code=item.code, name=item.name)
            for item in questionnaire_repository.list_categories(session)
        ],
        personality_types=[
            QuestionOptionOut(code=item.code, name=item.name)
            for item in personality_repository.list_personality_types(session)
        ],
    )


def create_admin_question(
    session: Session,
    payload: QuestionWrite,
    *,
    actor: User | None = None,
) -> AdminQuestionOut:
    version = require_single_active_version(session)
    display_order = payload.display_order or questionnaire_repository.next_display_order(
        session, version.id
    )
    if questionnaire_repository.display_order_taken(session, version.id, display_order):
        raise AppError("That display order is already used in this version.", status_code=409)
    category = _resolve_category(session, payload.category_code)
    trait = _resolve_trait(session, payload.personality_code)
    created = questionnaire_repository.create_question(
        session,
        version_id=version.id,
        category_id=category.id,
        personality_type_id=trait.id,
        question_text=payload.question_text.strip(),
        weight=Decimal(str(payload.weight)),
        reverse_scored=payload.reverse_scored,
        display_order=display_order,
        status=QuestionStatus.ACTIVE.value,
    )
    audit_repository.record(
        session,
        actor_id=actor.id if actor else None,
        action="QUESTION_CREATED",
        entity_type="question",
        entity_id=str(created.id),
        details={
            "category": payload.category_code,
            "personality": payload.personality_code,
            "display_order": display_order,
        },
    )
    session.commit()
    loaded = _loaded(session, created.id)
    return _admin_out(loaded, 0)


def update_admin_question(
    session: Session,
    question_id: int,
    payload: QuestionPatch,
    *,
    actor: User | None = None,
) -> AdminQuestionOut:
    question = _loaded(session, question_id)
    version = require_single_active_version(session)
    if question.questionnaire_version_id != version.id:
        raise AppError("Question not found", status_code=404)

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise AppError("No updates were provided.", status_code=400)

    counts = questionnaire_repository.answer_counts_by_question(session, [question.id])
    locked = counts.get(question.id, 0) > 0
    scoring_keys = {
        "question_text",
        "category_code",
        "personality_code",
        "weight",
        "reverse_scored",
        "display_order",
    }
    if locked and scoring_keys.intersection(changes):
        raise AppError(
            "Scoring fields are locked because this item already has answers. Deactivate it instead of editing.",
            status_code=409,
        )

    if "status" in changes:
        status = changes["status"]
        if status not in {QuestionStatus.ACTIVE.value, QuestionStatus.INACTIVE.value}:
            raise AppError("Status must be ACTIVE or INACTIVE.", status_code=400)
        question.status = status

    if "question_text" in changes:
        question.question_text = changes["question_text"].strip()
    if "weight" in changes:
        question.weight = Decimal(str(changes["weight"]))
    if "reverse_scored" in changes:
        question.reverse_scored = changes["reverse_scored"]
    if "display_order" in changes:
        order = changes["display_order"]
        if questionnaire_repository.display_order_taken(
            session, question.questionnaire_version_id, order, exclude_id=question.id
        ):
            raise AppError("That display order is already used in this version.", status_code=409)
        question.display_order = order
    if "category_code" in changes:
        question.category_id = _resolve_category(session, changes["category_code"]).id
    if "personality_code" in changes:
        question.personality_type_id = _resolve_trait(session, changes["personality_code"]).id

    action = "QUESTION_UPDATED"
    if changes.get("status") == QuestionStatus.INACTIVE.value:
        action = "QUESTION_DEACTIVATED"
    elif changes.get("status") == QuestionStatus.ACTIVE.value:
        action = "QUESTION_ACTIVATED"
    audit_repository.record(
        session,
        actor_id=actor.id if actor else None,
        action=action,
        entity_type="question",
        entity_id=str(question.id),
        details={"fields": sorted(changes.keys())},
    )
    session.commit()
    loaded = _loaded(session, question.id)
    refreshed = questionnaire_repository.answer_counts_by_question(session, [loaded.id])
    return _admin_out(loaded, refreshed.get(loaded.id, 0))
