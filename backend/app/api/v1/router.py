"""Domain routes mounted under /api."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.auth import router as auth_router
from app.api.v1.history import router as history_router
from app.api.v1.personality_types import router as personality_types_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.questions import router as questions_router
from app.api.v1.results import router as results_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(questions_router, prefix="/questions", tags=["questions"])
api_router.include_router(
    assessments_router, prefix="/assessments", tags=["assessments"]
)
api_router.include_router(
    personality_types_router,
    prefix="/personality-types",
    tags=["personality-types"],
)
api_router.include_router(
    predictions_router,
    prefix="/predictions",
    tags=["predictions"],
)
api_router.include_router(
    results_router,
    prefix="/results",
    tags=["results"],
)
api_router.include_router(
    history_router,
    prefix="/history",
    tags=["history"],
)
