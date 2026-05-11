"""Supervised learning pipeline for the RTD coffee choice classifier.

Problem
-------
Multiclass classification: predict ``target_try_new_rtd_coffee_choice``
(0 = will not try, 1 = might try, 2 = will definitely try) using ONLY the features that
the feature-selection step (``src/feature_engineering/feature_selection_visualization.py``)
flagged as statistically significant (ANOVA p ≤ 0.05, deduplicated by source
variable). This keeps the model parsimonious and makes the coefficients
directly interpretable for the Business Insight dashboard.

Pipeline
--------
1. Load ``CLEAN_CSV`` (uses ``CLUSTERS_CSV`` only when nothing extra is asked).
2. Read the selected features from
   ``outputs/feature_selection_summary.csv`` and use those source variables
   only. If the file is missing, fall back to a curated default list.
3. Stratified train/test split (80/20).
4. Train three models with balanced classes where supported:
     * Logistic Regression  → exposes interpretable coefficients
     * Random Forest        → non-linear baseline + impurity importance
     * Gradient Boosting    → strong non-linear comparator
5. Evaluate via 5-fold stratified CV (Accuracy / macro Precision / macro Recall /
   macro F1 / OVR ROC-AUC) AND on the held-out test set.
6. Persist artefacts:
     * ``models/supervised_logreg.joblib`` (full pipeline)
     * ``models/supervised_best.joblib``   (highest-CV-F1 model)
     * ``outputs/supervised_metrics.json``
     * ``outputs/supervised_coefficients.csv``
     * ``outputs/supervised_coefficients.png``
     * ``outputs/supervised_feature_importance.png``
     * ``outputs/supervised_model_comparison.png``
     * ``outputs/supervised_confusion_matrix.png``
     * ``outputs/supervised_roc_curve.png``
     * ``outputs/supervised_feature_schema.json`` (for the web UI)

Run::

    python -m src.feature_engineering.feature_selection_visualization
    python -m src.supervised.train
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CLEAN_CSV,
    LEGACY_BINARY_TARGET_COLUMN,
    MODELS_DIR,
    OUTPUTS_DIR,
    TARGET_COLUMN,
    ensure_dirs,
    setup_thai_font,
)

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_SPLITS = 5
TOP_N_FEATURES = 5  # data-driven rule: top N source variables by ANOVA F-score
CLASS_LABELS = {
    0: "ไม่ลอง",
    1: "อาจจะลอง",
    2: "ลองแน่นอน",
}
TARGET_OPTIONS = [
    {"value": 0, "key": "no", "label": CLASS_LABELS[0], "short_label": "ไม่ลอง", "color": "#D85A5A"},
    {"value": 1, "key": "maybe", "label": CLASS_LABELS[1], "short_label": "อาจจะ", "color": "#E0A458"},
    {"value": 2, "key": "try", "label": CLASS_LABELS[2], "short_label": "ลอง", "color": "#5BB89A"},
]

FEATURE_SUMMARY_CSV = OUTPUTS_DIR / "feature_selection_summary.csv"

# Fallback in case the user runs train.py without the feature-selection step.
# These are the source variables the feature-selection report currently keeps
# (ANOVA p ≤ 0.05, deduped by source variable, capped at TOP_N_FEATURES).
FALLBACK_NUMERIC = ["coffee_value", "coffee_aroma", "coffee_convenience", "coffee_nutrition"]
FALLBACK_CATEGORICAL = ["most_freq_rtd_brand"]

# Friendly labels reused across the model report and the web UI.
FEATURE_LABELS: dict[str, str] = {
    "coffee_value": "Perceived value",
    "coffee_aroma": "Aroma preference",
    "coffee_convenience": "Convenience importance",
    "coffee_nutrition": "Nutrition importance",
    "coffee_smooth": "Smooth taste preference",
    "coffee_brand_trust": "Brand trust importance",
    "coffee_packaging": "Packaging importance",
    "coffee_fresh_taste": "Fresh taste preference",
    "coffee_caffeine": "Caffeine importance",
    "most_freq_rtd_brand": "Primary RTD coffee brand",
    "dur_online": "Daily online usage",
    "presenter_effect": "Presenter influence",
}


def load_dataset() -> pd.DataFrame:
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(
            f"{CLEAN_CSV} not found. Run "
            "`python -m src.feature_engineering.feature_selection_visualization` first."
        )
    df = pd.read_csv(CLEAN_CSV)
    print(f"Loaded {df.shape[0]} rows x {df.shape[1]} cols from {CLEAN_CSV.name}")
    return df


def load_selected_features(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Read the deduped source variables from the feature-selection report.

    Selection rule (data-driven, no human curation):
        ``Top TOP_N_FEATURES rows by F-score from feature_selection_summary.csv,
        after deduplicating by source variable.``
    """
    if not FEATURE_SUMMARY_CSV.exists():
        print(
            f"NOTE: {FEATURE_SUMMARY_CSV.name} not found, using fallback feature list. "
            "Run `python -m src.feature_engineering.feature_selection_visualization` "
            "to refresh the selection."
        )
        numeric = [c for c in FALLBACK_NUMERIC if c in df.columns]
        categorical = [c for c in FALLBACK_CATEGORICAL if c in df.columns]
        return numeric, categorical

    summary = pd.read_csv(FEATURE_SUMMARY_CSV).sort_values("f_score", ascending=False)
    numeric, categorical = [], []
    seen: set[str] = set()
    for _, row in summary.iterrows():
        src = row["source_var"]
        if src in seen or src not in df.columns:
            continue
        seen.add(src)
        if row["feature_type"] == "numeric":
            numeric.append(src)
        elif row["feature_type"] == "categorical":
            categorical.append(src)
        if len(numeric) + len(categorical) >= TOP_N_FEATURES:
            break
    print(
        f"Selected top {TOP_N_FEATURES} from {FEATURE_SUMMARY_CSV.name}: "
        f"{len(numeric)} numeric + {len(categorical)} categorical"
    )
    return numeric, categorical


