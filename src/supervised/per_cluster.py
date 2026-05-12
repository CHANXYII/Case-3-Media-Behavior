from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLUSTERS_CSV, LEGACY_BINARY_TARGET_COLUMN, OUTPUTS_DIR, TARGET_COLUMN, ensure_dirs, setup_thai_font

CLASS_LABELS = {0: "ไม่ลอง", 1: "อาจจะลอง", 2: "ลองแน่นอน"}
TARGET_OPTIONS = [
    {"value": 0, "key": "no", "label": CLASS_LABELS[0], "short_label": "ไม่ลอง", "color": "#D85A5A"},
    {"value": 1, "key": "maybe", "label": CLASS_LABELS[1], "short_label": "อาจจะ", "color": "#E0A458"},
    {"value": 2, "key": "try", "label": CLASS_LABELS[2], "short_label": "ลอง", "color": "#5BB89A"},
]

FEATURE_SUMMARY_CSV = OUTPUTS_DIR / "feature_selection_summary.csv"

DEFAULT_FEATURE_LABELS = {
    "coffee_value": "Perceived value",
    "coffee_aroma": "Aroma",
    "coffee_convenience": "Convenience",
    "coffee_nutrition": "Nutrition",
    "coffee_smooth": "Smoothness",
    "coffee_caffeine": "Caffeine",
    "coffee_brand_trust": "Brand trust",
    "coffee_packaging": "Packaging",
    "coffee_fresh_taste": "Fresh-brew taste",
    "coffee_intensity": "Intensity",
    "coffee_premium": "Premium feel",
}

PERSONA_LABELS = {
    0: "P0 - สายกาแฟตัวจริง",
    1: "P1 - สายไม่กาแฟ",
    2: "P2 - สายพรีเมียม",
}


def load_selected_numeric_features(df: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    if not FEATURE_SUMMARY_CSV.exists():
        raise FileNotFoundError(
            f"Missing {FEATURE_SUMMARY_CSV}. Run feature selection stage before per-cluster analysis."
        )
    summary = pd.read_csv(FEATURE_SUMMARY_CSV).sort_values("f_score", ascending=False)
    summary = summary[summary["source_var"].isin(df.columns)].drop_duplicates("source_var")
    summary = summary[summary["feature_type"] == "numeric"].copy()
    if summary.empty:
        raise ValueError("No numeric features found in feature_selection_summary.csv for per-cluster model.")

    features = summary["source_var"].tolist()
    labels = {
        row.source_var: str(row.display_label) if pd.notna(row.display_label) and str(row.display_label).strip()
        else DEFAULT_FEATURE_LABELS.get(row.source_var, row.source_var.replace("_", " ").title())
        for row in summary.itertuples(index=False)
    }
    return features, labels


def fit_logreg(X: pd.DataFrame, y: pd.Series) -> tuple[np.ndarray, np.ndarray, dict]:
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X.fillna(X.median()))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        clf = LogisticRegression(
            max_iter=4000, class_weight="balanced", solver="lbfgs",
        )
        clf.fit(Xs, y)
    return clf.coef_, clf.intercept_, {
        "classes": [int(c) for c in clf.classes_],
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "train_accuracy": float(clf.score(Xs, y)),
    }


def cluster_summary(df: pd.DataFrame, features: list[str]) -> dict:
    return {
        "global_means": {f: float(df[f].mean()) for f in features},
        "global_stds": {f: float(df[f].std(ddof=0)) for f in features},
    }


