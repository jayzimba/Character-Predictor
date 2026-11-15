"""Phase 17: create, edit and deactivate questions without rewriting history."""

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _create_payload(**overrides) -> dict:
    payload = {
        "question_text": "I am comfortable trying a new approach when the first plan stalls.",
        "category_code": "adaptability",
        "personality_code": "SANGUINE",
        "weight": 1.0,
        "reverse_scored": False,
    }
    payload.update(overrides)
    return payload


def test_user_cannot_create_questions(api_client, db_session):
    seed_all(db_session)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    response = api_client.post(
        "/api/admin/questions",
        headers=user,
        json=_create_payload(),
    )
    assert response.status_code == 403


def test_admin_creates_question_and_participant_sees_it(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)

    created = api_client.post(
        "/api/admin/questions",
        headers=admin,
        json=_create_payload(),
    )
    assert created.status_code == 201
    row = created.json()["data"]
    assert row["scoring_locked"] is False
    assert row["answer_count"] == 0
    assert row["status"] == "ACTIVE"
    assert row["display_order"] == 33

    instrument = api_client.get("/api/questions", headers=user).json()["data"]
    assert instrument["question_count"] == 33
    assert any(item["id"] == row["id"] for item in instrument["questions"])


def test_deactivate_hides_item_from_participants(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    created = api_client.post(
        "/api/admin/questions",
        headers=admin,
        json=_create_payload(),
    ).json()["data"]

    deactivated = api_client.patch(
        f"/api/admin/questions/{created['id']}",
        headers=admin,
        json={"status": "INACTIVE"},
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["data"]["status"] == "INACTIVE"

    instrument = api_client.get("/api/questions", headers=user).json()["data"]
    assert instrument["question_count"] == 32
    assert all(item["id"] != created["id"] for item in instrument["questions"])


def test_answered_question_cannot_change_scoring_fields(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=user,
        json={"consent_accepted": True},
    ).json()["data"]
    questions = api_client.get("/api/questions", headers=user).json()["data"]["questions"]
    first_id = questions[0]["id"]
    api_client.post(
        f"/api/assessments/{started['id']}/answers",
        headers=user,
        json={"answers": [{"question_id": first_id, "response_value": 4}]},
    )

    locked = api_client.patch(
        f"/api/admin/questions/{first_id}",
        headers=admin,
        json={"weight": 2.0},
    )
    assert locked.status_code == 409

    deactivated = api_client.patch(
        f"/api/admin/questions/{first_id}",
        headers=admin,
        json={"status": "INACTIVE"},
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["data"]["scoring_locked"] is True
    assert deactivated.json()["data"]["answer_count"] == 1
