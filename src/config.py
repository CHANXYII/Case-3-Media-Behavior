"""Shared paths and plot setup for the Case 3 Media Behavior project.

Every analysis script imports from this module so paths stay consistent
regardless of the current working directory.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
ASSETS_DIR: Path = PROJECT_ROOT / "assets"

RAW_CSV: Path = RAW_DATA_DIR / "Case_3_Media_Behavior.csv"
CLEAN_CSV: Path = PROCESSED_DATA_DIR / "media_behavior_cleaned.csv"
CLUSTERS_CSV: Path = PROCESSED_DATA_DIR / "media_behavior_with_clusters.csv"
COLUMN_MAPPING_JSON: Path = PROCESSED_DATA_DIR / "column_mapping.json"

FONT_PATH: Path = ASSETS_DIR / "DB-Adman-X.ttf"

TARGET_COLUMN: str = "target_try_new_rtd_coffee"


def ensure_dirs() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def setup_thai_font() -> str | None:
    """Register the Thai-friendly font for matplotlib/seaborn.

    Returns the resolved font family name, or None if the font file is
    missing (in which case seaborn defaults are applied).
    """
    if FONT_PATH.exists():
        font_manager.fontManager.addfont(str(FONT_PATH))
        font_name = font_manager.FontProperties(fname=str(FONT_PATH)).get_name()
        plt.rcParams["font.family"] = font_name
        plt.rcParams["font.sans-serif"] = [font_name]
        sns.set_theme(
            style="whitegrid",
            rc={"font.family": font_name, "font.sans-serif": [font_name]},
        )
        return font_name
    sns.set_theme(style="whitegrid")
    return None
