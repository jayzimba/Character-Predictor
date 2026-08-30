"""Readiness checks. Liveness stays in the router and does not touch MySQL."""

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models import PersonalityType, Question, Role


def inspect_database(session: Session) -> dict:
    """Confirm the engine can execute SQL and report seed-table counts."""
    session.execute(text("SELECT 1"))
    return {
        "connected": True,
        "roles": session.scalar(select(func.count()).select_from(Role)) or 0,
        "personality_types": session.scalar(select(func.count()).select_from(PersonalityType))
        or 0,
        "questions": session.scalar(select(func.count()).select_from(Question)) or 0,
    }
