"""Phase 13: classify a completed assessment without inventing mix values."""

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.ml.constants import LABEL_ORDER
from app.ml.instrument import instrument_from_session
from app.ml.predict import features_from_assessment, load_estimator, mix_from_estimator
from app.models.enums import ModelStatus
from app.repositories import assessment as assessment_repository


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _complete_assessment(api_client, headers) -> dict:
    started = api_client.post(
        "/api/assessments",
        headers=headers,
        json={"consent_accepted": True},
    ).json()["data"]
    questions = api_client.get("/api/questions", headers=headers).json()["data"]["questions"]
    api_client.post(
        f"/api/assessments/{started['id']}/answers",
        headers=headers,
        json={"answers": [{"question_id": item["id"], "response_value": 4} for item in questions]},
    )
    submitted = api_client.post(f"/api/assessments/{started['id']}/submit", headers=headers)
    assert submitted.status_code == 200
    return submitted.json()["data"]


def test_classify_uses_demo_mode_without_active_model(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    assessment = _complete_assessment(api_client, headers)

    classified = api_client.post(
        "/api/predictions/classify",
        headers=headers,
        json={"assessment_id": assessment["id"]},
    )
    assert classified.status_code == 200
    data = classified.json()["data"]
    assert data["is_demo_mode"] is True
    assert data["mix_source"] == "demo_item_totals"
    assert data["model_id"] is None
    mix = data["personality_mix"]
    assert round(sum(mix.values()), 2) == 100.0
    assert data["predicted_personality"] in LABEL_ORDER
    assert "clinical" in data["disclaimer"].lower()

    dashboard = api_client.get("/api/users/me/dashboard", headers=headers).json()["data"]
    assert dashboard["latest_personality"]["code"] == data["predicted_personality"]
    assert dashboard["is_demo_mode"] is True
    assert dashboard["latest_mix"]["choleric"] == mix["choleric"]

    again = api_client.post(
        "/api/predictions/classify",
        headers=headers,
        json={"assessment_id": assessment["id"]},
    )
    assert again.status_code == 409


def test_classify_uses_active_model_predict_proba(
    api_client, db_session, tmp_path, monkeypatch
):
    seed_all(db_session)
    monkeypatch.setattr("app.services.training.models_directory", lambda: tmp_path)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)

    assert api_client.post("/api/admin/models/train/demo", headers=admin).status_code == 200
    evaluated = api_client.post("/api/admin/models/evaluate/demo", headers=admin)
    assert evaluated.status_code == 200
    activated = api_client.post("/api/admin/models/activate-selected", headers=admin)
    assert activated.status_code == 200
    assert activated.json()["data"]["status"] == ModelStatus.ACTIVE.value

    assessment = _complete_assessment(api_client, user)
    classified = api_client.post(
        "/api/predictions/classify",
        headers=user,
        json={"assessment_id": assessment["id"]},
    )
    assert classified.status_code == 200
    data = classified.json()["data"]
    assert data["is_demo_mode"] is True
    assert data["mix_source"] == "predict_proba"
    assert data["algorithm"] in {"DECISION_TREE", "NAIVE_BAYES", "KNN"}
    assert round(sum(data["personality_mix"].values()), 2) == 100.0

    db_session.expire_all()
    row = assessment_repository.get_by_id(db_session, assessment["id"])
    instrument = instrument_from_session(db_session)
    features = features_from_assessment(row, instrument)
    estimator = load_estimator(activated.json()["data"]["file_path"])
    predicted, confidence, mix, source = mix_from_estimator(estimator, features)
    assert source == "predict_proba"
    assert data["predicted_personality"] == predicted
    assert data["confidence"] == confidence
    assert data["personality_mix"]["choleric"] == mix["CHOLERIC"]


def test_classify_rejects_other_users_and_incomplete(api_client, db_session):
    seed_all(db_session)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=user,
        json={"consent_accepted": True},
    ).json()["data"]
    incomplete = api_client.post(
        "/api/predictions/classify",
        headers=user,
        json={"assessment_id": started["id"]},
    )
    assert incomplete.status_code == 400

    other = api_client.post(
        "/api/auth/register",
        json={
            "first_name": "Pat",
            "last_name": "Other",
            "email": "pat.other@example.com",
            "password": "Secure123",
            "confirm_password": "Secure123",
        },
    )
    other_headers = {"Authorization": f"Bearer {other.json()['data']['access_token']}"}
    completed = _complete_assessment(api_client, user)
    stolen = api_client.post(
        "/api/predictions/classify",
        headers=other_headers,
        json={"assessment_id": completed["id"]},
    )
    assert stolen.status_code == 404
