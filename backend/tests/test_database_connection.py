"""Phase 3: FastAPI obtains a session and fails cleanly when MySQL cannot answer."""

from sqlalchemy.exc import OperationalError

from app.core.deps import db_session
from app.database.seed import seed_all
from app.main import app


def test_readiness_uses_injected_session(api_client, db_session):
    seed_all(db_session)

    response = api_client.get("/api/health/ready")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["status"] == "ready"
    assert body["data"]["database"]["connected"] is True
    assert body["data"]["database"]["personality_types"] == 4
    assert body["data"]["database"]["questions"] == 32


def test_readiness_returns_503_when_database_is_down():
    def _broken_db():
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    app.dependency_overrides[db_session] = _broken_db
    try:
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            response = client.get("/api/health/ready")
    finally:
        app.dependency_overrides.clear()

    body = response.json()
    assert response.status_code == 503
    assert body["success"] is False
    assert body["data"] is None
    assert "unavailable" in body["message"].lower()


def test_liveness_does_not_require_the_database():
    """Liveness must stay up so operators can still reach the process."""
    from fastapi.testclient import TestClient

    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "healthy"
