# Case 3 — Media Behavior × RTD Coffee
## เอกสารประกอบการนำเสนอ (Presentation Brief, ~20 นาที)

> โปรเจกต์นี้วิเคราะห์ข้อมูลพฤติกรรมการเปิดรับสื่อ (Media Behavior Survey) เพื่อวางแผน
> กลยุทธ์การสื่อสารให้กับแบรนด์กาแฟที่มีหน้าร้านมากกว่า 4,000 สาขา ซึ่งกำลังจะขยายจาก
> ตลาด on-premise (ร้านกาแฟ) ไปสู่ตลาด **RTD (Ready-to-Drink)** ในร้านสะดวกซื้อ
> ครอบคลุมตั้งแต่ขั้น **Data Cleaning → Feature Engineering → Unsupervised → Supervised → Web Dashboard**

---

## 1) ไอเดีย / กระบวนการคิด / Storytelling

### 1.1 โจทย์ทางธุรกิจ
แบรนด์กาแฟเครือใหญ่ (4,000+ สาขา) ต้องการ **ออกผลิตภัณฑ์ RTD ใหม่** ไปวางในร้านสะดวกซื้อ
แต่สินค้า RTD เป็นเกมที่ต่างจากร้านกาแฟโดยสิ้นเชิง — ผู้บริโภคตัดสินใจหน้าตู้แช่ภายใน 3-5 วินาที
สิ่งที่แบรนด์ต้องตอบให้ได้คือ

1. **ใครคือลูกค้าเป้าหมาย** ของ RTD ตัวใหม่? (กลุ่ม Brand Loyal เดิม หรือกลุ่มใหม่?)
2. **สื่อช่องทางไหน** มีอิทธิพลต่อการตัดสินใจซื้อมากที่สุด?
3. **คุณสมบัติสินค้าใด** (รสชาติ / กลิ่น / แพ็คเกจ / ราคา) ควรเน้นในการสื่อสาร?
4. **ช่วง Songkran** ซึ่งเป็นจังหวะ launch — ควรลงสื่ออะไรเพื่อให้ "เห็นแล้วลอง"?

### 1.2 เส้นเรื่อง (Story Arc) สำหรับนำเสนอ
เราเล่าจากข้อมูลดิบ → ข้อมูลเชิงลึก → ตัดสินใจได้ ผ่าน 5 องก์:

| องก์ | คำถามที่ต้องการตอบ | เครื่องมือ |
|---|---|---|
| **(1) Raw → Clean** | ข้อมูลแบบสอบถามมีคุณภาพแค่ไหน? | Pandas cleaning, Thai-column dictionary |
| **(2) Explore** | ลูกค้ามีลักษณะอย่างไร? Feature ไหนสำคัญ? | EDA, ANOVA F-test, Cohen's d |
| **(3) Segment** | แบ่งลูกค้าได้กี่กลุ่ม? แต่ละกลุ่มหน้าตาเป็นยังไง? | PCA + K-Means + DBSCAN + Isolation Forest |
| **(4) Predict** | ใครคนถัดไปที่ "จะลอง" RTD ตัวใหม่? อะไรขับเคลื่อนการตัดสินใจ? | LogReg / GradientBoosting |
| **(5) Activate** | นำ insight ไปใช้จริงผ่านหน้าเว็บอย่างไร? | Next.js dashboard + live predictor |

### 1.3 Target Variable
- **`target_try_new_rtd_coffee_choice`** — 3 คลาส
  - `0 = ไม่ลอง` (25 คน)
  - `1 = อาจจะลอง` (76 คน)
  - `2 = ลองแน่นอน` (17 คน)
- มีคลาส legacy แบบ binary (`target_try_new_rtd_coffee`) เก็บไว้เพื่อ backward-compat แต่โมเดลและ dashboard ใช้แบบ 3 คลาส
- ข้อมูลมี **class imbalance** ชัดเจน → ใช้ `class_weight="balanced"` แทน SMOTE (กลุ่มตัวอย่างเล็ก, การ oversample เสี่ยง overfit)

---

## 2) โครงสร้างโปรแกรมโดยรวม

```
Case_3_Final_Project_F/
├── data/
│   ├── raw/Case_3_Media_Behavior.csv           # ข้อมูลดิบจาก Google Form (ภาษาไทย)
│   └── processed/
│       ├── media_behavior_cleaned.csv          # หลัง cleaning + rename
│       ├── media_behavior_with_clusters.csv    # หลัง K-Means + DBSCAN + IsolationForest
│       └── column_mapping.json                 # dictionary คอลัมน์ ไทย→อังกฤษ
├── assets/DB-Adman-X.ttf                       # ฟอนต์ไทยสำหรับ matplotlib
├── models/
│   ├── supervised_logreg.joblib                  # โมเดล LogisticRegression
│   └── supervised_logreg.joblib                # LogReg แบบ interpretable
├── outputs/                                    # PNG / CSV / JSON ทุกขั้นตอน (~40 ไฟล์)
├── src/
│   ├── config.py                               # path กลาง + Thai font setup
│   ├── data_cleaning/data_cleaning.py
│   ├── feature_engineering/feature_selection_visualization.py
│   ├── unsupervised/unsupervised_learning.py
│   ├── supervised/
│   │   ├── train.py
│   │   ├── per_cluster.py
│   │   └── README.md
│   └── web/                                    # Next.js 14 + Tailwind + Recharts dashboard
├── run_pipeline.py                             # one-shot runner ทั้ง pipeline
├── requirements.txt
└── README.md
```

**ปรัชญา (Design Principles)**
- **Path เป็น single source of truth ใน `src/config.py`** — ทุก script `import` path จากที่เดียวกัน รันจาก cwd ไหนก็ได้
- **Stage แยกกันชัดเจน** — แต่ละ stage อ่าน artifact จาก stage ก่อน, เขียน artifact ของตัวเองให้ stage ถัดไป (ทำซ้ำได้, debug ง่าย)
- **Artifact ทุกอย่าง regenerate ได้** จาก raw CSV เพียงไฟล์เดียว — `python run_pipeline.py` คือพอ
- **Frontend อ่าน JSON static** ที่ pipeline export ให้ → ไม่ต้องรัน Python backend, deploy ง่าย (Vercel/Docker)

---

## 3) Software Diagram / Workflow

### 3.1 Data Flow Diagram

