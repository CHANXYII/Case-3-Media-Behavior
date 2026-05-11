import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch
from sklearn.feature_selection import f_classif
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CLEAN_CSV,
    LEGACY_BINARY_TARGET_COLUMN,
    OUTPUTS_DIR,
    RAW_CSV,
    TARGET_COLUMN,
    ensure_dirs,
    setup_thai_font,
)
from src.data_cleaning.data_cleaning import clean_data

raw_data_path = RAW_CSV
clean_data_path = CLEAN_CSV
output_dir = OUTPUTS_DIR
target_column = TARGET_COLUMN

setup_thai_font()

age_group_mapping = {
    "ต่ำกว่า 18ปี": 17.0,
    "18-22ปี": 20.0,
    "23-29ปี": 26.0,
    "30-39ปี": 35.0,
    "40-49ปี": 45.0,
    "50ปี ขึ้นไป": 55.0,
}

likert_cols = [
    "coffee_fresh_taste", "coffee_intensity", "coffee_smooth", "coffee_acidity",
    "coffee_aroma", "coffee_caffeine", "coffee_origin", "coffee_convenience",
    "coffee_value", "coffee_nutrition", "coffee_brand_trust", "coffee_premium",
    "coffee_packaging", "tea_aroma", "tea_intensity", "tea_no_sugar",
    "tea_zero_kcal", "tea_nutrition", "tea_origin", "tea_brewing",
    "tea_convenience", "tea_brand_trust", "tea_premium", "tea_packaging",
]

numeric_feature_labels = {
    "coffee_value": "Perceived value",
    "coffee_aroma": "Aroma preference",
    "coffee_convenience": "Convenience importance",
    "coffee_nutrition": "Nutrition importance",
    "coffee_smooth": "Smooth taste preference",
    "coffee_brand_trust": "Brand trust importance",
    "coffee_packaging": "Packaging importance",
    "coffee_fresh_taste": "Fresh taste preference",
    "coffee_caffeine": "Caffeine importance",
}

categorical_feature_labels = {
    "most_freq_rtd_brand": "Primary RTD coffee brand",
    "dur_online": "Daily online usage",
    "presenter_effect": "Presenter influence",
    "most_freq_radio": "Most-listened radio station",
    "most_freq_coffee": "Most-consumed coffee format",
    "dur_radio": "Daily radio usage",
    "most_freq_rtd_tea_brand": "Primary RTD tea brand",
}

categorical_value_labels = {
    ("most_freq_rtd_brand", "ไม่ดื่มกาแฟ Ready to drink เลย"): "No regular RTD coffee brand",
    ("dur_online", "มากกว่า 6 ชม./วัน"): "Online use > 6 hrs/day",
    ("presenter_effect", "มีผล"): "Presenter influences purchase",
    ("presenter_effect", "ไม่มีผล"): "Presenter does not influence purchase",
    ("dur_radio", "1-2 ชม./วัน"): "Radio use 1-2 hrs/day",
}

positive_driver_color = "#2C7FB8"
negative_driver_color = "#D95F02"


def split_answers(value):
    text = str(value).strip()
    if pd.isna(value) or not text or text.lower() == "nan":
        return []
    return [item.strip() for item in text.split(",") if item.strip() and item.strip().lower() != "nan"]


def first_value(series):
    series = series.dropna()
    series = series[series.astype(str).str.strip() != ""]
    return series.iloc[0] if len(series) else np.nan


def merge_province(series):
    values = []
    for value in series.dropna():
        for item in split_answers(value):
            if item not in values:
                values.append(item)
    return ",".join(values) if values else np.nan


def derive_binary_target(value):
    answers = split_answers(value)
    if any("ลอง" in answer and answer != "ไม่ลอง" for answer in answers):
        return 1.0
    if answers and all(answer == "ไม่ลอง" for answer in answers):
        return 0.0
    return np.nan


def derive_target(value):
    answers = split_answers(value)
    if not answers:
        return np.nan
    if any(answer == "ลองเลย ชอบลองของออกใหม่อยู่แล้ว" for answer in answers):
        return 2.0
    if any("ลอง" in answer and answer != "ไม่ลอง" for answer in answers):
        return 1.0
    if all(answer == "ไม่ลอง" for answer in answers):
        return 0.0
    return np.nan


