"""Password-reset token persistence. Tokens are stored hashed."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import PasswordResetToken, User


def create_token(
    session: Session,
    *,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> PasswordResetToken:
    record = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    session.add(record)
    session.flush()
    return record


def invalidate_unused_for_user(session: Session, user_id: int, now: datetime) -> None:
    tokens = session.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        )
    ).all()
    for token in tokens:
        token.used_at = now


def get_unused_by_hash(
    session: Session,
    token_hash: str,
) -> PasswordResetToken | None:
    statement = (
        select(PasswordResetToken)
        .options(selectinload(PasswordResetToken.user).selectinload(User.role))
        .where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
        )
    )
    return session.scalar(statement)