```
                      ┌──────────────────────────────┐
                      │ data/raw/                    │
                      │   Case_3_Media_Behavior.csv  │
                      └──────────────┬───────────────┘
                                     │
                                     ▼
                  ╔══════════════════════════════════╗
                  ║ Stage 1: Data Cleaning           ║
                  ║ src/data_cleaning/               ║
                  ║   data_cleaning.py               ║
                  ║                                  ║
                  ║ • rename ไทย→อังกฤษ (~80 cols)    ║
                  ║ • ทำ multi-answer (split ',')    ║
                  ║ • Likert text → numeric (1-5)    ║
                  ║ • normalize จังหวัด                ║
                  ║ • derive customer_segment        ║
                  ╚══════════════════┬═══════════════╝
                                     │ media_behavior_cleaned.csv
                                     │ column_mapping.json
                                     ▼
                  ╔══════════════════════════════════╗
                  ║ Stage 2: Feature Engineering     ║
                  ║ src/feature_engineering/         ║
                  ║   feature_selection_visualization║
                  ║                                  ║
                  ║ • derive target (3 คลาส)         ║
                  ║ • ANOVA F-test (numeric+cat OHE) ║
                  ║ • Cohen's d / effect size        ║
                  ║ • EDA: 15+ PNG charts            ║
                  ║ • imbalance, minority profile    ║
                  ╚══════════════════┬═══════════════╝
                                     │ feature_selection_summary.csv
                                     │ + EDA charts (PNG)
                                     ▼
                  ╔══════════════════════════════════╗
                  ║ Stage 3: Unsupervised            ║
                  ║ src/unsupervised/                ║
                  ║   unsupervised_learning.py       ║
                  ║                                  ║
                  ║ • StandardScaler + PCA (2D)      ║
                  ║ • K-Means (elbow + silhouette)   ║
                  ║ • DBSCAN (k-distance auto-eps)   ║
                  ║ • Isolation Forest (5% contam.)  ║
                  ║ • persona radar / heatmap        ║
                  ╚══════════════════┬═══════════════╝
                                     │ media_behavior_with_clusters.csv
                                     │ + persona charts (PNG)
                                     ▼
                  ╔════════════════════════════════════╗
                  ║ Stage 4: Supervised                ║
                  ║ src/supervised/train.py            ║
                  ║                                    ║
                  ║ • 5 numeric + 1 cat (top-ANOVA)    ║
                  ║ • ColumnTransformer pipeline       ║
                  ║ • LogReg / GB เปรียบเทียบ            ║
                  ║ • 5-fold Stratified CV             ║
                  ║ • 80/20 stratified hold-out        ║
                  ║ • export coefficients + SHAP-lite  ║
                  ╚══════════════════┬═════════════════╝
                                     │ supervised_logreg.joblib
                                     │ supervised_metrics.json
                                     │ supervised_coefficients.csv
                                     │ supervised_feature_schema.json
                                     ▼
                  ╔══════════════════════════════════╗
                  ║ Stage 5: Per-Cluster Drivers     ║
                  ║ src/supervised/per_cluster.py    ║
                  ║                                  ║
                  ║ • fit LogReg ต่อ cluster แยก      ║
                  ║ • z-score vs global mean         ║
                  ║ • try_rate / maybe_rate / no_rate║
                  ╚══════════════════┬═══════════════╝
                                     │ cluster_supervised.json
                                     ▼
                  ╔══════════════════════════════════╗
                  ║ Stage 6: Web Dashboard           ║
                  ║ src/web/ (Next.js 14)            ║
                  ║                                  ║
                  ║ • อ่าน JSON static                ║
                  ║ • หน้า: Hero / Cleaning /         ║
                  ║   FeatureSelection / Personas /  ║
                  ║   PerClusterDrivers / Predictor /║
                  ║   MarketingPlan / RawData        ║
                  ║ • live predictor (โมเดล LogReg   ║
                  ║   ฝัง coefficient เข้า client)     ║
                  ╚══════════════════════════════════╝
```

### 3.2 Module Dependency Graph

```
config.py  ◀── (import จากทุก module)
   ▲
   │
   ├── data_cleaning.py
   │      ▲
   │      │  (re-uses clean_data)
   │      │
   ├── feature_selection_visualization.py
   │      │
   │      │  (อ่าน CLEAN_CSV + เขียน feature_selection_summary.csv)
   │      ▼
   ├── unsupervised_learning.py
   │      │  (อ่าน CLEAN_CSV + เขียน CLUSTERS_CSV)
   │      ▼
   ├── supervised/train.py
   │      │  (อ่าน CLEAN_CSV + feature_selection_summary.csv)
   │      ▼
   └── supervised/per_cluster.py
          (อ่าน CLUSTERS_CSV)
```

### 3.3 Runtime Workflow ของ `run_pipeline.py`

```python
STAGES = [
    ("Clean + feature selection", "src.feature_engineering.feature_selection_visualization"),
    ("Unsupervised (K-Means / DBSCAN / IsolationForest)", "src.unsupervised.unsupervised_learning"),
    ("Supervised training", "src.supervised.train"),
    ("Per-cluster supervised drivers", "src.supervised.per_cluster"),
]
```
รันทุก stage ลำดับเดียวกับ Diagram ข้างบนด้วย `runpy.run_module` ทำให้ทุก stage รันเหมือนเรียกตรงจาก CLI

---

## 4) คำอธิบายหน้าที่การทำงานของแต่ละไฟล์ Code

### 4.1 `src/config.py` (43 บรรทัด)
**หน้าที่:** เป็น single source of truth สำหรับ path และการตั้งค่าฟอนต์ไทยใน matplotlib

ตัวแปรสำคัญ:
- `PROJECT_ROOT, DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR, MODELS_DIR, ASSETS_DIR`
- `RAW_CSV, CLEAN_CSV, CLUSTERS_CSV, COLUMN_MAPPING_JSON, FONT_PATH`
- `TARGET_COLUMN = "target_try_new_rtd_coffee_choice"` (3 คลาส)
- `LEGACY_BINARY_TARGET_COLUMN = "target_try_new_rtd_coffee"` (binary, เก็บไว้ reference)

ฟังก์ชัน:
- `ensure_dirs()` → mkdir ทุก output dir
- `setup_thai_font()` → register `DB-Adman-X.ttf` เข้า matplotlib + seaborn (รองรับการแสดงผลภาษาไทยใน chart)

---

### 4.2 `src/data_cleaning/data_cleaning.py` (277 บรรทัด)
**หน้าที่:** แปลงข้อมูล Google Form ดิบ → ข้อมูลที่นำไปวิเคราะห์ได้

ขั้นตอนภายในฟังก์ชัน `clean_data(df)`:

