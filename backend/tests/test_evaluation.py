"""Phase 12: held-out sklearn metrics and the model registry."""

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.ml.dataset.generate_demo import build_demo_frame
from app.ml.evaluate import evaluate_estimator, evaluate_training_run, select_best
from app.ml.instrument import instrument_from_catalog
from app.ml.preprocessing import prepare_dataset
from app.ml.train import train_classifiers
from app.models import MLModel, ModelMetric
from app.models.enums import ModelStatus


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _prepared():
    return prepare_dataset(
        build_demo_frame(n_per_class=25, seed=42),
        instrument_from_catalog(),
    )


def test_held_out_scores_match_sklearn(tmp_path):
    prepared = _prepared()
    run = train_classifiers(prepared, dataset_name="demo.csv", output_dir=tmp_path)
    result = evaluate_training_run(run, prepared)

    assert result.n_test == 20
    assert result.selected_algorithm
    by_name = {item.algorithm: item for item in result.scores}
    for model in run.models:
        expected = evaluate_estimator(model.estimator, prepared.X_test, prepared.y_test)
        actual = by_name[model.algorithm]
        assert actual.accuracy == expected["accuracy"]
        assert actual.f1_macro == expected["f1_macro"]
        assert actual.confusion_matrix["matrix"] == expected["confusion_matrix"]["matrix"]

    winner = select_best(result.scores)
    assert result.selected_algorithm == winner.algorithm
    assert sum(item.selected for item in result.scores) == 1


def test_evaluate_demo_requires_admin_and_prior_training(
    api_client, db_session, tmp_path, monkeypatch
):
    seed_all(db_session)
    monkeypatch.setattr("app.services.training.models_directory", lambda: tmp_path)

    denied = api_client.post("/api/admin/models/evaluate/demo")
    assert denied.status_code == 401

    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    assert api_client.post("/api/admin/models/evaluate/demo", headers=user).status_code == 403

    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    missing = api_client.post("/api/admin/models/evaluate/demo", headers=admin)
    assert missing.status_code == 400

    trained = api_client.post("/api/admin/models/train/demo", headers=admin)
    assert trained.status_code == 200

    evaluated = api_client.post("/api/admin/models/evaluate/demo", headers=admin)
    assert evaluated.status_code == 200
    data = evaluated.json()["data"]
    assert data["registered"] is True
    assert data["n_test"] == 20
    assert data["is_synthetic"] is True
    assert len(data["scores"]) == 3
    assert data["selected_algorithm"] in {row["algorithm"] for row in data["scores"]}
    assert "test_accuracy" not in data
    selected = next(row for row in data["scores"] if row["selected"])
    assert selected["model_id"] == data["selected_model_id"]

    registry = api_client.get("/api/admin/models", headers=admin).json()["data"]
    assert len(registry) == 3
    assert all(row["status"] == ModelStatus.TRAINED.value for row in registry)
    assert all(row["metrics"] is not None for row in registry)

    stored = db_session.query(MLModel).count()
    metrics = db_session.query(ModelMetric).count()
    assert stored == 3
    assert metrics == 3
