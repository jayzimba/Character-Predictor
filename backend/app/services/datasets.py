"""Admin dataset validation. Does not train or invent accuracy numbers."""

from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.ml.collected import collected_frame
from app.ml.constants import DEMO_CSV_HEADER, DEMO_CSV_NAME, LABEL_COLUMN
from app.ml.dataset import demo_csv_path
from app.ml.instrument import instrument_from_session
from app.ml.preprocessing import DatasetError, PreparedDataset, prepare_csv, prepare_dataset
from app.schemas.dataset import DatasetReportOut, DemoDatasetOut

MAX_UPLOAD_BYTES = 2 * 1024 * 1024
ALLOWED_SUFFIXES = {".csv"}

DISCLAIMER = (
    "Preprocessing prepares category features for a later training phase. "
    "No classifier is fitted here. DEMO/SYNTHETIC rows must not be reported "
    "as research findings."
)


def _report(source: str, prepared: PreparedDataset, *, unlabelled_collected: int = 0) -> DatasetReportOut:
    payload = prepared.report.to_dict()
    return DatasetReportOut(
        source=source,
        disclaimer=DISCLAIMER,
        unlabelled_collected=unlabelled_collected,
        trained=False,
        **payload,
    )


def demo_metadata() -> DemoDatasetOut:
    path = demo_csv_path()
    return DemoDatasetOut(
        filename=DEMO_CSV_NAME,
        path=str(path),
        disclaimer=DEMO_CSV_HEADER,
    )


def prepared_demo(session: Session) -> PreparedDataset:
    instrument = instrument_from_session(session)
    try:
        return prepare_csv(demo_csv_path(), instrument)
    except DatasetError as exc:
        raise AppError(str(exc), status_code=400) from exc


def prepared_from_bytes(session: Session, filename: str, content: bytes) -> PreparedDataset:
    if len(content) > MAX_UPLOAD_BYTES:
        raise AppError("CSV is larger than 2 MB.", status_code=400)
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise AppError("Upload a .csv file.", status_code=400)
    if not content.strip():
        raise AppError("The uploaded file is empty.", status_code=400)
    instrument = instrument_from_session(session)
    try:
        return prepare_csv(content, instrument)
    except DatasetError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
        raise AppError("The file could not be read as CSV.", status_code=400) from exc


def validate_demo(session: Session) -> DatasetReportOut:
    return _report(DEMO_CSV_NAME, prepared_demo(session))


def validate_bytes(session: Session, filename: str, content: bytes) -> DatasetReportOut:
    return _report(Path(filename).name, prepared_from_bytes(session, filename, content))


def preview_collected_assessments(session: Session) -> DatasetReportOut:
    instrument = instrument_from_session(session)
    frame = collected_frame(session, instrument)
    if frame.empty:
        raise AppError(
            "No completed assessments can be turned into features yet.",
            status_code=404,
        )
    labelled = frame[frame[LABEL_COLUMN].notna()].copy()
    unlabelled = int(frame[LABEL_COLUMN].isna().sum())
    if labelled.empty:
        return DatasetReportOut(
            source="completed_assessments",
            disclaimer=DISCLAIMER,
            format="likert",
            is_synthetic=False,
            origin_counts={"COLLECTED": int(len(frame))},
            rows_in=int(len(frame)),
            rows_kept=0,
            duplicates_removed=0,
            missing_dropped=0,
            invalid_range_dropped=0,
            invalid_label_dropped=0,
            unlabelled_collected=unlabelled,
            class_counts={},
            feature_names=list(instrument.feature_columns),
            preview=[],
            split=None,
            warnings=[
                f"{unlabelled} completed assessment(s) produced category scores, "
                "but none have a stored class label yet. Labelling happens after "
                "the prediction phase."
            ],
            errors=[],
            scaling_applied=False,
            scaling_note=(
                "StandardScaler is not fitted here. KNN will use a scikit-learn "
                "Pipeline fitted on the training fold only."
            ),
            ready_for_training=False,
            trained=False,
        )
    try:
        prepared = prepare_dataset(labelled, instrument)
    except DatasetError as exc:
        raise AppError(str(exc), status_code=400) from exc
    return _report("completed_assessments", prepared, unlabelled_collected=unlabelled)
