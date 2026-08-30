"""Phase 7: dashboard summary reads persisted assessments only."""

from datetime import datetime
from decimal import Decimal

from app.database.seed import DEMO_USER_EMAIL, DEMO_USER_PASSWORD, seed_all
from app.models import Assessment, PersonalityType, PredictionResult, QuestionnaireVersion
from app.models.enums import AssessmentStatus


def _login(api_client) -> str:
    response = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": DEMO_USER_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_dashboard_requires_auth(api_client, db_session):
    seed_all(db_session)
    response = api_client.get("/api/users/me/dashboard")
    assert response.status_code == 401


def test_empty_dashboard_for_new_user(api_client, db_session):
    seed_all(db_session)
    token = _login(api_client)

    response = api_client.get(
        "/api/users/me/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["assessments_completed"] == 0
    assert data["assessments_in_progress"] == 0
    assert data["latest_personality"] is None
    assert data["latest_mix"] is None
    assert data["is_demo_mode"] is False
    assert data["completion"] is None


def test_dashboard_reports_stored_prediction(api_client, db_session):
    seed_all(db_session)
    token = _login(api_client)
    me = api_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = me.json()["data"]["id"]

    version = db_session.query(QuestionnaireVersion).one()
    choleric = (
        db_session.query(PersonalityType).filter_by(code="CHOLERIC").one()
    )
    assessment = Assessment(
        user_id=user_id,
        questionnaire_version_id=version.id,
        status=AssessmentStatus.COMPLETED.value,
        started_at=datetime(2026, 8, 1, 10, 0, 0),
        completed_at=datetime(2026, 8, 1, 10, 20, 0),
        consent_accepted_at=datetime(2026, 8, 1, 10, 0, 0),
    )
    db_session.add(assessment)
    db_session.flush()
    db_session.add(
        PredictionResult(
            assessment_id=assessment.id,
            personality_type_id=choleric.id,
            predicted_personality="CHOLERIC",
            confidence_score=Decimal("0.8200"),
            choleric_percentage=Decimal("82.00"),
            melancholic_percentage=Decimal("7.00"),
            phlegmatic_percentage=Decimal("5.00"),
            sanguine_percentage=Decimal("6.00"),
            is_demo_mode=True,
        )
    )
    db_session.commit()

    response = api_client.get(
        "/api/users/me/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()["data"]
    assert data["assessments_completed"] == 1
    assert data["latest_personality"]["code"] == "CHOLERIC"
    assert data["latest_mix"]["choleric"] == 82.0
    assert data["latest_mix"]["sanguine"] == 6.0
    assert data["latest_confidence"] == 0.82
    assert data["is_demo_mode"] is True
    assert data["completion"]["percent"] == 100
