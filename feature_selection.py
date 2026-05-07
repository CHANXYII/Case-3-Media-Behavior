from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import font_manager
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import f_classif

# Setup & Configuration
from data_cleaning import clean_data

raw_data_path = Path("Case_3_Media_Behavior.csv")
clean_data_path = Path("media_behavior_cleaned.csv")
output_dir = Path("analysis_outputs")
plot_font_path = Path("DB-Adman-X.ttf")
target_column = "target_try_new_rtd_coffee"

font_manager.fontManager.addfont(str(plot_font_path))
plot_font = font_manager.FontProperties(fname=str(plot_font_path)).get_name()
plt.rcParams["font.family"] = plot_font
plt.rcParams["font.sans-serif"] = [plot_font]
sns.set_theme(style="whitegrid", rc={"font.family": plot_font, "font.sans-serif": [plot_font]})

age_group_mapping = {
    "ต่ำกว่า 18ปี": 17.0,
    "18-22ปี": 20.0,
    "23-29ปี": 26.0,
    "30-39ปี": 35.0,
    "40-49ปี": 45.0,
    "50ปี ขึ้นไป": 55.0,
}

likert_cols = [
    "coffee_fresh_taste", "coffee_intensity", "coffee_smooth", "coffee_acidity",
    "coffee_aroma", "coffee_caffeine", "coffee_origin", "coffee_convenience",
    "coffee_value", "coffee_nutrition", "coffee_brand_trust", "coffee_premium",
    "coffee_packaging", "tea_aroma", "tea_intensity", "tea_no_sugar",
    "tea_zero_kcal", "tea_nutrition", "tea_origin", "tea_brewing",
    "tea_convenience", "tea_brand_trust", "tea_premium", "tea_packaging",
]

def split_answers(value):
    text = str(value).strip()
    if pd.isna(value) or not text or text.lower() == "nan":
        return []
    return [item.strip() for item in text.split(",") if item.strip() and item.strip().lower() != "nan"]

def first_value(series):
    series = series.dropna()
    series = series[series.astype(str).str.strip() != ""]
    return series.iloc[0] if len(series) else np.nan

# Custom aggregation function to merge multiple province entries into a single string
def merge_province(series):
    values = []
    for value in series.dropna():
        for item in split_answers(value):
            if item not in values:
                values.append(item)
    return ",".join(values) if values else np.nan

# Target Derivation Logic
def derive_target(value):
    answers = split_answers(value)
    if any("ลอง" in answer and answer != "ไม่ลอง" for answer in answers):
        return 1.0
    if answers and all(answer == "ไม่ลอง" for answer in answers):
        return 0.0
    return np.nan

# Data Preparation & Feature Engineering
def nice_label_format(text):
    return text.replace("__", " = ").replace("_", " ")

def build_clean_data():
    raw_df = pd.read_csv(raw_data_path)
    raw_df["respondent_id"] = np.arange(1, len(raw_df) + 1)
    raw_df["age_group_raw"] = raw_df["อายุ"]

    df = clean_data(raw_df)
    agg = {col: (merge_province if col == "province" else first_value) for col in df.columns if col != "respondent_id"}
    df = df.groupby("respondent_id", as_index=False).agg(agg)

    df["age_group"] = df["age_group_raw"].astype(str).replace("nan", np.nan)
    df["age"] = df["age_group"].map(age_group_mapping)
    df[target_column] = df["will_try_new_rtd_coffee"].apply(derive_target)

    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_data_path, index=False, encoding="utf-8-sig")
    return df

# Feature Selection & Visualization
def prepare_feature_data(df):
    analysis_df = df.dropna(subset=[target_column]).copy()
    target = analysis_df[target_column].astype(int)

    # Select numeric columns for scaling (including Likert scale columns)
    numeric_cols = [
        col for col in analysis_df.columns
        if pd.api.types.is_numeric_dtype(analysis_df[col]) and col not in ["respondent_id", target_column]
    ]
    numeric_df = analysis_df[numeric_cols].fillna(analysis_df[numeric_cols].median(numeric_only=True))
    scaled_numeric = pd.DataFrame(
        StandardScaler().fit_transform(numeric_df),
        columns=numeric_cols,
        index=analysis_df.index,
    )

    # Identify categorical columns for encoding (excluding certain columns)
    excluded_cols = {
        "respondent_id", "province", "timestamp", "reason_like", "reason_dislike",
        "reason_fav_tea", "customer_segment", "age_group_raw", "will_try_new_rtd_coffee",
    }
    category_cols = []
    for col in analysis_df.select_dtypes(include="object").columns:
        if col in excluded_cols:
            continue
        sample = analysis_df[col].fillna("").astype(str)
        if sample.str.contains(",").mean() == 0 and 1 < sample.nunique() <= 15:
            category_cols.append(col)

    encoded_df = pd.get_dummies(analysis_df[category_cols].fillna("ไม่ระบุ"), dtype=int)
    feature_df = pd.concat([scaled_numeric, encoded_df], axis=1)

    f_scores, p_values = f_classif(feature_df, target)
    feature_scores = pd.DataFrame({
        "feature": feature_df.columns,
        "f_score": f_scores,
        "p_value": p_values,
    }).sort_values("f_score", ascending=False)

    return analysis_df, feature_scores

