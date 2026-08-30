"""Phase 9: start, save and submit assessments without classifying."""

from decimal import Decimal

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.models import AssessmentAnswer, Question
from app.services.scoring import weighted_likert


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _start(api_client, headers) -> dict:
    response = api_client.post(
        "/api/assessments",
        headers=headers,
        json={"consent_accepted": True},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_weighted_likert_reverses_low_agreement():
    assert weighted_likert(1, Decimal("1.00"), True) == Decimal("5.00")
    assert weighted_likert(5, Decimal("1.00"), True) == Decimal("1.00")
    assert weighted_likert(4, Decimal("2.00"), False) == Decimal("8.00")


def test_start_requires_auth(api_client, db_session):
    seed_all(db_session)
    response = api_client.post("/api/assessments", json={"consent_accepted": True})
    assert response.status_code == 401


def test_start_requires_consent(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    response = api_client.post(
        "/api/assessments",
        headers=headers,
        json={"consent_accepted": False},
    )
    assert response.status_code == 400


def test_start_is_idempotent_while_in_progress(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    first = _start(api_client, headers)
    second = _start(api_client, headers)
    assert first["id"] == second["id"]
    assert first["status"] == "IN_PROGRESS"
    assert first["answered"] == 0
    assert first["total"] == 32


def test_save_answers_and_hide_weighted_score(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    assessment = _start(api_client, headers)
    questions = api_client.get("/api/questions", headers=headers).json()["data"]["questions"]
    first_id = questions[0]["id"]

    saved = api_client.post(
        f"/api/assessments/{assessment['id']}/answers",
        headers=headers,
        json={"answers": [{"question_id": first_id, "response_value": 4}]},
    )
    assert saved.status_code == 200
    body = saved.json()["data"]
    assert body["answered"] == 1
    assert body["answers"][0]["response_value"] == 4
    assert "weighted_score" not in saved.text

    loaded = api_client.get(f"/api/assessments/{assessment['id']}", headers=headers)
    assert loaded.json()["data"]["answers"][0]["question_id"] == first_id


def test_reverse_scored_item_stores_directed_weight(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    assessment = _start(api_client, headers)
    reverse_item = (
        db_session.query(Question).filter_by(reverse_scored=True).order_by(Question.id).first()
    )
    assert reverse_item is not None

    response = api_client.post(
        f"/api/assessments/{assessment['id']}/answers",
        headers=headers,
        json={"answers": [{"question_id": reverse_item.id, "response_value": 1}]},
    )
    assert response.status_code == 200

    stored = (
        db_session.query(AssessmentAnswer)
        .filter_by(assessment_id=assessment["id"], question_id=reverse_item.id)
        .one()
    )
    db_session.refresh(stored)
    assert stored.weighted_score == Decimal("5.00")


def test_submit_rejects_incomplete_then_completes(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    assessment = _start(api_client, headers)
    questions = api_client.get("/api/questions", headers=headers).json()["data"]["questions"]

    incomplete = api_client.post(
        f"/api/assessments/{assessment['id']}/submit",
        headers=headers,
    )
    assert incomplete.status_code == 400

    payload = {
        "answers": [
            {"question_id": item["id"], "response_value": 3} for item in questions
        ]
    }
    saved = api_client.post(
        f"/api/assessments/{assessment['id']}/answers",
        headers=headers,
        json=payload,
    )
    assert saved.status_code == 200
    assert saved.json()["data"]["answered"] == 32

    submitted = api_client.post(
        f"/api/assessments/{assessment['id']}/submit",
        headers=headers,
    )
    assert submitted.status_code == 200
    data = submitted.json()["data"]
    assert data["status"] == "COMPLETED"
    assert data["answered"] == 32
    assert "classification" in submitted.json()["message"].lower()
    assert "predicted" not in submitted.text.lower()

    again = api_client.post(
        f"/api/assessments/{assessment['id']}/submit",
        headers=headers,
    )
    assert again.status_code == 409

    dashboard = api_client.get("/api/users/me/dashboard", headers=headers)
    assert dashboard.json()["data"]["assessments_completed"] == 1
    assert dashboard.json()["data"]["latest_personality"] is None
    assert dashboard.json()["data"]["latest_mix"] is None

    retake = _start(api_client, headers)
    assert retake["id"] != assessment["id"]
    assert retake["status"] == "IN_PROGRESS"


def test_user_cannot_open_another_users_assessment(api_client, db_session):
    seed_all(db_session)
    user_headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    assessment = _start(api_client, user_headers)
    admin_headers = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)

    response = api_client.get(
        f"/api/assessments/{assessment['id']}",
        headers=admin_headers,
    )
    assert response.status_code == 404
