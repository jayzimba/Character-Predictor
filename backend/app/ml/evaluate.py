"""Held-out evaluation. Every number comes from sklearn.metrics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from app.ml.constants import LABEL_ORDER

EVAL_FILENAME = "last_evaluation.json"
from app.ml.preprocessing import PreparedDataset
from app.ml.train import TrainingRun

SELECTION_RULE = (
    "Highest held-out F1-macro, then accuracy, then precision-macro, "
    "then algorithm name. Scores come from sklearn.metrics on the test fold."
)


class EvaluationError(ValueError):
    """The held-out fold cannot be scored."""


@dataclass
class ModelScores:
    algorithm: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float
    confusion_matrix: dict
    cv_folds: int | None
    cv_mean_accuracy: float | None
    selected: bool = False

    def sort_key(self) -> tuple:
        return (
            self.f1_macro,
            self.accuracy,
            self.precision_macro,
            self.algorithm,
        )

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "accuracy": self.accuracy,
            "precision_macro": self.precision_macro,
            "recall_macro": self.recall_macro,
            "f1_macro": self.f1_macro,
            "precision_weighted": self.precision_weighted,
            "recall_weighted": self.recall_weighted,
            "f1_weighted": self.f1_weighted,
            "confusion_matrix": self.confusion_matrix,
            "cv_folds": self.cv_folds,
            "cv_mean_accuracy": self.cv_mean_accuracy,
            "selected": self.selected,
        }


@dataclass
class EvaluationResult:
    dataset_name: str
    is_synthetic: bool
    n_test: int
    selection_rule: str
    selected_algorithm: str
    scores: list[ModelScores]
    warnings: list[str]

    def to_dict(self) -> dict:
        return {
            "dataset_name": self.dataset_name,
            "is_synthetic": self.is_synthetic,
            "n_test": self.n_test,
            "selection_rule": self.selection_rule,
            "selected_algorithm": self.selected_algorithm,
            "scores": [item.to_dict() for item in self.scores],
            "warnings": self.warnings,
        }


def score_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    labels = list(range(len(LABEL_ORDER)))
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(
            precision_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        ),
        "confusion_matrix": {
            "labels": list(LABEL_ORDER),
            "matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        },
    }


def evaluate_estimator(estimator, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    return score_predictions(y_test, estimator.predict(X_test))


def select_best(scores: list[ModelScores]) -> ModelScores:
    return max(scores, key=lambda item: item.sort_key())


def evaluate_estimators(
    *,
    estimators: dict[str, object],
    prepared: PreparedDataset,
    dataset_name: str,
    is_synthetic: bool,
    cv_by_algorithm: dict[str, dict | None] | None = None,
) -> EvaluationResult:
    if prepared.X_test is None or prepared.y_test is None or len(prepared.X_test) == 0:
        raise EvaluationError("A held-out test fold is required for evaluation.")

    warnings = [
        "These metrics were computed with sklearn.metrics on the held-out test fold.",
        "They are not hard-coded. A later phase serves predictions from an active model.",
    ]
    if is_synthetic or prepared.report.is_synthetic:
        warnings.append(
            "The test fold is DEMO/SYNTHETIC. Do not report these scores as research findings."
        )

    rows: list[ModelScores] = []
    for algorithm, estimator in estimators.items():
        payload = evaluate_estimator(estimator, prepared.X_test, prepared.y_test)
        cv = (cv_by_algorithm or {}).get(algorithm)
        rows.append(
            ModelScores(
                algorithm=algorithm,
                cv_folds=cv["folds"] if cv else None,
                cv_mean_accuracy=cv["mean"] if cv else None,
                **payload,
            )
        )

    winner = select_best(rows)
    for row in rows:
        row.selected = row.algorithm == winner.algorithm

    return EvaluationResult(
        dataset_name=dataset_name,
        is_synthetic=is_synthetic,
        n_test=int(len(prepared.X_test)),
        selection_rule=SELECTION_RULE,
        selected_algorithm=winner.algorithm,
        scores=sorted(rows, key=lambda item: item.sort_key(), reverse=True),
        warnings=warnings,
    )


def evaluate_training_run(
    run: TrainingRun,
    prepared: PreparedDataset,
    estimators: dict[str, object] | None = None,
) -> EvaluationResult:
    loaded = estimators or {item.algorithm: item.estimator for item in run.models}
    cv_by_algorithm = {item.algorithm: item.cv for item in run.models}
    return evaluate_estimators(
        estimators=loaded,
        prepared=prepared,
        dataset_name=run.dataset_name,
        is_synthetic=run.is_synthetic,
        cv_by_algorithm=cv_by_algorithm,
    )
