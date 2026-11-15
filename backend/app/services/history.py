"""List the caller's assessments with stored classification, if any."""

from sqlalchemy.orm import Session

from app.models import Assessment, User
from app.repositories import assessment as assessment_repository
from app.schemas.history import HistoryItemOut


def _item(session: Session, assessment: Assessment) -> HistoryItemOut:
    answered = assessment_repository.count_answers(session, assessment.id)
    total = assessment_repository.count_questions_for_version(
        session, assessment.questionnaire_version_id, active_only=True
    )
    prediction = assessment.prediction
    type_row = prediction.personality_type if prediction is not None else None
    return HistoryItemOut(
        assessment_id=assessment.id,
        status=assessment.status,
        started_at=assessment.started_at,
        completed_at=assessment.completed_at,
        answered=answered,
        total=total,
        has_prediction=prediction is not None,
        predicted_personality=prediction.predicted_personality if prediction else None,
        personality_name=type_row.name if type_row else None,
        confidence=float(prediction.confidence_score) if prediction else None,
        is_demo_mode=bool(prediction.is_demo_mode) if prediction else False,
    )


def list_history(session: Session, user: User) -> list[HistoryItemOut]:
    rows = assessment_repository.list_history_for_user(session, user.id)
    return [_item(session, row) for row in rows]
