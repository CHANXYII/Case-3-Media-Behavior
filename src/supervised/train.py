"""Supervised training stub.

This module is a placeholder for the next development stage. It loads the
cleaned dataset and prints a baseline class distribution so the dev who picks
this up has a working entry point to extend.

Run:
    python -m src.supervised.train
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLEAN_CSV, TARGET_COLUMN, ensure_dirs


def load_dataset() -> pd.DataFrame:
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(
            f"{CLEAN_CSV} not found. Run `python -m src.data_cleaning.data_cleaning` "
            "and `python -m src.feature_engineering.feature_selection` first."
        )
    return pd.read_csv(CLEAN_CSV)


def main() -> None:
    ensure_dirs()
    df = load_dataset()
    print(f"Loaded cleaned dataset: {df.shape[0]} rows x {df.shape[1]} cols")

    if TARGET_COLUMN not in df.columns:
        raise KeyError(f"Target column '{TARGET_COLUMN}' missing from cleaned CSV.")

    target = df[TARGET_COLUMN].dropna().astype(int)
    counts = target.value_counts().sort_index()
    print("\nTarget class distribution:")
    for label, count in counts.items():
        print(f"  {label}: {count} ({count / len(target):.1%})")

    print(
        "\nTODO (next dev): implement feature pipeline, train baseline + boosted "
        "model, persist to models/, save metrics to outputs/supervised_metrics.json."
    )


if __name__ == "__main__":
    main()
