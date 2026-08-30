"""Authenticated profile. Role cannot be changed from these endpoints."""

from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.core.responses import success_response
from app.schemas.user import ChangePasswordRequest, ProfileUpdateRequest
from app.services import auth as auth_service
from app.services import dashboard as dashboard_service
from app.services import users as user_service

router = APIRouter()


@router.get("/me/dashboard")
def get_my_dashboard(db: DbSession, current_user: CurrentUser):
    data = dashboard_service.get_user_dashboard(db, current_user)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Dashboard loaded",
    )


@router.get("/me")
def get_my_profile(current_user: CurrentUser):
    return success_response(
        data=auth_service.get_profile(current_user),
        message="Profile loaded",
    )


@router.patch("/me")
def update_my_profile(
    payload: ProfileUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    data = user_service.update_profile(db, current_user, payload)
    return success_response(data=data, message="Profile updated")


@router.post("/me/password")
def change_my_password(
    payload: ChangePasswordRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    user_service.change_password(db, current_user, payload)
    return success_response(message="Password updated")
