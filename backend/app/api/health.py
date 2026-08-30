"""Liveness does not touch MySQL. Readiness uses a request-scoped session."""

from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings
from app.core.deps import DbSession
from app.core.responses import success_response
from app.services.health import inspect_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Process liveness. Safe to call even when MySQL is down."""
    settings = get_settings()
    return success_response(
        data={
            "status": "healthy",
            "version": __version__,
            "environment": settings.app_env,
            "demo_mode": settings.ml_demo_mode,
        },
        message="Service is running",
    )


@router.get("/health/ready")
def readiness_check(db: DbSession):
    """Fail with 503 (via the OperationalError handler) if MySQL cannot answer."""
    database = inspect_database(db)
    return success_response(
        data={
            "status": "ready",
            "database": database,
        },
        message="Database is reachable",
    )
