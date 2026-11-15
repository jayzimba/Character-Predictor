"""Personality results dashboard. Mix values are never invented here."""

from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.core.responses import success_response
from app.services import results as results_service

router = APIRouter()


@router.get("/latest")
def get_latest_result(db: DbSession, current_user: CurrentUser):
    data = results_service.get_latest_result(db, current_user)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Latest personality result loaded",
    )


@router.get("/{assessment_id}")
def get_result(assessment_id: int, db: DbSession, current_user: CurrentUser):
    data = results_service.get_result(db, current_user, assessment_id)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Personality result loaded",
    )
