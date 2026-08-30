"""Public catalogue. No authentication — descriptions are not personal data."""

from fastapi import APIRouter

from app.core.deps import DbSession
from app.core.responses import success_response
from app.schemas.personality import PersonalityTypeOut
from app.services import personality as personality_service

router = APIRouter()


@router.get("")
def list_personality_types(db: DbSession):
    records = personality_service.list_personality_types(db)
    payload = [PersonalityTypeOut.model_validate(item).model_dump() for item in records]
    return success_response(
        data=payload,
        message="Personality types loaded",
    )
