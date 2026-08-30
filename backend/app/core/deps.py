"""FastAPI dependencies.

Routers import CurrentUser / AdminUser from here so authentication
stays in one place. Frontend role checks are never trusted.
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models import User
from app.models.enums import RoleCode
from app.repositories import user as user_repository


def db_session() -> Generator[Session, None, None]:
    """FastAPI-facing session dependency. Tests override this function."""
    yield from get_db()


DbSession = Annotated[Session, Depends(db_session)]

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    db: DbSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError("Not authenticated", status_code=401)
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (ValueError, KeyError, TypeError) as exc:
        raise AppError("Invalid or expired token", status_code=401) from exc

    user = user_repository.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise AppError("Not authenticated", status_code=401)
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role.code != RoleCode.ADMIN.value:
        raise AppError("Administrator access required", status_code=403)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
