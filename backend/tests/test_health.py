"""Phase 1: the API process starts and reports a healthy status."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_current_phase_metadata():
    response = client.get("/")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["phase"] == 21


def test_health_endpoint():
    response = client.get("/api/health")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert "version" in body["data"]