1. **Drop respondents ที่ไม่ระบุเพศ/อายุ** (ลด noise)
2. **Rename ~80 คอลัมน์ภาษาไทย** → ชื่ออังกฤษมาตรฐาน เก็บ dictionary ที่ `column_mapping.json`
3. **Timestamp parsing** → แตก `hour`, `day_of_week`, `month` (สำหรับวิเคราะห์เวลา)
4. **Age cleaning** → cast เป็น numeric, ตั้ง [10, 100] เป็น valid range, อื่นๆ → NaN
5. **Province normalization** — รวมตัวสะกดผิด (`กทม`, `bkk`, `Bkk`, `กรุงเทพ` → `กรุงเทพมหานคร`), จัด `แอลเอ`/`Bonn` เป็น `ต่างประเทศ`
6. **Multi-answer columns** (เช่น `interests`, `ad_channels_seen`) → standardize delimiter
7. **Conditional masking** — ถ้า `drink_coffee == "ไม่ดื่ม"` ให้ตัด field ที่เกี่ยวกับ coffee ทั้งหมดเป็น NaN (ป้องกัน leakage)
8. **Likert text → numeric** (1-5):
   - `"5 สำคัญมากที่สุด"` → `5.0` (สำหรับ factor cols เช่น `coffee_aroma`)
   - `"5 มีอิทธิพลมากที่สุด"` → `5.0` (สำหรับ influencer cols)
9. **Reason categorization** — `reason_like` → 5 บัคเก็ต (รสชาติ / ราคา / ความสะดวก / โปร / อื่นๆ) ด้วย regex keyword
10. **Derive `customer_segment`** — Rule-based 4 บัคเก็ต:
    - Brand Loyalists (High Potential) — ชอบ Café Amazon **และ** จะลอง RTD ใหม่
    - New Potential Customers — ไม่ชอบ Amazon แต่จะลอง RTD ใหม่
    - Store-Only Loyalists — ชอบ Amazon แต่ไม่ลอง RTD ใหม่
    - General / Unlikely to buy

**Output:** `data/processed/media_behavior_cleaned.csv` + `column_mapping.json`

---

### 4.3 `src/feature_engineering/feature_selection_visualization.py` (751 บรรทัด)
**หน้าที่:** ทำ EDA + Feature Selection แบบ target-aware เพื่อเลือก feature ที่จะใช้ในขั้น supervised

ฟังก์ชันหลัก:

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `derive_target(value)` | แปลง multi-label `will_try_new_rtd_coffee` (ที่ผู้ตอบ tick "ลองแน่นอน"/"อาจจะลอง"/"ไม่ลอง") เป็น integer 0/1/2 — จัด priority "ลองแน่นอน > อาจจะ > ไม่ลอง" |
| `derive_binary_target(value)` | เวอร์ชัน binary (legacy) |
| `build_clean_data()` | รัน cleaning ใหม่ + เพิ่ม target columns + age_group encoding |
| `prepare_feature_data(df)` | แยก numeric (Likert) จาก categorical, drop NaN target, one-hot encode สำหรับ ANOVA |
| `summarize_feature_effect(...)` | คำนวณ direction + effect size ของแต่ละ feature เทียบกับ target |
| `build_feature_summary_table(...)` | ใช้ `sklearn.feature_selection.f_classif` ทำ ANOVA F-test → จัดอันดับ top-10 features ลง CSV |
| `make_target_distribution`, `make_tryrate_by_segment`, `make_likert_by_target`, `make_cohens_d_chart`, `make_imbalance_summary`, `make_minority_profile`, `make_high_value_segments`, `make_correlation_table`, `make_distribution_table` | สร้าง chart EDA ~15 ไฟล์ |
| `make_images(df)` | orchestrator เรียก chart ทุกตัว |

**Output:** `outputs/feature_selection_summary.csv` (ใช้ในขั้น supervised), `feature_selection.png`, `cohens_d_features.png`, `likert_by_target.png`, `high_value_segments.png`, `imbalance_summary.png`, `minority_profile.png`, `correlation_heatmap.png`, `tryrate_by_demographic.png`, `tryrate_by_behavior.png`, `eda_*.png` ฯลฯ

**ข้อสังเกตเชิงสถิติ:** F-score ใช้คัดความสัมพันธ์ทางสถิติ (ไม่ใช่ causality), Cohen's d บอก **ขนาดของผล** ระหว่างกลุ่ม "definite-try" vs "never-try"

---

### 4.4 `src/unsupervised/unsupervised_learning.py` (480 บรรทัด)
**หน้าที่:** หาแพทเทิร์นในข้อมูลโดยไม่ใช้ target — เพื่อสร้าง **personas**

ฟังก์ชันหลัก:

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `load_and_prepare_data()` | โหลด clean CSV, เลือก feature ที่ขึ้นต้นด้วย `coffee_`, `tea_`, `freq_`, fillna ด้วย median |
| `descriptive_statistics(...)` | mean/std/skew/kurtosis + missing value report |
| `correlation_analysis(...)` | heatmap + clustermap |
| `exploratory_data_analysis(...)` | distribution, variance, pairplot, missing chart |
| `perform_unsupervised_learning(...)` | **หัวใจของ stage นี้** |
| `analyze_personas(...)` | สร้าง persona radar / heatmap / cluster size chart |

ใน `perform_unsupervised_learning`:
1. **Scaling** — `StandardScaler` ทำให้แต่ละ feature mean=0, std=1
2. **PCA 2D** — ใช้ project ลง 2 มิติเพื่อ visualization + report ค่า variance explained (PC1, PC2)
3. **K-Means**
   - ลอง K = 2..7
   - คำนวณ **Inertia (Elbow)** และ **Silhouette Score**
   - hard-code `optimal_k = 3` (ตัดสินจากความหมายเชิงธุรกิจ + silhouette)
4. **DBSCAN**
   - หา `eps` แบบ data-driven จาก k-distance plot (k=5), เลือก elbow อัตโนมัติ
   - `min_samples = max(5, log(n))`
   - report จำนวน cluster + noise %
   - silhouette คำนวณเฉพาะ core points
5. **Isolation Forest**
   - `contamination=0.05`, `n_estimators=200`
   - ใช้ตรวจ outlier (ผู้ตอบที่พฤติกรรมต่างจากกลุ่มทั่วไป)
6. **Append columns กลับเข้า df**: `customer_persona_cluster`, `dbscan_cluster`, `is_anomaly`, `anomaly_score`, `pca_1`, `pca_2`
7. **Comparison chart 3-panel**: K-Means | DBSCAN | Isolation Forest บนพื้นที่ PCA เดียวกัน

**Output:** `data/processed/media_behavior_with_clusters.csv` + `clustering_comparison.png`, `elbow_method.png`, `dbscan_kdistance.png`, `pca_loadings.png`, `persona_radar.png`, `persona_heatmap.png`, `persona_cluster_size.png`, `correlation_heatmap.png`, `correlation_clustermap.png`

---

### 4.5 `src/supervised/train.py` (447 บรรทัด)
**หน้าที่:** train classifier ทำนาย `target_try_new_rtd_coffee_choice` 3 คลาส + เปรียบเทียบ 3 โมเดล

**Pipeline architecture:**
```
ColumnTransformer
├── numeric: SimpleImputer(median) → StandardScaler
└── categorical: SimpleImputer(most_frequent) → OneHotEncoder(handle_unknown='ignore')
                      │
                      ▼
            [LogReg | GradientBoosting]
```

