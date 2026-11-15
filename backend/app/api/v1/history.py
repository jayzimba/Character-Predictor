"""Assessment history. Mix percentages are not computed here."""

from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.core.responses import success_response
from app.services import history as history_service

router = APIRouter()


@router.get("")
def list_history(db: DbSession, current_user: CurrentUser):
    data = history_service.list_history(db, current_user)
    return success_response(
        data=[item.model_dump(mode="json") for item in data],
        message="Assessment history loaded",
    )