def nice_label_format(text):
    return text.replace("__", " = ").replace("_", " ")


def format_p_value(p_value):
    if p_value < 0.001:
        return "p < 0.001"
    return f"p = {p_value:.3f}"


def get_feature_metadata(feature, analysis_df):
    if feature in analysis_df.columns:
        return {
            "source_var": feature,
            "feature_type": "numeric",
            "level": None,
        }

    for col in analysis_df.select_dtypes(include="object").columns:
        prefix = f"{col}_"
        if feature.startswith(prefix):
            return {
                "source_var": col,
                "feature_type": "categorical",
                "level": feature[len(prefix):],
            }

    return {
        "source_var": feature,
        "feature_type": "unknown",
        "level": None,
    }


def get_feature_display_label(source_var, feature_type, level=None):
    if feature_type == "numeric":
        return numeric_feature_labels.get(source_var, nice_label_format(source_var).title())

    if feature_type == "categorical":
        if (source_var, level) in categorical_value_labels:
            return categorical_value_labels[(source_var, level)]
        base_label = categorical_feature_labels.get(source_var, nice_label_format(source_var).title())
        return f"{base_label} = {level}"

    return nice_label_format(source_var)


def summarize_feature_effect(source_var, feature_type, analysis_df, target, level=None):
    try_mask = target == 2
    maybe_mask = target == 1
    no_mask = target == 0

    if feature_type == "numeric":
        values = pd.to_numeric(analysis_df[source_var], errors="coerce")
        mean_try = values[try_mask].mean()
        mean_maybe = values[maybe_mask].mean()
        mean_not_try = values[no_mask].mean()
        delta = mean_try - mean_not_try
        return {
            "effect_value": delta,
            "direction": "positive" if delta >= 0 else "negative",
            "effect_label": f"try vs no {delta:+.2f} avg; maybe {mean_maybe:.2f}",
        }

    if feature_type == "categorical":
        mask = analysis_df[source_var].fillna("ไม่ระบุ").astype(str).eq(level)
        rate_try_in = try_mask[mask].mean()
        rate_try_out = try_mask[~mask].mean()
        rate_maybe_in = maybe_mask[mask].mean()
        rate_maybe_out = maybe_mask[~mask].mean()
        lift = (rate_try_in - rate_try_out) * 100
        maybe_lift = (rate_maybe_in - rate_maybe_out) * 100
        return {
            "effect_value": lift,
            "direction": "positive" if lift >= 0 else "negative",
            "effect_label": f"{lift:+.1f} pts definite try; {maybe_lift:+.1f} pts maybe",
        }

    return {
        "effect_value": np.nan,
        "direction": "positive",
        "effect_label": "",
    }


def build_feature_summary_table(analysis_df, feature_scores, top_n=10):
    target = analysis_df[target_column].astype(int)
    significant_scores = feature_scores[feature_scores["p_value"] <= 0.05].copy()

    rows = []
    used_source_vars = set()

    for _, row in significant_scores.iterrows():
        metadata = get_feature_metadata(row["feature"], analysis_df)
        source_var = metadata["source_var"]

        if source_var in used_source_vars:
            continue

        effect_summary = summarize_feature_effect(
            source_var=source_var,
            feature_type=metadata["feature_type"],
            analysis_df=analysis_df,
            target=target,
            level=metadata["level"],
        )

        rows.append({
            "feature": row["feature"],
            "source_var": source_var,
            "feature_type": metadata["feature_type"],
            "display_label": get_feature_display_label(
                source_var=source_var,
                feature_type=metadata["feature_type"],
                level=metadata["level"],
            ),
            "f_score": row["f_score"],
            "p_value": row["p_value"],
            **effect_summary,
        })
        used_source_vars.add(source_var)

        if len(rows) >= top_n:
            break

    return pd.DataFrame(rows)


