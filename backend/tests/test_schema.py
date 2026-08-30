"""Phase 2: relational constraints can be explained and they actually fire."""

from decimal import Decimal

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from app.database.base import Base
from app.database.seed import seed_all
from app.models import (
    Assessment,
    AssessmentAnswer,
    AssessmentStatus,
    QuestionnaireVersion,
    Role,
    User,
)


def test_expected_tables_are_registered():
    table_names = set(Base.metadata.tables)
    assert {
        "roles",
        "users",
        "password_reset_tokens",
        "personality_types",
        "question_categories",
        "questionnaire_versions",
        "questions",
        "assessments",
        "assessment_answers",
        "prediction_results",
        "ml_models",
        "model_metrics",
        "audit_logs",
    }.issubset(table_names)


def test_sqlite_schema_creates(db_session):
    inspector = inspect(db_session.get_bind())
    assert "users" in inspector.get_table_names()
    assert "questions" in inspector.get_table_names()


def test_email_must_be_unique(db_session):
    role = Role(code="USER", name="User")
    db_session.add(role)
    db_session.flush()

    db_session.add(
        User(
            role_id=role.id,
            first_name="A",
            last_name="One",
            email="same@example.com",
            password_hash="hashed-1",
        )
    )
    db_session.flush()

    db_session.add(
        User(
            role_id=role.id,
            first_name="B",
            last_name="Two",
            email="same@example.com",
            password_hash="hashed-2",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_duplicate_answer_for_same_question_is_rejected(db_session):
    seed_all(db_session)
    user = db_session.scalar(select(User).where(User.email == "user@temperamentlab.local"))
    version = db_session.scalar(select(QuestionnaireVersion))
    question_id = version.questions[0].id

    assessment = Assessment(
        user_id=user.id,
        questionnaire_version_id=version.id,
        status=AssessmentStatus.IN_PROGRESS.value,
    )
    db_session.add(assessment)
    db_session.flush()

    db_session.add(
        AssessmentAnswer(
            assessment_id=assessment.id,
            question_id=question_id,
            response_value=4,
            weighted_score=Decimal("4.00"),
        )
    )
    db_session.flush()
    db_session.add(
        AssessmentAnswer(
            assessment_id=assessment.id,
            question_id=question_id,
            response_value=2,
            weighted_score=Decimal("2.00"),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_likert_value_outside_one_to_five_is_rejected(db_session):
    seed_all(db_session)
    user = db_session.scalar(select(User).where(User.email == "user@temperamentlab.local"))
    version = db_session.scalar(select(QuestionnaireVersion))
    assessment = Assessment(
        user_id=user.id,
        questionnaire_version_id=version.id,
        status=AssessmentStatus.IN_PROGRESS.value,
    )
    db_session.add(assessment)
    db_session.flush()

    db_session.add(
        AssessmentAnswer(
            assessment_id=assessment.id,
            question_id=version.questions[0].id,
            response_value=6,
            weighted_score=Decimal("6.00"),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
