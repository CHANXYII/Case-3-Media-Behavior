from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import font_manager
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Setup & Configuration
clean_data_path = Path("media_behavior_cleaned.csv")
output_dir = Path("analysis_outputs")
output_dir.mkdir(parents=True, exist_ok=True)

plot_font_path = Path("DB-Adman-X.ttf")
if plot_font_path.exists():
    font_manager.fontManager.addfont(str(plot_font_path))
    plot_font = font_manager.FontProperties(fname=str(plot_font_path)).get_name()
    plt.rcParams["font.family"] = plot_font
    sns.set_theme(style="whitegrid", rc={"font.family": plot_font})
else:
    sns.set_theme(style="whitegrid")

# Clustering
def load_and_prepare_data():
    df = pd.read_csv(clean_data_path)
    
    # Choose only columns that are Likert scale scores for behavior clustering
    cluster_features = [col for col in df.columns if 'coffee_' in col or 'tea_' in col or 'freq_' in col]
    
    # Filter only numeric variables
    numeric_df = df[cluster_features].select_dtypes(include=[np.number])
    
    # Handle missing values
    numeric_df = numeric_df.fillna(numeric_df.median())
    
    return df, numeric_df

# Unsupervised Learning Pipeline
def perform_unsupervised_learning(original_df, numeric_df):
    # Step 3.1: Feature Scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_df)
    
    # Step 3.2: Dimensionality Reduction (PCA)
    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(scaled_data)
    
    print(f"PCA explained variance ratio: {pca.explained_variance_ratio_.sum() * 100:.2f}%")
    
    # Step 3.3: Find the optimal number of clusters (K) using the Elbow Method
    inertia = []
    k_range = range(2, 8)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled_data)
        inertia.append(kmeans.inertia_)
        
    # Draw: Elbow Method
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(k_range, inertia, marker='o', linestyle='--')
    ax.set_title("Elbow Method for Finding Optimal Number of Clusters (K)")
    ax.set_xlabel("Number of Clusters (K)")
    ax.set_ylabel("Inertia (Sum of Squared Distances)")
    plt.savefig(output_dir / "elbow_method.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    # Step 3.4: Customize Customer Segmentation (Clustering with K-Means)
    optimal_k = 3
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)
    
    # Calculate Silhouette Score to evaluate clustering quality
    sil_score = silhouette_score(scaled_data, clusters)
    print(f"Silhouette Score (K={optimal_k}): {sil_score:.4f}")
    
    # Put the results back into the original DataFrame
    original_df['customer_persona_cluster'] = clusters
    original_df['pca_1'] = pca_result[:, 0]
    original_df['pca_2'] = pca_result[:, 1]
    
    # Step 3.5: Visualize Customer Persona (PCA Scatter Plot)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.scatterplot(
        x='pca_1', y='pca_2', 
        hue='customer_persona_cluster', 
        palette='viridis', 
        data=original_df, 
        alpha=0.7, 
        s=100,
        ax=ax
    )
    ax.set_title("Customer Segmentation (PCA 2D Projection)")
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    plt.legend(title='Persona Cluster')
    plt.savefig(output_dir / "customer_clusters_pca.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    return original_df

# Customer Persona Analysis
def analyze_personas(df):
    # Save data with clusters for use in Supervised Learning
    output_data_path = "media_behavior_with_clusters.csv"
    df.to_csv(output_data_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved data with clusters to: {output_data_path}")

if __name__ == "__main__":
    original_df, numeric_df = load_and_prepare_data()
    clustered_df = perform_unsupervised_learning(original_df, numeric_df)
    analyze_personas(clustered_df)
