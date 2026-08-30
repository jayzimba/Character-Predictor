"""FastAPI application entry point.

Phase 13: completed assessments can be classified. The results page is later.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app import __version__
from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.responses import success_response
from app.database.session import get_engine, get_session_factory

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        with get_session_factory()() as session:
            session.execute(text("SELECT 1"))
        logger.info("Database connection verified at startup.")
    except Exception:
        logger.warning(
            "Database is not reachable at startup. Liveness remains available."
        )
    if settings.jwt_secret == "change-me-to-a-long-random-string":
        logger.warning(
            "JWT_SECRET is still the example value. Change it before any deployment."
        )
    yield
    get_engine().dispose()


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Educational personality classification API. "
        "Predictions are not a clinical psychological diagnosis."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["meta"])
def root():
    return success_response(
        data={
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "health": f"{settings.api_prefix}/health",
            "ready": f"{settings.api_prefix}/health/ready",
            "phase": 13,
        },
        message="Completed assessments can be classified. The detailed results page is later.",
    )
