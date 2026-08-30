"""Bundled development datasets. Uploaded personal files stay out of git."""

from pathlib import Path

from app.ml.constants import DEMO_CSV_NAME

DATASET_DIR = Path(__file__).resolve().parent
DEMO_CSV_PATH = DATASET_DIR / DEMO_CSV_NAME


def demo_csv_path() -> Path:
    if not DEMO_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Bundled DEMO CSV is missing: {DEMO_CSV_PATH}. "
            "Run python -m app.ml.dataset.generate_demo"
        )
    return DEMO_CSV_PATH
