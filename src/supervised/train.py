from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, auc, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score, roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    CLEAN_CSV, LEGACY_BINARY_TARGET_COLUMN, OUTPUTS_DIR,
    TARGET_COLUMN, ensure_dirs, setup_thai_font,
)

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_SPLITS = 5
TOP_N_FEATURES = 5
CLASS_LABELS = {0: "ไม่ลอง", 1: "อาจจะลอง", 2: "ลองแน่นอน"}
TARGET_OPTIONS = [
    {"value": 0, "key": "no", "label": CLASS_LABELS[0], "short_label": "ไม่ลอง", "color": "#D85A5A"},
    {"value": 1, "key": "maybe", "label": CLASS_LABELS[1], "short_label": "อาจจะ", "color": "#E0A458"},
    {"value": 2, "key": "try", "label": CLASS_LABELS[2], "short_label": "ลอง", "color": "#5BB89A"},
]

FEATURE_SUMMARY_CSV = OUTPUTS_DIR / "feature_selection_summary.csv"

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
    "most_freq_rtd_tea_brand": "Primary RTD tea brand",
    "dur_online": "Daily online usage",
    "presenter_effect": "Presenter influence",
}


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_CSV)
    print(f"Loaded {df.shape[0]} rows x {df.shape[1]} cols from {CLEAN_CSV.name}")
    return df


def load_selected_features(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    summary = pd.read_csv(FEATURE_SUMMARY_CSV).sort_values("f_score", ascending=False)
    summary = summary[summary["source_var"].isin(df.columns)].drop_duplicates("source_var")
    selected = summary.head(TOP_N_FEATURES)
    numeric = selected.loc[selected["feature_type"] == "numeric", "source_var"].tolist()
    categorical = selected.loc[selected["feature_type"] == "categorical", "source_var"].tolist()
    print(f"Selected top {TOP_N_FEATURES} from {FEATURE_SUMMARY_CSV.name}: "
          f"{len(numeric)} numeric + {len(categorical)} categorical")
    return numeric, categorical


def build_preprocessor(numeric_cols: list[str], categorical_cols: list[str]) -> ColumnTransformer:
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
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
        f"cv_{metric}_mean": float(np.mean(scores[f"test_{metric}"])) for metric in scoring
    } | {
        f"cv_{metric}_std": float(np.std(scores[f"test_{metric}"])) for metric in scoring
    }


def evaluate_holdout(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = model.predict(X_test)
    proba = model.predict_proba(X_test)
    metrics = {
        "test_accuracy": float(accuracy_score(y_test, y_pred)),
        "test_precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "test_f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
    }
    metrics["test_roc_auc_ovr_macro"] = float(
        roc_auc_score(y_test, proba, multi_class="ovr", average="macro")
    )
    labels = sorted(CLASS_LABELS)
    metrics["confusion_matrix"] = confusion_matrix(y_test, y_pred, labels=labels).tolist()
    metrics["classification_report"] = classification_report(
        y_test, y_pred, labels=labels,
        target_names=[CLASS_LABELS[i] for i in labels],
        zero_division=0, output_dict=True,
    )
    return metrics


def plot_model_comparison(results: dict[str, dict], path: Path):
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
    if len(results) == 1:
        only_model = next(iter(results))
        ax.set_title(f"{only_model} — 5-fold Stratified CV (mean)")
    else:
        ax.set_title("Model Comparison — 5-fold Stratified CV (mean)")
    ax.set_ylabel("Score")
    ax.set_xlabel("")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=8, padding=2)
    if len(results) > 1:
        ax.legend(title="Model", loc="lower right")
    elif ax.legend_ is not None:
        ax.legend_.remove()
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_per_class_performance(results: dict[str, dict], path: Path):
    """Plot precision, recall, F1 for each class separately (hold-out test set)"""
    rows = []
    for model_name, info in results.items():
        report = info["holdout"]["classification_report"]
        for class_value in sorted(CLASS_LABELS.keys()):
            class_label = CLASS_LABELS[class_value]
            if class_label in report:
                class_metrics = report[class_label]
                rows.append({
                    "model": model_name,
                    "class": class_label,
                    "class_value": class_value,
                    "precision": class_metrics["precision"],
                    "recall": class_metrics["recall"],
                    "f1-score": class_metrics["f1-score"],
                    "support": class_metrics["support"],
                })

    per_class_df = pd.DataFrame(rows)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics_to_plot = ["precision", "recall", "f1-score"]
    metric_labels = ["Precision", "Recall", "F1-Score"]

    for ax, metric, label in zip(axes, metrics_to_plot, metric_labels):
        plot_data = per_class_df.pivot(index="class", columns="model", values=metric)
        colors = [TARGET_OPTIONS[i]["color"] for i in range(len(CLASS_LABELS))]
        plot_data.plot(kind="bar", ax=ax, color=colors, legend=False, width=0.7)
        ax.set_title(f"{label} by Class", fontsize=12, fontweight="bold")
        ax.set_ylabel(label)
        ax.set_xlabel("")
        ax.set_ylim(0, 1)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.grid(axis="y", alpha=0.3)

        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", fontsize=9, padding=2)

    plt.suptitle("Per-Class Performance (Hold-out Test Set)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_confusion_matrices(results: dict[str, dict], path: Path):
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]
    for ax, (name, info) in zip(axes, results.items()):
        cm = np.array(info["holdout"]["confusion_matrix"])
        labels = [CLASS_LABELS[i] for i in sorted(CLASS_LABELS)]
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                    xticklabels=labels, yticklabels=labels)
        ax.set_title(f"{name}\nMacro F1 = {info['holdout']['test_f1_macro']:.3f}")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
    plt.suptitle("Hold-out Confusion Matrices", fontsize=13)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_roc_curves(results: dict[str, dict], X_test: pd.DataFrame, y_test: pd.Series, path: Path):
    fig, ax = plt.subplots(figsize=(7, 6))
    for name, info in results.items():
        model = info["model"]
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
    coef_df.drop(columns="abs_coefficient").to_csv(
        OUTPUTS_DIR / "supervised_coefficients.csv", index=False, encoding="utf-8-sig"
    )

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


