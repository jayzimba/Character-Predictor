"""Administrator analytics. Aggregates only — no Likert answers."""

from fastapi import APIRouter

from app.core.deps import AdminUser, DbSession
from app.core.responses import success_response
from app.services import analytics as analytics_service

router = APIRouter()


@router.get("")
def get_analytics(db: DbSession, _: AdminUser):
    payload = analytics_service.get_analytics(db).model_dump(mode="json")
    return success_response(data=payload, message="Analytics loaded")
