"""Validate, clean and featurise labelled assessment datasets.

Does not train a classifier. StandardScaler is returned unfitted so Phase 11
can fit it on the training fold only (required for honest KNN).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import IO

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.ml.constants import (
    COLLECTED_ORIGIN,
    DEFAULT_RANDOM_STATE,
    DEFAULT_TEST_SIZE,
    DEMO_ORIGIN,
    LABEL_COLUMN,
    LABEL_ORDER,
    LIKERT_MAX,
    LIKERT_MIN,
    ORIGIN_COLUMN,
    UNSPECIFIED_ORIGIN,
)
from app.ml.feature_engineering import category_scores_from_likert
from app.ml.instrument import InstrumentSpec

FORMAT_LIKERT = "likert"
FORMAT_CATEGORY_SCORES = "category_scores"


class DatasetError(ValueError):
    """The file cannot be turned into a training matrix."""


@dataclass
class DatasetReport:
    format: str
    is_synthetic: bool
    origin_counts: dict[str, int]
    rows_in: int
    rows_kept: int
    duplicates_removed: int
    missing_dropped: int
    invalid_range_dropped: int
    invalid_label_dropped: int
    class_counts: dict[str, int]
    feature_names: list[str]
    preview: list[dict]
    split: dict | None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    scaling_applied: bool = False
    scaling_note: str = (
        "StandardScaler is not fitted here. KNN will use a scikit-learn "
        "Pipeline fitted on the training fold only."
    )
    ready_for_training: bool = False

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "is_synthetic": self.is_synthetic,
            "origin_counts": self.origin_counts,
            "rows_in": self.rows_in,
            "rows_kept": self.rows_kept,
            "duplicates_removed": self.duplicates_removed,
            "missing_dropped": self.missing_dropped,
            "invalid_range_dropped": self.invalid_range_dropped,
            "invalid_label_dropped": self.invalid_label_dropped,
            "class_counts": self.class_counts,
            "feature_names": self.feature_names,
            "preview": self.preview,
            "split": self.split,
            "warnings": self.warnings,
            "errors": self.errors,
            "scaling_applied": self.scaling_applied,
            "scaling_note": self.scaling_note,
            "ready_for_training": self.ready_for_training,
        }


@dataclass
class PreparedDataset:
    X: np.ndarray
    y: np.ndarray
    y_labels: np.ndarray
    feature_names: list[str]
    X_train: np.ndarray | None
    X_test: np.ndarray | None
    y_train: np.ndarray | None
    y_test: np.ndarray | None
    report: DatasetReport

    def knn_scaler_pipeline(self) -> Pipeline:
        """Unfitted scaler for Phase 11. Never fit this on the full matrix."""
        return Pipeline([("scaler", StandardScaler())])


def read_dataset_csv(source: str | Path | IO[str] | IO[bytes] | bytes) -> pd.DataFrame:
    if isinstance(source, bytes):
        return pd.read_csv(BytesIO(source), comment="#")
    return pd.read_csv(source, comment="#")


def _normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = {column: str(column).strip().lower() for column in frame.columns}
    return frame.rename(columns=renamed)


def _normalise_label(value) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().upper().replace(" ", "_")
    aliases = {
        "CHOLERIC": "CHOLERIC",
        "MELANCHOLIC": "MELANCHOLIC",
        "PHLEGMATIC": "PHLEGMATIC",
        "SANGUINE": "SANGUINE",
    }
    return aliases.get(text)


def _normalise_origin(value) -> str:
    if pd.isna(value):
        return UNSPECIFIED_ORIGIN
    text = str(value).strip().upper()
    if "DEMO" in text or "SYNTHETIC" in text:
        return DEMO_ORIGIN
    if text == COLLECTED_ORIGIN:
        return COLLECTED_ORIGIN
    return UNSPECIFIED_ORIGIN


def detect_format(frame: pd.DataFrame, instrument: InstrumentSpec) -> str:
    columns = set(frame.columns)
    has_scores = all(column in columns for column in instrument.feature_columns)
    has_likert = all(column in columns for column in instrument.likert_columns)
    if has_scores:
        return FORMAT_CATEGORY_SCORES
    if has_likert:
        return FORMAT_LIKERT
    missing_scores = [column for column in instrument.feature_columns if column not in columns]
    missing_likert = [column for column in instrument.likert_columns if column not in columns]
    raise DatasetError(
        "CSV must include either Likert columns "
        f"({instrument.likert_columns[0]}…{instrument.likert_columns[-1]}) "
        "or category score columns "
        f"({instrument.feature_columns[0]}…{instrument.feature_columns[-1]}). "
        f"Missing scores: {missing_scores[:4]}. Missing Likert: {missing_likert[:4]}."
    )


def encode_labels(labels: list[str] | np.ndarray) -> np.ndarray:
    index = {name: position for position, name in enumerate(LABEL_ORDER)}
    try:
        return np.array([index[str(label)] for label in labels], dtype=np.int64)
    except KeyError as exc:
        raise DatasetError(f"Unknown personality label: {exc}") from exc


def decode_labels(codes: np.ndarray) -> np.ndarray:
    return np.array([LABEL_ORDER[int(code)] for code in codes], dtype=object)


def _is_valid_likert(value) -> bool:
    if pd.isna(value):
        return False
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    if not number.is_integer():
        return False
    return LIKERT_MIN <= int(number) <= LIKERT_MAX


def knn_scaler_pipeline() -> Pipeline:
    return Pipeline([("scaler", StandardScaler())])


def prepare_dataset(
    frame: pd.DataFrame,
    instrument: InstrumentSpec,
    *,
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> PreparedDataset:
    warnings: list[str] = []
    errors: list[str] = []

    if frame.empty:
        raise DatasetError("The CSV contains no data rows.")

    working = _normalise_columns(frame.copy())
    if LABEL_COLUMN not in working.columns:
        raise DatasetError(f"The CSV must include a '{LABEL_COLUMN}' column.")

    fmt = detect_format(working, instrument)
    rows_in = len(working)

    if ORIGIN_COLUMN in working.columns:
        working[ORIGIN_COLUMN] = working[ORIGIN_COLUMN].map(_normalise_origin)
    else:
        working[ORIGIN_COLUMN] = UNSPECIFIED_ORIGIN
        warnings.append(
            f"No '{ORIGIN_COLUMN}' column. Rows are marked {UNSPECIFIED_ORIGIN} "
            "and must not be presented as a research sample."
        )

    original_labels = working[LABEL_COLUMN]
    working[LABEL_COLUMN] = original_labels.map(_normalise_label)
    unknown_label = original_labels.notna() & working[LABEL_COLUMN].isna()
    invalid_label_dropped = int(unknown_label.sum())
    working = working.loc[~unknown_label]

    missing_before = len(working)
    required = [LABEL_COLUMN]
    required.extend(
        instrument.likert_columns if fmt == FORMAT_LIKERT else instrument.feature_columns
    )
    working = working.dropna(subset=required)
    missing_dropped = missing_before - len(working)

    working = working[working[LABEL_COLUMN].isin(LABEL_ORDER)]

    invalid_range_dropped = 0
    if fmt == FORMAT_LIKERT:
        valid_mask = working[list(instrument.likert_columns)].map(_is_valid_likert).all(axis=1)
        invalid_range_dropped = int((~valid_mask).sum())
        working = working[valid_mask]
        for column in instrument.likert_columns:
            working[column] = working[column].astype(int)
        feature_rows = [
            category_scores_from_likert(
                {key: int(row[key]) for key in instrument.likert_columns},
                instrument,
            )
            for row in working.to_dict(orient="records")
        ]
        features = pd.DataFrame(feature_rows, index=working.index)
        incomplete = features[list(instrument.feature_columns)].isna().any(axis=1)
        if incomplete.any():
            missing_dropped += int(incomplete.sum())
            features = features.loc[~incomplete]
            working = working.loc[features.index]
    else:
        for column in instrument.feature_columns:
            working[column] = pd.to_numeric(working[column], errors="coerce")
        valid_mask = working[list(instrument.feature_columns)].notna().all(axis=1)
        extra_missing = int((~valid_mask).sum())
        missing_dropped += extra_missing
        working = working[valid_mask]
        out_of_range = ~working[list(instrument.feature_columns)].apply(
            lambda col: col.between(LIKERT_MIN, LIKERT_MAX * 5)
        ).all(axis=1)
        invalid_range_dropped = int(out_of_range.sum())
        working = working.loc[~out_of_range]
        features = working[list(instrument.feature_columns)].copy()

    combined = features.join(working[[LABEL_COLUMN, ORIGIN_COLUMN]])
    before_dedup = len(combined)
    combined = combined.drop_duplicates(
        subset=[*instrument.feature_columns, LABEL_COLUMN],
        keep="first",
    )
    duplicates_removed = before_dedup - len(combined)

    origin_counts = (
        combined[ORIGIN_COLUMN].value_counts().astype(int).to_dict()
        if not combined.empty
        else {}
    )
    is_synthetic = origin_counts.get(DEMO_ORIGIN, 0) > 0
    if is_synthetic:
        warnings.append(
            "This file contains DEMO/SYNTHETIC rows. Metrics from any later "
            "model trained on it are not research findings."
        )
    if origin_counts.get(COLLECTED_ORIGIN, 0) and is_synthetic:
        warnings.append("Synthetic and collected rows are mixed. Keep them separate for evaluation.")

    if combined.empty:
        errors.append("No usable labelled rows remained after cleaning.")

    class_counts = (
        combined[LABEL_COLUMN].value_counts().reindex(LABEL_ORDER, fill_value=0).astype(int).to_dict()
        if not combined.empty
        else {label: 0 for label in LABEL_ORDER}
    )

    preview = []
    for _, row in combined.head(5).iterrows():
        preview.append(
            {
                **{name: round(float(row[name]), 2) for name in instrument.feature_columns},
                LABEL_COLUMN: row[LABEL_COLUMN],
                ORIGIN_COLUMN: row[ORIGIN_COLUMN],
            }
        )

    X = (
        combined[list(instrument.feature_columns)].to_numpy(dtype=np.float64)
        if not combined.empty
        else np.empty((0, len(instrument.feature_columns)))
    )
    y_labels = (
        combined[LABEL_COLUMN].to_numpy(dtype=object)
        if not combined.empty
        else np.array([], dtype=object)
    )
    y = encode_labels(y_labels) if len(y_labels) else np.array([], dtype=np.int64)

    split_info = None
    X_train = X_test = y_train = y_test = None
    ready = False
    counts = [int(class_counts[label]) for label in LABEL_ORDER]
    if combined.empty:
        pass
    elif min(counts) < 2:
        warnings.append(
            "Stratified 80/20 split was skipped: need at least two rows per "
            "personality class. Training is a later phase."
        )
    else:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=random_state,
                stratify=y,
            )
        except ValueError as exc:
            warnings.append(f"Stratified 80/20 split was skipped: {exc}")
        else:
            split_info = {
                "test_size": test_size,
                "random_state": random_state,
                "stratified": True,
                "train_size": int(len(X_train)),
                "held_out_size": int(len(X_test)),
                "train_class_counts": {
                    LABEL_ORDER[code]: int((y_train == code).sum())
                    for code in range(len(LABEL_ORDER))
                },
                "test_class_counts": {
                    LABEL_ORDER[code]: int((y_test == code).sum())
                    for code in range(len(LABEL_ORDER))
                },
            }
            ready = True

    if ready and is_synthetic:
        warnings.append("The split is ready for a later training phase on DEMO data only.")

    report = DatasetReport(
        format=fmt,
        is_synthetic=is_synthetic,
        origin_counts={str(key): int(value) for key, value in origin_counts.items()},
        rows_in=rows_in,
        rows_kept=int(len(combined)),
        duplicates_removed=int(duplicates_removed),
        missing_dropped=int(missing_dropped),
        invalid_range_dropped=int(invalid_range_dropped),
        invalid_label_dropped=int(invalid_label_dropped),
        class_counts=class_counts,
        feature_names=list(instrument.feature_columns),
        preview=preview,
        split=split_info,
        warnings=warnings,
        errors=errors,
        ready_for_training=ready,
    )
    return PreparedDataset(
        X=X,
        y=y,
        y_labels=y_labels,
        feature_names=list(instrument.feature_columns),
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        report=report,
    )


def prepare_csv(
    source: str | Path | IO[str] | IO[bytes] | bytes,
    instrument: InstrumentSpec,
    **kwargs,
) -> PreparedDataset:
    return prepare_dataset(read_dataset_csv(source), instrument, **kwargs)
