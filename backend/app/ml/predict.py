"""Turn one completed assessment into a class label and a mix.

The mix is either sklearn ``predict_proba`` or a documented DEMO MODE
normalisation of personality-linked item totals. Percentages are never invented.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np

from app.ml.collected import assessment_likert_row
from app.ml.constants import LABEL_ORDER
from app.ml.feature_engineering import category_scores_from_likert, directed_item_score
from app.ml.instrument import InstrumentSpec
from app.models import Assessment

MIX_SOURCE_PROBA = "predict_proba"
MIX_SOURCE_DEMO = "demo_item_totals"
DEMO_REASON_NO_MODEL = "No ACTIVE model is registered. A labelled rule-based fallback was used."
DEMO_REASON_SYNTHETIC = (
    "The active model was trained on DEMO/SYNTHETIC data. "
    "Do not report this result as a research finding."
)


class PredictionError(ValueError):
    """The assessment cannot be turned into a feature vector."""


@dataclass
class Inference:
    predicted_code: str
    confidence: float
    mix: dict[str, float]
    mix_source: str
    is_demo_mode: bool
    demo_reason: str | None
    algorithm: str | None
    model_id: int | None


def features_from_assessment(assessment: Assessment, instrument: InstrumentSpec) -> np.ndarray:
    answers = assessment_likert_row(assessment)
    if any(key not in answers for key in instrument.likert_columns):
        raise PredictionError("Every active item must be answered before classification.")
    scores = category_scores_from_likert(answers, instrument)
    if len(scores) != len(instrument.feature_columns):
        raise PredictionError("Category features could not be completed for this assessment.")
    return np.array(
        [[scores[column] for column in instrument.feature_columns]],
        dtype=np.float64,
    )


def _round_mix(raw: dict[str, float]) -> dict[str, float]:
    rounded = {code: round(float(raw.get(code, 0.0)), 2) for code in LABEL_ORDER}
    drift = round(100.0 - sum(rounded.values()), 2)
    top = max(LABEL_ORDER, key=lambda code: (rounded[code], code))
    rounded[top] = round(rounded[top] + drift, 2)
    return rounded


def demo_inference(assessment: Assessment, instrument: InstrumentSpec) -> Inference:
    """Normalise personality-linked item totals. This is not a trained classifier."""
    answers = assessment_likert_row(assessment)
    totals = {code: 0.0 for code in LABEL_ORDER}
    for item in instrument.items:
        if item.key not in answers or not item.personality_code:
            continue
        totals[item.personality_code] += float(directed_item_score(answers[item.key], item))
    vector = np.array([totals[code] for code in LABEL_ORDER], dtype=np.float64)
    if float(vector.sum()) <= 0:
        mix = {code: 25.0 for code in LABEL_ORDER}
        predicted = LABEL_ORDER[0]
        confidence = 0.25
    else:
        mix = _round_mix(
            {code: float(value / vector.sum() * 100.0) for code, value in zip(LABEL_ORDER, vector)}
        )
        predicted = LABEL_ORDER[int(vector.argmax())]
        confidence = float(vector.max() / vector.sum())
    return Inference(
        predicted_code=predicted,
        confidence=round(confidence, 4),
        mix=mix,
        mix_source=MIX_SOURCE_DEMO,
        is_demo_mode=True,
        demo_reason=DEMO_REASON_NO_MODEL,
        algorithm=None,
        model_id=None,
    )


def load_estimator(file_path: str | Path):
    payload = joblib.load(file_path)
    if isinstance(payload, dict) and "estimator" in payload:
        return payload["estimator"]
    return payload


def mix_from_estimator(estimator, features: np.ndarray) -> tuple[str, float, dict[str, float], str]:
    predicted_index = int(estimator.predict(features)[0])
    predicted = LABEL_ORDER[predicted_index]
    if not hasattr(estimator, "predict_proba"):
        mix = {code: 0.0 for code in LABEL_ORDER}
        mix[predicted] = 100.0
        return predicted, 1.0, mix, "predicted_class_only"
    proba = estimator.predict_proba(features)[0]
    classes = [int(value) for value in estimator.classes_]
    raw = {code: 0.0 for code in LABEL_ORDER}
    for class_index, probability in zip(classes, proba):
        raw[LABEL_ORDER[class_index]] = float(probability) * 100.0
    confidence = float(max(proba))
    return predicted, round(confidence, 4), _round_mix(raw), MIX_SOURCE_PROBA


def model_inference(
    *,
    estimator,
    features: np.ndarray,
    model_id: int,
    algorithm: str,
    is_synthetic: bool,
) -> Inference:
    predicted, confidence, mix, source = mix_from_estimator(estimator, features)
    return Inference(
        predicted_code=predicted,
        confidence=confidence,
        mix=mix,
        mix_source=source,
        is_demo_mode=is_synthetic,
        demo_reason=DEMO_REASON_SYNTHETIC if is_synthetic else None,
        algorithm=algorithm,
        model_id=model_id,
    )
