"""Phase 20: headers, RBAC, isolation, and validation that does not leak secrets."""

from app.core.openapi import openapi_urls
from app.core.security import decode_access_token
from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.models import User


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def _register(api_client, email: str, password: str = "OtherUser1") -> dict[str, str]:
    created = api_client.post(
        "/api/auth/register",
        json={
            "first_name": "Nora",
            "last_name": "West",
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )
    assert created.status_code == 201
    return {"Authorization": f"Bearer {created.json()['data']['access_token']}"}


def test_openapi_docs_follow_debug_flag():
    assert openapi_urls(debug=True)["docs_url"] == "/docs"
    assert openapi_urls(debug=False) == {
        "docs_url": None,
        "redoc_url": None,
        "openapi_url": None,
    }


def test_security_headers_are_present(api_client):
    response = api_client.get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "no-store" in response.headers["Cache-Control"]


def test_jwt_carries_only_identity_claims(api_client, db_session):
    seed_all(db_session)
    login = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": DEMO_USER_PASSWORD},
    )
    token = login.json()["data"]["access_token"]
    payload = decode_access_token(token)
    assert set(payload) == {"sub", "role", "iat", "exp"}
    assert "email" not in payload
    assert "password" not in payload


def test_register_rejects_role_injection_and_echoes_no_password(api_client, db_session):
    seed_all(db_session)
    secret = "InjectAdmin1"
    response = api_client.post(
        "/api/auth/register",
        json={
            "first_name": "Pat",
            "last_name": "Ng",
            "email": "pat.ng@example.com",
            "password": secret,
            "confirm_password": secret,
            "role": "ADMIN",
        },
    )
    assert response.status_code == 422
    assert secret not in response.text
    assert "password_hash" not in response.text


def test_register_always_assigns_user_role(api_client, db_session):
    seed_all(db_session)
    created = api_client.post(
        "/api/auth/register",
        json={
            "first_name": "Pat",
            "last_name": "Ng",
            "email": "pat.ng@example.com",
            "password": "Secure123",
            "confirm_password": "Secure123",
        },
    )
    assert created.status_code == 201
    assert created.json()["data"]["user"]["role"]["code"] == "USER"
    assert "password" not in created.json()["data"]["user"]
    assert "password_hash" not in created.text


def test_inactive_user_cannot_sign_in(api_client, db_session):
    seed_all(db_session)
    user = db_session.query(User).filter_by(email=DEMO_USER_EMAIL).one()
    user.is_active = False
    db_session.commit()
    response = api_client.post(
        "/api/auth/login",
        json={"email": DEMO_USER_EMAIL, "password": DEMO_USER_PASSWORD},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["message"]


def test_likert_out_of_range_is_rejected(api_client, db_session):
    seed_all(db_session)
    headers = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=headers,
        json={"consent_accepted": True},
    ).json()["data"]
    questions = api_client.get("/api/questions", headers=headers).json()["data"]["questions"]
    response = api_client.post(
        f"/api/assessments/{started['id']}/answers",
        headers=headers,
        json={"answers": [{"question_id": questions[0]["id"], "response_value": 6}]},
    )
    assert response.status_code == 422


ADMIN_GETS = [
    "/api/admin/overview",
    "/api/admin/users",
    "/api/admin/assessments",
    "/api/admin/questions",
    "/api/admin/models",
    "/api/admin/audit-logs",
    "/api/analytics",
]


def test_admin_routes_require_admin_role(api_client, db_session):
    seed_all(db_session)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    for path in ADMIN_GETS:
        assert api_client.get(path).status_code == 401
        assert api_client.get(path, headers=user).status_code == 403


def test_regular_user_cannot_read_another_users_answers(api_client, db_session):
    seed_all(db_session)
    owner = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=owner,
        json={"consent_accepted": True},
    ).json()["data"]
    questions = api_client.get("/api/questions", headers=owner).json()["data"]["questions"]
    api_client.post(
        f"/api/assessments/{started['id']}/answers",
        headers=owner,
        json={"answers": [{"question_id": questions[0]["id"], "response_value": 2}]},
    )
    other = _register(api_client, "nora.isolation@example.com")
    response = api_client.get(f"/api/assessments/{started['id']}", headers=other)
    assert response.status_code == 404
    assert "response_value" not in response.text
    assert "weighted_score" not in response.text


def test_admin_catalogue_and_audit_omit_likert_and_passwords(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=user,
        json={"consent_accepted": True},
    ).json()["data"]
    questions = api_client.get("/api/questions", headers=user).json()["data"]["questions"]
    api_client.post(
        f"/api/assessments/{started['id']}/answers",
        headers=user,
        json={"answers": [{"question_id": questions[0]["id"], "response_value": 2}]},
    )

    users = api_client.get("/api/admin/users", headers=admin)
    assert users.status_code == 200
    assert "password_hash" not in users.text
    assert DEMO_USER_PASSWORD not in users.text

    assessments = api_client.get("/api/admin/assessments", headers=admin)
    assert assessments.status_code == 200
    assert "response_value" not in assessments.text
    assert "weighted_score" not in assessments.text

    created = api_client.post(
        "/api/admin/questions",
        headers=admin,
        json={
            "question_text": "I stay calm when a plan has to change at short notice.",
            "category_code": "adaptability",
            "personality_code": "PHLEGMATIC",
            "weight": 1.0,
        },
    )
    assert created.status_code == 201

    logs = api_client.get("/api/admin/audit-logs", headers=admin)
    assert logs.status_code == 200
    data = logs.json()["data"]
    assert data["total"] >= 1
    actions = {item["action"] for item in data["items"]}
    assert "QUESTION_CREATED" in actions
    dumped = logs.text
    assert "response_value" not in dumped
    assert "password_hash" not in dumped
    assert "weighted_score" not in dumped


def test_auth_rate_limit_returns_429(api_client, db_session):
    seed_all(db_session)
    payload = {"email": DEMO_USER_EMAIL, "password": "WrongPass1"}
    statuses = [
        api_client.post("/api/auth/login", json=payload).status_code for _ in range(21)
    ]
    assert 429 in statuses
    assert statuses[-1] == 429
