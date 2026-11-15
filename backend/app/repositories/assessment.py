"""Assessment persistence. Classification is stored on prediction_results."""

from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Assessment, AssessmentAnswer, MLModel, PredictionResult, Question, User
from app.models.enums import AssessmentStatus, QuestionStatus


def _with_prediction(statement):
    return statement.options(
        selectinload(Assessment.prediction).selectinload(
            PredictionResult.personality_type
        )
    )


def count_all(session: Session, status: str | None = None) -> int:
    statement = select(func.count(Assessment.id))
    if status is not None:
        statement = statement.where(Assessment.status == status)
    return int(session.scalar(statement) or 0)


def count_predictions(session: Session, *, demo_only: bool = False) -> int:
    statement = select(func.count(PredictionResult.id))
    if demo_only:
        statement = statement.where(PredictionResult.is_demo_mode.is_(True))
    return int(session.scalar(statement) or 0)


def prediction_counts_by_code(session: Session) -> dict[str, int]:
    rows = session.execute(
        select(
            PredictionResult.predicted_personality,
            func.count(PredictionResult.id),
        ).group_by(PredictionResult.predicted_personality)
    ).all()
    return {str(code): int(count) for code, count in rows}


def prediction_counts_by_demo_flag(session: Session) -> dict[bool, int]:
    rows = session.execute(
        select(
            PredictionResult.is_demo_mode,
            func.count(PredictionResult.id),
        ).group_by(PredictionResult.is_demo_mode)
    ).all()
    return {bool(flag): int(count) for flag, count in rows}


def prediction_counts_by_algorithm(session: Session) -> dict[str, int]:
    rows = session.execute(
        select(
            func.coalesce(MLModel.algorithm, "NONE"),
            func.count(PredictionResult.id),
        )
        .select_from(PredictionResult)
        .outerjoin(MLModel, MLModel.id == PredictionResult.model_id)
        .group_by(func.coalesce(MLModel.algorithm, "NONE"))
    ).all()
    return {str(name): int(count) for name, count in rows}


def mean_confidence(session: Session) -> float | None:
    value = session.scalar(select(func.avg(PredictionResult.confidence_score)))
    if value is None:
        return None
    return round(float(value), 4)


def classified_user_counts_by_field(session: Session, field: str) -> dict[str, int]:
    column = getattr(User, field)
    rows = session.execute(
        select(column, func.count(func.distinct(User.id)))
        .select_from(PredictionResult)
        .join(Assessment, Assessment.id == PredictionResult.assessment_id)
        .join(User, User.id == Assessment.user_id)
        .group_by(column)
    ).all()
    counts: dict[str, int] = {}
    for key, count in rows:
        label = str(key) if key else "NOT_PROVIDED"
        counts[label] = counts.get(label, 0) + int(count)
    return counts


def _day_counts(session: Session, column, extra=None) -> dict[str, int]:
    statement = select(func.date(column), func.count()).group_by(func.date(column))
    if extra is not None:
        statement = statement.where(extra)
    rows = session.execute(statement).all()
    counts: dict[str, int] = {}
    for day, count in rows:
        if day is None:
            continue
        counts[str(day)[:10]] = int(count)
    return counts


def activity_series(session: Session, *, recent_days: int = 14) -> list[dict]:
    started = _day_counts(session, Assessment.started_at)
    completed = _day_counts(
        session,
        Assessment.completed_at,
        Assessment.status == AssessmentStatus.COMPLETED.value,
    )
    classified = _day_counts(session, PredictionResult.created_at)
    demo = _day_counts(
        session,
        PredictionResult.created_at,
        PredictionResult.is_demo_mode.is_(True),
    )
    today = date.today()
    keys = set(started) | set(completed) | set(classified) | set(demo)
    for offset in range(recent_days):
        keys.add((today - timedelta(days=offset)).isoformat())
    series = []
    for key in sorted(keys):
        series.append(
            {
                "date": key,
                "started": started.get(key, 0),
                "completed": completed.get(key, 0),
                "classified": classified.get(key, 0),
                "demo": demo.get(key, 0),
            }
        )
    return series


def list_for_admin(session: Session) -> list[Assessment]:
    statement = (
        select(Assessment)
        .options(
            selectinload(Assessment.user),
            selectinload(Assessment.prediction).selectinload(
                PredictionResult.personality_type
            ),
        )
        .order_by(Assessment.started_at.desc(), Assessment.id.desc())
    )
    return list(session.scalars(statement).all())


def count_for_user(session: Session, user_id: int, status: str | None = None) -> int:
    statement = select(func.count(Assessment.id)).where(Assessment.user_id == user_id)
    if status is not None:
        statement = statement.where(Assessment.status == status)
    return int(session.scalar(statement) or 0)


def get_latest_for_user(session: Session, user_id: int) -> Assessment | None:
    statement = _with_prediction(
        select(Assessment)
        .where(Assessment.user_id == user_id)
        .order_by(Assessment.started_at.desc(), Assessment.id.desc())
        .limit(1)
    )
    return session.scalar(statement)


def get_latest_completed_for_user(session: Session, user_id: int) -> Assessment | None:
    statement = _with_prediction(
        select(Assessment)
        .where(
            Assessment.user_id == user_id,
            Assessment.status == AssessmentStatus.COMPLETED.value,
        )
        .order_by(Assessment.completed_at.desc(), Assessment.id.desc())
        .limit(1)
    )
    return session.scalar(statement)