def build_preprocessor(numeric_cols: list[str], categorical_cols: list[str]) -> ColumnTransformer:
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # sklearn < 1.2
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", ohe),
    ])
    return ColumnTransformer([
        ("num", numeric_pipe, numeric_cols),
        ("cat", categorical_pipe, categorical_cols),
    ])


def get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    names: list[str] = []
    for name, transformer, cols in preprocessor.transformers_:
        if name == "num":
            names.extend(cols)
        elif name == "cat":
            ohe = transformer.named_steps["onehot"]
            names.extend(ohe.get_feature_names_out(cols).tolist())
    return names


def cross_validate_model(model: Pipeline, X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "accuracy": "accuracy",
        "precision_macro": "precision_macro",
        "recall_macro": "recall_macro",
        "f1_macro": "f1_macro",
        "roc_auc_ovr_macro": "roc_auc_ovr",
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        scores = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    return {
        f"cv_{metric}_mean": float(np.mean(scores[f"test_{metric}"]))
        for metric in scoring
    } | {
        f"cv_{metric}_std": float(np.std(scores[f"test_{metric}"]))
        for metric in scoring
    }


def evaluate_holdout(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = model.predict(X_test)
    proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
    metrics = {
        "test_accuracy": float(accuracy_score(y_test, y_pred)),
        "test_precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
    }
    if proba is not None:
        metrics["test_roc_auc_ovr_macro"] = float(
            roc_auc_score(y_test, proba, multi_class="ovr", average="macro")
        )
    labels = sorted(CLASS_LABELS)
    metrics["confusion_matrix"] = confusion_matrix(y_test, y_pred, labels=labels).tolist()
    metrics["classification_report"] = classification_report(
        y_test,
        y_pred,
        labels=labels,
        target_names=[CLASS_LABELS[i] for i in labels],
        zero_division=0,
        output_dict=True,
    )
    return metrics


def plot_model_comparison(results: dict[str, dict], path: Path) -> None:
    metrics = ["accuracy", "precision_macro", "recall_macro", "f1_macro", "roc_auc_ovr_macro"]
    rows = []
    for model_name, info in results.items():
        for metric in metrics:
            rows.append({
                "model": model_name,
                "metric": metric,
                "score": info["cv"][f"cv_{metric}_mean"],
                "std": info["cv"][f"cv_{metric}_std"],
            })
    cmp_df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.barplot(data=cmp_df, x="metric", y="score", hue="model", ax=ax, palette="Set2")
    ax.set_xticklabels(["Accuracy", "Precision\nmacro", "Recall\nmacro", "F1\nmacro", "ROC-AUC\nOVR"])
    ax.set_ylim(0, 1)
    ax.set_title("Model Comparison — 5-fold Stratified CV (mean)")
    ax.set_ylabel("Score")
    ax.set_xlabel("")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=8, padding=2)
    ax.legend(title="Model", loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_confusion_matrices(results: dict[str, dict], path: Path) -> None:
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]
    for ax, (name, info) in zip(axes, results.items()):
        cm = np.array(info["holdout"]["confusion_matrix"])
        labels = [CLASS_LABELS[i] for i in sorted(CLASS_LABELS)]
        sns.heatmap(
            cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
            xticklabels=labels,
            yticklabels=labels,
        )
        ax.set_title(f"{name}\nMacro F1 = {info['holdout']['test_f1_macro']:.3f}")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
    plt.suptitle("Hold-out Confusion Matrices", fontsize=13)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_roc_curves(results: dict[str, dict], X_test: pd.DataFrame, y_test: pd.Series, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    for name, info in results.items():
        model = info["model"]
        if not hasattr(model, "predict_proba"):
            continue
        proba = model.predict_proba(X_test)
        classes = list(model.named_steps["clf"].classes_)
        if 2 not in classes:
            continue
        class_index = classes.index(2)
        y_one_vs_rest = (y_test == 2).astype(int)
        fpr, tpr, _ = roc_curve(y_one_vs_rest, proba[:, class_index])
        ax.plot(fpr, tpr, lw=2, label=f"{name} · definite try (AUC = {auc(fpr, tpr):.3f})")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — Definite Try vs Rest (Hold-out Test Set)")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def export_logreg_coefficients(model: Pipeline, feature_names: list[str]) -> pd.DataFrame:
    clf: LogisticRegression = model.named_steps["clf"]
    rows = []
    for class_value, class_coefs in zip(clf.classes_, clf.coef_):
        class_value = int(class_value)
        for feature, coef in zip(feature_names, class_coefs):
            rows.append({
                "class": class_value,
                "class_label": CLASS_LABELS.get(class_value, str(class_value)),
                "feature": feature,
                "coefficient": coef,
                "odds_ratio": np.exp(coef),
                "abs_coefficient": abs(coef),
            })
    coef_df = pd.DataFrame(rows).sort_values("abs_coefficient", ascending=False).reset_index(drop=True)

    csv_path = OUTPUTS_DIR / "supervised_coefficients.csv"
    coef_df.drop(columns="abs_coefficient").to_csv(csv_path, index=False, encoding="utf-8-sig")

    plot_df = coef_df[coef_df["class"] == 2].head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, max(5, 0.4 * len(plot_df))))
    colors = ["#1D9E75" if c > 0 else "#D85A30" for c in plot_df["coefficient"]]
    ax.barh(plot_df["feature"], plot_df["coefficient"], color=colors, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_title(
        "Logistic Regression Coefficients — Definite Try Class\n"
        "(green = pushes toward 'ลองแน่นอน', orange = pushes against)"
    )
    ax.set_xlabel("Coefficient (log-odds, on standardised numeric / one-hot categorical)")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "supervised_coefficients.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    return coef_df


def export_tree_importance(model: Pipeline, feature_names: list[str]) -> None:
    clf = model.named_steps["clf"]
    if not hasattr(clf, "feature_importances_"):
        return
    imp = pd.DataFrame({
        "feature": feature_names,
        "importance": clf.feature_importances_,
    }).sort_values("importance", ascending=False).iloc[::-1]

    fig, ax = plt.subplots(figsize=(10, max(5, 0.4 * len(imp))))
    ax.barh(imp["feature"], imp["importance"], color="#7F77DD", alpha=0.85)
    ax.set_title("Random Forest — Feature Importances")
    ax.set_xlabel("Mean decrease in impurity")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "supervised_feature_importance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_feature_schema(
    df: pd.DataFrame,
    numeric_cols: list[str],
    categorical_cols: list[str],
) -> dict:
    """Describe each input feature so the web UI can build controls automatically."""
    schema: dict = {"numeric": [], "categorical": []}
    for col in numeric_cols:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        schema["numeric"].append({
            "name": col,
            "label": FEATURE_LABELS.get(col, col.replace("_", " ").title()),
            "min": float(series.min()) if len(series) else 1.0,
            "max": float(series.max()) if len(series) else 5.0,
            "median": float(series.median()) if len(series) else 3.0,
            "is_likert": bool(series.dropna().between(1, 5).all() and series.nunique() <= 5),
        })
    for col in categorical_cols:
        choices = (
            df[col].dropna().astype(str).str.strip()
            .replace("", np.nan).dropna().unique().tolist()
        )
        choices = sorted(choices)
        mode = df[col].mode(dropna=True)
        default = str(mode.iloc[0]) if len(mode) else (choices[0] if choices else "")
        schema["categorical"].append({
            "name": col,
            "label": FEATURE_LABELS.get(col, col.replace("_", " ").title()),
            "choices": choices,
            "default": default,
        })
    return schema


