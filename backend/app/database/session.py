"""Engine and session factory used by Alembic, seeds, and FastAPI."""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """One SQLAlchemy session per request. Routers receive this via Depends."""
    session = get_session_factory()()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ensure_database_exists() -> None:
    """Create the MySQL schema if the server is reachable and it is missing."""
    settings = get_settings()
    url = make_url(settings.database_url)
    if url.get_backend_name() not in {"mysql", "mariadb"}:
        return
    database_name = url.database
    if not database_name:
        raise ValueError("DATABASE_URL must include a database name.")

    target_engine = create_engine(url)
    try:
        with target_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return
    except Exception:
        pass
    finally:
        target_engine.dispose()

    # App users from Docker/MariaDB images cannot use the `mysql` system schema.
    admin_engine = create_engine(url.set(database=None))
    with admin_engine.connect() as connection:
        connection.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        connection.commit()
    admin_engine.dispose()
