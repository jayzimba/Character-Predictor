"""Administrator audit-log listing. Likert answers are never stored here."""

from sqlalchemy.orm import Session

from app.repositories import audit as audit_repository
from app.schemas.audit import AuditLogListOut, AuditLogOut

DISCLAIMER = (
    "These rows are administrator actions already stored in MySQL. "
    "They do not include Likert answers or passwords."
)


def _to_out(row) -> AuditLogOut:
    return AuditLogOut(
        id=row.id,
        action=row.action,
        entity_type=row.entity_type,
        entity_id=row.entity_id,
        details=row.details,
        actor_email=row.actor.email if row.actor else None,
        created_at=row.created_at,
    )


def list_logs(
    session: Session, *, limit: int = 100, offset: int = 0
) -> tuple[AuditLogListOut, str]:
    rows = audit_repository.list_recent(session, limit=limit, offset=offset)
    payload = AuditLogListOut(
        total=audit_repository.count_all(session),
        items=[_to_out(row) for row in rows],
    )
    return payload, DISCLAIMER
