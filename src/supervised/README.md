# Supervised Learning

Trains a three-class classifier that predicts
`target_try_new_rtd_coffee_choice`: `0 = ไม่ลอง`, `1 = อาจจะลอง`, and
`2 = ลองแน่นอน`. The legacy binary column `target_try_new_rtd_coffee` is still
written for reference, but the model and dashboard use the three-choice target.

## Features used

| # | Source variable      | Type        | Label                    |
|---|----------------------|-------------|--------------------------|
| 1 | coffee_value         | numeric     | Perceived value          |
| 2 | coffee_aroma         | numeric     | Aroma preference         |
| 3 | coffee_convenience   | numeric     | Convenience importance   |
| 4 | coffee_nutrition     | numeric     | Nutrition importance     |
| 5 | coffee_smooth        | numeric     | Smooth taste preference  |
| 6 | coffee_brand_trust   | numeric     | Brand trust importance   |
| 7 | coffee_packaging     | numeric     | Packaging importance     |
| 8 | most_freq_rtd_brand  | categorical | Primary RTD coffee brand |
| 9 | dur_online           | categorical | Daily online usage       |
|10 | presenter_effect     | categorical | Presenter influence      |

## Inputs

- `data/processed/media_behavior_cleaned.csv` — produced by
  `src/feature_engineering/feature_selection_visualization.py`.
- `outputs/feature_selection_summary.csv` — the selected-features file.

The target column is derived in `feature_selection.derive_target` from
`will_try_new_rtd_coffee`. Rows where the target is NaN are dropped; the latest
static dashboard data has 118 labelled respondents: 25 `ไม่ลอง`, 76
`อาจจะลอง`, and 17 `ลองแน่นอน`.

## What the pipeline does

1. **Feature selection** — reads the ANOVA-filtered source variables from
   `feature_selection_summary.csv` (7 Likert numeric + 3 categorical).
2. **Preprocessing** — median-impute + `StandardScaler` for numeric, mode-impute
   + `OneHotEncoder(handle_unknown='ignore')` for categorical, all wrapped in a
   `ColumnTransformer` so the same fitted transforms are reused at inference.
3. **Imbalance handling** — `class_weight='balanced'` on the linear and tree
   models (no SMOTE; sample size is small, so re-weighting is safer).
4. **Train/Test split** — stratified 80/20 hold-out (`random_state=42`).
5. **Models** — three classifiers compared on the same pipeline:
   - `LogisticRegression` (lbfgs, balanced) — interpretable class coefficients.
   - `RandomForest` (400 trees, balanced) — non-linear baseline + impurity importance.
   - `GradientBoosting` (250 trees, lr=0.05, depth 3) — non-linear comparator.
6. **Evaluation** — 5-fold stratified CV on the train set (Accuracy, macro
   Precision, macro Recall, macro F1, OVR ROC-AUC) plus the held-out test set
   with full classification report and confusion matrix.

## Results (last run)

| Model              | CV F1 (mean ± std) | CV ROC-AUC | Test F1 | Test ROC-AUC |
|--------------------|--------------------|------------|---------|--------------|
| LogisticRegression | 0.843 ± 0.031      | 0.845      | 0.895   | 0.863        |
| **RandomForest**   | **0.921 ± 0.043**  | **0.849**  | **0.927** | **0.926**  |
| GradientBoosting   | 0.866 ± 0.071      | 0.792      | 0.878   | 0.695        |

**Selected model: `RandomForest`** — highest CV F1 (0.921) and strong
generalisation (test F1 = 0.927, test ROC-AUC = 0.926). The
`LogisticRegression` pipeline is also persisted because it is the source of
the business-facing coefficients deliverable.

## Outputs

Artefacts written by `train.py`:

- `models/supervised_best.joblib` — best pipeline (preprocessor + classifier).
- `models/supervised_logreg.joblib` — interpretable logistic-regression pipeline.
- `outputs/supervised_metrics.json` — full CV + hold-out metrics, feature
  lists, and class distribution.
- `outputs/supervised_coefficients.csv` — every logistic-regression coefficient
  with its odds ratio, sorted by absolute weight.
- `outputs/supervised_coefficients.png` — coefficient bar chart.
- `outputs/supervised_feature_importance.png` — Random Forest impurity importance.
- `outputs/supervised_model_comparison.png` — CV metric comparison across models.
- `outputs/supervised_confusion_matrix.png` — hold-out confusion matrices.
- `outputs/supervised_roc_curve.png` — hold-out ROC curves.
- `outputs/supervised_feature_schema.json` — feature schema for the web UI.

## How to read the coefficients

`supervised_coefficients.csv` columns:

- `class` / `class_label` — which target choice the coefficient belongs to.
- `feature` — the encoded feature name (one-hot columns look like
  `most_freq_rtd_brand_Arabic`).
- `coefficient` — log-odds change in the predicted probability when the
  (standardised) feature increases by one unit.
- `odds_ratio` — `exp(coefficient)`. For a class row, > 1 increases the odds of
  that class relative to the others; < 1 decreases them.

## Run

```bash
python -m src.feature_engineering.feature_selection_visualization   # build CLEAN_CSV + select features
python -m src.supervised.train                                      # train + evaluate
streamlit run src/web/app.py                                        # interactive predictor
```
