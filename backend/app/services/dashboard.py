"""Assemble the signed-in user's dashboard from persisted assessments."""

from sqlalchemy.orm import Session

from app.models import Assessment, User
from app.models.enums import AssessmentStatus
from app.repositories import assessment as assessment_repository
from app.schemas.dashboard import (
    AssessmentCompletion,
    DashboardOut,
    DashboardPersonality,
    PersonalityMix,
)


def _completion_for(session: Session, assessment: Assessment | None) -> AssessmentCompletion | None:
    if assessment is None:
        return None
    total = assessment_repository.count_questions_for_version(
        session, assessment.questionnaire_version_id
    )
    if assessment.status == AssessmentStatus.COMPLETED.value:
        answered = total
        percent = 100 if total else 0
    else:
        answered = assessment_repository.count_answers(session, assessment.id)
        percent = round((answered / total) * 100) if total else 0
    return AssessmentCompletion(
        answered=answered,
        total=total,
        percent=percent,
        status=assessment.status,
    )


def get_user_dashboard(session: Session, user: User) -> DashboardOut:
    completed = assessment_repository.count_for_user(
        session, user.id, AssessmentStatus.COMPLETED.value
    )
    in_progress = assessment_repository.count_for_user(
        session, user.id, AssessmentStatus.IN_PROGRESS.value
    )
    latest = assessment_repository.get_latest_for_user(session, user.id)
    latest_completed = assessment_repository.get_latest_completed_for_user(
        session, user.id
    )

    personality = None
    mix = None
    confidence = None
    is_demo = False
    latest_id = None
    latest_at = None

    result_source = latest_completed
    if result_source is not None:
        latest_id = result_source.id
        latest_at = result_source.completed_at or result_source.started_at
        prediction = result_source.prediction
        if prediction is not None:
            type_row = prediction.personality_type
            personality = DashboardPersonality(
                code=type_row.code,
                name=type_row.name,
                tagline=type_row.tagline,
            )
            mix = PersonalityMix(
                choleric=float(prediction.choleric_percentage),
                melancholic=float(prediction.melancholic_percentage),
                phlegmatic=float(prediction.phlegmatic_percentage),
                sanguine=float(prediction.sanguine_percentage),
            )
            confidence = float(prediction.confidence_score)
            is_demo = bool(prediction.is_demo_mode)
    elif latest is not None:
        latest_id = latest.id
        latest_at = latest.started_at

    return DashboardOut(
        assessments_completed=completed,
        assessments_in_progress=in_progress,
        latest_personality=personality,
        latest_assessment_id=latest_id,
        latest_assessment_at=latest_at,
        latest_confidence=confidence,
        latest_mix=mix,
        is_demo_mode=is_demo,
        completion=_completion_for(session, latest or latest_completed),
    )
