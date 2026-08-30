"""Personality catalogue. Read-only in Phase 3."""

from sqlalchemy.orm import Session

from app.models import PersonalityType
from app.repositories import personality as personality_repository


def list_personality_types(session: Session) -> list[PersonalityType]:
    return personality_repository.list_personality_types(session)