def per_cluster_block(df, cluster_id, features, feature_labels, glob_means, glob_stds) -> dict:
    if cluster_id is None:
        sub = df
        label = "global"
    else:
        sub = df[df["customer_persona_cluster"] == cluster_id]
        label = f"cluster_{cluster_id}"

    labelled = sub.dropna(subset=[TARGET_COLUMN]).copy()
    labelled[TARGET_COLUMN] = labelled[TARGET_COLUMN].astype(int)
    choice_counts = {str(i): int((labelled[TARGET_COLUMN] == i).sum()) for i in sorted(CLASS_LABELS)}
    labelled_size = len(labelled)
    choice_rates = {
        str(i): (choice_counts[str(i)] / labelled_size if labelled_size else None)
        for i in sorted(CLASS_LABELS)
    }

    feat_block = []
    for f in features:
        m = float(sub[f].mean())
        s = glob_stds.get(f, 1.0) or 1.0
        feat_block.append({
            "name": f,
            "label": feature_labels.get(f, DEFAULT_FEATURE_LABELS.get(f, f)),
            "cluster_mean": m,
            "global_mean": glob_means[f],
            "z_vs_global": (m - glob_means[f]) / s if s else 0.0,
        })

    block = {
        "id": label,
        "cluster_id": cluster_id,
        "size": int(len(sub)),
        "labelled_size": int(labelled_size),
        "choice_counts": choice_counts,
        "choice_rates": choice_rates,
        "no_count": choice_counts["0"],
        "maybe_count": choice_counts["1"],
        "try_count": choice_counts["2"],
        "no_rate": choice_rates["0"],
        "maybe_rate": choice_rates["1"],
        "try_rate": choice_rates["2"],
        "interest_count": choice_counts["1"] + choice_counts["2"],
        "interest_rate": ((choice_counts["1"] + choice_counts["2"]) / labelled_size if labelled_size else None),
        "feature_means": feat_block,
    }

    if (
        len(labelled) >= 12
        and labelled[TARGET_COLUMN].nunique() >= 2
        and labelled[TARGET_COLUMN].value_counts().min() >= 3
    ):
        coefs, intercepts, meta = fit_logreg(labelled[features], labelled[TARGET_COLUMN])
        coefficients_by_class: dict[str, list[dict]] = {}
        for class_value, class_coefs in zip(meta["classes"], coefs):
            coef_rows = [{
                "feature": fname,
                "label": feature_labels.get(fname, DEFAULT_FEATURE_LABELS.get(fname, fname)),
                "coefficient": float(c),
                "odds_ratio": float(np.exp(c)),
                "abs_coefficient": float(abs(c)),
            } for fname, c in zip(features, class_coefs)]
            coef_rows.sort(key=lambda r: r["abs_coefficient"], reverse=True)
            coefficients_by_class[str(class_value)] = coef_rows
        block["model"] = {
            "type": "multinomial_logistic_regression",
            "classes": meta["classes"],
            "class_labels": {str(k): v for k, v in CLASS_LABELS.items()},
            "intercepts": {str(cls): float(value) for cls, value in zip(meta["classes"], intercepts)},
            "train_accuracy": meta["train_accuracy"],
            "scaler_mean": meta["scaler_mean"],
            "scaler_scale": meta["scaler_scale"],
            "coefficients_by_class": coefficients_by_class,
            "coefficients": coefficients_by_class.get("2", []),
            "fitted": True,
        }
    else:
        block["model"] = {"fitted": False, "reason": "insufficient or single-class data"}

    return block


