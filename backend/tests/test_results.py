"""Phase 14: results dashboard reads a stored prediction and catalogue copy."""

from app.database.seed import DEMO_USER_EMAIL, DEMO_USER_PASSWORD, seed_all


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


def test_latest_result_requires_auth(api_client):
    response = api_client.get("/api/results/latest")
    assert response.status_code == 401


def test_latest_result_404_without_classification(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    response = api_client.get("/api/results/latest", headers=headers)
    assert response.status_code == 404
    assert "classified" in response.json()["message"].lower()


def test_results_use_stored_mix_and_catalogue_writeup(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    classified = _complete_and_classify(api_client, headers)

    latest = api_client.get("/api/results/latest", headers=headers)
    assert latest.status_code == 200
    data = latest.json()["data"]
    mix = data["personality_mix"]

    assert data["assessment_id"] == classified["assessment_id"]
    assert data["headline"] == f"Your assessment indicates {classified['personality_name']}."
    assert "diagnos" not in data["headline"].lower()
    assert "clinical" in data["disclaimer"].lower()
    assert data["mix_source"] == "stored"
    assert data["predicted_personality"] == classified["predicted_personality"]
    assert mix == classified["personality_mix"]
    assert round(sum(mix.values()), 2) == 100.0
    assert data["personality"]["code"] == classified["predicted_personality"]
    assert data["personality"]["name"] == classified["personality_name"]
    assert data["personality"]["strengths"]
    assert data["personality"]["development_areas"]
    assert data["personality"]["career_environments"]
    assert data["personality"]["development_suggestions"]
    assert data["is_demo_mode"] is True

    by_id = api_client.get(f"/api/results/{classified['assessment_id']}", headers=headers)
    assert by_id.status_code == 200
    assert by_id.json()["data"]["personality_mix"] == mix

    dashboard = api_client.get("/api/users/me/dashboard", headers=headers).json()["data"]
    assert dashboard["latest_mix"]["choleric"] == mix["choleric"]
    assert dashboard["latest_personality"]["code"] == data["predicted_personality"]


def test_result_hides_other_users_and_unclassified(api_client, db_session):
    seed_all(db_session)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=user,
        json={"consent_accepted": True},
    ).json()["data"]
    unclassified = api_client.get(f"/api/results/{started['id']}", headers=user)
    assert unclassified.status_code == 404

    classified = _complete_and_classify(api_client, user)
    other = api_client.post(
        "/api/auth/register",
        json={
            "first_name": "Pat",
            "last_name": "Other",
            "email": "pat.results@example.com",
            "password": "Secure123",
            "confirm_password": "Secure123",
        },
    )
    other_headers = {"Authorization": f"Bearer {other.json()['data']['access_token']}"}
    stolen = api_client.get(
        f"/api/results/{classified['assessment_id']}",
        headers=other_headers,
    )
    assert stolen.status_code == 404
