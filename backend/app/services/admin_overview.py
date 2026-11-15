"""Admin aggregates from stored rows. Distribution is a count of predictions."""

from sqlalchemy.orm import Session

from app.ml.constants import LABEL_ORDER
from app.models import Assessment
from app.models.enums import AssessmentStatus, RoleCode
from app.repositories import assessment as assessment_repository
from app.repositories import ml_models as model_repository
from app.repositories import user as user_repository
from app.schemas.admin import (
    ActiveModelSummary,
    AdminAssessmentOut,
    AdminOverviewOut,
    PersonalityCounts,
)


def _personality_counts(session: Session) -> PersonalityCounts:
    stored = assessment_repository.prediction_counts_by_code(session)
    values = {code.lower(): int(stored.get(code, 0)) for code in LABEL_ORDER}
    return PersonalityCounts(**values)


def get_overview(session: Session) -> AdminOverviewOut:
    active = model_repository.get_active(session)
    active_out = None
    if active is not None:
        active_out = ActiveModelSummary(
            id=active.id,
            algorithm=active.algorithm,
            version=active.version,
            status=active.status,
            dataset_name=active.dataset_name,
            is_synthetic_dataset=bool(active.is_synthetic_dataset),
        )
    return AdminOverviewOut(
        users_total=user_repository.count_users(session),
        users_admin=user_repository.count_users_by_role(session, RoleCode.ADMIN.value),
        users_regular=user_repository.count_users_by_role(session, RoleCode.USER.value),
        assessments_completed=assessment_repository.count_all(
            session, AssessmentStatus.COMPLETED.value
        ),
        assessments_in_progress=assessment_repository.count_all(
            session, AssessmentStatus.IN_PROGRESS.value
        ),
        classifications_stored=assessment_repository.count_predictions(session),
        demo_classifications=assessment_repository.count_predictions(
            session, demo_only=True
        ),
        personality_counts=_personality_counts(session),
        active_model=active_out,
    )


def _assessment_item(session: Session, assessment: Assessment) -> AdminAssessmentOut:
    user = assessment.user
    prediction = assessment.prediction
    type_row = prediction.personality_type if prediction is not None else None
    answered = assessment_repository.count_answers(session, assessment.id)
    total = assessment_repository.count_questions_for_version(
        session, assessment.questionnaire_version_id, active_only=True
    )
    return AdminAssessmentOut(
        assessment_id=assessment.id,
        user_id=assessment.user_id,
        user_email=user.email,
        user_name=f"{user.first_name} {user.last_name}".strip(),
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


def list_assessments(session: Session) -> list[AdminAssessmentOut]:
    rows = assessment_repository.list_for_admin(session)
    return [_assessment_item(session, row) for row in rows]
