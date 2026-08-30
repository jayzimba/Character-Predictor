"""Active questionnaire for authenticated participants."""

from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.core.responses import success_response
from app.services import questionnaire as questionnaire_service

router = APIRouter()


@router.get("")
def get_active_questionnaire(db: DbSession, _: CurrentUser):
    data = questionnaire_service.get_active_questionnaire(db)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Active questionnaire loaded",
    )
