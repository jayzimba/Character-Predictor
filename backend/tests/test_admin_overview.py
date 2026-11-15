"""Phase 16: admin overview and assessment list, without Likert answers."""

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


def _complete_and_classify(api_client, headers) -> dict:
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
    classified = api_client.post(
        "/api/predictions/classify",
        headers=headers,
        json={"assessment_id": started["id"]},
    )
    assert classified.status_code == 200
    return classified.json()["data"]


def test_overview_requires_admin(api_client, db_session):
    seed_all(db_session)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    forbidden = api_client.get("/api/admin/overview", headers=user)
    assert forbidden.status_code == 403
    unauth = api_client.get("/api/admin/overview")
    assert unauth.status_code == 401


def test_overview_counts_seeded_users_without_invented_distribution(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    response = api_client.get("/api/admin/overview", headers=admin)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["users_total"] == 2
    assert data["users_admin"] == 1
    assert data["users_regular"] == 1
    assert data["assessments_completed"] == 0
    assert data["classifications_stored"] == 0
    assert data["personality_counts"] == {
        "choleric": 0,
        "melancholic": 0,
        "phlegmatic": 0,
        "sanguine": 0,
    }
    assert data["active_model"] is None


def test_overview_and_assessments_use_stored_predictions(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    classified = _complete_and_classify(api_client, user)
    code = classified["predicted_personality"].lower()

    overview = api_client.get("/api/admin/overview", headers=admin).json()["data"]
    assert overview["assessments_completed"] == 1
    assert overview["classifications_stored"] == 1
    assert overview["demo_classifications"] == 1
    assert overview["personality_counts"][code] == 1
    assert sum(overview["personality_counts"].values()) == 1

    listings = api_client.get("/api/admin/assessments", headers=admin)
    assert listings.status_code == 200
    rows = listings.json()["data"]
    match = next(item for item in rows if item["assessment_id"] == classified["assessment_id"])
    assert match["user_email"] == DEMO_USER_EMAIL
    assert match["has_prediction"] is True
    assert match["predicted_personality"] == classified["predicted_personality"]
    assert match["confidence"] == classified["confidence"]
    assert "answers" not in match
    assert "response_value" not in match
    dumped = listings.text
    assert "weighted_score" not in dumped


def test_regular_user_cannot_list_admin_assessments(api_client, db_session):
    seed_all(db_session)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    response = api_client.get("/api/admin/assessments", headers=user)
    assert response.status_code == 403
