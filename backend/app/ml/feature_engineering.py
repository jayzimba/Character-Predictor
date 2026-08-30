"""Roll Likert answers into category scores. This is not a class label."""

from __future__ import annotations

from decimal import Decimal

from app.ml.instrument import InstrumentSpec, ItemSpec
from app.services.scoring import weighted_likert


def directed_item_score(value: int, item: ItemSpec) -> Decimal:
    return weighted_likert(int(value), item.weight, item.reverse_scored)


def category_scores_from_likert(
    answers: dict[str, int],
    instrument: InstrumentSpec,
) -> dict[str, float]:
    """Mean weighted directed score per category.

    Missing items leave that category absent so the caller can drop the row
    instead of inventing a value.
    """
    scores: dict[str, float] = {}
    for code in instrument.category_codes:
        items = instrument.items_for_category(code)
        values: list[Decimal] = []
        for item in items:
            if item.key not in answers:
                values = []
                break
            values.append(directed_item_score(answers[item.key], item))
        if not values:
            continue
        total = sum(values, Decimal("0"))
        scores[f"{code}_score"] = float((total / len(values)).quantize(Decimal("0.01")))
    return scores