def plot_cluster_coefficients(block: dict, output_path: Path, class_key: str = "2"):
    if not block.get("model", {}).get("fitted"):
        return
    coef_rows = block["model"].get("coefficients_by_class", {}).get(class_key, [])
    if not coef_rows:
        return

    plot_df = pd.DataFrame(coef_rows).copy()
    plot_df = plot_df.sort_values("coefficient", ascending=True)
    colors = ["#1D9E75" if c > 0 else "#D85A30" for c in plot_df["coefficient"]]
    persona = PERSONA_LABELS.get(block.get("cluster_id"), f"Cluster {block.get('cluster_id')}")

    fig, ax = plt.subplots(figsize=(10, max(5.5, 0.55 * len(plot_df))))
    ax.barh(plot_df["label"], plot_df["coefficient"], color=colors, alpha=0.88)
    ax.axvline(0, color="black", linewidth=0.7)

    max_abs = max(0.1, float(plot_df["coefficient"].abs().max()))
    for idx, row in enumerate(plot_df.itertuples(index=False)):
        coef = row.coefficient
        offset = 0.03 * max_abs if coef >= 0 else -0.03 * max_abs
        ax.text(
            coef + offset,
            idx,
            f"{coef:+.3f}  |  OR {row.odds_ratio:.2f}x",
            va="center",
            ha="left" if coef >= 0 else "right",
            fontsize=9,
            color="#2F2F2F",
        )

    ax.set_title(
        f"{persona} - Logistic Regression Coefficients for 'ลองแน่นอน'\n"
        "(green = pushes toward definite try, orange = pushes against)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Coefficient (log-odds on standardised feature)")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    fig.text(
        0.01,
        0.01,
        f"n={block['labelled_size']} labelled rows | try_rate={block['try_rate']:.1%} | maybe_rate={block['maybe_rate']:.1%}",
        ha="left",
        fontsize=9,
        color="#666666",
    )
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_cluster_comparison(block_a: dict, block_b: dict, output_path: Path, class_key: str = "2"):
    if not block_a.get("model", {}).get("fitted") or not block_b.get("model", {}).get("fitted"):
        return

    coef_a = pd.DataFrame(block_a["model"].get("coefficients_by_class", {}).get(class_key, [])).copy()
    coef_b = pd.DataFrame(block_b["model"].get("coefficients_by_class", {}).get(class_key, [])).copy()
    if coef_a.empty or coef_b.empty:
        return

    cmp_df = coef_a[["feature", "label", "coefficient"]].merge(
        coef_b[["feature", "coefficient"]],
        on="feature",
        suffixes=("_p0", "_p2"),
    )
    cmp_df["abs_max"] = cmp_df[["coefficient_p0", "coefficient_p2"]].abs().max(axis=1)
    cmp_df = cmp_df.sort_values("abs_max", ascending=False).reset_index(drop=True)

    y = np.arange(len(cmp_df))
    height = 0.36
    fig, ax = plt.subplots(figsize=(11, max(5.8, 0.62 * len(cmp_df))))
    ax.barh(y - height / 2, cmp_df["coefficient_p0"], height=height, color="#C2410C", alpha=0.88, label="P0")
    ax.barh(y + height / 2, cmp_df["coefficient_p2"], height=height, color="#15803D", alpha=0.88, label="P2")
    ax.axvline(0, color="black", linewidth=0.7)

    max_abs = max(0.1, float(cmp_df[["coefficient_p0", "coefficient_p2"]].abs().to_numpy().max()))
    for idx, row in enumerate(cmp_df.itertuples(index=False)):
        for coef, yy in ((row.coefficient_p0, y[idx] - height / 2), (row.coefficient_p2, y[idx] + height / 2)):
            ax.text(
                coef + (0.03 * max_abs if coef >= 0 else -0.03 * max_abs),
                yy,
                f"{coef:+.3f}",
                va="center",
                ha="left" if coef >= 0 else "right",
                fontsize=8.5,
                color="#2F2F2F",
            )

    ax.set_yticks(y)
    ax.set_yticklabels(cmp_df["label"])
    ax.invert_yaxis()
    ax.set_title(
        "P0 vs P2 - Coefficient Comparison for 'ลองแน่นอน'\n"
        "(same 10 standardized numeric features, fit separately within each persona)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlabel("Coefficient (log-odds on standardised feature)")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    fig.text(
        0.01,
        0.01,
        f"P0: n={block_a['labelled_size']} labelled, try_rate={block_a['try_rate']:.1%} | "
        f"P2: n={block_b['labelled_size']} labelled, try_rate={block_b['try_rate']:.1%}",
        ha="left",
        fontsize=9,
        color="#666666",
    )
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    ensure_dirs()
    setup_thai_font()
    df = pd.read_csv(CLUSTERS_CSV)
    features, feature_labels = load_selected_numeric_features(df)
    df[features] = df[features].apply(pd.to_numeric, errors="coerce")

    print("Selected numeric per-cluster features from feature_selection_summary.csv:")
    for f in features:
        print(f"  - {f} ({feature_labels.get(f, f)})")

    summary = cluster_summary(df, features)
    glob_means = summary["global_means"]
    glob_stds = summary["global_stds"]

    blocks = [per_cluster_block(df, None, features, feature_labels, glob_means, glob_stds)]
    for cid in sorted(df["customer_persona_cluster"].dropna().unique()):
        blocks.append(per_cluster_block(df, int(cid), features, feature_labels, glob_means, glob_stds))

    payload = {
        "target": TARGET_COLUMN,
        "legacy_binary_target": LEGACY_BINARY_TARGET_COLUMN,
        "target_options": TARGET_OPTIONS,
        "features": [{"name": f, "label": feature_labels.get(f, DEFAULT_FEATURE_LABELS.get(f, f))} for f in features],
        "global_means": glob_means,
        "global_stds": glob_stds,
        "blocks": blocks,
    }

    out_path = OUTPUTS_DIR / "cluster_supervised.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    for block in blocks:
        if block.get("cluster_id") == 0:
            plot_cluster_coefficients(block, OUTPUTS_DIR / "cluster_p0_coefficients.png")
        if block.get("cluster_id") == 2:
            plot_cluster_coefficients(block, OUTPUTS_DIR / "cluster_p2_coefficients.png")

    p0_block = next((b for b in blocks if b.get("cluster_id") == 0), None)
    p2_block = next((b for b in blocks if b.get("cluster_id") == 2), None)
    if p0_block and p2_block:
        plot_cluster_comparison(p0_block, p2_block, OUTPUTS_DIR / "cluster_p0_p2_comparison.png")

    print(f"Saved per-cluster supervised payload → {out_path}")
    for b in blocks:
        head = b["id"]
        tr = b["try_rate"]
        mr = b["maybe_rate"]
        print(f"  {head:<11s}  n={b['size']:>3d}  labelled={b['labelled_size']:>3d}  "
              f"try_rate={'-' if tr is None else f'{tr:.2f}'}  "
              f"maybe_rate={'-' if mr is None else f'{mr:.2f}'}  "
              f"fitted={b['model'].get('fitted', False)}")


if __name__ == "__main__":
    main()