def build_clean_data():
    raw_df = pd.read_csv(raw_data_path)
    raw_df["respondent_id"] = np.arange(1, len(raw_df) + 1)
    raw_df["age_group_raw"] = raw_df["อายุ"]

    df = clean_data(raw_df)
    agg = {col: (merge_province if col == "province" else first_value) for col in df.columns if col != "respondent_id"}
    df = df.groupby("respondent_id", as_index=False).agg(agg)

    df["age_group"] = df["age_group_raw"].astype(str).replace("nan", np.nan)
    df["age"] = df["age_group"].map(age_group_mapping)
    df[LEGACY_BINARY_TARGET_COLUMN] = df["will_try_new_rtd_coffee"].apply(derive_binary_target)
    df[target_column] = df["will_try_new_rtd_coffee"].apply(derive_target)

    ensure_dirs()
    df.to_csv(clean_data_path, index=False, encoding="utf-8-sig")
    return df


def prepare_feature_data(df):
    analysis_df = df.dropna(subset=[target_column]).copy()
    target = analysis_df[target_column].astype(int)

    numeric_cols = [
        col for col in analysis_df.columns
        if pd.api.types.is_numeric_dtype(analysis_df[col])
        and col not in ["respondent_id", target_column, LEGACY_BINARY_TARGET_COLUMN]
    ]
    numeric_df = analysis_df[numeric_cols].fillna(analysis_df[numeric_cols].median(numeric_only=True))
    scaled_numeric = pd.DataFrame(
        StandardScaler().fit_transform(numeric_df),
        columns=numeric_cols,
        index=analysis_df.index,
    )

    excluded_cols = {
        "respondent_id", "province", "timestamp", "reason_like", "reason_dislike",
        "reason_fav_tea", "customer_segment", "age_group_raw", "will_try_new_rtd_coffee",
    }
    category_cols = []
    for col in analysis_df.select_dtypes(include="object").columns:
        if col in excluded_cols:
            continue
        sample = analysis_df[col].fillna("").astype(str)
        if sample.str.contains(",").mean() == 0 and 1 < sample.nunique() <= 15:
            category_cols.append(col)

    encoded_df = pd.get_dummies(analysis_df[category_cols].fillna("ไม่ระบุ"), dtype=int)
    feature_df = pd.concat([scaled_numeric, encoded_df], axis=1)

    f_scores, p_values = f_classif(feature_df, target)
    feature_scores = pd.DataFrame({
        "feature": feature_df.columns,
        "f_score": f_scores,
        "p_value": p_values,
    }).sort_values("f_score", ascending=False)

    return analysis_df, feature_scores


def make_distribution_table(df):
    rows = []
    cols = [col for col in likert_cols if col in df.columns]
    for col in cols:
        score_dist = pd.to_numeric(df[col], errors="coerce").value_counts(normalize=True)
        rows.append(score_dist.reindex([1.0, 2.0, 3.0, 4.0, 5.0], fill_value=0).rename(nice_label_format(col)))
    dist_df = pd.DataFrame(rows)
    dist_df.columns = ["1", "2", "3", "4", "5"]
    return dist_df


def make_correlation_table(df):
    cols = [col for col in likert_cols if col in df.columns]
    corr = df[cols + [target_column]].corr(numeric_only=True)[target_column]
    corr = corr.drop(target_column).dropna().sort_values(key=np.abs, ascending=False).head(8)
    heatmap_cols = [target_column] + corr.index.tolist()
    heatmap_df = df[heatmap_cols].corr(numeric_only=True)
    heatmap_df.index = [nice_label_format(col) for col in heatmap_df.index]
    heatmap_df.columns = [nice_label_format(col) for col in heatmap_df.columns]
    return heatmap_df