def get_latest_classified_for_user(session: Session, user_id: int) -> Assessment | None:
    statement = (
        select(Assessment)
        .join(PredictionResult)
        .options(
            selectinload(Assessment.prediction).selectinload(
                PredictionResult.personality_type
            ),
            selectinload(Assessment.prediction).selectinload(PredictionResult.model),
        )
        .where(Assessment.user_id == user_id)
        .order_by(Assessment.completed_at.desc(), Assessment.id.desc())
        .limit(1)
    )
    return session.scalar(statement)


def count_answers(session: Session, assessment_id: int) -> int:
    return int(
        session.scalar(
            select(func.count(AssessmentAnswer.id)).where(
                AssessmentAnswer.assessment_id == assessment_id
            )
        )
        or 0
    )


def count_questions_for_version(
    session: Session,
    version_id: int,
    *,
    active_only: bool = True,
) -> int:
    statement = select(func.count(Question.id)).where(
        Question.questionnaire_version_id == version_id
    )
    if active_only:
        statement = statement.where(Question.status == QuestionStatus.ACTIVE.value)
    return int(session.scalar(statement) or 0)


def get_by_id(session: Session, assessment_id: int) -> Assessment | None:
    statement = (
        select(Assessment)
        .options(
            selectinload(Assessment.answers)
            .selectinload(AssessmentAnswer.question)
            .selectinload(Question.category),
            selectinload(Assessment.answers)
            .selectinload(AssessmentAnswer.question)
            .selectinload(Question.personality_trait),
            selectinload(Assessment.prediction).selectinload(
                PredictionResult.personality_type
            ),
            selectinload(Assessment.prediction).selectinload(PredictionResult.model),
        )
        .where(Assessment.id == assessment_id)
    )
    return session.scalar(statement)


def get_in_progress_for_user(session: Session, user_id: int) -> Assessment | None:
    statement = (
        select(Assessment)
        .options(selectinload(Assessment.answers))
        .where(
            Assessment.user_id == user_id,
            Assessment.status == AssessmentStatus.IN_PROGRESS.value,
        )
        .order_by(Assessment.started_at.desc(), Assessment.id.desc())
        .limit(1)
    )
    return session.scalar(statement)


def list_for_user(session: Session, user_id: int) -> list[Assessment]:
    statement = (
        select(Assessment)
        .options(selectinload(Assessment.answers))
        .where(Assessment.user_id == user_id)
        .order_by(Assessment.started_at.desc(), Assessment.id.desc())
    )
    return list(session.scalars(statement).all())


def list_history_for_user(session: Session, user_id: int) -> list[Assessment]:
    statement = (
        select(Assessment)
        .options(
            selectinload(Assessment.prediction).selectinload(
                PredictionResult.personality_type
            )
        )
        .where(Assessment.user_id == user_id)
        .order_by(Assessment.started_at.desc(), Assessment.id.desc())
    )
    return list(session.scalars(statement).all())


def create_assessment(
    session: Session,
    *,
    user_id: int,
    questionnaire_version_id: int,
    started_at: datetime,
    consent_accepted_at: datetime,
) -> Assessment:
    assessment = Assessment(
        user_id=user_id,
        questionnaire_version_id=questionnaire_version_id,
        status=AssessmentStatus.IN_PROGRESS.value,
        started_at=started_at,
        consent_accepted_at=consent_accepted_at,
    )
    session.add(assessment)
    session.flush()
    session.refresh(assessment)
    return assessment


def get_answer(
    session: Session, assessment_id: int, question_id: int
) -> AssessmentAnswer | None:
    statement = select(AssessmentAnswer).where(
        AssessmentAnswer.assessment_id == assessment_id,
        AssessmentAnswer.question_id == question_id,
    )
    return session.scalar(statement)


def upsert_answer(
    session: Session,
    *,
    assessment_id: int,
    question_id: int,
    response_value: int,
    weighted_score,
) -> AssessmentAnswer:
    existing = get_answer(session, assessment_id, question_id)
    if existing:
        existing.response_value = response_value
        existing.weighted_score = weighted_score
        return existing
    answer = AssessmentAnswer(
        assessment_id=assessment_id,
        question_id=question_id,
        response_value=response_value,
        weighted_score=weighted_score,
    )
    session.add(answer)
    return answer


def create_prediction(
    session: Session,
    *,
    assessment_id: int,
    model_id: int | None,
    personality_type_id: int,
    predicted_personality: str,
    confidence_score,
    choleric_percentage,
    melancholic_percentage,
    phlegmatic_percentage,
    sanguine_percentage,
    is_demo_mode: bool,
) -> PredictionResult:
    row = PredictionResult(
        assessment_id=assessment_id,
        model_id=model_id,
        personality_type_id=personality_type_id,
        predicted_personality=predicted_personality,
        confidence_score=confidence_score,
        choleric_percentage=choleric_percentage,
        melancholic_percentage=melancholic_percentage,
        phlegmatic_percentage=phlegmatic_percentage,
        sanguine_percentage=sanguine_percentage,
        is_demo_mode=is_demo_mode,
    )
    session.add(row)
    session.flush()
    return row
