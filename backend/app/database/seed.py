"""Idempotent development seed.

Creates roles, demo users, four personality types, categories, and
questionnaire version 1. Safe to run more than once.

Demo passwords are for local use only. They are hashed with bcrypt
before insert — never stored in plaintext.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.database.seed_catalog import (
    PERSONALITY_TYPES,
    QUESTION_CATEGORIES,
    QUESTIONS,
)
from app.models import (
    PersonalityType,
    Question,
    QuestionCategory,
    QuestionnaireVersion,
    Role,
    RoleCode,
    User,
)

DEMO_ADMIN_EMAIL = "admin@temperamentlab.local"
DEMO_USER_EMAIL = "user@temperamentlab.local"
DEMO_ADMIN_PASSWORD = "AdminDemo123!"
DEMO_USER_PASSWORD = "DemoUser123!"

QUESTIONNAIRE_VERSION_CODE = "v1"


def _get_or_create_role(session: Session, code: str, name: str, description: str) -> Role:
    role = session.scalar(select(Role).where(Role.code == code))
    if role:
        return role
    role = Role(code=code, name=name, description=description)
    session.add(role)
    session.flush()
    return role


def _get_or_create_user(
    session: Session,
    *,
    role: Role,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    age_group: str | None = None,
) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user:
        return user
    user = User(
        role_id=role.id,
        first_name=first_name,
        last_name=last_name,
        email=email.lower(),
        password_hash=hash_password(password),
        age_group=age_group,
        is_active=True,
    )
    session.add(user)
    session.flush()
    return user


def seed_roles_and_users(session: Session) -> dict[str, User]:
    admin_role = _get_or_create_role(
        session,
        RoleCode.ADMIN.value,
        "Administrator",
        "Manages users, questions, models, and analytics.",
    )
    user_role = _get_or_create_role(
        session,
        RoleCode.USER.value,
        "User",
        "Takes assessments and views personal results.",
    )
    admin = _get_or_create_user(
        session,
        role=admin_role,
        first_name="Ada",
        last_name="Admin",
        email=DEMO_ADMIN_EMAIL,
        password=DEMO_ADMIN_PASSWORD,
    )
    member = _get_or_create_user(
        session,
        role=user_role,
        first_name="Sam",
        last_name="Student",
        email=DEMO_USER_EMAIL,
        password=DEMO_USER_PASSWORD,
        age_group="AGE_18_24",
    )
    return {"admin": admin, "user": member}


def seed_personality_types(session: Session) -> dict[str, PersonalityType]:
    by_code: dict[str, PersonalityType] = {}
    for item in PERSONALITY_TYPES:
        existing = session.scalar(
            select(PersonalityType).where(PersonalityType.code == item["code"])
        )
        if existing:
            by_code[item["code"]] = existing
            continue
        record = PersonalityType(**item)
        session.add(record)
        session.flush()
        by_code[item["code"]] = record
    return by_code


def seed_categories(session: Session) -> dict[str, QuestionCategory]:
    by_code: dict[str, QuestionCategory] = {}
    for index, (code, name, description) in enumerate(QUESTION_CATEGORIES, start=1):
        existing = session.scalar(
            select(QuestionCategory).where(QuestionCategory.code == code)
        )
        if existing:
            by_code[code] = existing
            continue
        record = QuestionCategory(
            code=code,
            name=name,
            description=description,
            display_order=index,
        )
        session.add(record)
        session.flush()
        by_code[code] = record
    return by_code


def seed_questionnaire(
    session: Session,
    categories: dict[str, QuestionCategory],
    types: dict[str, PersonalityType],
) -> QuestionnaireVersion:
    version = session.scalar(
        select(QuestionnaireVersion).where(
            QuestionnaireVersion.version_code == QUESTIONNAIRE_VERSION_CODE
        )
    )
    if version is None:
        version = QuestionnaireVersion(
            version_code=QUESTIONNAIRE_VERSION_CODE,
            name="Behavioural tendencies instrument",
            description=(
                "Likert items mapped to behavioural categories. "
                "Scores become ML features; they are not the final class label."
            ),
            is_active=True,
        )
        session.add(version)
        session.flush()

    existing_count = session.scalar(
        select(func.count())
        .select_from(Question)
        .where(Question.questionnaire_version_id == version.id)
    )
    if existing_count:
        return version

    for order, (category_code, type_code, reverse_scored, text) in enumerate(
        QUESTIONS, start=1
    ):
        session.add(
            Question(
                questionnaire_version_id=version.id,
                category_id=categories[category_code].id,
                personality_type_id=types[type_code].id,
                question_text=text,
                weight=1,
                status="ACTIVE",
                display_order=order,
                reverse_scored=reverse_scored,
            )
        )
    session.flush()
    return version


def seed_all(session: Session) -> dict[str, int]:
    users = seed_roles_and_users(session)
    types = seed_personality_types(session)
    categories = seed_categories(session)
    version = seed_questionnaire(session, categories, types)
    session.commit()
    return {
        "users": len(users),
        "personality_types": len(types),
        "categories": len(categories),
        "questions": len(QUESTIONS),
        "questionnaire_version_id": version.id,
    }


def run() -> None:
    from app.database.session import ensure_database_exists, get_session_factory

    ensure_database_exists()
    session = get_session_factory()()
    try:
        summary = seed_all(session)
        print("Seed complete:", summary)
    finally:
        session.close()


if __name__ == "__main__":
    run()
