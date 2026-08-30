"""Start, save and submit assessments. No class label is produced here."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Assessment, User
from app.models.enums import AssessmentStatus, QuestionStatus
from app.repositories import assessment as assessment_repository
from app.repositories import questionnaire as questionnaire_repository
from app.schemas.assessment import (
    AnswerIn,
    AnswerOut,
    AssessmentDetailOut,
    AssessmentSummaryOut,
    AnswersRequest,
    ConsentRequest,
)
from app.services.questionnaire import require_single_active_version
from app.services.scoring import weighted_likert


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _totals(session: Session, assessment: Assessment) -> tuple[int, int]:
    answered = assessment_repository.count_answers(session, assessment.id)
    total = assessment_repository.count_questions_for_version(
        session, assessment.questionnaire_version_id, active_only=True
    )
    return answered, total


def _summary(session: Session, assessment: Assessment) -> AssessmentSummaryOut:
    answered, total = _totals(session, assessment)
    return AssessmentSummaryOut(
        id=assessment.id,
        status=assessment.status,
        questionnaire_version_id=assessment.questionnaire_version_id,
        started_at=assessment.started_at,
        completed_at=assessment.completed_at,
        consent_accepted_at=assessment.consent_accepted_at,
        answered=answered,
        total=total,
    )


def _detail(session: Session, assessment: Assessment) -> AssessmentDetailOut:
    summary = _summary(session, assessment)
    answers = [
        AnswerOut(question_id=item.question_id, response_value=item.response_value)
        for item in assessment.answers
    ]
    return AssessmentDetailOut(**summary.model_dump(), answers=answers)


def _owned(assessment: Assessment | None, user: User) -> Assessment:
    if assessment is None or assessment.user_id != user.id:
        raise AppError("Assessment not found", status_code=404)
    return assessment


def start_assessment(session: Session, user: User, payload: ConsentRequest) -> AssessmentDetailOut:
    if not payload.consent_accepted:
        raise AppError("Consent is required before an assessment can start.", status_code=400)
    existing = assessment_repository.get_in_progress_for_user(session, user.id)
    if existing:
        return _detail(session, existing)

    version = require_single_active_version(session)
    now = _utcnow()
    assessment = assessment_repository.create_assessment(
        session,
        user_id=user.id,
        questionnaire_version_id=version.id,
        started_at=now,
        consent_accepted_at=now,
    )
    session.commit()
    loaded = assessment_repository.get_by_id(session, assessment.id)
    return _detail(session, loaded)


def list_my_assessments(session: Session, user: User) -> list[AssessmentSummaryOut]:
    rows = assessment_repository.list_for_user(session, user.id)
    return [_summary(session, row) for row in rows]


def get_my_assessment(session: Session, user: User, assessment_id: int) -> AssessmentDetailOut:
    assessment = _owned(assessment_repository.get_by_id(session, assessment_id), user)
    return _detail(session, assessment)


def save_answers(
    session: Session,
    user: User,
    assessment_id: int,
    payload: AnswersRequest,
) -> AssessmentDetailOut:
    assessment = _owned(assessment_repository.get_by_id(session, assessment_id), user)
    if assessment.status != AssessmentStatus.IN_PROGRESS.value:
        raise AppError("This assessment can no longer be changed.", status_code=409)

    question_ids = [item.question_id for item in payload.answers]
    questions = {
        item.id: item
        for item in questionnaire_repository.get_questions_by_ids(session, question_ids)
    }
    for item in payload.answers:
        question = questions.get(item.question_id)
        if (
            question is None
            or question.questionnaire_version_id != assessment.questionnaire_version_id
            or question.status != QuestionStatus.ACTIVE.value
        ):
            raise AppError("One or more questions are not part of this assessment.", status_code=400)
        score = weighted_likert(item.response_value, question.weight, question.reverse_scored)
        assessment_repository.upsert_answer(
            session,
            assessment_id=assessment.id,
            question_id=question.id,
            response_value=item.response_value,
            weighted_score=score,
        )
    session.commit()
    loaded = assessment_repository.get_by_id(session, assessment.id)
    return _detail(session, loaded)


def submit_assessment(session: Session, user: User, assessment_id: int) -> AssessmentSummaryOut:
    assessment = _owned(assessment_repository.get_by_id(session, assessment_id), user)
    if assessment.status == AssessmentStatus.COMPLETED.value:
        raise AppError("This assessment has already been submitted.", status_code=409)
    if assessment.consent_accepted_at is None:
        raise AppError("Consent is required before submit.", status_code=400)

    answered, total = _totals(session, assessment)
    if total == 0 or answered < total:
        raise AppError(
            "Answer every question before submitting.",
            status_code=400,
            errors={"answered": answered, "total": total},
        )
    assessment.status = AssessmentStatus.COMPLETED.value
    assessment.completed_at = _utcnow()
    session.commit()
    session.refresh(assessment)
    return _summary(session, assessment)
