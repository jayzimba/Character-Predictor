"""Phase 15: history lists the caller's assessments with stored predictions only."""

from app.database.seed import DEMO_USER_EMAIL, DEMO_USER_PASSWORD, seed_all


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _complete(api_client, headers) -> dict:
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


def test_history_requires_auth(api_client):
    response = api_client.get("/api/history")
    assert response.status_code == 401


def test_history_empty_for_new_user(api_client, db_session):
    seed_all(db_session)
    other = api_client.post(
        "/api/auth/register",
        json={
            "first_name": "Pat",
            "last_name": "History",
            "email": "pat.history@example.com",
            "password": "Secure123",
            "confirm_password": "Secure123",
        },
    )
    headers = {"Authorization": f"Bearer {other.json()['data']['access_token']}"}
    response = api_client.get("/api/history", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_history_lists_in_progress_without_invented_type(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=headers,
        json={"consent_accepted": True},
    ).json()["data"]
    history = api_client.get("/api/history", headers=headers)
    assert history.status_code == 200
    rows = history.json()["data"]
    match = next(item for item in rows if item["assessment_id"] == started["id"])
    assert match["status"] == "IN_PROGRESS"
    assert match["has_prediction"] is False
    assert match["personality_name"] is None
    assert match["confidence"] is None
    assert match["predicted_personality"] is None


def test_history_uses_stored_prediction(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    completed = _complete(api_client, headers)
    classified = api_client.post(
        "/api/predictions/classify",
        headers=headers,
        json={"assessment_id": completed["id"]},
    )
    assert classified.status_code == 200
    prediction = classified.json()["data"]

    history = api_client.get("/api/history", headers=headers)
    assert history.status_code == 200
    match = next(
        item
        for item in history.json()["data"]
        if item["assessment_id"] == completed["id"]
    )
    assert match["status"] == "COMPLETED"
    assert match["has_prediction"] is True
    assert match["predicted_personality"] == prediction["predicted_personality"]
    assert match["personality_name"] == prediction["personality_name"]
    assert match["confidence"] == prediction["confidence"]
    assert match["is_demo_mode"] is True
    assert "personality_mix" not in match

    other = api_client.post(
        "/api/auth/register",
        json={
            "first_name": "Pat",
            "last_name": "Other",
            "email": "pat.history.other@example.com",
            "password": "Secure123",
            "confirm_password": "Secure123",
        },
    )
    other_headers = {"Authorization": f"Bearer {other.json()['data']['access_token']}"}
    stolen = api_client.get("/api/history", headers=other_headers)
    assert stolen.status_code == 200
    assert all(item["assessment_id"] != completed["id"] for item in stolen.json()["data"])
