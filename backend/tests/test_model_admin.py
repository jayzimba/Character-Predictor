"""Phase 18: activate, archive and annotate models without deleting history."""

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.models import AuditLog, MLModel
from app.models.enums import ModelStatus


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _register_demo(api_client, admin, tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.training.models_directory", lambda: tmp_path)
    trained = api_client.post("/api/admin/models/train/demo", headers=admin)
    assert trained.status_code == 200
    evaluated = api_client.post("/api/admin/models/evaluate/demo", headers=admin)
    assert evaluated.status_code == 200
    return evaluated.json()["data"]


def test_user_cannot_administer_models(api_client, db_session, tmp_path, monkeypatch):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    evaluation = _register_demo(api_client, admin, tmp_path, monkeypatch)
    model_id = evaluation["selected_model_id"]

    assert api_client.get(f"/api/admin/models/{model_id}", headers=user).status_code == 403
    assert api_client.post(f"/api/admin/models/{model_id}/activate", headers=user).status_code == 403
    assert api_client.post(f"/api/admin/models/{model_id}/archive", headers=user).status_code == 403
    assert (
        api_client.patch(
            f"/api/admin/models/{model_id}",
            headers=user,
            json={"notes": "should fail"},
        ).status_code
        == 403
    )


def test_activate_archives_previous_and_keeps_one_active(
    api_client, db_session, tmp_path, monkeypatch
):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    evaluation = _register_demo(api_client, admin, tmp_path, monkeypatch)

    first = api_client.post("/api/admin/models/activate-selected", headers=admin)
    assert first.status_code == 200
    first_id = first.json()["data"]["id"]
    assert first.json()["data"]["status"] == ModelStatus.ACTIVE.value
    assert first.json()["data"]["artifact_present"] is True
    assert first_id == evaluation["selected_model_id"]

    registry = api_client.get("/api/admin/models", headers=admin).json()["data"]
    assert len(registry) == 3
    assert sum(row["status"] == ModelStatus.ACTIVE.value for row in registry) == 1
    assert all(
        row["status"] == ModelStatus.TRAINED.value
        for row in registry
        if row["id"] != first_id
    )

    other = next(row for row in registry if row["id"] != first_id)
    second = api_client.post(f"/api/admin/models/{other['id']}/activate", headers=admin)
    assert second.status_code == 200
    assert second.json()["data"]["status"] == ModelStatus.ACTIVE.value

    db_session.expire_all()
    rows = {row.id: row for row in db_session.query(MLModel).all()}
    assert sum(row.status == ModelStatus.ACTIVE.value for row in rows.values()) == 1
    assert rows[other["id"]].status == ModelStatus.ACTIVE.value
    assert rows[first_id].status == ModelStatus.ARCHIVED.value

    logs = db_session.query(AuditLog).filter(AuditLog.action == "MODEL_ACTIVATED").all()
    assert len(logs) == 2
    assert all(row.entity_type == "ml_model" for row in logs)


def test_model_detail_notes_and_archive(api_client, db_session, tmp_path, monkeypatch):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    evaluation = _register_demo(api_client, admin, tmp_path, monkeypatch)
    model_id = evaluation["selected_model_id"]

    detail = api_client.get(f"/api/admin/models/{model_id}", headers=admin)
    assert detail.status_code == 200
    data = detail.json()["data"]
    assert data["metrics"] is not None
    assert "matrix" in data["metrics"]["confusion_matrix"]
    assert data["prediction_count"] == 0
    assert data["artifact_present"] is True

    notes = api_client.patch(
        f"/api/admin/models/{model_id}",
        headers=admin,
        json={"notes": "Winner on held-out F1-macro. DEMO/SYNTHETIC labels."},
    )
    assert notes.status_code == 200
    assert "DEMO/SYNTHETIC" in notes.json()["data"]["notes"]

    activated = api_client.post(f"/api/admin/models/{model_id}/activate", headers=admin)
    assert activated.status_code == 200

    archived = api_client.post(f"/api/admin/models/{model_id}/archive", headers=admin)
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == ModelStatus.ARCHIVED.value

    db_session.expire_all()
    assert db_session.query(MLModel).filter(MLModel.status == ModelStatus.ACTIVE.value).count() == 0

    again = api_client.post(f"/api/admin/models/{model_id}/archive", headers=admin)
    assert again.status_code == 400

    missing = api_client.get("/api/admin/models/9999", headers=admin)
    assert missing.status_code == 404


def test_cannot_activate_model_without_artifact(api_client, db_session, tmp_path, monkeypatch):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    evaluation = _register_demo(api_client, admin, tmp_path, monkeypatch)
    model_id = evaluation["selected_model_id"]

    db_session.expire_all()
    row = db_session.get(MLModel, model_id)
    row.file_path = str(tmp_path / "missing.joblib")
    db_session.commit()

    failed = api_client.post(f"/api/admin/models/{model_id}/activate", headers=admin)
    assert failed.status_code == 400
    assert "artefact" in failed.json()["message"].lower()
