"""Shared fixtures. Schema tests use in-memory SQLite so MySQL is optional."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import db_session as fastapi_db_session
from app.core.rate_limit import reset_auth_limiter
from app.database.base import Base
from app.main import app
from app.models import *  # noqa: F403


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Session:
    factory = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def api_client(db_engine) -> TestClient:
    """Each request gets its own session bound to the shared in-memory database."""
    factory = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def _override_get_db():
        session = factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[fastapi_db_session] = _override_get_db
    reset_auth_limiter()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    reset_auth_limiter()
