"""Authenticated assessment taking. Classification is not started here."""

from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.core.responses import success_response
from app.schemas.assessment import AnswersRequest, ConsentRequest
from app.services import assessments as assessment_service

router = APIRouter()


@router.post("")
def start_assessment(payload: ConsentRequest, db: DbSession, current_user: CurrentUser):
    data = assessment_service.start_assessment(db, current_user, payload)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Assessment ready",
    )


@router.get("")
def list_assessments(db: DbSession, current_user: CurrentUser):
    data = assessment_service.list_my_assessments(db, current_user)
    return success_response(
        data=[item.model_dump(mode="json") for item in data],
        message="Assessments loaded",
    )


@router.get("/{assessment_id}")
def get_assessment(assessment_id: int, db: DbSession, current_user: CurrentUser):
    data = assessment_service.get_my_assessment(db, current_user, assessment_id)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Assessment loaded",
    )


@router.post("/{assessment_id}/answers")
def save_answers(
    assessment_id: int,
    payload: AnswersRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    data = assessment_service.save_answers(db, current_user, assessment_id, payload)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Progress saved",
    )


@router.post("/{assessment_id}/submit")
def submit_assessment(assessment_id: int, db: DbSession, current_user: CurrentUser):
    data = assessment_service.submit_assessment(db, current_user, assessment_id)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Assessment submitted. Classification is not available yet.",
    )
