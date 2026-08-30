"""User persistence. No password or JWT logic here."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Role, User
from app.models.enums import RoleCode


def get_by_email(session: Session, email: str) -> User | None:
    statement = (
        select(User)
        .options(selectinload(User.role))
        .where(User.email == email.strip().lower())
    )
    return session.scalar(statement)


def get_by_id(session: Session, user_id: int) -> User | None:
    statement = select(User).options(selectinload(User.role)).where(User.id == user_id)
    return session.scalar(statement)


def get_role_by_code(session: Session, code: str) -> Role | None:
    return session.scalar(select(Role).where(Role.code == code))


def list_users(session: Session) -> list[User]:
    statement = select(User).options(selectinload(User.role)).order_by(User.id)
    return list(session.scalars(statement).all())


def create_user(
    session: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    password_hash: str,
    gender: str | None,
    age_group: str | None,
    role: Role,
) -> User:
    user = User(
        role_id=role.id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash,
        gender=gender,
        age_group=age_group,
        is_active=True,
    )
    session.add(user)
    session.flush()
    session.refresh(user)
    user.role = role
    return user


def get_default_user_role(session: Session) -> Role | None:
    return get_role_by_code(session, RoleCode.USER.value)
