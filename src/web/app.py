"""Web app stub.

Placeholder for the next development stage. Currently this is a tiny
Streamlit app that loads the clustered dataset and shows a couple of the
existing persona charts so the next dev has a working entry point.

Run:
    pip install streamlit
    streamlit run src/web/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLUSTERS_CSV, OUTPUTS_DIR


def main() -> None:
    try:
        import streamlit as st
    except ImportError:
        print(
            "streamlit is not installed. Install it with `pip install streamlit` "
            "and run `streamlit run src/web/app.py`."
        )
        return

    import pandas as pd

    st.set_page_config(page_title="Case 3 — Media Behavior", layout="wide")
    st.title("Case 3 — Media Behavior Personas")
    st.caption(
        "Stub web app. Extend this with prediction, persona drilldown, and "
        "Songkran-period media analysis."
    )

    if CLUSTERS_CSV.exists():
        df = pd.read_csv(CLUSTERS_CSV)
        st.subheader(f"Clustered dataset — {len(df):,} rows")
        if "kmeans_cluster" in df.columns:
            st.bar_chart(df["kmeans_cluster"].value_counts().sort_index())
        st.dataframe(df.head(20))
    else:
        st.warning(
            f"Clustered dataset not found at {CLUSTERS_CSV}. "
            "Run `python -m src.unsupervised.unsupervised_learning` first."
        )

    chart_files = [
        "persona_radar.png",
        "persona_heatmap.png",
        "persona_cluster_size.png",
        "customer_clusters_pca.png",
    ]
    available = [OUTPUTS_DIR / name for name in chart_files if (OUTPUTS_DIR / name).exists()]
    if available:
        st.subheader("Persona charts")
        cols = st.columns(2)
        for idx, path in enumerate(available):
            cols[idx % 2].image(str(path), caption=path.name, use_column_width=True)


if __name__ == "__main__":
    main()