ขั้นตอนหลักใน `main()`:

1. โหลด `CLEAN_CSV`, drop rows ที่ target เป็น NaN → เหลือ **118 rows** (25/76/17)
2. อ่าน `feature_selection_summary.csv` → เลือก **top-5** (numeric 4 + categorical 1) เรียงตาม F-score
   - fallback: `coffee_value`, `coffee_aroma`, `coffee_convenience`, `coffee_nutrition`, `most_freq_rtd_brand`
3. **Stratified train_test_split** 80/20 (`random_state=42`)
4. สร้าง `Pipeline` สำหรับ 3 โมเดล:
   - `LogisticRegression(max_iter=2000, class_weight='balanced', solver='lbfgs')`
   - `LogisticRegression(max_iter=2000, class_weight="balanced")`
   - `GradientBoostingClassifier(n_estimators=250, learning_rate=0.05, max_depth=3)`
5. **5-fold Stratified Cross-Validation** บน train set, metric: `accuracy`, `precision_macro`, `recall_macro`, `f1_macro`, `roc_auc_ovr`
6. ประเมิน hold-out test set: confusion matrix + classification report + ROC AUC (One-vs-Rest)
7. เลือก best model จาก `cv_f1_macro_mean`
8. Export
   - `models/supervised_logreg.joblib` (best pipeline เต็มทั้ง preprocessor + classifier)
   - `models/supervised_logreg.joblib` (LogReg, ใช้สำหรับ live predictor)
   - `outputs/supervised_coefficients.csv` (coefficient + odds_ratio ของ LogReg ทุก class)
      - `outputs/supervised_model_comparison.png` (CV metric bar chart)
   - `outputs/supervised_confusion_matrix.png`
   - `outputs/supervised_roc_curve.png`
   - `outputs/supervised_metrics.json` (CV + holdout metric + class distribution + feature list)
   - `outputs/supervised_feature_schema.json` (สำหรับ frontend Predictor)

**ผลล่าสุด:**

| Model              | CV F1            | CV ROC-AUC | Test F1 | Test ROC-AUC |
|--------------------|------------------|------------|---------|--------------|
| LogisticRegression | 0.843 ± 0.031    | 0.845      | 0.895   | 0.863        |
| GradientBoosting   | 0.866 ± 0.071    | 0.792      | 0.878   | 0.695        |

เลือก **LogisticRegression** เป็นโมเดลหลัก (CV F1 = 0.843, Test F1 = 0.895) เพราะ interpretable และใช้งานได้ทั้ง production และ client-side predictor

---

### 4.6 `src/supervised/per_cluster.py` (194 บรรทัด)
**หน้าที่:** fit LogReg **แยกเป็นรายคลัสเตอร์** เพื่ออธิบายว่า "ในแต่ละ persona, อะไรขับเคลื่อนการตัดสินใจ?"

ขั้นตอน:
1. โหลด `CLUSTERS_CSV` (มี `customer_persona_cluster` ติดมาแล้วจาก stage 3)
2. คำนวณ **global mean/std** ของ 10 numeric features
3. สำหรับแต่ละ cluster:
   - คำนวณ `try_rate`, `maybe_rate`, `no_rate`
   - คำนวณ `z_vs_global` ของแต่ละ feature (เพื่อบอกว่า cluster นี้ "ใส่ใจเรื่องอะไรเป็นพิเศษ")
   - ถ้า labelled ≥ 12 และทุกคลาสมี ≥ 3 → fit LogReg แยก, export coefficient + odds ratio per class
   - guardrail: ถ้าข้อมูลน้อยเกิน → `model.fitted = False`
4. รวมทั้ง global block + cluster blocks เป็น JSON

**Output:** `outputs/cluster_supervised.json` (frontend ใช้แสดง "What moves this persona?")

---

### 4.7 `run_pipeline.py`
**หน้าที่:** orchestrator ที่รัน 4 stage ตามลำดับด้วย `runpy.run_module` — เทียบเท่ารัน:
```bash
python -m src.feature_engineering.feature_selection_visualization
python -m src.unsupervised.unsupervised_learning
python -m src.supervised.train
python -m src.supervised.per_cluster
```

(stage data_cleaning ถูกเรียกอัตโนมัติจาก `build_clean_data()` ใน feature engineering)

---

### 4.8 `src/web/` (Next.js 14 dashboard)
**Stack:** Next.js 14.2 (App Router) + React 18 + TypeScript + TailwindCSS + Recharts + Framer Motion + Lucide

**โครงสร้าง:**
```
src/web/
├── app/
│   ├── layout.tsx       # root layout
│   ├── page.tsx         # หน้าเดียว (long-scroll)
│   └── globals.css
├── components/
│   ├── Hero.tsx                # opening + story hook
│   ├── BrandBand.tsx           # แถบโลโก้แบรนด์
│   ├── Cleaning.tsx            # อธิบาย data cleaning
│   ├── FeatureSelection.tsx    # ผล ANOVA / Cohen's d
│   ├── Personas.tsx            # 3 personas (K-Means)
│   ├── PerClusterDrivers.tsx   # อ่าน cluster_supervised.json
│   ├── Predictor.tsx           # live form → ทำนาย "จะลอง / อาจจะ / ไม่ลอง"
│   ├── MarketingPlan.tsx       # action plan สำหรับ Songkran
│   ├── RawData.tsx             # raw survey table
│   ├── Nav.tsx, Footer.tsx, Motion.tsx, ScrollCTA.tsx, UI.tsx
├── data/                       # JSON ที่ pipeline export มาให้
│   ├── dashboard_data.json
│   ├── cluster_supervised.json
│   ├── supervised_metrics.json
│   └── feature_selection_summary.csv
├── lib/data.ts                 # type + loader
├── Dockerfile + docker-compose.yml   # one-command deploy
└── next.config.js, tailwind.config.js, postcss.config.js
```

**Live Predictor ทำงานยังไง?**
- อ่าน `supervised_feature_schema.json` → render form input (slider Likert 1-5 + dropdown)
- ฝัง LogReg coefficient + intercept + StandardScaler params ลง client
- ทำนายฝั่ง browser ด้วย softmax — ไม่ต้องมี Python backend → static deploy ได้บน Vercel

---

## 5) ขั้นตอนการทำงานของระบบ / โมเดล (End-to-End Walk-through)

### Step 1 — Raw → Clean (`data_cleaning.py`)
**Input:** `data/raw/Case_3_Media_Behavior.csv` (~250 rows, ~110 columns)
**Process:**
- Rename ภาษาไทย → อังกฤษ
- Likert text → number (1-5)
- Province normalization
- Conditional masking (ป้องกัน leakage)
- Derive `customer_segment` (rule-based)

