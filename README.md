# Case-3-Media-Behavior

## 📌 Project Overview (โจทย์ของโปรเจกต์)
This project analyzes consumer media behavior survey data to support communication strategy planning for a coffee brand with over 4,000 outlets. The business is preparing to expand from on-premise coffee shops to the Ready-to-Drink (RTD) market in convenience stores.

**Primary analysis goals:**
- Identify communication strategies to reach new RTD consumers.
- Retain and extend brand-loyal customers by aligning in-store and RTD product experiences.
- Analyze media behavior during **Songkran festival** to find the most effective launch touchpoints.

---

## 📂 Repository structure
- `Case_3_Media_Behavior.csv`: raw survey dataset
- `column_mapping.json`: mapping of raw column names to cleaned feature names
- `data_cleaning.py`: data preprocessing pipeline for cleaning and transforming the survey data
- `feature_selection.py`: analysis and selection of the most informative features
- `unsupervised_learning.py`: clustering and segmentation analysis on cleaned data
- `media_behavior_cleaned.csv`: cleaned dataset after preprocessing
- `media_behavior_with_clusters.csv`: cleaned dataset with cluster labels added
- `analysis_outputs/`: generated visualizations and analysis charts

---

## 🚀 How to use
1. Install dependencies (if needed):
   ```bash
   pip install pandas numpy scikit-learn matplotlib seaborn
   ```

2. Run the preprocessing script:
   ```bash
   python data_cleaning.py
   ```

3. Run feature selection and clustering analysis:
   ```bash
   python feature_selection.py
   python unsupervised_learning.py
   ```

4. Review output files:
   - `media_behavior_cleaned.csv`
   - `media_behavior_with_clusters.csv`
   - images in `analysis_outputs/`

---

## 📈 What this project does
- Cleans and standardizes survey responses.
- Maps raw questionnaire fields to usable analytical variables.
- Selects the most relevant features for segmentation.
- Applies unsupervised learning to identify consumer clusters.
- Produces charts that help interpret media behavior and target groups.

---

## 🔧 Notes
- The repository currently focuses on data preparation and clustering analysis.
- If you want to push this project to GitHub, commit the new `README.md` and then use `git push origin main`.
- Remove large generated files from version control if you prefer to keep the repo lightweight.
