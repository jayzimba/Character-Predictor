"""Append-only audit records. Callers commit the surrounding transaction."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import AuditLog


def record(
    session: Session,
    *,
    actor_id: int | None,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    row = AuditLog(
        user_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    session.add(row)
    session.flush()
    return row


def count_all(session: Session) -> int:
    return int(session.scalar(select(func.count(AuditLog.id))) or 0)


def list_recent(
    session: Session, *, limit: int = 100, offset: int = 0
) -> list[AuditLog]:
    statement = (
        select(AuditLog)
        .options(selectinload(AuditLog.actor))
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.scalars(statement).all())