def main() -> None:
    ensure_dirs()
    setup_thai_font()

    df = load_dataset()

    if TARGET_COLUMN not in df.columns:
        raise KeyError(f"Target column '{TARGET_COLUMN}' missing from dataset.")

    labelled = df.dropna(subset=[TARGET_COLUMN]).copy()
    labelled[TARGET_COLUMN] = labelled[TARGET_COLUMN].astype(int)
    print(f"Labelled rows: {len(labelled)} (dropped {len(df) - len(labelled)} unlabelled)")
    print("Class distribution:")
    for label, count in labelled[TARGET_COLUMN].value_counts().sort_index().items():
        print(f"  {label}: {count} ({count / len(labelled):.1%})")

    numeric_cols, categorical_cols = load_selected_features(labelled)
    print(f"\nFeatures used by the model:")
    for col in numeric_cols:
        print(f"  numeric     : {col}  ({FEATURE_LABELS.get(col, col)})")
    for col in categorical_cols:
        print(f"  categorical : {col}  ({FEATURE_LABELS.get(col, col)})")

    feature_cols = numeric_cols + categorical_cols
    if not feature_cols:
        raise RuntimeError("No features selected — check feature_selection_summary.csv.")

    X = labelled[feature_cols]
    y = labelled[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    print(f"\nTrain/Test split: {len(X_train)}/{len(X_test)} (stratified, test_size={TEST_SIZE})")

    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    model_specs = {
        "LogisticRegression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            solver="lbfgs",
            multi_class="auto",
            random_state=RANDOM_STATE,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=250,
            learning_rate=0.05,
            max_depth=3,
            random_state=RANDOM_STATE,
        ),
    }

    results: dict[str, dict] = {}
    for name, estimator in model_specs.items():
        print(f"\n--- {name} ---")
        pipe = Pipeline([("preprocess", preprocessor), ("clf", estimator)])
        cv_metrics = cross_validate_model(pipe, X_train, y_train)
        for metric in ("accuracy", "precision_macro", "recall_macro", "f1_macro", "roc_auc_ovr_macro"):
            mean = cv_metrics[f"cv_{metric}_mean"]
            std = cv_metrics[f"cv_{metric}_std"]
            print(f"  CV {metric:>9}: {mean:.4f} (+/- {std:.4f})")
        pipe.fit(X_train, y_train)
        holdout = evaluate_holdout(pipe, X_test, y_test)
        for k, v in holdout.items():
            if isinstance(v, float):
                print(f"  {k:>17}: {v:.4f}")
        results[name] = {"model": pipe, "cv": cv_metrics, "holdout": holdout}

    # Choose the best model by macro F1 (handles class imbalance better than accuracy).
    best_name = max(results, key=lambda n: results[n]["cv"]["cv_f1_macro_mean"])
    print(f"\nBest model by CV macro F1: {best_name} "
          f"(F1 = {results[best_name]['cv']['cv_f1_macro_mean']:.4f})")

    plot_model_comparison(results, OUTPUTS_DIR / "supervised_model_comparison.png")
    plot_confusion_matrices(results, OUTPUTS_DIR / "supervised_confusion_matrix.png")
    plot_roc_curves(results, X_test, y_test, OUTPUTS_DIR / "supervised_roc_curve.png")

    logreg_pipe: Pipeline = results["LogisticRegression"]["model"]
    feature_names = get_feature_names(logreg_pipe.named_steps["preprocess"])
    coef_df = export_logreg_coefficients(logreg_pipe, feature_names)
    print("\nLogistic-regression coefficients (sorted by |coef|):")
    print(coef_df.head(15).to_string(index=False))

    rf_pipe: Pipeline = results["RandomForest"]["model"]
    rf_feature_names = get_feature_names(rf_pipe.named_steps["preprocess"])
    export_tree_importance(rf_pipe, rf_feature_names)

    joblib.dump(logreg_pipe, MODELS_DIR / "supervised_logreg.joblib")
    joblib.dump(results[best_name]["model"], MODELS_DIR / "supervised_best.joblib")

    schema = build_feature_schema(labelled, numeric_cols, categorical_cols)
    schema["target"] = TARGET_COLUMN
    schema["legacy_binary_target"] = LEGACY_BINARY_TARGET_COLUMN
    schema["target_options"] = TARGET_OPTIONS
    schema["best_model"] = best_name
    schema["model_files"] = {
        "logreg": "supervised_logreg.joblib",
        "best": "supervised_best.joblib",
    }
    schema_path = OUTPUTS_DIR / "supervised_feature_schema.json"
    schema_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")

    metrics_payload = {
        "target": TARGET_COLUMN,
        "legacy_binary_target": LEGACY_BINARY_TARGET_COLUMN,
        "target_options": TARGET_OPTIONS,
        "n_labelled": int(len(labelled)),
        "class_distribution": labelled[TARGET_COLUMN].value_counts().sort_index().to_dict(),
        "feature_counts": {"numeric": len(numeric_cols), "categorical": len(categorical_cols)},
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "split": {"test_size": TEST_SIZE, "random_state": RANDOM_STATE, "stratified": True},
        "cv": {"n_splits": CV_SPLITS, "stratified": True, "random_state": RANDOM_STATE},
        "models": {
            name: {"cv": info["cv"], "holdout": info["holdout"]}
            for name, info in results.items()
        },
        "best_model_by_cv_f1_macro": best_name,
    }
    metrics_path = OUTPUTS_DIR / "supervised_metrics.json"
    metrics_path.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nSaved metrics:        {metrics_path}")
    print(f"Saved coefficients:   {OUTPUTS_DIR / 'supervised_coefficients.csv'}")
    print(f"Saved feature schema: {schema_path}")
    print(f"Saved model (LogReg): {MODELS_DIR / 'supervised_logreg.joblib'}")
    print(f"Saved model (best):   {MODELS_DIR / 'supervised_best.joblib'}")


if __name__ == "__main__":
    main()
