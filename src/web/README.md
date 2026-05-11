# Web App

Multi-page Streamlit dashboard for the Case 3 Media Behavior project. Each
page maps to a section required by the project brief.

```
src/web/
    app.py                        # Home page (entry point for streamlit run)
    _shared.py                    # cached loaders + page header helper
    pages/
        1_Unsupervised_Learning.py
        2_Supervised_Learning.py  # interactive trial-intent predictor
        3_Business_Insight.py
```

Streamlit auto-discovers files under `pages/` and renders them as separate
sidebar entries.

## What you can do on each page

- **Home (`app.py`)** — project summary and dataset metrics.
- **Unsupervised Learning** — persona radar / heatmap / cluster size chart,
  K-Means vs DBSCAN vs Isolation Forest comparison, and the cluster
  assignments table. Indicators on this page are the *unsupervised* ones
  (cluster count, anomaly rate).
- **Supervised Learning** — *the page the team asked for*:
  - Slider/dropdown form for the 10 features the feature-selection step
    flagged as significant.
  - Click **Predict** to get probabilities for `ไม่ลอง`, `อาจจะลอง`, and
    `ลองแน่นอน`.
  - Pick which model scores the respondent: the best-by-CV-macro-F1 model or
    the LogisticRegression model. With
    LogReg you also see a per-feature contribution bar chart so you can
    explain what pushed the `ลองแน่นอน` probability.
  - Tabs for cross-validated model comparison, raw coefficient table, and
    diagnostic charts.
- **Business Insight** — top positive/negative drivers from the LogReg
  coefficients, high-value segment charts, and a recommended marketing
  playbook.

## Run

From the project root:

```bash
pip install -r requirements.txt
python -m src.feature_engineering.feature_selection_visualization
python -m src.unsupervised.unsupervised_learning
python -m src.supervised.train
streamlit run src/web/app.py
```

The first three commands produce the artefacts the dashboard reads from
`outputs/` and `models/`. The dashboard refuses to render specific pages if
those artefacts are missing and tells you which command to run.
