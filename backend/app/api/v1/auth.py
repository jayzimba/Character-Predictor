"""Authentication routes. Registration always assigns the USER role."""

from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, DbSession
from app.core.rate_limit import limit_auth_attempts
from app.core.responses import success_response
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
)
from app.services import auth as auth_service

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    db: DbSession,
    _: None = Depends(limit_auth_attempts),
):
    data = auth_service.register_user(db, payload)
    return success_response(
        data=data,
        message="Account created",
        status_code=201,
    )


@router.post("/login")
def login(
    payload: LoginRequest,
    db: DbSession,
    _: None = Depends(limit_auth_attempts),
):
    data = auth_service.login_user(db, payload)
    return success_response(data=data, message="Signed in")


@router.get("/me")
def me(current_user: CurrentUser):
    return success_response(
        data=auth_service.get_profile(current_user),
        message="Current user",
    )


@router.post("/password-reset/request")
def request_password_reset(
    payload: PasswordResetRequest,
    db: DbSession,
    _: None = Depends(limit_auth_attempts),
):
    data = auth_service.request_password_reset(db, payload)
    return success_response(data=data, message=data["message"])


@router.post("/password-reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: DbSession,
    _: None = Depends(limit_auth_attempts),
):
    auth_service.confirm_password_reset(db, payload)
    return success_response(message="Password updated. You can sign in with the new password.")
