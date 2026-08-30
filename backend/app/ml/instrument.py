"""Questionnaire metadata used to turn Likert answers into category features."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.seed_catalog import QUESTIONS
from app.ml.constants import CATEGORY_CODES, FEATURE_COLUMNS
from app.models import Question
from app.models.enums import QuestionStatus
from app.repositories import questionnaire as questionnaire_repository
from app.services.questionnaire import require_single_active_version


def likert_column(display_order: int) -> str:
    return f"q{display_order:02d}"


@dataclass(frozen=True)
class ItemSpec:
    key: str
    display_order: int
    category_code: str
    weight: Decimal
    reverse_scored: bool
    personality_code: str | None = None


@dataclass(frozen=True)
class InstrumentSpec:
    version_code: str
    items: tuple[ItemSpec, ...]
    category_codes: tuple[str, ...] = CATEGORY_CODES

    @property
    def likert_columns(self) -> tuple[str, ...]:
        return tuple(item.key for item in self.items)

    @property
    def feature_columns(self) -> tuple[str, ...]:
        return tuple(f"{code}_score" for code in self.category_codes)

    @property
    def items_by_key(self) -> dict[str, ItemSpec]:
        return {item.key: item for item in self.items}

    def items_for_category(self, category_code: str) -> tuple[ItemSpec, ...]:
        return tuple(item for item in self.items if item.category_code == category_code)


def instrument_from_catalog(version_code: str = "v1") -> InstrumentSpec:
    """Build the instrument from the seed catalogue (no database required)."""
    items = tuple(
        ItemSpec(
            key=likert_column(order),
            display_order=order,
            category_code=category_code,
            weight=Decimal("1.00"),
            reverse_scored=reverse_scored,
            personality_code=personality_code,
        )
        for order, (category_code, personality_code, reverse_scored, _text) in enumerate(
            QUESTIONS, start=1
        )
    )
    return InstrumentSpec(version_code=version_code, items=items)


def instrument_from_questions(
    questions: list[Question],
    version_code: str,
) -> InstrumentSpec:
    items = []
    for question in sorted(questions, key=lambda row: row.display_order):
        trait = question.personality_trait.code if question.personality_trait else None
        items.append(
            ItemSpec(
                key=likert_column(question.display_order),
                display_order=question.display_order,
                category_code=question.category.code,
                weight=Decimal(question.weight),
                reverse_scored=question.reverse_scored,
                personality_code=trait,
            )
        )
    return InstrumentSpec(version_code=version_code, items=tuple(items))


def instrument_from_session(session: Session) -> InstrumentSpec:
    version = require_single_active_version(session)
    questions = questionnaire_repository.list_questions_for_version(
        session, version.id, active_only=True
    )
    active = [row for row in questions if row.status == QuestionStatus.ACTIVE.value]
    return instrument_from_questions(active, version.version_code)


# Imported by tests that want the canonical feature list without constructing a spec.
assert FEATURE_COLUMNS == instrument_from_catalog().feature_columns
