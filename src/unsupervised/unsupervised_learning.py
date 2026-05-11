import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import IsolationForest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CLEAN_CSV, CLUSTERS_CSV, OUTPUTS_DIR, ensure_dirs, setup_thai_font

clean_data_path = CLEAN_CSV
output_dir = OUTPUTS_DIR
ensure_dirs()
setup_thai_font()


def load_and_prepare_data():
    df = pd.read_csv(clean_data_path)
    cluster_features = [col for col in df.columns if 'coffee_' in col or 'tea_' in col or 'freq_' in col]
    numeric_df = df[cluster_features].select_dtypes(include=[np.number])
    numeric_df = numeric_df.fillna(numeric_df.median())
    return df, numeric_df


def descriptive_statistics(df, numeric_df):
    print("\n" + "="*60)
    print("\nBasic Descriptive Statistics: ")
    desc = numeric_df.describe().T
    desc["skewness"] = numeric_df.skew()
    desc["kurtosis"] = numeric_df.kurt()
    print(desc.round(3).to_string())

    print("\nMissing Values (original data): ")
    cluster_features = numeric_df.columns.tolist()
    missing = df[cluster_features].isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_report = pd.DataFrame({"missing_count": missing, "missing_%": missing_pct})
    print(missing_report[missing_report["missing_count"] > 0].to_string() or "  No missing values found.")

    print("Categorical Column Value Counts: ")
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols[:5]:
        print(f"\n  {col}:")
        print(df[col].value_counts().head(5).to_string())

    plot_cols = numeric_df.columns[:9]
    n = len(plot_cols)
    ncols = 3
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(14, nrows * 3))
    axes = axes.flatten()
    for i, col in enumerate(plot_cols):
        axes[i].hist(numeric_df[col], bins=20, color="#5DCAA5", edgecolor="white", alpha=0.85)
        axes[i].set_title(col, fontsize=10)
        axes[i].set_xlabel("Value")
        axes[i].set_ylabel("Count")
        skew_val = numeric_df[col].skew()
        axes[i].text(0.97, 0.95, f"skew={skew_val:.2f}", transform=axes[i].transAxes,
                     ha="right", va="top", fontsize=8, color="gray")
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("Distribution of Clustering Features", fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / "descriptive_distributions.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("\nSaved: descriptive_distributions.png")

    fig, ax = plt.subplots(figsize=(14, 5))
    numeric_df[plot_cols].boxplot(ax=ax, vert=True, patch_artist=True,
                                   boxprops=dict(facecolor="#AFA9EC", alpha=0.7),
                                   medianprops=dict(color="#3C3489", linewidth=2))
    ax.set_title("Boxplots of Clustering Features (first 9)")
    ax.set_xticklabels(plot_cols, rotation=45, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "descriptive_boxplots.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: descriptive_boxplots.png")


def correlation_analysis(numeric_df):
    print("\n" + "="*60)
    corr_matrix = numeric_df.corr()

    print("\nTop 10 Correlated Feature Pairs (|r| > 0.5): ")
    corr_pairs = (
        corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        .stack().reset_index()
    )
    corr_pairs.columns = ["feature_1", "feature_2", "correlation"]
    corr_pairs["abs_corr"] = corr_pairs["correlation"].abs()
    top_pairs = corr_pairs[corr_pairs["abs_corr"] > 0.5].sort_values("abs_corr", ascending=False)
    print(top_pairs.head(10).to_string(index=False) if not top_pairs.empty else "  No pairs with |r| > 0.5 found.")

    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
                center=0, linewidths=0.5, linecolor="white",
                annot_kws={"size": 7}, ax=ax)
    ax.set_title("Correlation Matrix (lower triangle)", fontsize=13)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "correlation_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: correlation_heatmap.png")

    g = sns.clustermap(corr_matrix, cmap="RdYlGn", center=0, figsize=(12, 12),
                       linewidths=0.3, annot=False)
    g.fig.suptitle("Clustered Correlation Map", y=1.01, fontsize=13)
    plt.savefig(output_dir / "correlation_clustermap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: correlation_clustermap.png")

    return corr_matrix


