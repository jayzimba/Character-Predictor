"""Phase 4: registration, login, JWT, and server-side role checks."""

from app.core.security import decode_access_token
from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register_payload(**overrides) -> dict:
    payload = {
        "first_name": "Jordan",
        "last_name": "Lee",
        "email": "jordan.lee@example.com",
        "password": "Secure123",
        "confirm_password": "Secure123",
        "age_group": "AGE_18_24",
    }
    payload.update(overrides)
    return payload


def test_register_login_and_me(api_client, db_session):
    seed_all(db_session)

    created = api_client.post("/api/auth/register", json=_register_payload())
    assert created.status_code == 201
    body = created.json()
    assert body["success"] is True
    assert body["data"]["user"]["role"]["code"] == "USER"
    assert "password" not in body["data"]["user"]
    token = body["data"]["access_token"]
    assert decode_access_token(token)["role"] == "USER"

    me = api_client.get("/api/auth/me", headers=_auth_header(token))
    assert me.status_code == 200
    assert me.json()["data"]["email"] == "jordan.lee@example.com"


def test_duplicate_email_is_rejected(api_client, db_session):
    seed_all(db_session)
    first = api_client.post("/api/auth/register", json=_register_payload())
    assert first.status_code == 201
    second = api_client.post("/api/auth/register", json=_register_payload())
    assert second.status_code == 409
    assert second.json()["success"] is False


def test_password_mismatch_is_rejected(api_client, db_session):
    seed_all(db_session)
    response = api_client.post(
        "/api/auth/register",
        json=_register_payload(confirm_password="Different123"),
    )
    assert response.status_code == 422


def test_login_with_seeded_user(api_client, db_session):
    seed_all(db_session)
    response = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": DEMO_USER_PASSWORD},
    )
    assert response.status_code == 200
    assert response.json()["data"]["user"]["role"]["code"] == "USER"


def test_login_rejects_wrong_password(api_client, db_session):
    seed_all(db_session)
    response = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": "WrongPass1"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["message"]


def test_me_requires_a_token(api_client, db_session):
    seed_all(db_session)
    response = api_client.get("/api/auth/me")
    assert response.status_code == 401


def test_user_cannot_list_admin_users(api_client, db_session):
    seed_all(db_session)
    login = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": DEMO_USER_PASSWORD},
    )
    token = login.json()["data"]["access_token"]
    response = api_client.get("/api/admin/users", headers=_auth_header(token))
    assert response.status_code == 403


def test_admin_can_list_users(api_client, db_session):
    seed_all(db_session)
    login = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_ADMIN_PASSWORD},
    )
    token = login.json()["data"]["access_token"]
    response = api_client.get("/api/admin/users", headers=_auth_header(token))
    assert response.status_code == 200
    emails = [item["email"] for item in response.json()["data"]]
    assert DEMO_ADMIN_EMAIL in emails
    assert DEMO_USER_EMAIL in emails


def test_profile_update(api_client, db_session):
    seed_all(db_session)
    login = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": DEMO_USER_PASSWORD},
    )
    token = login.json()["data"]["access_token"]
    response = api_client.patch(
        "/api/users/me",
        headers=_auth_header(token),
        json={"first_name": "Samuel"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["first_name"] == "Samuel"


def test_password_reset_debug_flow(api_client, db_session):
    seed_all(db_session)
    requested = api_client.post(
        "/api/auth/password-reset/request",
        json={"email": DEMO_USER_EMAIL},
    )
    assert requested.status_code == 200
    token = requested.json()["data"]["reset_token"]

    confirmed = api_client.post(
        "/api/auth/password-reset/confirm",
        json={
            "token": token,
            "new_password": "NewPass123",
            "confirm_password": "NewPass123",
        },
    )
    assert confirmed.status_code == 200

    old_login = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": DEMO_USER_PASSWORD},
    )
    assert old_login.status_code == 401

    new_login = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": "NewPass123"},
    )
    assert new_login.status_code == 200