def build_feature_schema(df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]) -> dict:
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
        choices = sorted(
            df[col].dropna().astype(str).str.strip().replace("", np.nan).dropna().unique().tolist()
        )
        mode = df[col].mode(dropna=True)
        default = str(mode.iloc[0]) if len(mode) else (choices[0] if choices else "")
        schema["categorical"].append({
            "name": col,
            "label": FEATURE_LABELS.get(col, col.replace("_", " ").title()),
            "choices": choices,
            "default": default,
        })
    return schema


def main():
    ensure_dirs()
    setup_thai_font()

    df = load_dataset()
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
    X = labelled[feature_cols]
    y = labelled[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    print(f"\nTrain/Test split: {len(X_train)}/{len(X_test)} (stratified, test_size={TEST_SIZE})")

    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    model_specs = {
        "LogisticRegression": LogisticRegression(
            max_iter=2000, class_weight="balanced", solver="lbfgs",
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

    best_name = max(results, key=lambda n: results[n]["cv"]["cv_f1_macro_mean"])
    print(f"\nBest model by CV macro F1: {best_name} "
          f"(F1 = {results[best_name]['cv']['cv_f1_macro_mean']:.4f})")

    plot_model_comparison(results, OUTPUTS_DIR / "supervised_model_comparison.png")
    plot_per_class_performance(results, OUTPUTS_DIR / "supervised_per_class_performance.png")
    plot_confusion_matrices(results, OUTPUTS_DIR / "supervised_confusion_matrix.png")
    plot_roc_curves(results, X_test, y_test, OUTPUTS_DIR / "supervised_roc_curve.png")

    logreg_pipe: Pipeline = results["LogisticRegression"]["model"]
    feature_names = get_feature_names(logreg_pipe.named_steps["preprocess"])
    coef_df = export_logreg_coefficients(logreg_pipe, feature_names)
    print("\nLogistic-regression coefficients (sorted by |coef|):")
    print(coef_df.head(15).to_string(index=False))

    schema = build_feature_schema(labelled, numeric_cols, categorical_cols)
    schema["target"] = TARGET_COLUMN
    schema["legacy_binary_target"] = LEGACY_BINARY_TARGET_COLUMN
    schema["target_options"] = TARGET_OPTIONS
    schema["best_model"] = "LogisticRegression"
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
        "models": {name: {"cv": info["cv"], "holdout": info["holdout"]} for name, info in results.items()},
        "best_model_by_cv_f1_macro": "LogisticRegression",
    }
    metrics_path = OUTPUTS_DIR / "supervised_metrics.json"
    metrics_path.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nSaved metrics:        {metrics_path}")
    print(f"Saved coefficients:   {OUTPUTS_DIR / 'supervised_coefficients.csv'}")
    print(f"Saved feature schema: {schema_path}")
if __name__ == "__main__":
    main()