# Visualization Functions
def make_distribution_table(df):
    rows = []
    cols = [col for col in likert_cols if col in df.columns]
    for col in cols:
        score_dist = pd.to_numeric(df[col], errors="coerce").value_counts(normalize=True)
        rows.append(score_dist.reindex([1.0, 2.0, 3.0, 4.0, 5.0], fill_value=0).rename(nice_label_format(col)))
    dist_df = pd.DataFrame(rows)
    dist_df.columns = ["1", "2", "3", "4", "5"]
    return dist_df

# Correlation Analysis
def make_correlation_table(df):
    cols = [col for col in likert_cols if col in df.columns]
    corr = df[cols + [target_column]].corr(numeric_only=True)[target_column]
    corr = corr.drop(target_column).dropna().sort_values(key=np.abs, ascending=False).head(8)
    heatmap_cols = [target_column] + corr.index.tolist()
    heatmap_df = df[heatmap_cols].corr(numeric_only=True)
    heatmap_df.index = [nice_label_format(col) for col in heatmap_df.index]
    heatmap_df.columns = [nice_label_format(col) for col in heatmap_df.columns]
    return heatmap_df

# Main Function to Generate All Visualizations
def make_images(df):
    analysis_df, feature_scores = prepare_feature_data(df)
    distribution_df = make_distribution_table(analysis_df)
    correlation_df = make_correlation_table(analysis_df)

    # Demographic Profile
    gender_counts = df["gender"].fillna("ไม่ระบุ").value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=gender_counts.index, y=gender_counts.values, ax=ax, palette="Blues_d")
    ax.set_title("Demographic Profile: เพศ")
    ax.set_xlabel("")
    ax.set_ylabel("จำนวนคน")
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(output_dir / "demographic_gender.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Demographic Profile: Age Group
    age_counts = df["age_group"].fillna("ไม่ระบุ").value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=age_counts.index, y=age_counts.values, ax=ax, palette="Greens")
    ax.set_title("Demographic Profile: ช่วงอายุ")
    ax.set_xlabel("")
    ax.set_ylabel("จำนวนคน")
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    plt.savefig(output_dir / "demographic_age.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Demographic Profile: Occupation
    occupation_counts = df["occupation"].fillna("ไม่ระบุ").value_counts().head(8)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=occupation_counts.values, y=occupation_counts.index, ax=ax, palette="Purples")
    ax.set_title("Demographic Profile: อาชีพ")
    ax.set_xlabel("จำนวนคน")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(output_dir / "demographic_occupation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Feature Selection: Top Features Affecting Target
    top_features = feature_scores.head(10).copy()
    top_features["feature"] = top_features["feature"].apply(nice_label_format)
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.barplot(x="f_score", y="feature", data=top_features, ax=ax, palette="Oranges")
    ax.set_title("Feature Selection: ตัวแปรที่มีผลต่อ Target")
    ax.set_xlabel("F-score")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(output_dir / "feature_selection.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Distribution Analysis: Likert Scale Responses
    fig, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(distribution_df, annot=True, fmt=".2f", cmap="YlGnBu", ax=ax)
    ax.set_title("Distribution Analysis: การกระจายคำตอบ Likert")
    ax.set_xlabel("คะแนน")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(output_dir / "distribution_analysis.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Correlation Heatmap: Top Features vs Target
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_df, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap: ความสัมพันธ์กับ Target")
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    df = build_clean_data()
    make_images(df)
    print(f"\nClean data file: {clean_data_path}")
    
    print("\nOutput images:")
    print(output_dir / "demographic_gender.png")
    print(output_dir / "demographic_age.png")
    print(output_dir / "demographic_occupation.png")
    print(output_dir / "feature_selection.png")
    print(output_dir / "distribution_analysis.png")
    print(output_dir / "correlation_heatmap.png")

    print("\nFeature selection = f_classif")
    print("Scale transformation = StandardScaler on numeric/Likert columns")
    print("Encoding = pd.get_dummies on categorical columns")
