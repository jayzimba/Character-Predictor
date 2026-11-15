"""Admin analytics from stored assessments and predictions.

Does not read Likert answers. Mix percentages are not invented here;
personality totals are counts of stored predicted_personality values.
"""

from sqlalchemy.orm import Session

from app.ml.constants import LABEL_ORDER
from app.models.enums import AgeGroup, AssessmentStatus, Gender, RoleCode
from app.repositories import assessment as assessment_repository
from app.repositories import user as user_repository
from app.schemas.analytics import (
    AnalyticsOut,
    AnalyticsTotals,
    NamedCount,
    PersonalityCounts,
    TimePoint,
)

DISCLAIMER = (
    "These figures are counts of rows already stored in MySQL. "
    "They are not a new classification run. DEMO MODE predictions are "
    "labelled separately and must not be reported as research findings."
)

AGE_LABELS = {
    AgeGroup.UNDER_18.value: "Under 18",
    AgeGroup.AGE_18_24.value: "18–24",
    AgeGroup.AGE_25_34.value: "25–34",
    AgeGroup.AGE_35_44.value: "35–44",
    AgeGroup.AGE_45_54.value: "45–54",
    AgeGroup.AGE_55_PLUS.value: "55+",
    "NOT_PROVIDED": "Not provided",
}

GENDER_LABELS = {
    Gender.FEMALE.value: "Female",
    Gender.MALE.value: "Male",
    Gender.OTHER.value: "Other",
    Gender.PREFER_NOT_TO_SAY.value: "Prefer not to say",
    "NOT_PROVIDED": "Not provided",
}


def _named(counts: dict[str, int], labels: dict[str, str]) -> list[NamedCount]:
    ordered = [key for key in labels if key in counts]
    ordered.extend(key for key in counts if key not in labels)
    return [
        NamedCount(
            key=key,
            label=labels.get(key, key.replace("_", " ").title()),
            count=counts[key],
        )
        for key in ordered
    ]


def get_analytics(session: Session) -> AnalyticsOut:
    started = assessment_repository.count_all(session)
    completed = assessment_repository.count_all(
        session, AssessmentStatus.COMPLETED.value
    )
    in_progress = assessment_repository.count_all(
        session, AssessmentStatus.IN_PROGRESS.value
    )
    stored = assessment_repository.count_predictions(session)
    demo = assessment_repository.count_predictions(session, demo_only=True)
    model_backed = stored - demo
    completion_rate = round(completed / started, 4) if started else None

    personality = assessment_repository.prediction_counts_by_code(session)
    personality_out = PersonalityCounts(
        **{code.lower(): int(personality.get(code, 0)) for code in LABEL_ORDER}
    )

    source = assessment_repository.prediction_counts_by_demo_flag(session)
    source_counts = [
        NamedCount(key="DEMO", label="DEMO MODE", count=int(source.get(True, 0))),
        NamedCount(
            key="MODEL",
            label="Not DEMO MODE",
            count=int(source.get(False, 0)),
        ),
    ]

    algorithms = assessment_repository.prediction_counts_by_algorithm(session)
    algorithm_counts = [
        NamedCount(
            key=name,
            label="No linked model" if name == "NONE" else name.replace("_", " "),
            count=count,
        )
        for name, count in sorted(algorithms.items(), key=lambda item: (-item[1], item[0]))
    ]

    age_counts = assessment_repository.classified_user_counts_by_field(session, "age_group")
    gender_counts = assessment_repository.classified_user_counts_by_field(session, "gender")

    recent_days = 14
    raw_series = assessment_repository.activity_series(session, recent_days=recent_days)
    series = [TimePoint(**point) for point in raw_series]

    return AnalyticsOut(
        disclaimer=DISCLAIMER,
        window_days=recent_days,
        totals=AnalyticsTotals(
            users_regular=user_repository.count_users_by_role(
                session, RoleCode.USER.value
            ),
            assessments_started=started,
            assessments_completed=completed,
            assessments_in_progress=in_progress,
            classifications_stored=stored,
            demo_classifications=demo,
            model_classifications=model_backed,
            completion_rate=completion_rate,
            mean_confidence=assessment_repository.mean_confidence(session),
        ),
        personality_counts=personality_out,
        source_counts=source_counts,
        algorithm_counts=algorithm_counts,
        age_group_counts=_named(age_counts, AGE_LABELS),
        gender_counts=_named(gender_counts, GENDER_LABELS),
        series=series,
    )
