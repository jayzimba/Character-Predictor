"""Audit-log payloads. Details never include Likert answers or passwords."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    entity_type: str | None = None
    entity_id: str | None = None
    details: dict[str, Any] | None = None
    actor_email: str | None = None
    created_at: datetime


class AuditLogListOut(BaseModel):
    total: int
    items: list[AuditLogOut] = Field(default_factory=list)
