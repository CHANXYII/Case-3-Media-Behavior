# Web App

This folder is the final stage of the pipeline: a small web app that lets a
non-technical stakeholder explore the cluster personas and (once supervised
training is complete) score a hypothetical respondent against the trial-intent
model.

## Recommended stack

- **Backend / app**: Streamlit (fastest path) or FastAPI + a static frontend.
- **Data sources**:
  - `data/processed/media_behavior_with_clusters.csv` for persona / segment exploration.
  - `outputs/*.png` to embed the existing analysis charts.
  - `models/<saved_model>.joblib` produced by `src/supervised/train.py` for live prediction.

## Suggested page layout

1. **Overview** — project goal, dataset size, target definition.
2. **Personas** — show the K-Means clusters with `outputs/persona_radar.png`,
   `outputs/persona_heatmap.png`, `outputs/persona_cluster_size.png`.
3. **Trial-intent drivers** — embed `outputs/cohens_d_features.png`,
   `outputs/likert_by_target.png`, `outputs/high_value_segments.png`.
4. **Predict** — form that collects the same features the supervised model was
   trained on, calls `src.supervised.predict.predict_one`, returns the
   probability and the closest persona.

## Run (once implemented)

```bash
pip install streamlit
streamlit run src/web/app.py
```

Or with FastAPI:

```bash
pip install fastapi uvicorn
uvicorn src.web.app:app --reload
```

## Files to create next

- `app.py` — main entry point.
- `components/` — small helpers for charts, tables, prediction form.
- `static/` — any custom CSS/JS or copies of the Thai font for the browser.
