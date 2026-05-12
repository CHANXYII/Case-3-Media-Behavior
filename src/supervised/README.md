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
static dashboard data has 118 labelled respondents:ง`, 76
`อาจจะลอง`, and 17 `ลองแน่นอน`.

## What the pipeline does

1. **Feature selection** — reads the ANOVA-filtered source variables from
   `feature_selection_summary.csv` (7 Likert numeric + 3 categorical).
2. **Preprocessing** — median-impute + `StandardScaler` for numeric, mode-impute
   + `OneHotEncoder(handle_unknown='ignore')` for categorical, all wrapped in a
   `ColumnTransformer` so the same fitted transforms are reused at inference.
3. **Imbalance handling** — `class_weight='balanced'` on LogisticRegression
   (no SMOTE; sample size is small, so re-weigest set
   with full classification report and confusion matrix.

## Results (last run)

| Model              | CV F1 (mean ± std) | CV ROC-AUC | Test F1 | Test ROC-AUC |
|--------------------|--------------------|------------|---------|--------------|
| **LogisticRegreression`** — strong CV F1 (0.843) and excellent
generalisation (test F1 = 0.895, test ROC-AUC = 0.863). Interpretable
coefficients enable business communication and client-side web prediction.
Used for production export and coefficient-based interpretation.

## Outputs

Artefacts written by `train.py`:

- `outputs/supervised_metrics.json` — full CV + hold-out metrics, feature
  lists, and class distribution.
- `outputs/supervised_coefficients.csv` — every logistic-regression coefficient
  with its odds ratio, sorted by absolute weight.
- `outputs/supervised_coefficients.png` — coefficient bar chart.
- `outputs/supervised_model_comparison.png` — cross-validated metric summary for the exported model.
- `outputs/supervised_confusion_matrix.png` — hold-out confusion matris.
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
  that class relative  others; < 1 decreases them.

## Run

```bash
python -m src.feature_engineering.feature_selection_visualization   # build CLEAN_CSV + select features
python -m src.supervised.train                                      # train + evaluate
cd src/web && npm run dev                                          # interactive predictor
```
