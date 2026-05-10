# Supervised Learning

This folder is the next stage of the pipeline: train a classifier that predicts
the target variable `target_try_new_rtd_coffee` (whether a respondent is willing
to try a new RTD coffee product) from the cleaned media-behavior features.

## Inputs

- `data/processed/media_behavior_cleaned.csv` — produced by `src/data_cleaning/data_cleaning.py`.
- `data/processed/media_behavior_with_clusters.csv` — optional, produced by `src/unsupervised/unsupervised_learning.py`. Use the `kmeans_cluster` column as an extra feature.

The supporting feature analysis (`src/feature_engineering/feature_selection_visualization.py`) already produces target-aware diagnostics (target distribution, class imbalance, Cohen's d, high-value segments) that should guide model design.

## Suggested next steps for the next dev

1. Implement `train.py`:
   - Load `CLEAN_CSV` from `src.config`.
   - Build the feature matrix using the same encoding rules as `feature_selection_visualization.prepare_feature_data` (numeric + low-cardinality one-hot).
   - Address class imbalance (see `outputs/imbalance_summary.png`) — try `class_weight="balanced"` or SMOTE.
   - Train a baseline (LogisticRegression) and a stronger model (GradientBoosting / XGBoost / LightGBM).
   - Save the fitted model to `models/` (joblib) and metrics to `outputs/supervised_metrics.json`.

2. Implement `evaluate.py`:
   - Stratified k-fold cross-validation, ROC-AUC, PR-AUC, confusion matrix.
   - SHAP / permutation importance plots into `outputs/`.

3. Implement `predict.py`:
   - Loads the saved model and scores any new respondent dataframe.
   - Used by the web app in `src/web/`.

## Run (once implemented)

```bash
python -m src.supervised.train
python -m src.supervised.evaluate
```