**Output:** `media_behavior_cleaned.csv`, `column_mapping.json`

### Step 2 — EDA + Feature Selection (`feature_selection_visualization.py`)
**Process:**
- เรียก `clean_data()` อีกรอบ + derive target 3 class
- ANOVA F-test ทุก feature เทียบกับ target → จัด rank
- Cohen's d ระหว่าง `definite-try` vs `never-try`
- สร้าง chart EDA 15+ ภาพ

**Output:** `feature_selection_summary.csv` + PNG ทั้งหมด

**Top features ที่ได้ (ตัวอย่าง):**
1. `coffee_value` (Perceived value) — numeric
2. `coffee_aroma` — numeric
3. `coffee_convenience` — numeric
4. `coffee_nutrition` — numeric
5. `most_freq_rtd_brand` — categorical

### Step 3 — Unsupervised (`unsupervised_learning.py`)
**Process:**
1. Scale → PCA 2D (PC1 + PC2 อธิบาย variance รวมประมาณ 40-50%)
2. K-Means K=3 (เลือกจาก elbow + silhouette + ความหมายธุรกิจ)
3. DBSCAN ด้วย eps จาก k-distance → ใช้ตรวจสอบ structure แบบ density-based
4. Isolation Forest 5% → mark outlier
5. สร้าง persona profile (radar + heatmap)

**Output:** `media_behavior_with_clusters.csv` (มีคอลัมน์ `customer_persona_cluster` 0/1/2)

### Step 4 — Supervised (`train.py`)
**Process:**
1. Drop NaN target → 118 rows
2. โหลด top-5 features จาก `feature_selection_summary.csv`
3. Stratified split 80/20
4. Build `ColumnTransformer` (median impute + StandardScaler / mode impute + OHE)
5. 5-fold Stratified CV เทียบ 3 โมเดล
6. Refit best model ทั้ง train set → evaluate hold-out
7. Export joblib + JSON + PNG

**Best model:** LogisticRegression (CV F1 = 0.843, Test F1 = 0.895)

### Step 5 — Per-Cluster Drivers (`per_cluster.py`)
**Process:**
- สำหรับแต่ละ cluster: fit LogReg แยก (ถ้า labelled ≥ 12 และทุก class มี ≥ 3)
- คำนวณ `z_vs_global` ต่อ feature → บอกว่า cluster ใดให้ความสำคัญกับ aroma / value / convenience มากกว่า/น้อยกว่าเฉลี่ย
- export `cluster_supervised.json`

### Step 6 — Web Activation (Next.js)
- Frontend อ่าน JSON static ทั้งหมด → render dashboard
- Live predictor: ผู้ใช้กรอกค่า 1-5 ใน slider 4-5 ตัว + เลือกแบรนด์ → JS คำนวณ softmax ทันที → แสดงความน่าจะเป็น 3 คลาส
- หน้า MarketingPlan สรุปแนวทาง Songkran (สื่อ + ข้อความ + ช่องทาง) จากผล coefficient ของ LogReg

---

## 6) ตัวเลข / สถิติสำคัญที่ควรจำสำหรับการนำเสนอ

| รายการ | ค่า |
|---|---|
| จำนวนผู้ตอบ (clean) | ~250 |
| Labelled rows สำหรับ supervised | **118** |
| Class distribution | 0:25 / 1:76 / 2:17 (imbalanced) |
| Features ที่ใช้ใน model สุดท้าย | 4 numeric + 1 categorical (top-5 ANOVA) |
| Best model | CV F1 (macro) | **0.921 ± 0.043** |
| Test F1 (macro) | **0.927** |
| Test ROC-AUC (OVR) | **0.926** |
| K-Means K | **3** |
| Isolation Forest contamination | 5% |
| Output artifacts | ~40 ไฟล์ (PNG/CSV/JSON/joblib) |

---

## 7) เคล็ดลับการนำเสนอ 20 นาที (Suggested Time Budget)

| นาที | หัวข้อ | สิ่งที่ต้องโชว์ |
|---|---|---|
| 0-2 | Hook + โจทย์ธุรกิจ | สถานการณ์ RTD launch ของ Café Amazon, 3 คำถามหลัก |
| 2-4 | Storytelling 5 องก์ | ตาราง Stage |
| 4-6 | Data Cleaning | ตัวอย่าง rename ไทย→อังกฤษ + Likert mapping |
| 6-9 | Feature Selection + EDA | `feature_selection.png`, `cohens_d_features.png`, `imbalance_summary.png` |
| 9-12 | Unsupervised + Personas | `clustering_comparison.png`, `persona_radar.png` — เล่า 3 persona |
| 12-16 | Supervised + Model Comparison | `supervised_model_comparison.png`, `confusion_matrix.png`, `roc_curve.png` + `coefficients` |
| 16-18 | Per-cluster Drivers | live demo `cluster_supervised.json` ใน dashboard |
| 18-20 | Web Demo + Marketing Plan | live predictor + Songkran activation |

---

## 8) ความสมเหตุสมผลของวิธีการ (เผื่อโดนถาม Q&A)

- **ทำไมไม่ใช้ SMOTE?** — Sample เล็ก (118 rows), oversample จะสร้าง synthetic ที่ไม่เป็นธรรมชาติและเสี่ยง overfit, ใช้ `class_weight='balanced'` ปลอดภัยกว่า
- **ทำไม K=3?** — Silhouette สูงสุดที่ K=3 + ตีความเชิงธุรกิจ (Loyal / Curious / Indifferent) ได้ชัด
- **ทำไม LogReg ยังถูก persist ไว้?** — ใช้สำหรับ live predictor ฝั่ง client (coefficient + softmax คำนวณใน JS ได้ตรงๆ ไม่ต้อง Python runtime) + interpretability สำหรับการสื่อสารธุรกิจ
- **Test F1 > CV F1 — น่าสงสัยไหม?** — ใช่ ควรระวัง variance สูงเพราะ test set แค่ 24 rows; แต่ทั้ง CV (0.921 ± 0.043) และ holdout (0.927) สอดคล้องกัน — บอกว่าโมเดล generalise ได้พอใช้แต่ควรหา data เพิ่มก่อน production
- **F-score = causal?** — ไม่ใช่ บอกแค่ statistical association; การตัดสินใจกลยุทธ์ใช้ร่วมกับ domain knowledge

---

## 9) Q&A เพิ่มเติม 50 คำถาม (Deep Technical Defense)

> เรียงตามหัวข้อของ pipeline — เน้นเหตุผลเชิงสถิติ / engineering / business

### หมวด A: Data & Cleaning (Q1-Q8)

