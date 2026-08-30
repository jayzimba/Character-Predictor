"""Registration, login, and password reset. JWT is created here, not in routers."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    hash_password,
    token_expiry_seconds,
    verify_password,
)
from app.models import User
from app.repositories import password_reset as reset_repository
from app.repositories import user as user_repository
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserOut


def _to_user_out(user: User) -> UserOut:
    return UserOut.model_validate(user)


def _token_payload(user: User) -> dict:
    return TokenResponse(
        access_token=create_access_token(user_id=user.id, role=user.role.code),
        token_type="bearer",
        expires_in=token_expiry_seconds(),
        user=_to_user_out(user),
    ).model_dump()


def register_user(session: Session, payload: RegisterRequest) -> dict:
    if user_repository.get_by_email(session, payload.email):
        raise AppError("An account with this email already exists", status_code=409)

    role = user_repository.get_default_user_role(session)
    if role is None:
        raise AppError("User role is not configured. Run the database seed.", status_code=500)

    try:
        user = user_repository.create_user(
            session,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            gender=payload.gender.value if payload.gender else None,
            age_group=payload.age_group.value if payload.age_group else None,
            role=role,
        )
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise AppError("An account with this email already exists", status_code=409) from exc

    return _token_payload(user)


def login_user(session: Session, payload: LoginRequest) -> dict:
    user = user_repository.get_by_email(session, payload.email)
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        raise AppError("Invalid email or password", status_code=401)
    return _token_payload(user)


def get_profile(user: User) -> dict:
    return _to_user_out(user).model_dump()


def request_password_reset(session: Session, payload: PasswordResetRequest) -> dict:
    """Always succeeds. The raw token is returned only in debug mode."""
    user = user_repository.get_by_email(session, payload.email)
    response = {
        "message": "If that email is registered, a reset token has been issued."
    }
    if user is None or not user.is_active:
        return response

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    reset_repository.invalidate_unused_for_user(session, user.id, now)
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    reset_repository.create_token(
        session,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=now + timedelta(minutes=30),
    )
    session.commit()

    if get_settings().app_debug:
        response["reset_token"] = raw_token
        response["demo_note"] = (
            "Returned only because APP_DEBUG=true. A production system would "
            "email this token and never include it in the API response."
        )
    return response


def confirm_password_reset(session: Session, payload: PasswordResetConfirm) -> None:
    token_hash = hashlib.sha256(payload.token.encode("utf-8")).hexdigest()
    record = reset_repository.get_unused_by_hash(session, token_hash)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if record is None or record.expires_at < now:
        raise AppError("Invalid or expired reset token", status_code=400)

    record.user.password_hash = hash_password(payload.new_password)
    record.used_at = now
    session.commit()
