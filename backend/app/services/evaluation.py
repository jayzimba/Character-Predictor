"""Score the held-out fold and write the model registry."""

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.ml.constants import DEMO_CSV_NAME
from app.ml.evaluate import EVAL_FILENAME, EvaluationError, evaluate_estimators
from app.ml.preprocessing import PreparedDataset
from app.ml.train import load_artefacts, load_last_run, write_run_dict
from app.repositories import ml_models as model_repository
from app.schemas.evaluation import EvaluationOut, ModelScoresOut, RegistryModelOut
from app.services import datasets as dataset_service
from app.services import training as training_service

DISCLAIMER = (
    "Held-out metrics come from sklearn.metrics on the test fold. "
    "DEMO/SYNTHETIC scores must not be reported as research findings. "
    "Live predictions use the one ACTIVE registered model."
)


def _parse_trained_at(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=None)


def last_evaluation() -> EvaluationOut | None:
    path = training_service.models_directory() / EVAL_FILENAME
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return EvaluationOut(**payload)


def list_registry(session: Session) -> list[RegistryModelOut]:
    """Kept for callers that still import evaluation.list_registry."""
    from app.services import models_admin as models_admin_service

    return models_admin_service.list_models(session)


def _evaluate_prepared(
    session: Session,
    prepared: PreparedDataset,
    dataset_name: str,
) -> EvaluationOut:
    output_dir = training_service.models_directory()
    last_run = load_last_run(output_dir)
    if last_run is None:
        raise AppError("Train the classifiers before evaluating the held-out fold.", status_code=400)
    try:
        estimators = load_artefacts(output_dir)
    except FileNotFoundError as exc:
        raise AppError(str(exc), status_code=400) from exc

    cv_by_algorithm = {
        item["algorithm"]: item.get("cv") for item in last_run.get("models", [])
    }
    try:
        result = evaluate_estimators(
            estimators=estimators,
            prepared=prepared,
            dataset_name=dataset_name,
            is_synthetic=prepared.report.is_synthetic,
            cv_by_algorithm=cv_by_algorithm,
        )
    except EvaluationError as exc:
        raise AppError(str(exc), status_code=400) from exc

    version = model_repository.next_run_version(session)
    trained_at = _parse_trained_at(last_run.get("trained_at"))
    dataset_size = int(last_run.get("n_train", 0)) + int(last_run.get("n_test", 0))
    file_by_algorithm = {
        item["algorithm"]: item.get("file_path") for item in last_run.get("models", [])
    }

    scored = []
    selected_id = None
    for row in result.scores:
        notes = (
            "Selected on held-out F1-macro (sklearn.metrics). Not activated for prediction."
            if row.selected
            else "Evaluated on the held-out fold. Not selected."
        )
        model = model_repository.create_registered_model(
            session,
            algorithm=row.algorithm,
            version=version,
            file_path=file_by_algorithm.get(row.algorithm),
            dataset_name=dataset_name,
            dataset_size=dataset_size or result.n_test + int(last_run.get("n_train", 0)),
            train_size=int(last_run.get("n_train", 0)),
            test_size=result.n_test,
            is_synthetic_dataset=result.is_synthetic,
            trained_at=trained_at,
            notes=notes,
            scores=row.to_dict(),
        )
        payload = row.to_dict()
        payload["model_id"] = model.id
        scored.append(ModelScoresOut(**payload))
        if row.selected:
            selected_id = model.id

    session.commit()

    last_run["held_out_evaluated"] = True
    last_run["registered"] = True
    write_run_dict(output_dir, last_run)

    evaluation = EvaluationOut(
        disclaimer=DISCLAIMER,
        dataset_name=result.dataset_name,
        is_synthetic=result.is_synthetic,
        n_test=result.n_test,
        selection_rule=result.selection_rule,
        selected_algorithm=result.selected_algorithm,
        selected_model_id=selected_id,
        version=version,
        registered=True,
        scores=scored,
        warnings=result.warnings,
    )
    (output_dir / EVAL_FILENAME).write_text(
        evaluation.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return evaluation


def evaluate_demo(session: Session) -> EvaluationOut:
    return _evaluate_prepared(session, dataset_service.prepared_demo(session), DEMO_CSV_NAME)


def evaluate_upload(session: Session, filename: str, content: bytes) -> EvaluationOut:
    return _evaluate_prepared(
        session,
        dataset_service.prepared_from_bytes(session, filename, content),
        Path(filename).name,
    )
