"""Fit classifiers from a prepared split. Does not register or evaluate the test fold."""

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.ml.constants import DEMO_CSV_NAME
from app.ml.preprocessing import PreparedDataset
from app.ml.train import TrainingError, load_last_run, train_classifiers
from app.schemas.training import TrainingRunOut
from app.services import datasets as dataset_service

DISCLAIMER = (
    "Classifiers are fitted on the training fold only. Held-out test "
    "metrics and the model registry belong to a later phase. DEMO/SYNTHETIC "
    "fits must not be reported as research models."
)


def models_directory() -> Path:
    settings = get_settings()
    path = Path(settings.ml_models_dir)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    return path


def _to_schema(payload: dict) -> TrainingRunOut:
    return TrainingRunOut(disclaimer=DISCLAIMER, **payload)


def _fit(prepared: PreparedDataset, dataset_name: str) -> TrainingRunOut:
    try:
        run = train_classifiers(
            prepared,
            dataset_name=dataset_name,
            output_dir=models_directory(),
        )
    except TrainingError as exc:
        raise AppError(str(exc), status_code=400) from exc
    return _to_schema(run.to_dict())


def train_demo(session: Session) -> TrainingRunOut:
    prepared = dataset_service.prepared_demo(session)
    return _fit(prepared, DEMO_CSV_NAME)


def train_upload(session: Session, filename: str, content: bytes) -> TrainingRunOut:
    prepared = dataset_service.prepared_from_bytes(session, filename, content)
    return _fit(prepared, Path(filename).name)


def last_training_run() -> TrainingRunOut | None:
    payload = load_last_run(models_directory())
    if payload is None:
        return None
    return _to_schema(payload)