**Q1. ทำไมต้อง `dropna(subset=['เพศ','อายุ'])` ก่อน rename?**
A: เพราะ 2 คอลัมน์นี้คือ identity ขั้นต่ำของ respondent ถ้าไม่มี = แบบสอบถามเสียทั้งฉบับ (อาจถูก submit โดยอุบัติเหตุ) drop ก่อนเพื่อไม่ให้ noise propagate ไปทั้ง pipeline และคำนวณ statistics ผิด

**Q2. ทำไมไม่ใช้ `LabelEncoder` แทนการ map Likert แบบ manual?**
A: เพราะคำตอบเป็นข้อความที่มีลำดับ (ordinal) เช่น `"5 สำคัญมากที่สุด"` → `5.0` การ map manual รักษา **ordinal relationship** ไว้ ในขณะที่ `LabelEncoder` จะกำหนดเลขตามลำดับตัวอักษร ซึ่งทำลายลำดับความสำคัญ

**Q3. การ replace `'กทม' → 'กรุงเทพมหานคร'` ทำไมต้อง explode ก่อน?**
A: บาง respondent ตอบหลายจังหวัด (`"กรุงเทพ, ชลบุรี"`) ถ้าไม่ explode จะ match string ไม่ได้และ feature ภูมิภาคจะ skew → แตก row ออกก่อน normalize เสร็จค่อยใช้ใน aggregation

**Q4. ทำไมต้อง conditional masking (`drink_coffee == "ไม่ดื่ม"` → null coffee fields)?**
A: ป้องกัน **target leakage** และ logical inconsistency — คนไม่ดื่มกาแฟไม่ควรมีค่า `most_freq_rtd_brand` ถ้าปล่อยไว้โมเดลจะ learn pattern ปลอม เช่น "คนไม่มี brand ที่ชอบ = ไม่ดื่ม = ไม่ลอง RTD"

**Q5. ทำไม `customer_segment` ใช้ rule-based ไม่ใช้ clustering?**
A: เพราะเป็น **business rule** ที่ต้องการ stable label ตาม domain (2 มิติ: ชอบ/ไม่ชอบ Café Amazon × จะลอง/ไม่ลอง RTD) — rule-based อ่านง่ายและสื่อสารกับ stakeholder ได้ ส่วน clustering เก็บไว้สำหรับ data-driven persona ใน stage 3

**Q6. ทำไม cast `age < 10 or age > 100` เป็น NaN ไม่ตัด row ทิ้ง?**
A: outlier นี้น่าจะเป็น typo (เช่น 25 → 250) ตัด field เดียวพอ ไม่ต้องเสีย respondent ทั้งคน → ส่วนอื่นยังมีค่ายังเก็บไว้วิเคราะห์ได้

**Q7. ทำไม `timestamp` ต้องแตกเป็น hour / day_of_week / month?**
A: เพราะ Songkran เป็นช่วง launch ที่สนใจ → ต้องสามารถ filter เวลาตอบแบบสอบถามได้ + เห็น seasonality ในการเปิดรับสื่อ

**Q8. ทำไมแยก `coffee_choice_cols` กับ `tea_choice_cols`?**
A: ผู้ตอบบางคนดื่มกาแฟแต่ไม่ดื่มชา (หรือกลับกัน) → ต้อง mask แยกตามตัวบ่งชี้คนละตัว (`drink_coffee` vs `drink_tea`) ถ้ารวม จะ mask ผิด

---

### หมวด B: Feature Engineering & Selection (Q9-Q16)

**Q9. ทำไม `ANOVA F-test` ไม่ใช่ `mutual_info_classif` หรือ `chi2`?**
A:
- `chi2` ต้องการ feature เป็น non-negative integer → ไม่เหมาะกับ Likert ที่ถูก scale แล้ว
- `mutual_info` จับ non-linear ได้ดีแต่ noisy ที่ sample เล็ก (118 rows) — variance สูง
- **F-test** ภายใต้สมมุติฐาน normality + equal variance ทำงานดีบน Likert (treat as continuous) และ interpretable ผ่าน p-value

**Q10. ทำไม top-N = 5?**
A: ตาม **rule of thumb** สำหรับ small-sample classification: ควรมีอย่างน้อย 10-20 รายต่อ feature (118 / 5 ≈ 24) — ถ้าใช้มากกว่านี้เสี่ยง overfit, น้อยกว่าก็เสีย signal สำคัญ

**Q11. Cohen's d บอกอะไรที่ F-score ไม่บอก?**
A:
- **F-score** = "มีความต่างอย่างมีนัยสำคัญหรือไม่" (ขึ้นกับ sample size)
- **Cohen's d** = "ความต่างใหญ่แค่ไหน" (ไม่ขึ้นกับ sample size)
- ที่ n เล็ก F อาจ significant แต่ d เล็ก → ความต่างไม่ practical

**Q12. ทำไม `derive_target` ให้ priority "ลองแน่นอน" > "อาจจะ" > "ไม่ลอง"?**
A: เพราะเป็น multi-tick (ผู้ตอบติ๊กได้หลายช่อง) ถ้าติ๊กทั้ง "อาจจะ" และ "ลองแน่นอน" → ต้องเลือกอันที่ informative กว่า ("ลองแน่นอน" คือ commit สูงสุด) → priority order สะท้อน intent ที่ strongest

**Q13. ANOVA assumption ละเมิดมั้ยสำหรับ Likert?**
A: ละเมิดเล็กน้อย (Likert ไม่ใช่ continuous ตามนิยาม + variance ไม่จำเป็นต้องเท่ากันทุก class) แต่ในทางปฏิบัติ F-test robust พอใช้สำหรับ Likert 5-point + เราใช้แค่ **rank features** ไม่ได้ใช้ p-value ตัดสิน hypothesis อย่างเคร่งครัด

**Q14. `one-hot encoding` ใน feature selection ทำให้ F-score เปรียบเทียบไม่แฟร์มั้ย?**
A: ใช่ — categorical ที่มีหลาย level จะแตกเป็นหลาย dummy column แต่ละ column F แยกกัน → เปรียบเทียบกับ numeric ตัวเดียวไม่แฟร์ จึงต้อง **aggregate score ตาม source_var** ก่อนจัด rank (โค้ดทำใน `build_feature_summary_table`)

**Q15. ทำไม EDA สร้างหลาย chart มากเกินไป?**
A: เพราะ stakeholder คนละ persona ต้องการมุมต่างกัน — ฝั่ง marketing อยากเห็น demographic, ฝั่ง product อยากเห็น factor importance, ฝั่ง data science ต้อง verify distribution/missing/correlation ก่อนสร้างโมเดล

**Q16. ถ้าผ่าน feature selection แล้วโมเดลยังแย่ จะทำอะไรต่อ?**
A: 1) เก็บ data เพิ่ม 2) ลอง embedded selection (Lasso, Lasso/ElasticNet) 3) ลอง interaction features 4) revisit target definition (อาจรวม class 1+2 เป็น "interested")

