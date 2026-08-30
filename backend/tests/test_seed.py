"""Phase 2: seed catalog is complete and idempotent."""

from sqlalchemy import func, select

from app.database.seed import seed_all
from app.database.seed_catalog import QUESTION_CATEGORIES, QUESTIONS
from app.models import PersonalityType, Question, QuestionCategory, Role, User


def test_catalog_sizes():
    assert len(QUESTION_CATEGORIES) == 16
    assert len(QUESTIONS) == 32


def test_seed_creates_reference_data(db_session):
    summary = seed_all(db_session)

    assert summary["personality_types"] == 4
    assert summary["categories"] == 16
    assert summary["questions"] == 32
    assert db_session.scalar(select(func.count()).select_from(Role)) == 2
    assert db_session.scalar(select(func.count()).select_from(User)) == 2
    assert db_session.scalar(select(func.count()).select_from(PersonalityType)) == 4
    assert db_session.scalar(select(func.count()).select_from(QuestionCategory)) == 16
    assert db_session.scalar(select(func.count()).select_from(Question)) == 32


def test_seed_is_idempotent(db_session):
    seed_all(db_session)
    seed_all(db_session)

    assert db_session.scalar(select(func.count()).select_from(User)) == 2
    assert db_session.scalar(select(func.count()).select_from(Question)) == 32


def test_seeded_passwords_are_hashed(db_session):
    seed_all(db_session)
    admin = db_session.scalar(
        select(User).where(User.email == "admin@temperamentlab.local")
    )
    assert admin is not None
    assert admin.password_hash != "AdminDemo123!"
    assert admin.password_hash.startswith("$2")
