"""Phase 11: fit DT, NB and KNN on the training fold only."""

from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.ml.dataset.generate_demo import build_demo_frame
from app.ml.instrument import instrument_from_catalog
from app.ml.preprocessing import prepare_dataset
from app.ml.train import train_classifiers
from app.models.enums import AlgorithmName


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _prepared():
    instrument = instrument_from_catalog()
    return prepare_dataset(build_demo_frame(n_per_class=25, seed=42), instrument)


def test_train_classifiers_fits_three_models_on_training_fold(tmp_path):
    prepared = _prepared()
    run = train_classifiers(prepared, dataset_name="demo.csv", output_dir=tmp_path)

    assert run.held_out_evaluated is False
    assert run.registered is False
    assert run.is_synthetic is True
    assert run.n_train == 80
    assert run.n_test == 20
    assert {item.algorithm for item in run.models} == {
        AlgorithmName.DECISION_TREE.value,
        AlgorithmName.NAIVE_BAYES.value,
        AlgorithmName.KNN.value,
    }

    by_name = {item.algorithm: item for item in run.models}
    assert isinstance(by_name[AlgorithmName.DECISION_TREE.value].estimator, DecisionTreeClassifier)
    knn = by_name[AlgorithmName.KNN.value]
    assert knn.uses_scaler is True
    assert isinstance(knn.estimator, Pipeline)
    assert isinstance(knn.estimator.named_steps["clf"], KNeighborsClassifier)
    assert hasattr(knn.estimator.named_steps["scaler"], "n_features_in_")
    assert knn.estimator.named_steps["scaler"].n_features_in_ == 16

    for item in run.models:
        assert item.cv is not None
        assert item.cv["split"] == "training_fold_only"
        assert item.cv["folds"] == 5
        assert 0 <= item.cv["mean"] <= 1
        assert (tmp_path / item.file_name).exists()
        labels = item.estimator.predict(prepared.X_train[:1])
        assert int(labels[0]) in range(4)

    payload = run.to_dict()
    assert "test_accuracy" not in payload
    assert payload["held_out_evaluated"] is False


def test_train_demo_requires_admin(api_client, db_session, tmp_path, monkeypatch):
    seed_all(db_session)
    monkeypatch.setattr("app.services.training.models_directory", lambda: tmp_path)

    denied = api_client.post("/api/admin/models/train/demo")
    assert denied.status_code == 401

    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    forbidden = api_client.post("/api/admin/models/train/demo", headers=user)
    assert forbidden.status_code == 403

    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    trained = api_client.post("/api/admin/models/train/demo", headers=admin)
    assert trained.status_code == 200
    data = trained.json()["data"]
    assert data["is_synthetic"] is True
    assert data["held_out_evaluated"] is False
    assert data["registered"] is False
    assert len(data["models"]) == 3
    assert "test_accuracy" not in data
    assert all(model["cv"]["split"] == "training_fold_only" for model in data["models"])

    listed = api_client.get("/api/admin/models/training", headers=admin)
    assert listed.status_code == 200
    assert listed.json()["data"]["n_train"] == 80
    assert listed.json()["data"]["dataset_name"] == "temperament_demo_v1.csv"
