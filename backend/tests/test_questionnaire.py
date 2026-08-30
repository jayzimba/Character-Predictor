"""Phase 8: the active questionnaire is served from the database."""

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.models import Question, QuestionnaireVersion
from app.models.enums import QuestionStatus


def _login(api_client, email: str, password: str) -> str:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_questions_require_auth(api_client, db_session):
    seed_all(db_session)
    response = api_client.get("/api/questions")
    assert response.status_code == 401


def test_user_receives_active_instrument_without_scoring_fields(api_client, db_session):
    seed_all(db_session)
    token = _login(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)

    response = api_client.get(
        "/api/questions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["version_code"] == "v1"
    assert data["question_count"] == 32
    assert len(data["questions"]) == 32
    assert data["questions"][0]["display_order"] == 1
    assert data["likert_scale"][0]["value"] == 1
    dumped = response.text
    assert "reverse_scored" not in dumped
    assert "weight" not in dumped
    assert "personality_trait" not in dumped
    assert "personality_type" not in dumped


def test_inactive_questions_are_hidden_from_participants(api_client, db_session):
    seed_all(db_session)
    question = db_session.query(Question).order_by(Question.display_order).first()
    question.status = QuestionStatus.INACTIVE.value
    db_session.commit()

    token = _login(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    response = api_client.get(
        "/api/questions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json()["data"]["question_count"] == 31


def test_user_cannot_list_admin_questions(api_client, db_session):
    seed_all(db_session)
    token = _login(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    response = api_client.get(
        "/api/admin/questions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_admin_sees_scoring_metadata(api_client, db_session):
    seed_all(db_session)
    token = _login(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    response = api_client.get(
        "/api/admin/questions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    rows = response.json()["data"]
    assert len(rows) == 32
    assert any(row["reverse_scored"] is True for row in rows)
    assert all("weight" in row for row in rows)
    assert all(row["personality_trait"]["code"] for row in rows)


def test_missing_active_version_is_not_found(api_client, db_session):
    seed_all(db_session)
    version = db_session.query(QuestionnaireVersion).one()
    version.is_active = False
    db_session.commit()

    token = _login(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    response = api_client.get(
        "/api/questions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
