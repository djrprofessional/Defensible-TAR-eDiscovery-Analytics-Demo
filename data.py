from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic_review_set.csv"


def load_demo_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)
