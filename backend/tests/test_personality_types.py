"""Phase 3: public catalogue is read through the service/repository layers."""

from app.database.seed import seed_all


def test_personality_types_endpoint(api_client, db_session):
    seed_all(db_session)

    response = api_client.get("/api/personality-types")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    codes = [item["code"] for item in body["data"]]
    assert codes == ["CHOLERIC", "MELANCHOLIC", "PHLEGMATIC", "SANGUINE"]
    assert "clinical" in body["data"][0]["disclaimer"].lower()
