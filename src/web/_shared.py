"""Shared helpers used by every Streamlit page in this project."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from src.config import (
    CLEAN_CSV,
    CLUSTERS_CSV,
    MODELS_DIR,
    OUTPUTS_DIR,
    TARGET_COLUMN,
)

SCHEMA_PATH = OUTPUTS_DIR / "supervised_feature_schema.json"
METRICS_PATH = OUTPUTS_DIR / "supervised_metrics.json"
COEF_PATH = OUTPUTS_DIR / "supervised_coefficients.csv"


def page_header(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


@st.cache_data(show_spinner=False)
def load_clean_df() -> pd.DataFrame:
    if CLEAN_CSV.exists():
        return pd.read_csv(CLEAN_CSV)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_clusters_df() -> pd.DataFrame:
    if CLUSTERS_CSV.exists():
        return pd.read_csv(CLUSTERS_CSV)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_schema() -> dict:
    if not SCHEMA_PATH.exists():
        return {}
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_metrics() -> dict:
    if not METRICS_PATH.exists():
        return {}
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_coefficients() -> pd.DataFrame:
    if not COEF_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(COEF_PATH)


@st.cache_resource(show_spinner=False)
def load_model(filename: str):
    path = MODELS_DIR / filename
    if not path.exists():
        return None
    return joblib.load(path)


def dataset_overview() -> dict:
    df = load_clean_df()
    clusters = load_clusters_df()
    if df.empty:
        return {
            "n_total": 0,
            "n_labelled": 0,
            "no_rate": 0.0,
            "maybe_rate": 0.0,
            "try_rate": 0.0,
            "interest_rate": 0.0,
            "n_clusters": 0,
        }
    labelled = df[TARGET_COLUMN].dropna()
    labelled_int = labelled.astype(int) if len(labelled) else labelled
    no_rate = float((labelled_int == 0).mean()) if len(labelled_int) else 0.0
    maybe_rate = float((labelled_int == 1).mean()) if len(labelled_int) else 0.0
    try_rate = float((labelled_int == 2).mean()) if len(labelled_int) else 0.0
    n_clusters = (
        int(clusters["customer_persona_cluster"].nunique())
        if "customer_persona_cluster" in clusters.columns
        else 0
    )
    return {
        "n_total": int(len(df)),
        "n_labelled": int(len(labelled)),
        "no_rate": no_rate,
        "maybe_rate": maybe_rate,
        "try_rate": try_rate,
        "interest_rate": maybe_rate + try_rate,
        "n_clusters": n_clusters,
    }


def show_image_grid(filenames: list[str], cols: int = 2) -> None:
    available = [OUTPUTS_DIR / name for name in filenames if (OUTPUTS_DIR / name).exists()]
    if not available:
        st.info("No charts available yet — run the analysis pipelines first.")
        return
    columns = st.columns(cols)
    for idx, path in enumerate(available):
        columns[idx % cols].image(str(path), caption=path.name, use_container_width=True)
