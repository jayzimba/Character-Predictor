"""Shared ML vocabulary. Scoring and classification stay separate."""

from app.database.seed_catalog import QUESTION_CATEGORIES
from app.models.enums import PersonalityCode

LABEL_COLUMN = "personality_type"
ORIGIN_COLUMN = "dataset_origin"

LABEL_ORDER = (
    PersonalityCode.CHOLERIC.value,
    PersonalityCode.MELANCHOLIC.value,
    PersonalityCode.PHLEGMATIC.value,
    PersonalityCode.SANGUINE.value,
)

CATEGORY_CODES = tuple(code for code, _name, _description in QUESTION_CATEGORIES)
FEATURE_COLUMNS = tuple(f"{code}_score" for code in CATEGORY_CODES)

DEMO_ORIGIN = "DEMO/SYNTHETIC"
COLLECTED_ORIGIN = "COLLECTED"
UNSPECIFIED_ORIGIN = "UNSPECIFIED"

LIKERT_MIN = 1
LIKERT_MAX = 5

DEMO_CSV_NAME = "temperament_demo_v1.csv"
DEMO_CSV_HEADER = (
    "# DEMO/SYNTHETIC — local development only. "
    "Do not report these rows or any model trained on them as research findings."
)

DEFAULT_TEST_SIZE = 0.2
DEFAULT_RANDOM_STATE = 42
