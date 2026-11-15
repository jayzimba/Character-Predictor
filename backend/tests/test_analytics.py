"""Phase 19: admin analytics are stored aggregates, never Likert answers."""

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


def test_analytics_requires_admin(api_client, db_session):
    seed_all(db_session)
    denied = api_client.get("/api/analytics")
    assert denied.status_code == 401
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    assert api_client.get("/api/analytics", headers=user).status_code == 403


def test_analytics_empty_counts_without_invented_mix(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    response = api_client.get("/api/analytics", headers=admin)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["totals"]["classifications_stored"] == 0
    assert data["totals"]["mean_confidence"] is None
    assert data["personality_counts"] == {
        "choleric": 0,
        "melancholic": 0,
        "phlegmatic": 0,
        "sanguine": 0,
    }
    assert data["window_days"] == 14
    assert len(data["series"]) == 14
    assert all(
        point["started"] == 0 and point["classified"] == 0 for point in data["series"]
    )
    assert "answers" not in data
    assert "response_value" not in response.text
    assert "weighted_score" not in response.text


def test_analytics_counts_stored_prediction(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    classified = _complete_and_classify(api_client, user)
    code = classified["predicted_personality"].lower()

    data = api_client.get("/api/analytics", headers=admin).json()["data"]
    totals = data["totals"]
    assert totals["assessments_completed"] == 1
    assert totals["classifications_stored"] == 1
    assert totals["demo_classifications"] == 1
    assert totals["completion_rate"] == 1.0
    assert totals["mean_confidence"] == classified["confidence"]
    assert data["personality_counts"][code] == 1
    assert sum(data["personality_counts"].values()) == 1
    assert data["source_counts"][0]["key"] == "DEMO"
    assert data["source_counts"][0]["count"] == 1
    today = data["series"][-1]
    assert today["completed"] == 1
    assert today["classified"] == 1
    assert today["demo"] == 1
    age = {item["key"]: item["count"] for item in data["age_group_counts"]}
    assert age.get("AGE_18_24") == 1
    dumped = str(data)
    assert "response_value" not in dumped
