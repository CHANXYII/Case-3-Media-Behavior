"""Train one logistic regression per K-Means persona cluster.

This stage links the **unsupervised** customer personas with the
**supervised** trial-intent classifier, exposing the *behavioural
drivers* of trial intent inside each persona instead of a single
global coefficient set.

Output: ``outputs/cluster_supervised.json``

For every cluster we report:
- size, labelled count, base try-rate
- per-feature coefficient (log-odds), odds ratio, mean Likert score,
  and z-score relative to the global mean (so the dashboard can say
  "Cluster 2 cares 1.4 SD more about packaging than the average")

A *global* model on the full sample is also included for comparison.
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLUSTERS_CSV, OUTPUTS_DIR, TARGET_COLUMN, ensure_dirs

NUMERIC_FEATURES = [
    "coffee_value",
    "coffee_aroma",
    "coffee_convenience",
    "coffee_nutrition",
    "coffee_smooth",
    "coffee_brand_trust",
    "coffee_packaging",
    "coffee_fresh_taste",
    "coffee_intensity",
    "coffee_premium",
]

FEATURE_LABELS = {
    "coffee_value": "Perceived value",
    "coffee_aroma": "Aroma",
    "coffee_convenience": "Convenience",
    "coffee_nutrition": "Nutrition",
    "coffee_smooth": "Smoothness",
    "coffee_brand_trust": "Brand trust",
    "coffee_packaging": "Packaging",
    "coffee_fresh_taste": "Fresh-brew taste",
    "coffee_intensity": "Intensity",
    "coffee_premium": "Premium feel",
}


def fit_logreg(X: pd.DataFrame, y: pd.Series) -> tuple[np.ndarray, float, dict]:
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X.fillna(X.median()))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        clf = LogisticRegression(
            max_iter=4000,
            class_weight="balanced",
            solver="liblinear",
            C=1.0,
            random_state=42,
        )
        clf.fit(Xs, y)
    score = clf.score(Xs, y)
    return clf.coef_.ravel(), float(clf.intercept_[0]), {
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "train_accuracy": float(score),
    }


def cluster_summary(df: pd.DataFrame, features: list[str]) -> dict:
    summary: dict = {}
    summary["global_means"] = {f: float(df[f].mean()) for f in features}
    summary["global_stds"] = {f: float(df[f].std(ddof=0)) for f in features}
    return summary


def per_cluster_block(
    df: pd.DataFrame,
    cluster_id: int | None,
    features: list[str],
    glob_means: dict,
    glob_stds: dict,
) -> dict:
    if cluster_id is None:
        sub = df
        label = "global"
    else:
        sub = df[df["customer_persona_cluster"] == cluster_id]
        label = f"cluster_{cluster_id}"

    labelled = sub.dropna(subset=[TARGET_COLUMN]).copy()
    labelled[TARGET_COLUMN] = labelled[TARGET_COLUMN].astype(int)

    feat_block: list[dict] = []
    for f in features:
        m = float(sub[f].mean())
        s = glob_stds.get(f, 1.0) or 1.0
        feat_block.append({
            "name": f,
            "label": FEATURE_LABELS.get(f, f),
            "cluster_mean": m,
            "global_mean": glob_means[f],
            "z_vs_global": (m - glob_means[f]) / s if s else 0.0,
        })

    block = {
        "id": label,
        "cluster_id": cluster_id,
        "size": int(len(sub)),
        "labelled_size": int(len(labelled)),
        "try_rate": float(labelled[TARGET_COLUMN].mean()) if len(labelled) else None,
        "non_try_count": int((labelled[TARGET_COLUMN] == 0).sum()),
        "try_count": int((labelled[TARGET_COLUMN] == 1).sum()),
        "feature_means": feat_block,
    }

    if (
        len(labelled) >= 12
        and labelled[TARGET_COLUMN].nunique() == 2
        and labelled[TARGET_COLUMN].value_counts().min() >= 3
    ):
        coefs, intercept, meta = fit_logreg(labelled[features], labelled[TARGET_COLUMN])
        coef_rows = []
        for fname, c in zip(features, coefs):
            coef_rows.append({
                "feature": fname,
                "label": FEATURE_LABELS.get(fname, fname),
                "coefficient": float(c),
                "odds_ratio": float(np.exp(c)),
                "abs_coefficient": float(abs(c)),
            })
        coef_rows.sort(key=lambda r: r["abs_coefficient"], reverse=True)
        block["model"] = {
            "intercept": intercept,
            "train_accuracy": meta["train_accuracy"],
            "scaler_mean": meta["scaler_mean"],
            "scaler_scale": meta["scaler_scale"],
            "coefficients": coef_rows,
            "fitted": True,
        }
    else:
        block["model"] = {"fitted": False, "reason": "insufficient or single-class data"}

    return block


def main() -> None:
    ensure_dirs()
    if not CLUSTERS_CSV.exists():
        raise FileNotFoundError(
            f"{CLUSTERS_CSV} not found. Run the unsupervised stage first."
        )
    df = pd.read_csv(CLUSTERS_CSV)
    features = [f for f in NUMERIC_FEATURES if f in df.columns]
    df[features] = df[features].apply(pd.to_numeric, errors="coerce")

    summary = cluster_summary(df, features)
    glob_means = summary["global_means"]
    glob_stds = summary["global_stds"]

    blocks: list[dict] = [
        per_cluster_block(df, None, features, glob_means, glob_stds)
    ]
    for cid in sorted(df["customer_persona_cluster"].dropna().unique()):
        blocks.append(per_cluster_block(df, int(cid), features, glob_means, glob_stds))

    payload = {
        "target": TARGET_COLUMN,
        "features": [{"name": f, "label": FEATURE_LABELS.get(f, f)} for f in features],
        "global_means": glob_means,
        "global_stds": glob_stds,
        "blocks": blocks,
    }

    out_path = OUTPUTS_DIR / "cluster_supervised.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved per-cluster supervised payload → {out_path}")
    for b in blocks:
        head = b["id"]
        tr = b["try_rate"]
        print(f"  {head:<11s}  n={b['size']:>3d}  labelled={b['labelled_size']:>3d}  "
              f"try_rate={'-' if tr is None else f'{tr:.2f}'}  "
              f"fitted={b['model'].get('fitted', False)}")


if __name__ == "__main__":
    main()