def exploratory_data_analysis(df, numeric_df):
    print("\n" + "="*60)
    sample_cols = numeric_df.columns[:5].tolist()
    pair_data = numeric_df[sample_cols].copy()
    g = sns.pairplot(pair_data, diag_kind="kde", plot_kws={"alpha": 0.5, "color": "#1D9E75"},
                     diag_kws={"color": "#1D9E75"})
    g.fig.suptitle("Pairplot of Key Clustering Features", y=1.01, fontsize=13)
    plt.savefig(output_dir / "eda_pairplot.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("\nSaved: eda_pairplot.png")

    print("Feature Variance Ranking (top 10): ")
    variance = numeric_df.var().sort_values(ascending=False)
    print(variance.head(10).round(4).to_string())

    fig, ax = plt.subplots(figsize=(10, 5))
    variance.head(15).sort_values().plot(kind="barh", ax=ax, color="#7F77DD", alpha=0.8)
    ax.set_title("Feature Variance (top 15)")
    ax.set_xlabel("Variance")
    plt.tight_layout()
    plt.savefig(output_dir / "eda_variance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: eda_variance.png")

    cluster_features = numeric_df.columns.tolist()
    raw_slice = df[cluster_features]
    if raw_slice.isnull().any().any():
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.heatmap(raw_slice.isnull(), cbar=False, yticklabels=False, cmap="Reds", ax=ax)
        ax.set_title("Missing Value Map (red = missing)")
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.tight_layout()
        plt.savefig(output_dir / "eda_missing_values.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        print("Saved: eda_missing_values.png")


def perform_unsupervised_learning(original_df, numeric_df):
    print("\n" + "="*60)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_df)
    print(f"\nScaled {scaled_data.shape[1]} features for {scaled_data.shape[0]} samples.")

    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(scaled_data)
    explained = pca.explained_variance_ratio_
    print(f"\nPCA: ")
    print(f"PC1 explained variance: {explained[0]*100:.2f}%")
    print(f"PC2 explained variance: {explained[1]*100:.2f}%")
    print(f"Total explained: {explained.sum()*100:.2f}%")

    loadings = pd.DataFrame(pca.components_.T, index=numeric_df.columns, columns=["PC1", "PC2"])
    print("\nTop 5 features by PC1 loading (absolute): ")
    print(loadings["PC1"].abs().sort_values(ascending=False).head(5).round(4).to_string())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for i, ax in enumerate(axes):
        pc = f"PC{i+1}"
        top = loadings[pc].abs().sort_values(ascending=False).head(10)
        colors = ["#D85A30" if loadings.loc[f, pc] > 0 else "#378ADD" for f in top.index]
        axes[i].barh(top.index, loadings.loc[top.index, pc], color=colors, alpha=0.8)
        axes[i].axvline(0, color="gray", linewidth=0.8, linestyle="--")
        axes[i].set_title(f"{pc} Loadings (top 10 features)")
        axes[i].set_xlabel("Loading coefficient")
    plt.suptitle("PCA Feature Loadings", fontsize=13)
    plt.tight_layout()
    plt.savefig(output_dir / "pca_loadings.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: pca_loadings.png")

    print("\nMETHOD 1: K-Means Clustering")
    inertia = []
    silhouettes = []
    k_range = range(2, 8)
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(scaled_data)
        inertia.append(km.inertia_)
        silhouettes.append(silhouette_score(scaled_data, labels))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(k_range, inertia, marker='o', linestyle='--', color="#D85A30")
    ax1.set_title("Elbow Method (Inertia)")
    ax1.set_xlabel("Number of Clusters (K)")
    ax1.set_ylabel("Inertia")

    ax2.plot(k_range, silhouettes, marker='s', linestyle='--', color="#1D9E75")
    ax2.set_title("Silhouette Score by K")
    ax2.set_xlabel("Number of Clusters (K)")
    ax2.set_ylabel("Silhouette Score")
    best_k = list(k_range)[silhouettes.index(max(silhouettes))]
    ax2.axvline(best_k, color="gray", linestyle=":", alpha=0.8)
    ax2.text(best_k + 0.1, max(silhouettes), f"Best K={best_k}", fontsize=9, color="gray")

    plt.suptitle("Choosing Optimal K for K-Means", fontsize=13)
    plt.tight_layout()
    plt.savefig(output_dir / "elbow_method.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    optimal_k = 3
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(scaled_data)
    kmeans_sil = silhouette_score(scaled_data, kmeans_labels)
    print(f"Optimal K = {optimal_k}")
    print(f"Silhouette Score (K-Means, K={optimal_k}): {kmeans_sil:.4f}")

    print("\nMETHOD 2: DBSCAN Clustering (auto-determines clusters)")
    k_neighbors = 5
    nbrs = NearestNeighbors(n_neighbors=k_neighbors).fit(scaled_data)
    distances, _ = nbrs.kneighbors(scaled_data)
    k_distances = np.sort(distances[:, k_neighbors - 1])[::-1]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(k_distances, color="#7F77DD")
    ax.set_title(f"K-Distance Graph (k={k_neighbors}) — find the 'elbow' for eps")
    ax.set_xlabel("Points sorted by distance")
    ax.set_ylabel(f"{k_neighbors}-NN distance")

    knee_idx = np.argmax(np.diff(k_distances) < -0.01 * k_distances.max()) + 1
    if 0 < knee_idx < len(k_distances):
        ax.axhline(k_distances[knee_idx], color="#D85A30", linestyle="--", alpha=0.7,
                   label=f"Suggested eps ≈ {k_distances[knee_idx]:.3f}")
        ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(output_dir / "dbscan_kdistance.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: dbscan_kdistance.png")

    n_samples = scaled_data.shape[0]
    auto_min_samples = max(5, int(np.log(n_samples)))
    suggested_eps = k_distances[knee_idx] if 0 < knee_idx < len(k_distances) else 1.5

    dbscan = DBSCAN(eps=suggested_eps, min_samples=auto_min_samples)
    dbscan_labels = dbscan.fit_predict(scaled_data)

    n_clusters_db = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
    n_noise = (dbscan_labels == -1).sum()
    noise_pct = n_noise / len(dbscan_labels) * 100

    print(f"\neps = {suggested_eps:.3f}, min_samples = {auto_min_samples}")
    print(f"Clusters found by DBSCAN: {n_clusters_db}")
    print(f"Noise points (outliers): {n_noise} ({noise_pct:.1f}%)")

    if n_clusters_db > 1:
        mask_core = dbscan_labels != -1
        dbscan_sil = silhouette_score(scaled_data[mask_core], dbscan_labels[mask_core])
        print(f"\nSilhouette Score (DBSCAN, core points): {dbscan_sil:.4f}")
    else:
        dbscan_sil = None
        print("\nOnly 1 cluster detected — silhouette not applicable.")

    print("\nMETHOD 3: Anomaly Detection (Isolation Forest)")
    iso_forest = IsolationForest(contamination=0.05, random_state=42, n_estimators=200)
    anomaly_labels = iso_forest.fit_predict(scaled_data)
    anomaly_scores = iso_forest.decision_function(scaled_data)

    n_anomalies = (anomaly_labels == -1).sum()
    anomaly_pct = n_anomalies / len(anomaly_labels) * 100
    print(f"Anomalies detected: {n_anomalies} ({anomaly_pct:.1f}% of data)")

    original_df['customer_persona_cluster'] = kmeans_labels
    original_df['dbscan_cluster'] = dbscan_labels
    original_df['is_anomaly'] = (anomaly_labels == -1).astype(int)
    original_df['anomaly_score'] = anomaly_scores
    original_df['pca_1'] = pca_result[:, 0]
    original_df['pca_2'] = pca_result[:, 1]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    palette_km = sns.color_palette("Set2", optimal_k)
    palette_db = sns.color_palette("tab10", n_clusters_db + 1)

    for cluster_id in range(optimal_k):
        mask = original_df['customer_persona_cluster'] == cluster_id
        axes[0].scatter(original_df.loc[mask, 'pca_1'], original_df.loc[mask, 'pca_2'],
                        color=palette_km[cluster_id], alpha=0.7, s=60, label=f"Cluster {cluster_id}")
    axes[0].set_title(f"K-Means (K={optimal_k})\nSilhouette = {kmeans_sil:.3f}")
    axes[0].set_xlabel("PC1")
    axes[0].set_ylabel("PC2")
    axes[0].legend(title="Cluster")

    unique_labels = sorted(set(dbscan_labels))
    for idx, label in enumerate(unique_labels):
        mask = original_df['dbscan_cluster'] == label
        color = "gray" if label == -1 else palette_db[idx % len(palette_db)]
        marker = "x" if label == -1 else "o"
        name = "Noise" if label == -1 else f"Cluster {label}"
        axes[1].scatter(original_df.loc[mask, 'pca_1'], original_df.loc[mask, 'pca_2'],
                        color=color, alpha=0.7 if label != -1 else 0.3,
                        s=60, marker=marker, label=name)
    sil_text = f"\nSilhouette = {dbscan_sil:.3f}" if dbscan_sil else ""
    axes[1].set_title(f"DBSCAN ({n_clusters_db} clusters, {n_noise} noise){sil_text}")
    axes[1].set_xlabel("PC1")
    axes[1].set_ylabel("PC2")
    axes[1].legend(title="Cluster")

    normal_mask = original_df['is_anomaly'] == 0
    anomaly_mask = original_df['is_anomaly'] == 1
    axes[2].scatter(original_df.loc[normal_mask, 'pca_1'], original_df.loc[normal_mask, 'pca_2'],
                    c=original_df.loc[normal_mask, 'anomaly_score'],
                    cmap="RdYlGn", alpha=0.7, s=60, label="Normal")
    axes[2].scatter(original_df.loc[anomaly_mask, 'pca_1'], original_df.loc[anomaly_mask, 'pca_2'],
                    color="red", marker="x", s=80, linewidths=1.5, label=f"Anomaly ({n_anomalies})")
    axes[2].set_title(f"Anomaly Detection (Isolation Forest)\n{n_anomalies} anomalies ({anomaly_pct:.1f}%)")
    axes[2].set_xlabel("PC1")
    axes[2].set_ylabel("PC2")
    axes[2].legend()

    plt.suptitle("Comparison of Unsupervised Learning Methods (PCA 2D Projection)", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_dir / "clustering_comparison.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("\nSaved: clustering_comparison.png")

    print("\nModel Comparison Summary: ")
    print(f"{'Method':<30} {'Clusters':>10} {'Silhouette':>12} {'Notes'}")
    print(f"{'-'*65}")
    print(f"{'K-Means (K=3)':<30} {optimal_k:>10} {kmeans_sil:>12.4f}  {'Requires K pre-defined'}")
    db_sil_str = f"{dbscan_sil:.4f}" if dbscan_sil else "N/A"
    print(f"{'DBSCAN (auto)':<30} {n_clusters_db:>10} {db_sil_str:>12}  {'Auto-detects; marks noise'}")
    print(f"{'Isolation Forest':<30} {'-':>10} {'N/A':>12}  {f'{n_anomalies} anomalies ({anomaly_pct:.1f}%)'}")

    return original_df, n_clusters_db, dbscan_sil


def analyze_personas(df, numeric_df):
    print("\n" + "="*60)
    cluster_col = 'customer_persona_cluster'
    n_clusters = df[cluster_col].nunique()

    print("\nCluster Size Distribution: ")
    counts = df[cluster_col].value_counts().sort_index()
    pcts = (counts / len(df) * 100).round(1)
    for c, cnt in counts.items():
        print(f"  Cluster {c}: {cnt} customers ({pcts[c]}%)")

    print("\nMean Feature Values per Cluster: ")
    profile = df.groupby(cluster_col)[numeric_df.columns.tolist()].mean().round(3)
    print(profile.T.to_string())

    top_features = profile.std(axis=0).sort_values(ascending=False).head(8).index.tolist()

    angles = np.linspace(0, 2 * np.pi, len(top_features), endpoint=False).tolist()
    angles += angles[:1]

    fig, axes = plt.subplots(1, n_clusters, figsize=(6 * n_clusters, 6), subplot_kw=dict(polar=True))
    if n_clusters == 1:
        axes = [axes]
    colors = ["#D85A30", "#1D9E75", "#378ADD", "#7F77DD", "#E24B4A"]

    for i, ax in enumerate(axes):
        values = profile.loc[i, top_features].tolist()
        values += values[:1]
        ax.plot(angles, values, color=colors[i % len(colors)], linewidth=2)
        ax.fill(angles, values, color=colors[i % len(colors)], alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(top_features, size=8)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(["1", "2", "3", "4", "5"], size=7, color="gray")
        ax.set_title(f"Cluster {i}", fontsize=13, color=colors[i % len(colors)], pad=15)

    plt.suptitle("Customer Persona Radar Charts\n(top 8 most discriminating features, Likert scale 1-5)", fontsize=13)
    plt.tight_layout()
    plt.savefig(output_dir / "persona_radar.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("\nSaved: persona_radar.png")

    feat_min = profile[top_features].min()
    feat_max = profile[top_features].max()
    feat_range = (feat_max - feat_min).replace(0, 1)
    normalized = ((profile[top_features] - feat_min) / feat_range)

    fig, ax = plt.subplots(figsize=(min(len(top_features) * 1.2, 16), 4))
    sns.heatmap(normalized, annot=profile[top_features].round(2), fmt=".2f",
                cmap="RdYlGn", linewidths=0.5, ax=ax,
                annot_kws={"size": 8}, cbar_kws={"label": "Relative score (0=lowest cluster, 1=highest)"})
    ax.set_title("Cluster Profile Heatmap (color = relative rank per feature, number = raw Likert mean)")
    ax.set_ylabel("Cluster")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", fontsize=8)
    plt.tight_layout()
    plt.savefig(output_dir / "persona_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: persona_heatmap.png")

    print("\nAuto-Generated Persona Descriptions: ")
    persona_names = {}
    for cluster_id in range(n_clusters):
        row = profile.loc[cluster_id, top_features]
        high = row.nlargest(2).index.tolist()
        low = row.nsmallest(2).index.tolist()
        name = f"Persona {cluster_id}: High {', '.join(high)} / Low {', '.join(low)}"
        persona_names[cluster_id] = name
        print(f"{name}")

    fig, ax = plt.subplots(figsize=(6, 4))
    colors_bar = [colors[i % len(colors)] for i in range(n_clusters)]
    bars = ax.bar(counts.index.astype(str), counts.values, color=colors_bar, alpha=0.85, edgecolor="white")
    for bar, pct in zip(bars, pcts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{pct}%", ha="center", va="bottom", fontsize=10)
    ax.set_title("Customer Count per Persona Cluster")
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Number of Customers")
    plt.tight_layout()
    plt.savefig(output_dir / "persona_cluster_size.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: persona_cluster_size.png")

    fig, ax = plt.subplots(figsize=(10, 8))
    for i in range(n_clusters):
        mask = df[cluster_col] == i
        ax.scatter(df.loc[mask, 'pca_1'], df.loc[mask, 'pca_2'],
                   color=colors[i % len(colors)], alpha=0.7, s=80, label=f"Cluster {i}")
        cx = df.loc[mask, 'pca_1'].mean()
        cy = df.loc[mask, 'pca_2'].mean()
        ax.text(cx, cy, f"C{i}", fontsize=12, fontweight="bold",
                ha="center", va="center", color="white",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=colors[i % len(colors)], alpha=0.85))
    ax.set_title("Customer Segmentation - PCA 2D Projection\n(K-Means Personas)")
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    ax.legend(title="Persona Cluster", loc="upper right")
    plt.tight_layout()
    plt.savefig(output_dir / "customer_clusters_pca.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Saved: customer_clusters_pca.png")

    if 'is_anomaly' in df.columns:
        print("\nAnomaly Distribution per Cluster (K-Means):")
        anomaly_by_cluster = df.groupby(cluster_col)['is_anomaly'].agg(['sum', 'mean']).round(3)
        anomaly_by_cluster.columns = ['anomaly_count', 'anomaly_rate']
        print(anomaly_by_cluster.to_string())

    df.to_csv(CLUSTERS_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved final data with clusters to: {CLUSTERS_CSV}")
    return persona_names


if __name__ == "__main__":
    original_df, numeric_df = load_and_prepare_data()
    print(f"\nLoaded data: {original_df.shape[0]} rows, {original_df.shape[1]} columns")
    print(f"Clustering features selected: {len(numeric_df.columns)}")

    descriptive_statistics(original_df, numeric_df)
    correlation_analysis(numeric_df)
    exploratory_data_analysis(original_df, numeric_df)
    clustered_df, n_db_clusters, db_sil = perform_unsupervised_learning(original_df, numeric_df)
    personas = analyze_personas(clustered_df, numeric_df)

    print(f"\nOutput charts saved to: ./{output_dir}/")
    print(f"Final CSV: {CLUSTERS_CSV}")