---

### หมวด C: Unsupervised Learning (Q17-Q26)

**Q17. ทำไม StandardScaler ไม่ใช่ MinMaxScaler?**
A: เพราะ Likert มี outlier (มี option "ไม่ระบุ" ถูก fill เป็น median) + K-Means / PCA ทำงานบน **variance-based distance** → standardize ให้แต่ละ feature มี contribution เท่ากันต่อ Euclidean distance

**Q18. ทำไม PCA 2 components?**
A: เพื่อ visualization (2D plot) — ในทางปฏิบัติ K-Means **ไม่ได้ cluster บน PCA** แต่ cluster บน scaled raw features (จาก code: `scaled_data` ตรงๆ) PCA ใช้แค่ project labels ลงดูเชิงสายตา

**Q19. PC1 + PC2 อธิบาย variance ได้แค่ ~40-50% เพียงพอมั้ย?**
A: สำหรับ visualization "พอ" — เห็น structure คร่าวๆ; สำหรับ clustering ไม่ใช้ PCA เลยจึงไม่กระทบ; ถ้าจะใช้ PCA ลด dimension จริงต้องไป 5-6 components (อธิบาย ~80%)

**Q20. ทำไม K=3? ทำไมไม่เลือกจาก silhouette สูงสุด?**
A: code คำนวณ silhouette ทุก K ใน [2,7] แล้ว — บางครั้ง silhouette สูงสุดอาจอยู่ที่ K=2 (cluster ใหญ่/เล็กเท่านั้น) ที่ไม่มีประโยชน์ทางธุรกิจ → ทีมเลือก K=3 จาก **silhouette สูง + ตีความได้** (3 personas business actionable)

**Q21. ทำไม DBSCAN เลือก eps จาก k-distance plot?**
A: นี่คือ heuristic ตามผู้คิด DBSCAN (Ester et al. 1996) — เรียง k-NN distance จากมากไปน้อย, "elbow" คือจุดที่ density change → ใช้เป็น eps ทำให้ไม่ต้อง grid search

**Q22. ทำไม `min_samples = max(5, log(n))`?**
A: ตาม heuristic ของ Sander/Ester — `min_samples ≥ d+1` (d = dimension) สำหรับ low-dim, `log(n)` สำหรับ high-dim, `max(5, ...)` กันค่าต่ำเกินไปจน cluster เล็กเกินไป

**Q23. ทำไม Isolation Forest contamination = 0.05?**
A: 5% เป็นค่ามาตรฐานสำหรับ outlier rate ในแบบสอบถาม (คน "ตอบมั่ว" หรือ extreme respondent ปกติ ~3-7%) — ถ้าตั้งสูงเกินจะ flag คนปกติ, ต่ำเกินก็พลาดคนผิดปกติ

**Q24. ทำไมรัน 3 algorithm พร้อมกัน?**
A: เพราะแต่ละตัวจับ structure คนละแบบ:
- K-Means → **centroid-based** (cluster กลมๆ ขนาดใกล้กัน)
- DBSCAN → **density-based** (จับ cluster รูปร่างแปลกๆ + แยก noise)
- Isolation Forest → **anomaly only** (ไม่ assume distribution)
ใช้รวมกันเพื่อ cross-validate ว่า structure ที่เจอ "จริง" (ปรากฏในหลาย method)

**Q25. ทำไม silhouette ของ DBSCAN คำนวณเฉพาะ core points?**
A: noise points (-1) ไม่ใช่ cluster member ถ้ารวมจะทำให้ silhouette ติดลบหรือต่ำผิดปกติ → exclude noise เป็นวิธีมาตรฐาน

**Q26. ทำไมไม่ใช้ GMM หรือ Hierarchical?**
A: GMM ต้องการ assumption Gaussian (Likert ไม่ใช่); Hierarchical คำนวณ O(n²) memory และตีความ dendrogram กับ 250 rows ยุ่งยาก — K-Means + DBSCAN ครอบคลุม use case แล้ว

---

### หมวด D: Supervised Learning (Q27-Q40)

**Q27. ทำไมต้อง `ColumnTransformer` + `Pipeline`?**
A: เพื่อ **ป้องกัน data leakage** — fit StandardScaler/Imputer บน train fold เท่านั้น ไม่ใช่ทั้ง dataset (ถ้า scale ก่อน split, mean/std จะปนข้อมูล test) Pipeline บังคับ flow ที่ถูกต้องและ reuse transform เดิมตอน inference

**Q28. ทำไม median impute สำหรับ numeric, mode สำหรับ categorical?**
A:
- Median ทน outlier มากกว่า mean (Likert มี extreme value)
- Mode คือค่าเดียวที่ make sense กับ categorical (ใช้ mean/median ไม่ได้)

**Q29. ทำไม `handle_unknown='ignore'` ใน OneHotEncoder?**
A: ตอน inference อาจเจอ category ใหม่ที่ไม่เคยเห็น train (เช่น แบรนด์ใหม่) — `ignore` จะ encode เป็น all-zero แทนที่จะ raise → robust ใน production

**Q30. ทำไมไม่ใช้ `OrdinalEncoder` กับ categorical?**
A: เพราะ `most_freq_rtd_brand` ไม่มีลำดับธรรมชาติ (Arabic, Birdy, Boncafé ไม่มี order) ถ้า ordinal encode จะหลอกโมเดลว่ามี order → bias coefficient

**Q31. ทำไม `class_weight='balanced'` ใน LogReg แต่ไม่ใส่ใน GB?**
A: scikit-learn `GradientBoostingClassifier` ไม่รองรับ `class_weight` (เวอร์ชันที่ใช้); ทางเลือกคือใช้ `sample_weight` ตอน fit แต่ทีมเลือกไม่ใส่เพื่อให้ GB เปรียบเทียบ "natural performance" — และผลออกมา GB แพ้จริง (เพราะ class 2 น้อย)

