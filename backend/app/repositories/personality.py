"""Personality type queries. No HTTP or business rules here."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PersonalityType


def list_personality_types(session: Session) -> list[PersonalityType]:
    statement = select(PersonalityType).order_by(PersonalityType.id)
    return list(session.scalars(statement).all())


def get_by_code(session: Session, code: str) -> PersonalityType | None:
    return session.scalar(select(PersonalityType).where(PersonalityType.code == code))
