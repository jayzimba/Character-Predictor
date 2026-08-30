"""Turn completed assessments into a labelled or unlabelled feature table."""

from __future__ import annotations

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.ml.constants import COLLECTED_ORIGIN, LABEL_COLUMN, ORIGIN_COLUMN
from app.ml.feature_engineering import category_scores_from_likert
from app.ml.instrument import InstrumentSpec, likert_column
from app.models import Assessment, AssessmentAnswer, Question
from app.models.enums import AssessmentStatus


def list_completed_assessments(session: Session) -> list[Assessment]:
    statement = (
        select(Assessment)
        .options(
            selectinload(Assessment.answers)
            .selectinload(AssessmentAnswer.question)
            .selectinload(Question.category),
            selectinload(Assessment.answers)
            .selectinload(AssessmentAnswer.question)
            .selectinload(Question.personality_trait),
            selectinload(Assessment.prediction),
        )
        .where(Assessment.status == AssessmentStatus.COMPLETED.value)
        .order_by(Assessment.id)
    )
    return list(session.scalars(statement).all())


def assessment_likert_row(assessment: Assessment) -> dict[str, int]:
    answers: dict[str, int] = {}
    for item in assessment.answers:
        answers[likert_column(item.question.display_order)] = int(item.response_value)
    return answers


def collected_frame(session: Session, instrument: InstrumentSpec) -> pd.DataFrame:
    """One row per completed assessment. Label is present only after classification."""
    rows: list[dict] = []
    for assessment in list_completed_assessments(session):
        answers = assessment_likert_row(assessment)
        if any(key not in answers for key in instrument.likert_columns):
            continue
        scores = category_scores_from_likert(answers, instrument)
        if len(scores) != len(instrument.feature_columns):
            continue
        label = None
        if assessment.prediction is not None:
            label = assessment.prediction.predicted_personality
        rows.append(
            {
                ORIGIN_COLUMN: COLLECTED_ORIGIN,
                LABEL_COLUMN: label,
                "assessment_id": assessment.id,
                **answers,
                **scores,
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                ORIGIN_COLUMN,
                LABEL_COLUMN,
                "assessment_id",
                *instrument.likert_columns,
                *instrument.feature_columns,
            ]
        )
    return pd.DataFrame(rows)