def make_target_distribution(df):
    valid = df.dropna(subset=[target_column]).copy()
    counts = valid[target_column].astype(int).value_counts().reindex([0, 1, 2], fill_value=0)
    labels = ["ไม่ลอง (0)", "อาจจะลอง (1)", "ลองแน่นอน (2)"]
    colors = ["#D85A5A", "#E0A458", "#5BB89A"]
    total = len(valid)
    pcts = counts.values / total * 100

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # left: donut
    wedge_props = {"width": 0.5, "edgecolor": "white", "linewidth": 2}
    axes[0].pie(
        pcts,
        labels=None,
        colors=colors,
        autopct=lambda p: f"{p:.1f}%",
        startangle=90,
        wedgeprops=wedge_props,
        textprops={"fontsize": 14, "fontweight": "bold"},
        pctdistance=0.75,
    )
    axes[0].set_title("Trial Intent Distribution\n(% of valid respondents)", fontsize=14, fontweight="bold")
    axes[0].legend(
        labels=[f"{l}  n={c}" for l, c in zip(labels, counts.values)],
        loc="lower center",
        frameon=False,
        fontsize=11,
    )

    # right: horizontal bar with count + pct labels
    bars = axes[1].barh(labels, pcts, color=colors, alpha=0.9, height=0.45)
    axes[1].set_xlim(0, 110)
    for bar, pct, cnt in zip(bars, pcts, counts.values):
        axes[1].text(
            bar.get_width() + 1.5,
            bar.get_y() + bar.get_height() / 2,
            f"{pct:.1f}%  (n={cnt})",
            va="center",
            fontsize=13,
            fontweight="bold",
        )
    axes[1].set_xlabel("Percent of valid respondents")
    axes[1].set_title("Count breakdown", fontsize=14, fontweight="bold")
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    axes[1].grid(axis="x", linestyle="--", alpha=0.25)

    fig.suptitle(
        f"Target: Three-choice willingness to try new RTD coffee  |  n={total} valid  |  excluded NaN={len(df)-total}",
        fontsize=13,
        color="#555555",
        y=1.01,
    )
    plt.tight_layout()
    plt.savefig(output_dir / "target_distribution.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_tryrate_by_segment(df, seg_cols, title, filename):
    valid = df.dropna(subset=[target_column]).copy()
    valid[target_column] = valid[target_column].astype(int)
    valid["definite_try"] = valid[target_column].eq(2).astype(int)

    n_cols = len(seg_cols)
    fig, axes = plt.subplots(1, n_cols, figsize=(6 * n_cols, 7))
    if n_cols == 1:
        axes = [axes]

    for ax, col in zip(axes, seg_cols):
        if col not in valid.columns:
            ax.set_visible(False)
            continue

        grp = (
            valid.groupby(col, observed=True)["definite_try"]
            .agg(try_rate="mean", n="count")
            .reset_index()
            .sort_values("try_rate", ascending=True)
        )
        grp["try_pct"] = grp["try_rate"] * 100
        overall = valid["definite_try"].mean() * 100

        colors = [
            positive_driver_color if v >= overall else negative_driver_color
            for v in grp["try_pct"]
        ]
        bars = ax.barh(grp[col].astype(str), grp["try_pct"], color=colors, alpha=0.88, height=0.55)

        for bar, pct, n_val in zip(bars, grp["try_pct"], grp["n"]):
            ax.text(
                bar.get_width() + 0.8,
                bar.get_y() + bar.get_height() / 2,
                f"{pct:.1f}%  (n={n_val})",
                va="center",
                fontsize=10,
            )

        ax.axvline(overall, color="#555555", linestyle="--", linewidth=1.2, label=f"Overall {overall:.1f}%")
        ax.set_xlim(0, 110)
        ax.set_xlabel("Definite trial-intent rate (%)")
        ax.set_title(col.replace("_", " ").title(), fontsize=12, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle="--", alpha=0.2)
        ax.legend(fontsize=9, frameon=False)

    fig.suptitle(title, fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_likert_by_target(df):
    valid = df.dropna(subset=[target_column]).copy()
    valid[target_column] = valid[target_column].astype(int)

    top_likert = [col for col in [
        "coffee_value", "coffee_aroma", "coffee_convenience", "coffee_smooth",
        "coffee_brand_trust", "coffee_fresh_taste", "coffee_caffeine", "coffee_nutrition",
    ] if col in valid.columns]

    n = len(top_likert)
    ncols = 4
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.5 * nrows))
    axes_flat = axes.flatten() if n > 1 else [axes]

    palette = {0: "#D85A5A", 1: "#E0A458", 2: "#5BB89A"}
    group_labels = {0: "ไม่ลอง (0)", 1: "อาจจะลอง (1)", 2: "ลองแน่นอน (2)"}

    for ax, col in zip(axes_flat, top_likert):
        plot_df = valid[[col, target_column]].copy()
        plot_df[target_column] = plot_df[target_column].map(group_labels)
        sns.boxplot(
            data=plot_df,
            x=col,
            y=target_column,
            palette={v: palette[k] for k, v in group_labels.items()},
            orient="h",
            ax=ax,
            width=0.45,
            flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
        )
        mean_try = valid.loc[valid[target_column] == 2, col].mean()
        mean_not = valid.loc[valid[target_column] == 0, col].mean()
        delta = mean_try - mean_not
        ax.set_title(
            numeric_feature_labels.get(col, col.replace("_", " ").title()),
            fontsize=11,
            fontweight="bold",
        )
        ax.set_xlabel(f"Likert score (1-5)  |  Δ mean = {delta:+.2f}", fontsize=9)
        ax.set_ylabel("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    for ax in axes_flat[n:]:
        ax.set_visible(False)

    fig.suptitle(
        "Likert Attribute Scores by Three-Choice Trial Intent Group",
        fontsize=15,
        fontweight="bold",
        y=1.01,
    )
    plt.tight_layout()
    plt.savefig(output_dir / "likert_by_target.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_imbalance_summary(df):
    valid = df.dropna(subset=[target_column]).copy()
    valid[target_column] = valid[target_column].astype(int)
    counts = valid[target_column].value_counts().reindex([0, 1, 2], fill_value=0)
    total = int(counts.sum())
    majority = int(counts.max())
    minority = int(counts[counts > 0].min()) if (counts > 0).any() else 0
    imbalance_ratio = majority / minority if minority > 0 else float("inf")
    weights = {
        cls: (total / (len(counts) * count) if count > 0 else 0)
        for cls, count in counts.items()
    }
    baseline_acc = majority / total * 100 if total else 0

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    labels = ["ไม่ลอง (0)", "อาจจะลอง (1)", "ลองแน่นอน (2)"]
    colors = ["#D85A5A", "#E0A458", "#5BB89A"]
    bars = axes[0].bar(labels, counts.values, color=colors, alpha=0.88, width=0.45)
    for bar, n_val in zip(bars, counts.values):
        pct = n_val / total * 100 if total else 0
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"n={n_val}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=12, fontweight="bold",
        )
    axes[0].set_title("Class Distribution", fontsize=14, fontweight="bold")
    axes[0].set_ylabel("Count")
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)
    axes[0].grid(axis="y", linestyle="--", alpha=0.25)

    info_lines = [
        f"Imbalance ratio:  {imbalance_ratio:.2f} : 1  (majority : minority)",
        f"Class weight[0]:  {weights[0]:.3f}",
        f"Class weight[1]:  {weights[1]:.3f}",
        f"Class weight[2]:  {weights[2]:.3f}",
        f"Baseline accuracy (predict majority):  {baseline_acc:.1f}%",
        "",
        "Implication:",
        "  - Accuracy is misleading under imbalance.",
        "  - Use macro Precision-Recall / F1 for model eval.",
        "  - Apply class_weight='balanced' in models.",
        "  - Focus on definite-trial class (choice=2) profiling.",
    ]
    axes[1].axis("off")
    axes[1].text(
        0.05, 0.95, "\n".join(info_lines),
        transform=axes[1].transAxes, va="top", ha="left",
        fontsize=12, family="monospace",
        bbox=dict(boxstyle="round,pad=0.8", facecolor="#F5F5F5", edgecolor="#CCCCCC"),
    )
    axes[1].set_title("Imbalance Diagnostics", fontsize=14, fontweight="bold")

    fig.suptitle(
        f"Target Imbalance Analysis  |  n={total} valid respondents",
        fontsize=14, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    plt.savefig(output_dir / "imbalance_summary.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_minority_profile(df):
    valid = df.dropna(subset=[target_column]).copy()
    valid[target_column] = valid[target_column].astype(int)
    minority = valid[valid[target_column] == 2]
    n_minority = len(minority)

    seg_cols = ["gender", "age_group", "occupation", "income", "most_freq_coffee", "presenter_effect"]
    seg_cols = [c for c in seg_cols if c in minority.columns]

    ncols = 2
    nrows = (len(seg_cols) + 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 4.5 * nrows))
    axes_flat = axes.flatten() if len(seg_cols) > 1 else [axes]

    for ax, col in zip(axes_flat, seg_cols):
        grp = (minority[col].value_counts(normalize=True) * 100).reset_index()
        grp.columns = [col, "pct"]
        grp = grp.sort_values("pct", ascending=True)
        ax.barh(grp[col].astype(str), grp["pct"], color=positive_driver_color, alpha=0.85, height=0.5)
        val_counts = minority[col].value_counts()
        for i, (_, row) in enumerate(grp.iterrows()):
            n_val = val_counts.get(row[col], 0)
            ax.text(row["pct"] + 0.8, i, f"{row['pct']:.1f}%  (n={n_val})", va="center", fontsize=9)
        ax.set_xlim(0, 115)
        ax.set_title(col.replace("_", " ").title(), fontsize=11, fontweight="bold")
        ax.set_xlabel("% within definite-try group")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle="--", alpha=0.2)

    for ax in axes_flat[len(seg_cols):]:
        ax.set_visible(False)

    fig.suptitle(
        f"Who Are the Definite Triers?  |  Minority class (choice=2) profile  |  n={n_minority}",
        fontsize=14, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    plt.savefig(output_dir / "minority_profile.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_cohens_d_chart(df):
    valid = df.dropna(subset=[target_column]).copy()
    valid[target_column] = valid[target_column].astype(int)
    group1 = valid[valid[target_column] == 2]
    group0 = valid[valid[target_column] == 0]

    results = []
    for col in likert_cols:
        if col not in valid.columns:
            continue
        s1 = group1[col].dropna()
        s0 = group0[col].dropna()
        if len(s1) < 2 or len(s0) < 2:
            continue
        n1, n0 = len(s1), len(s0)
        pooled_std = np.sqrt(
            ((n1 - 1) * s1.std(ddof=1) ** 2 + (n0 - 1) * s0.std(ddof=1) ** 2) / (n1 + n0 - 2)
        )
        d = (s1.mean() - s0.mean()) / pooled_std if pooled_std > 0 else 0.0
        results.append({
            "feature": col,
            "cohens_d": d,
            "label": numeric_feature_labels.get(col, col.replace("_", " ").title()),
        })

    results_df = pd.DataFrame(results).sort_values("cohens_d", ascending=True)
    colors = [positive_driver_color if d >= 0 else negative_driver_color for d in results_df["cohens_d"]]

    fig, ax = plt.subplots(figsize=(11, max(6, len(results_df) * 0.45)))
    ax.barh(results_df["label"], results_df["cohens_d"], color=colors, alpha=0.88, height=0.55)
    for i, d in enumerate(results_df["cohens_d"]):
        offset = 0.015 if d >= 0 else -0.015
        ha = "left" if d >= 0 else "right"
        ax.text(d + offset, i, f"{d:+.3f}", va="center", fontsize=9, ha=ha)
    ax.axvline(0, color="#555555", linewidth=1)
    ax.axvline(0.5, color="#AAAAAA", linewidth=0.8, linestyle="--", label="Medium effect (d=0.5)")
    ax.axvline(-0.5, color="#AAAAAA", linewidth=0.8, linestyle="--")
    ax.axvline(0.8, color="#888888", linewidth=0.8, linestyle=":", label="Large effect (d=0.8)")
    ax.axvline(-0.8, color="#888888", linewidth=0.8, linestyle=":")
    ax.set_xlabel("Cohen's d  (positive = definite triers rate this attribute higher than non-triers)")
    ax.set_title(
        "Imbalance-Robust Effect Size per Likert Attribute\n(Cohen's d, pooled SD)",
        fontsize=13, fontweight="bold",
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.2)
    ax.legend(fontsize=9, frameon=False)
    plt.tight_layout()
    plt.savefig(output_dir / "cohens_d_features.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_high_value_segments(df, min_n=10, top_n=12):
    valid = df.dropna(subset=[target_column]).copy()
    valid[target_column] = valid[target_column].astype(int)
    valid["definite_try"] = valid[target_column].eq(2).astype(int)
    overall_rate = valid["definite_try"].mean() * 100

    seg_cols = [
        "gender", "age_group", "occupation", "income",
        "most_freq_coffee", "most_freq_rtd_brand", "presenter_effect", "dur_online",
    ]
    seg_cols = [c for c in seg_cols if c in valid.columns]

    rows = []
    for col in seg_cols:
        grp = valid.groupby(col, observed=True)["definite_try"].agg(try_rate="mean", n="count")
        for segment, row in grp.iterrows():
            if row["n"] >= min_n:
                rows.append({
                    "dimension": col.replace("_", " ").title(),
                    "segment": str(segment),
                    "try_rate_pct": row["try_rate"] * 100,
                    "n": int(row["n"]),
                })

    seg_df = pd.DataFrame(rows).sort_values("try_rate_pct", ascending=False).head(top_n)
    seg_df = seg_df.sort_values("try_rate_pct", ascending=True)
    seg_df["label"] = seg_df["dimension"] + ": " + seg_df["segment"]
    colors = [
        positive_driver_color if r >= overall_rate else negative_driver_color
        for r in seg_df["try_rate_pct"]
    ]

    fig, ax = plt.subplots(figsize=(12, max(6, len(seg_df) * 0.55)))
    ax.barh(seg_df["label"], seg_df["try_rate_pct"], color=colors, alpha=0.88, height=0.55)
    for i, (pct, n_val) in enumerate(zip(seg_df["try_rate_pct"], seg_df["n"])):
        ax.text(pct + 0.8, i, f"{pct:.1f}%  (n={n_val})", va="center", fontsize=10)
    ax.axvline(overall_rate, color="#555555", linestyle="--", linewidth=1.2,
        label=f"Overall {overall_rate:.1f}%")
    ax.set_xlim(0, 115)
    ax.set_xlabel("Definite trial-intent rate (%)")
    ax.set_title(
        f"Top {top_n} High-Value Audience Segments by Definite Trial Intent\n(min n={min_n} per segment)",
        fontsize=13, fontweight="bold",
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.2)
    ax.legend(fontsize=9, frameon=False)
    fig.text(
        0.01, 0.01,
        "Segments above dashed line are above-average definite trial intent. Prioritize for RTD coffee launch targeting.",
        ha="left", fontsize=9, color="#666666",
    )
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(output_dir / "high_value_segments.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_images(df):
    make_target_distribution(df)
    make_tryrate_by_segment(
        df,
        ["gender", "age_group", "occupation", "income"],
        "Definite Try Rate by Demographic Segment",
        "tryrate_by_demographic.png",
    )
    make_tryrate_by_segment(
        df,
        ["presenter_effect", "dur_online", "most_freq_coffee", "most_freq_rtd_brand"],
        "Definite Try Rate by Behavior / Media Segment",
        "tryrate_by_behavior.png",
    )
    make_likert_by_target(df)
    make_imbalance_summary(df)
    make_minority_profile(df)
    make_cohens_d_chart(df)
    make_high_value_segments(df)

    analysis_df, feature_scores = prepare_feature_data(df)
    distribution_df = make_distribution_table(analysis_df)
    correlation_df = make_correlation_table(analysis_df)

    gender_counts = df["gender"].fillna("ไม่ระบุ").value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=gender_counts.index, y=gender_counts.values, ax=ax, palette="Blues_d")
    ax.set_title("Demographic Profile: เพศ")
    ax.set_xlabel("")
    ax.set_ylabel("จำนวนคน")
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(output_dir / "demographic_gender.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    age_counts = df["age_group"].fillna("ไม่ระบุ").value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=age_counts.index, y=age_counts.values, ax=ax, palette="Greens")
    ax.set_title("Demographic Profile: ช่วงอายุ")
    ax.set_xlabel("")
    ax.set_ylabel("จำนวนคน")
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(output_dir / "demographic_age.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    occupation_counts = df["occupation"].fillna("ไม่ระบุ").value_counts().head(8)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=occupation_counts.values, y=occupation_counts.index, ax=ax, palette="Purples")
    ax.set_title("Demographic Profile: อาชีพ")
    ax.set_xlabel("จำนวนคน")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(output_dir / "demographic_occupation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    top_features = build_feature_summary_table(analysis_df, feature_scores, top_n=10)
    top_features.to_csv(output_dir / "feature_selection_summary.csv", index=False, encoding="utf-8-sig")

    plot_data = top_features.sort_values("f_score", ascending=True).copy()
    colors = [
        positive_driver_color if direction == "positive" else negative_driver_color
        for direction in plot_data["direction"]
    ]

    fig, ax = plt.subplots(figsize=(13, 8))
    ax.barh(plot_data["display_label"], plot_data["f_score"], color=colors, alpha=0.95)

    max_score = plot_data["f_score"].max()
    x_padding = max_score * 0.32
    ax.set_xlim(0, max_score + x_padding)

    for idx, (_, row) in enumerate(plot_data.iterrows()):
        annotation = f"{format_p_value(row['p_value'])} | {row['effect_label']}"
        ax.text(
            row["f_score"] + max_score * 0.02,
            idx,
            annotation,
            va="center",
            ha="left",
            fontsize=10,
            color="#2F2F2F",
        )

    ax.set_title(
        "Top data-driven drivers of trial intent for new RTD coffee",
        loc="left",
        fontsize=18,
        fontweight="bold",
        pad=16,
    )
    ax.text(
        0,
        1.02,
        (
            f"ANOVA feature screening | n = {len(analysis_df)} valid respondents | "
            f"definite try = {(analysis_df[target_column].eq(2)).mean():.1%} | "
            f"maybe = {(analysis_df[target_column].eq(1)).mean():.1%}"
        ),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=11,
        color="#555555",
    )
    ax.set_xlabel("ANOVA F-score (higher = stronger separation across the three target choices)")
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.legend(
        handles=[
            Patch(facecolor=positive_driver_color, label="Positive association with trial intent"),
            Patch(facecolor=negative_driver_color, label="Negative association with trial intent"),
        ],
        loc="lower right",
        frameon=False,
    )
    fig.text(
        0.01,
        0.01,
        (
            "Note: F-score highlights statistical association, not causality. "
            "Numeric effects compare definite triers vs non-triers; categorical effects show definite-try and maybe-rate gaps."
        ),
        ha="left",
        fontsize=9,
        color="#666666",
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(output_dir / "feature_selection.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(distribution_df, annot=True, fmt=".2f", cmap="YlGnBu", ax=ax)
    ax.set_title("Distribution Analysis: การกระจายคำตอบ Likert")
    ax.set_xlabel("คะแนน")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(output_dir / "distribution_analysis.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_df, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap: ความสัมพันธ์กับ Target")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    df = build_clean_data()
    make_images(df)
    print(f"Clean data file: {clean_data_path}")
    print("Output images:")
    print(output_dir / "target_distribution.png")
    print(output_dir / "tryrate_by_demographic.png")
    print(output_dir / "tryrate_by_behavior.png")
    print(output_dir / "likert_by_target.png")
    print(output_dir / "imbalance_summary.png")
    print(output_dir / "minority_profile.png")
    print(output_dir / "cohens_d_features.png")
    print(output_dir / "high_value_segments.png")
    print(output_dir / "demographic_gender.png")
    print(output_dir / "demographic_age.png")
    print(output_dir / "demographic_occupation.png")
    print(output_dir / "feature_selection.png")
    print(output_dir / "distribution_analysis.png")
    print(output_dir / "correlation_heatmap.png")
    print("Feature selection = f_classif")
    print("Scale transformation = StandardScaler on numeric/Likert columns")
    print("Encoding = pd.get_dummies on categorical columns")
