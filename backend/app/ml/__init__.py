"""Machine-learning engine.

Phase 12: evaluate the held-out fold and register models.
Prediction from an active model starts in Phase 13.
See docs/ARCHITECTURE.md.
"""

from app.ml.evaluate import evaluate_estimators, evaluate_training_run
from app.ml.preprocessing import (
    PreparedDataset,
    knn_scaler_pipeline,
    prepare_csv,
    prepare_dataset,
)
from app.ml.train import train_classifiers

__all__ = [
    "PreparedDataset",
    "evaluate_estimators",
    "evaluate_training_run",
    "knn_scaler_pipeline",
    "prepare_csv",
    "prepare_dataset",
    "train_classifiers",
]