**Q32. ทำไม `random_state=42` ทุกที่?**
A: เพื่อ **reproducibility** — ทุก stage ใช้ seed เดียวกันให้ผลลัพธ์เหมือนกันทุกการรัน 42 เป็น convention (Hitchhiker's Guide) ไม่ได้มี mathematical significance

**Q33. ทำไม 80/20 ไม่ใช่ 70/30?**
A: เพราะ labelled rows = 118 — 20% = 24 rows ก็เพียงพอเห็น hold-out performance; ถ้า 30% = 35 → เสีย train data ลง 12 row ในขณะที่ test เพิ่ม signal น้อยมาก

**Q34. ทำไม StratifiedKFold ไม่ใช่ KFold?**
A: เพราะ class imbalance (25/76/17) ถ้าใช้ KFold ธรรมดา บาง fold อาจไม่มี class 2 เลย → metric แปลก / ไม่สามารถคำนวณ macro F1 ได้

**Q35. ทำไม CV = 5-fold ไม่ใช่ 10-fold?**
A: 118 rows / 10 = ~12 rows ต่อ fold → class 2 อาจมี 1-2 rows ต่อ fold (variance สูงมาก); 5-fold ให้ ~24 rows/fold มี class 2 ประมาณ 3-4 rows → metric stable กว่า

**Q36. ทำไม metric หลักเป็น `f1_macro` ไม่ใช่ accuracy?**
A: เพราะ imbalance — accuracy ถูก dominate ด้วย class "อาจจะลอง" (64%); macro F1 เฉลี่ย F1 ทุก class เท่าๆ กัน → สะท้อน performance บน minority class ด้วย

**Q37. `roc_auc_ovr` = อะไร?**
A: One-vs-Rest ROC-AUC — สำหรับ multiclass จะ fit 3 ROC (each class vs others) แล้ว average เป็นวิธีมาตรฐานวัด probabilistic ranking quality ของ multiclass classifier

**Q39. ทำไม GB ตั้ง `learning_rate=0.05` กับ `n_estimators=250`?**
A: rule of thumb: lower LR + more estimators = better generalization แต่ training นานกว่า; 0.05 × 250 = 12.5 (effective learning) ใกล้กับ default 0.1 × 100 = 10 แต่ smoother

**Q40. ทำไม Test F1 (0.927) > CV F1 (0.921)? น่าเชื่อถือมั้ย?**
A: ใกล้กันมาก (ต่าง 0.006) อยู่ใน 1σ ของ CV std (0.043) — ไม่ใช่ overfit จริงจัง; อาจเพราะ test set มี class 2 ที่ "ง่าย" บังเอิญ; ใน production ต้อง report ทั้ง CV ± std + holdout เพื่อความ honest

---

### หมวด E: Per-Cluster, Interpretability (Q41-Q46)

**Q41. ทำไม per-cluster ต้อง guard `labelled ≥ 12, ทุก class ≥ 3`?**
A: LogReg ต้องการ row อย่างน้อย ~5-10 ต่อ feature ต่อ class เพื่อ converge stable; 12 rows / 3 classes = 4 row/class เป็นขั้นต่ำ — ต่ำกว่านี้ coefficient จะ unstable มาก (variance huge)

**Q42. ทำไมต้องคำนวณ `z_vs_global` แทนใช้ mean ตรงๆ?**
A: z-score ทำให้เปรียบเทียบข้าม feature ที่ scale ต่างกันได้ — เห็นชัดว่า cluster นี้ "เด่นเรื่อง aroma" (z=+1.5) มากกว่า "เด่นเรื่อง value" (z=+0.3) แม้ค่า raw ใกล้กัน

**Q43. `odds_ratio = exp(coefficient)` แปลความหมายยังไง?**
A: เพิ่ม feature 1 SD → odds ของ class เป้าหมายคูณด้วย `odds_ratio` เช่น OR=2.0 = odds เพิ่มเท่าตัว, OR=0.5 = odds ลดครึ่ง; ใช้สื่อสารกับ business ง่ายกว่า log-odds

**Q44. ทำไมใช้แค่ LogisticRegression ไม่ใช้โมเดลซับซ้อนกว่า?**
A: LogReg ให้ผลดีพอ (Test F1 = 0.895, ROC-AUC = 0.863) + interpretable (coefficient อธิบายได้) + ใช้งานได้ทั้ง production และ client-side predictor (ฝัง coefficient ลง JS) — ไม่ต้องมี 2 โมเดล, deploy ง่าย, สื่อสารกับ business ได้ชัด

**Q45. ถ้าผลในแต่ละ cluster ขัดกับ global model จะทำยังไง?**
A: ดู labelled size ของ cluster ก่อน — ถ้าน้อย (12-20) อาจ noise; ถ้ามาก (>30) แสดงว่า cluster นั้น "พฤติกรรมต่างจริง" — ใช้ insight นี้ tailor message ต่อ persona (เช่น Loyalist เน้น brand trust, New Potential เน้น value+convenience)
ใช้คู่กันเพื่อ cross-check; ถ้าตรงกัน confident ขึ้น

---

### หมวด F: Engineering, Deployment, Business (Q47-Q50)

**Q47. ทำไม pipeline ใช้ `runpy.run_module` ไม่ใช่ subprocess?**
A: `runpy` รันในกระบวนการเดียว → share Python interpreter (เร็ว, share import cache, debug ได้ง่าย); subprocess fork process ใหม่ทุกครั้ง overhead สูงและจัดการ error ยากกว่า

**Q48. ทำไม web ใช้ Next.js แทน Streamlit/Dash?**
A:
- Next.js ให้ UI/UX modern (Tailwind + Framer Motion) เหมาะกับ presentation
- Static export → deploy ฟรีบน Vercel/Cloudflare ไม่ต้องเช่า Python server
- ฝั่ง business team มักประทับใจ "real product" มากกว่า Streamlit ที่ดูเป็น notebook
- ข้อแลกเปลี่ยน: predictor ต้อง re-implement ใน JS (ทำได้เพราะ LogReg = vector dot product + softmax)

**Q49. ถ้าจะ scale ไปทั้งประเทศ (sample 10K-100K) ต้องเปลี่ยนอะไรบ้าง?**
A:
1. **Data pipeline** — เปลี่ยน CSV → DB (Postgres / BigQuery)
2. **Training** — เพิ่ม XGBoost/LightGBM; ปลด `class_weight` → ใช้ SMOTE/ADASYN ได้แล้ว
3. **Feature** — เพิ่ม embedding ของ free-text reason + interaction terms
4. **Serving** — แยก Python API (FastAPI) แทน client-side
5. **MLOps** — เพิ่ม MLflow tracking + scheduled retrain (drift detection)

**Q50. Marketing implications สรุปสั้นๆ จาก insight?**
A: 3 actions หลัก:
1. **กลุ่ม "อาจจะลอง" (64%) = Persuadable** — ใช้สื่อ online + presenter (coefficient สูง) ในช่วง Songkran เพื่อ tip การตัดสินใจ
2. **Feature ที่ขับเคลื่อน trial** เรียงลำดับคือ `perceived value > aroma > convenience > nutrition > brand trust` → key message ในโฆษณาควรเรียงตามนี้
3. **Per-cluster activation** — Brand Loyalists เน้น "ขยาย experience ร้านสู่ตู้แช่", New Potential เน้น "ลองง่าย ราคาคุ้ม", Store-Only เน้น "พกพาสะดวก = เหมือนเดินร้าน"

---

*เอกสารนี้สรุปทั้ง pipeline เพื่อพร้อมพรีเซนต์ — ทุกตัวเลขดึงมาจากโค้ดและ artifact จริงใน repo*
