"""Classify completed assessments. Mix values are never invented."""

from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.core.responses import success_response
from app.schemas.prediction import ClassifyRequest
from app.services import predictions as prediction_service

router = APIRouter()


@router.post("/classify")
def classify_assessment(
    payload: ClassifyRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    data = prediction_service.classify(db, current_user, payload)
    message = "Assessment classified"
    if data.is_demo_mode:
        message = "Assessment classified in DEMO MODE"
    return success_response(data=data.model_dump(), message=message)


@router.get("/{assessment_id}")
def get_prediction(assessment_id: int, db: DbSession, current_user: CurrentUser):
    data = prediction_service.get_prediction(db, current_user, assessment_id)
    return success_response(data=data.model_dump(), message="Prediction loaded")
