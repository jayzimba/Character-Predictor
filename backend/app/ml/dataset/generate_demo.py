"""Write a labelled DEMO/SYNTHETIC Likert CSV for local development.

Labels are assigned by construction. This is not a trained classifier and
must never be reported as a research sample.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.ml.constants import DEMO_CSV_HEADER, DEMO_ORIGIN, LABEL_COLUMN, LABEL_ORDER, ORIGIN_COLUMN
from app.ml.dataset import DEMO_CSV_PATH
from app.ml.instrument import instrument_from_catalog


def build_demo_frame(n_per_class: int = 25, seed: int = 42) -> pd.DataFrame:
    instrument = instrument_from_catalog()
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    for label in LABEL_ORDER:
        for _ in range(n_per_class):
            answers: dict[str, int] = {}
            for item in instrument.items:
                if item.personality_code == label:
                    raw = int(rng.integers(1, 3)) if item.reverse_scored else int(rng.integers(4, 6))
                else:
                    raw = int(rng.integers(3, 6)) if item.reverse_scored else int(rng.integers(1, 4))
                answers[item.key] = raw
            rows.append(
                {
                    ORIGIN_COLUMN: DEMO_ORIGIN,
                    LABEL_COLUMN: label,
                    **answers,
                }
            )
    columns = [ORIGIN_COLUMN, LABEL_COLUMN, *instrument.likert_columns]
    return pd.DataFrame(rows, columns=columns)


def write_demo_csv(path: Path | None = None, **kwargs) -> Path:
    target = path or DEMO_CSV_PATH
    frame = build_demo_frame(**kwargs)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        handle.write(DEMO_CSV_HEADER + "\n")
        frame.to_csv(handle, index=False)
    return target


def run() -> None:
    path = write_demo_csv()
    print(f"Wrote {path} ({sum(1 for _ in path.open()) - 2} data rows, DEMO/SYNTHETIC)")


if __name__ == "__main__":
    run()
