"""Likert scoring for feature engineering. This is not classification."""

from decimal import Decimal


def weighted_likert(
    response_value: int,
    weight: Decimal,
    reverse_scored: bool,
) -> Decimal:
    """Map 1–5 to a directed, weighted item score.

    Reverse-scored items flip the scale (1 becomes 5) before the weight is
    applied. The result is an input feature, not a temperament label.
    """
    if response_value < 1 or response_value > 5:
        raise ValueError("Likert responses must be between 1 and 5")
    directed = 6 - response_value if reverse_scored else response_value
    return (Decimal(directed) * Decimal(weight)).quantize(Decimal("0.01"))
