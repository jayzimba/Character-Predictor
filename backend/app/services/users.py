"""Authenticated profile updates."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.user import ChangePasswordRequest, ProfileUpdateRequest, UserOut


def update_profile(session: Session, user: User, payload: ProfileUpdateRequest) -> dict:
    data = payload.model_dump(exclude_unset=True)
    if "first_name" in data and data["first_name"]:
        user.first_name = data["first_name"].strip()
    if "last_name" in data and data["last_name"]:
        user.last_name = data["last_name"].strip()
    if "gender" in data:
        user.gender = data["gender"].value if data["gender"] else None
    if "age_group" in data:
        user.age_group = data["age_group"].value if data["age_group"] else None
    session.commit()
    session.refresh(user)
    return UserOut.model_validate(user).model_dump()


def change_password(session: Session, user: User, payload: ChangePasswordRequest) -> None:
    if payload.new_password != payload.confirm_password:
        raise AppError("Passwords do not match", status_code=422)
    if not verify_password(payload.current_password, user.password_hash):
        raise AppError("Current password is incorrect", status_code=400)
    if not any(char.isalpha() for char in payload.new_password) or not any(
        char.isdigit() for char in payload.new_password
    ):
        raise AppError(
            "Password must contain at least one letter and one number",
            status_code=422,
        )
    user.password_hash = hash_password(payload.new_password)
    session.commit()
