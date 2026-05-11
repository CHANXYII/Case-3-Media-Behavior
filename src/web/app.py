from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.config import OUTPUTS_DIR, RAW_CSV, TARGET_COLUMN
from src.web._shared import (
    load_clean_df, load_clusters_df, load_coefficients,
    load_metrics, load_model, load_schema,
)

CLASS_LABELS = {0: "ไม่ลอง", 1: "อาจจะลอง", 2: "ลองแน่นอน"}
CLASS_COLORS = {0: "#f43f5e", 1: "#f59e0b", 2: "#34d399"}

st.set_page_config(
    page_title="AI-Driven Marketing Pipeline",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root {
    --bg-0: #0b1020; --bg-1: #111a2e;
    --line: rgba(255,255,255,0.08);
    --muted: #94a3b8; --text: #e2e8f0;
    --accent-1: #22d3ee; --accent-2: #a78bfa; --accent-3: #34d399;
    --accent-4: #f472b6; --accent-5: #f59e0b; --accent-6: #f43f5e;
}
.block-container { padding-top: 1.2rem !important; max-width: 1200px; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.main { background: radial-gradient(1200px 600px at 20% -10%, rgba(34,211,238,0.18), transparent 60%),
                   radial-gradient(900px 500px at 90% 0%, rgba(167,139,250,0.18), transparent 60%),
                   linear-gradient(180deg, #0b1020 0%, #0a0f1f 100%); }
@keyframes fadeUp { from { opacity: 0; transform: translateY(28px); } to { opacity: 1; transform: translateY(0); } }
@keyframes glow { 0%,100% { box-shadow: 0 0 0 rgba(34,211,238,0.0); } 50% { box-shadow: 0 0 24px rgba(34,211,238,0.35); } }
@keyframes arrowFlow { 0% { transform: translateY(-6px); opacity: 0.2; } 50% { transform: translateY(0px); opacity: 1.0; } 100% { transform: translateY(8px); opacity: 0.2; } }
@keyframes barGrow { from { width: 0%; } }
@keyframes shine { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
.hero { text-align: center; padding: 32px 12px 8px; animation: fadeUp .8s ease-out both; }
.hero h1 { font-size: 44px; font-weight: 800; margin: 0;
    background: linear-gradient(90deg, #22d3ee, #a78bfa, #f472b6); background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shine 6s linear infinite; }
.hero p { color: var(--muted); margin: 8px 0 0; font-size: 16px; letter-spacing: 0.04em; }
.pipeline-tag { display: inline-block; padding: 4px 12px; border-radius: 999px;
    background: rgba(34,211,238,0.12); color: #67e8f9; border: 1px solid rgba(34,211,238,0.35);
    font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 12px; }
.stage-card { background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border: 1px solid var(--line); border-radius: 18px; padding: 22px 26px 18px; margin: 0 0 8px 0;
    animation: fadeUp .8s ease-out both; position: relative; overflow: hidden; }
.stage-card::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 4px;
    background: var(--stage-color, #22d3ee); border-radius: 4px 0 0 4px; }
.stage-num { display: inline-flex; align-items: center; justify-content: center;
    width: 36px; height: 36px; border-radius: 50%; background: var(--stage-color, #22d3ee);
    color: #0b1020; font-weight: 800; margin-right: 12px; box-shadow: 0 0 24px var(--stage-color, #22d3ee); }
.stage-title { color: var(--text); font-size: 22px; font-weight: 700; display: inline-block; vertical-align: middle; }
.stage-sub { color: var(--muted); font-size: 13px; letter-spacing: 0.06em; margin-top: 6px; text-transform: uppercase; }
.stat-row { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }
.stat { flex: 1 1 130px; background: rgba(255,255,255,0.03); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }
.stat-label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; }
.stat-value { color: var(--text); font-size: 24px; font-weight: 700; margin-top: 4px; }
.flow-arrow { text-align: center; color: rgba(255,255,255,0.45); font-size: 22px; line-height: 1; padding: 6px 0; animation: arrowFlow 2.4s ease-in-out infinite; }
.feat-bar { margin: 6px 0; }
.feat-bar-label { color: var(--text); font-size: 13px; }
.feat-bar-track { height: 10px; background: rgba(255,255,255,0.06); border-radius: 999px; overflow: hidden; }
.feat-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #22d3ee, #a78bfa); animation: barGrow 1.2s ease-out both; }
.coef-row { display: flex; align-items: center; gap: 12px; margin: 6px 0; }
.coef-label { flex: 0 0 38%; color: var(--text); font-size: 13px; text-align: right; }
.coef-bar-wrap { flex: 1; display: flex; height: 14px; background: rgba(255,255,255,0.04); border-radius: 999px; }
.coef-bar-pos, .coef-bar-neg { height: 100%; border-radius: 999px; animation: barGrow 1.2s ease-out both; }
.coef-bar-pos { background: linear-gradient(90deg, #34d399, #22d3ee); margin-left: 50%; }
.coef-bar-neg { background: linear-gradient(90deg, #f43f5e, #f59e0b); margin-right: 50%; margin-left: auto; }
.coef-value { flex: 0 0 70px; color: var(--muted); font-size: 12px; font-variant-numeric: tabular-nums; }
.predict-card { background: linear-gradient(135deg, rgba(34,211,238,0.10), rgba(167,139,250,0.10));
    border: 1px solid rgba(34,211,238,0.35); border-radius: 22px; padding: 22px 26px;
    animation: fadeUp .8s ease-out both, glow 4s ease-in-out infinite; }
.result-pill { display: inline-block; padding: 8px 16px; border-radius: 999px; font-weight: 700; letter-spacing: 0.04em; }
.result-yes { background: rgba(52,211,153,0.18); color: #34d399; border: 1px solid #34d399; }
.result-no { background: rgba(244,63,94,0.16); color: #f43f5e; border: 1px solid #f43f5e; }
.result-prob { font-size: 56px; font-weight: 800; color: var(--text); }
.stSlider [data-baseweb="slider"] > div { background: rgba(255,255,255,0.08) !important; }
button[kind="primary"] { background: linear-gradient(90deg, #22d3ee, #a78bfa) !important; border: none !important; color: #0b1020 !important; font-weight: 700 !important; }
</style>
""",
    unsafe_allow_html=True,
)

clean_df = load_clean_df()
clusters_df = load_clusters_df()
schema = load_schema()
metrics = load_metrics()
coef_df = load_coefficients()
feature_summary_path = OUTPUTS_DIR / "feature_selection_summary.csv"
feature_summary_df = pd.read_csv(feature_summary_path) if feature_summary_path.exists() else pd.DataFrame()

ARROW = "<div class='flow-arrow'>▼</div>"


def stage_open(num: int, color: str, title: str, sub: str) -> None:
    st.markdown(f"""
<div class='stage-card' style='--stage-color:{color};'>
    <div>
        <span class='stage-num'>{num}</span>
        <span class='stage-title'>{title}</span>
        <div class='stage-sub'>{sub}</div>
    </div>
""", unsafe_allow_html=True)


def stage_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def stat_block(items: list[tuple[str, str]]) -> None:
    cells = "".join(
        f"<div class='stat'><div class='stat-label'>{lbl}</div>"
        f"<div class='stat-value'>{val}</div></div>"
        for lbl, val in items
    )
    st.markdown(f"<div class='stat-row'>{cells}</div>", unsafe_allow_html=True)


st.markdown("""
<div class='hero'>
    <span class='pipeline-tag'>End-to-end Machine Learning Pipeline</span>
    <h1>AI-Driven Marketing Campaign System</h1>
    <p>Raw survey · Cleaning · Feature selection · Personas · Predictive model · Live predictor</p>
</div>
""", unsafe_allow_html=True)
st.markdown(ARROW, unsafe_allow_html=True)

n_raw_cols = 0
n_raw_rows = 0
if RAW_CSV.exists():
    raw_head = pd.read_csv(RAW_CSV, nrows=0)
    n_raw_cols = len(raw_head.columns)
    n_raw_rows = sum(1 for _ in open(RAW_CSV, encoding="utf-8")) - 1

stage_open(1, "#22d3ee", "Raw Data", "Source · CSV survey export")
stat_block([
    ("Respondents", f"{n_raw_rows:,}"),
    ("Raw columns", f"{n_raw_cols}"),
    ("File", RAW_CSV.name),
])
stage_close()
st.markdown(ARROW, unsafe_allow_html=True)

n_clean_rows = len(clean_df)
n_clean_cols = len(clean_df.columns)
n_labelled = clean_df[TARGET_COLUMN].dropna().shape[0] if TARGET_COLUMN in clean_df.columns else 0

stage_open(2, "#a78bfa", "Cleaning & Encoding", "Standardise · derive target · group answers")
stat_block([
    ("Cleaned rows", f"{n_clean_rows:,}"),
    ("Cleaned columns", f"{n_clean_cols}"),
    ("Labelled (target ≠ NaN)", f"{n_labelled:,}"),
])
stage_close()
st.markdown(ARROW, unsafe_allow_html=True)

stage_open(3, "#34d399", "Feature Selection", "Rule · top 5 source variables by ANOVA F-score (deduplicated)")
if not feature_summary_df.empty:
    top5 = (
        feature_summary_df.sort_values("f_score", ascending=False)
        .drop_duplicates("source_var").head(5)
    )
    max_f = float(top5["f_score"].max())
    bars_html = []
    for _, row in top5.iterrows():
        pct = (row["f_score"] / max_f) * 100
        bars_html.append(f"""<div class='feat-bar'>
<div style='display:flex;justify-content:space-between;'>
<span class='feat-bar-label'>{row['display_label']}</span>
<span class='feat-bar-label' style='color:#94a3b8'>F = {row['f_score']:.1f}</span>
</div>
<div class='feat-bar-track'>
<div class='feat-bar-fill' style='width:{pct:.1f}%; animation-delay:{0.1 * (5 - len(bars_html)):.1f}s;'></div>
</div>
</div>""")
    st.markdown("".join(bars_html), unsafe_allow_html=True)
else:
    st.info("Run the feature-selection stage first.")
stage_close()
st.markdown(ARROW, unsafe_allow_html=True)

stage_open(4, "#f472b6", "Unsupervised — Customer Personas", "K-Means · DBSCAN · Isolation Forest")
if not clusters_df.empty and "customer_persona_cluster" in clusters_df.columns:
    counts = clusters_df["customer_persona_cluster"].value_counts().sort_index()
    n_anom = int(clusters_df.get("is_anomaly", pd.Series([0])).sum())
    stats = [(f"Cluster {i} size", f"{int(c):,}") for i, c in counts.items()]
    stats.append(("Anomalies (IsoForest)", f"{n_anom}"))
    stat_block(stats)
    img_cols = st.columns(2)
    persona_img = OUTPUTS_DIR / "customer_clusters_pca.png"
    radar_img = OUTPUTS_DIR / "persona_radar.png"
    if persona_img.exists():
        img_cols[0].image(str(persona_img), width="stretch")
    if radar_img.exists():
        img_cols[1].image(str(radar_img), width="stretch")
else:
    st.info("Run the unsupervised stage first.")
stage_close()
st.markdown(ARROW, unsafe_allow_html=True)

stage_open(5, "#f59e0b", "Supervised — Predict RTD Coffee Choice",
           "Logistic Regression · Random Forest · Gradient Boosting (5-fold CV)")
if metrics:
    best = metrics.get("best_model_by_cv_f1_macro", "RandomForest")
    cv = metrics["models"][best]["cv"]
    ho = metrics["models"][best]["holdout"]
    stat_block([
        ("Best model", best),
        ("CV macro F1", f"{cv['cv_f1_macro_mean']:.3f}"),
        ("CV ROC-AUC", f"{cv['cv_roc_auc_ovr_macro_mean']:.3f}"),
        ("Test accuracy", f"{ho['test_accuracy']:.3f}"),
        ("Test macro recall", f"{ho['test_recall_macro']:.3f}"),
    ])

    if not coef_df.empty:
        st.markdown(
            "<div class='stage-sub' style='margin-top:14px'>"
            "Logistic regression coefficients for ลองแน่นอน · standardised features · "
            "green ↑ means more likely, red ↓ means less likely</div>",
            unsafe_allow_html=True,
        )
        ranked = coef_df.copy()
        if "class" in ranked.columns:
            ranked = ranked[ranked["class"].astype(int) == 2]
        ranked["abs"] = ranked["coefficient"].abs()
        ranked = ranked.sort_values("abs", ascending=False).head(8)
        max_abs = float(ranked["abs"].max())
        rows_html = []
        for _, row in ranked.iterrows():
            coef = float(row["coefficient"])
            pct = abs(coef) / max_abs * 50
            bar_cls = "coef-bar-pos" if coef >= 0 else "coef-bar-neg"
            bar = f"<div class='coef-bar-wrap'><div class='{bar_cls}' style='width:{pct:.1f}%'></div></div>"
            label = str(row["feature"]).replace("most_freq_rtd_brand_", "RTD brand · ")
            rows_html.append(
                f"<div class='coef-row'>"
                f"<div class='coef-label'>{label}</div>"
                f"{bar}"
                f"<div class='coef-value'>{coef:+.2f}  (×{float(row['odds_ratio']):.2f})</div>"
                f"</div>"
            )
        st.markdown("".join(rows_html), unsafe_allow_html=True)
else:
    st.info("Run the supervised stage first.")
stage_close()
st.markdown(ARROW, unsafe_allow_html=True)

st.markdown(
    "<div class='predict-card'>"
    "<span class='stage-num' style='--stage-color:#22d3ee;background:#22d3ee;'>6</span>"
    "<span class='stage-title'>Try the model</span>"
    "<div class='stage-sub'>Move the sliders, pick a brand · the trained pipeline scores live</div>",
    unsafe_allow_html=True,
)

if not schema or not metrics:
    st.warning("Run `python run_pipeline.py` first to generate the model artefacts.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

best_name = schema.get("best_model", "RandomForest")
best_model = load_model(schema["model_files"]["best"])
logreg_model = load_model(schema["model_files"]["logreg"])

with st.form("predict_form", clear_on_submit=False):
    cols = st.columns([1, 1, 1])
    inputs: dict = {}

    likert_specs = [s for s in schema["numeric"] if s.get("is_likert")]
    other_specs = [s for s in schema["numeric"] if not s.get("is_likert")]
    for idx, spec in enumerate(likert_specs):
        with cols[idx % len(cols)]:
            inputs[spec["name"]] = st.slider(
                spec["label"], int(spec["min"]), int(spec["max"]),
                int(round(spec["median"])), 1,
            )
    for idx, spec in enumerate(other_specs):
        with cols[idx % len(cols)]:
            inputs[spec["name"]] = st.number_input(
                spec["label"], float(spec["min"]), float(spec["max"]), float(spec["median"]),
            )
    for idx, spec in enumerate(schema["categorical"]):
        with cols[idx % len(cols)]:
            choices = spec["choices"]
            default = spec.get("default", choices[0] if choices else "")
            i_default = choices.index(default) if default in choices else 0
            inputs[spec["name"]] = st.selectbox(spec["label"], choices, index=i_default)

    model_choice = st.radio("Model", [best_name, "LogisticRegression"], index=0, horizontal=True)
    submitted = st.form_submit_button("Predict ✨", type="primary")

if submitted:
    feature_order = [s["name"] for s in schema["numeric"]] + [s["name"] for s in schema["categorical"]]
    X_one = pd.DataFrame([{c: inputs[c] for c in feature_order}])
    active = best_model if model_choice == best_name else logreg_model
    probas = active.predict_proba(X_one)[0]
    classes = [int(c) for c in active.named_steps["clf"].classes_]
    prob_by_class = {cls: float(probas[idx]) for idx, cls in enumerate(classes)}
    proba = prob_by_class.get(2, 0.0)
    pred = int(active.predict(X_one)[0])

    pred_label = CLASS_LABELS.get(pred, str(pred))
    pred_color = CLASS_COLORS.get(pred, "#94a3b8")
    pill = (
        f"<span class='result-pill' style='color:{pred_color};border-color:{pred_color};"
        f"background:rgba(255,255,255,0.06)'>{pred_label}</span>"
    )
    prob_rows = "".join(
        f"<div style='color:#94a3b8;font-size:12px;margin-top:4px'>"
        f"{CLASS_LABELS[cls]} · {prob_by_class.get(cls, 0.0) * 100:.1f}%</div>"
        for cls in sorted(CLASS_LABELS)
    )
    st.markdown(f"""
<div style='margin-top:16px; display:flex; align-items:center; gap:24px; flex-wrap:wrap;'>
    <div class='result-prob'>{proba * 100:.1f}%</div>
    <div>
        <div style='color:#94a3b8;font-size:12px;letter-spacing:0.12em;text-transform:uppercase'>P(ลองแน่นอน)</div>
        <div style='margin-top:8px'>{pill}</div>
        {prob_rows}
        <div style='color:#94a3b8;font-size:12px;margin-top:6px'>Model · {model_choice}</div>
    </div>
</div>
""", unsafe_allow_html=True)

    if model_choice == "LogisticRegression":
        preprocessor = logreg_model.named_steps["preprocess"]
        clf = logreg_model.named_steps["clf"]
        transformed = preprocessor.transform(X_one).ravel()
        names: list[str] = []
        for name, transformer, raw_cols in preprocessor.transformers_:
            if name == "num":
                names.extend(raw_cols)
            elif name == "cat":
                ohe = transformer.named_steps["onehot"]
                names.extend(ohe.get_feature_names_out(raw_cols).tolist())
        class_index = list(clf.classes_).index(2) if 2 in list(clf.classes_) else -1
        contribs = clf.coef_[class_index] * transformed
        contrib_df = (
            pd.DataFrame({"feature": names, "logodds": contribs})
            .assign(abs_=lambda d: d["logodds"].abs())
            .sort_values("abs_", ascending=False)
            .head(8).iloc[::-1].drop(columns="abs_")
        )
        st.markdown(
            "<div class='stage-sub' style='margin-top:14px'>How each input pushed this score</div>",
            unsafe_allow_html=True,
        )
        st.bar_chart(contrib_df.set_index("feature"))

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; color:#64748b; padding:24px 0 8px; font-size:12px; letter-spacing:0.1em;'>
    PIPELINE · python run_pipeline.py · streamlit run src/web/app.py
</div>
""", unsafe_allow_html=True)
