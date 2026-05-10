"""End-to-end pipeline runner for the Case 3 Media Behavior project.

Runs every stage in order so the dataset, charts, models, and dashboard
artefacts stay in sync:

    raw csv ─► clean + feature selection ─► unsupervised personas
                                       ─► supervised model + coefficients
                                       ─► web dashboard artefacts

Usage::

    python run_pipeline.py
"""
from __future__ import annotations

import runpy
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STAGES: list[tuple[str, str]] = [
    ("Clean + feature selection",
     "src.feature_engineering.feature_selection_visualization"),
    ("Unsupervised (K-Means / DBSCAN / IsolationForest)",
     "src.unsupervised.unsupervised_learning"),
    ("Supervised training",
     "src.supervised.train"),
]


def run_stage(label: str, module: str) -> None:
    print(f"\n{'='*72}\n▶ {label}  ({module})\n{'='*72}")
    start = time.time()
    runpy.run_module(module, run_name="__main__")
    print(f"   done in {time.time() - start:.1f}s")


def main() -> None:
    for label, module in STAGES:
        run_stage(label, module)
    print("\nAll stages completed. Launch the dashboard with:")
    print("    streamlit run src/web/app.py")


if __name__ == "__main__":
    main()
