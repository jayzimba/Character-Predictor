"""Fit the three classical classifiers on a prepared training fold.

Held-out test evaluation and the model registry are Phase 12. Any numeric
scores written here come from scikit-learn on the training fold only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from app.ml.constants import DEFAULT_RANDOM_STATE, LABEL_ORDER
from app.ml.preprocessing import PreparedDataset
from app.models.enums import AlgorithmName

RUN_FILENAME = "last_training_run.json"
ARTEFACT_NAMES = {
    AlgorithmName.DECISION_TREE.value: "decision_tree.joblib",
    AlgorithmName.NAIVE_BAYES.value: "naive_bayes.joblib",
    AlgorithmName.KNN.value: "knn.joblib",
}


class TrainingError(ValueError):
    """The prepared dataset cannot be used to fit classifiers."""


@dataclass
class FittedModel:
    algorithm: str
    sklearn_class: str
    estimator: object
    file_name: str
    file_path: str | None
    uses_scaler: bool
    hyperparameters: dict
    cv: dict | None


@dataclass
class TrainingRun:
    trained_at: str
    dataset_name: str
    is_synthetic: bool
    feature_names: list[str]
    label_order: list[str]
    random_state: int
    n_train: int
    n_test: int
    class_counts_train: dict[str, int]
    held_out_evaluated: bool
    registered: bool
    cv_note: str
    warnings: list[str] = field(default_factory=list)
    models: list[FittedModel] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "trained_at": self.trained_at,
            "dataset_name": self.dataset_name,
            "is_synthetic": self.is_synthetic,
            "feature_names": self.feature_names,
            "label_order": self.label_order,
            "random_state": self.random_state,
            "n_train": self.n_train,
            "n_test": self.n_test,
            "class_counts_train": self.class_counts_train,
            "held_out_evaluated": self.held_out_evaluated,
            "registered": self.registered,
            "cv_note": self.cv_note,
            "warnings": self.warnings,
            "models": [
                {
                    "algorithm": item.algorithm,
                    "sklearn_class": item.sklearn_class,
                    "file_name": item.file_name,
                    "file_path": item.file_path,
                    "uses_scaler": item.uses_scaler,
                    "hyperparameters": item.hyperparameters,
                    "cv": item.cv,
                }
                for item in self.models
            ],
        }


def _cv_folds(y_train: np.ndarray) -> int | None:
    if y_train.size == 0:
        return None
    smallest = int(np.bincount(y_train).min())
    if smallest >= 5:
        return 5
    if smallest >= 3:
        return 3
    return None


def _cv_accuracy(estimator, X, y, folds: int, random_state: int) -> dict:
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)
    scores = cross_val_score(estimator, X, y, cv=splitter, scoring="accuracy")
    return {
        "folds": folds,
        "scoring": "accuracy",
        "mean": float(scores.mean()),
        "std": float(scores.std(ddof=0)),
        "scores": [float(value) for value in scores],
        "split": "training_fold_only",
    }


def _estimators(random_state: int) -> list[tuple[str, object, dict, bool]]:
    tree = DecisionTreeClassifier(random_state=random_state)
    bayes = GaussianNB()
    knn = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(n_neighbors=5)),
        ]
    )
    return [
        (
            AlgorithmName.DECISION_TREE.value,
            tree,
            {"random_state": random_state},
            False,
        ),
        (AlgorithmName.NAIVE_BAYES.value, bayes, {}, False),
        (
            AlgorithmName.KNN.value,
            knn,
            {"n_neighbors": 5, "scaler": "StandardScaler"},
            True,
        ),
    ]


def train_classifiers(
    prepared: PreparedDataset,
    *,
    dataset_name: str,
    output_dir: Path | None = None,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> TrainingRun:
    if prepared.X_train is None or prepared.y_train is None:
        raise TrainingError("A stratified training split is required before fitting.")
    if not prepared.report.ready_for_training:
        raise TrainingError("The dataset is not ready for training.")

    warnings = list(prepared.report.warnings)
    if prepared.report.is_synthetic:
        warnings.append(
            "These classifiers were fitted on DEMO/SYNTHETIC rows. "
            "Do not report them as research models."
        )
    warnings.append(
        "Held-out test metrics are not computed in this phase. "
        "Phase 12 will evaluate the same split with sklearn.metrics."
    )

    folds = _cv_folds(prepared.y_train)
    cv_note = (
        f"Stratified {folds}-fold accuracy on the training fold only."
        if folds
        else "Cross-validation was skipped: a class has fewer than 3 training rows."
    )

    run = TrainingRun(
        trained_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        dataset_name=dataset_name,
        is_synthetic=prepared.report.is_synthetic,
        feature_names=list(prepared.feature_names),
        label_order=list(LABEL_ORDER),
        random_state=random_state,
        n_train=int(len(prepared.X_train)),
        n_test=int(len(prepared.X_test) if prepared.X_test is not None else 0),
        class_counts_train={
            LABEL_ORDER[code]: int((prepared.y_train == code).sum())
            for code in range(len(LABEL_ORDER))
        },
        held_out_evaluated=False,
        registered=False,
        cv_note=cv_note,
        warnings=warnings,
    )

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    for algorithm, estimator, hyperparams, uses_scaler in _estimators(random_state):
        cv_payload = None
        if folds:
            cv_payload = _cv_accuracy(
                estimator, prepared.X_train, prepared.y_train, folds, random_state
            )
        estimator.fit(prepared.X_train, prepared.y_train)
        file_name = ARTEFACT_NAMES[algorithm]
        file_path = None
        if output_dir is not None:
            target = output_dir / file_name
            joblib.dump(
                {
                    "estimator": estimator,
                    "metadata": {
                        "algorithm": algorithm,
                        "feature_names": run.feature_names,
                        "label_order": run.label_order,
                        "is_synthetic": run.is_synthetic,
                        "dataset_name": dataset_name,
                        "held_out_evaluated": False,
                        "registered": False,
                    },
                },
                target,
            )
            file_path = str(target)
        run.models.append(
            FittedModel(
                algorithm=algorithm,
                sklearn_class=type(
                    estimator.named_steps["clf"] if uses_scaler else estimator
                ).__name__,
                estimator=estimator,
                file_name=file_name,
                file_path=file_path,
                uses_scaler=uses_scaler,
                hyperparameters=hyperparams,
                cv=cv_payload,
            )
        )

    if output_dir is not None:
        (output_dir / RUN_FILENAME).write_text(
            json.dumps(run.to_dict(), indent=2),
            encoding="utf-8",
        )
    return run


def load_last_run(output_dir: Path) -> dict | None:
    path = output_dir / RUN_FILENAME
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_artefacts(output_dir: Path) -> dict[str, object]:
    """Load fitted estimators saved by the last training run."""
    missing = [
        name for name in ARTEFACT_NAMES.values() if not (output_dir / name).exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Train the classifiers first. Missing: " + ", ".join(missing)
        )
    loaded = {}
    for algorithm, name in ARTEFACT_NAMES.items():
        payload = joblib.load(output_dir / name)
        loaded[algorithm] = payload["estimator"]
    return loaded


def write_run_dict(output_dir: Path, payload: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / RUN_FILENAME).write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
