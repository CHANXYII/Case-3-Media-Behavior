# 01 | Case 3: Media Behavior x RTD Coffee Launch
## จากร้านกาแฟ 4,000+ สาขา สู่ชั้นวางในร้านสะดวกซื้อ

- เป้าหมายของโปรเจกต์คือหาว่าใครคือกลุ่มที่ควรสื่อสาร, ควรขายด้วย message แบบไหน, และควรเทงบไปที่ไหนสำหรับการเปิดตัว RTD coffee
- ข้อมูลอ้างอิงจาก survey 181 คน และผลลัพธ์ล่าสุดใน `outputs/` กับ `src/web/data/`
- Pipeline ครอบคลุม `Data Cleaning -> Feature Selection -> Unsupervised -> Supervised -> Web Dashboard`

---

# 02 | Executive Summary

- จากผู้ตอบ 181 คน เราแยกได้ 3 persona ที่ใช้งานได้จริง: `P0 สายกาแฟตัวจริง`, `P1 สายไม่กาแฟ`, `P2 สายพรีเมียม`
- สัญญาณลบแรงสุดของการลอง RTD คือ `ไม่มีแบรนด์ RTD ประจำ`; สัญญาณบวกที่ชัดคือ `ความคุ้มค่า` และ `กลิ่น`
- โมเดล global ที่เหมาะสุดคือ `Logistic Regression` เพราะอธิบายได้ และให้ `CV F1 macro = 0.616`, `Holdout ROC-AUC = 0.805`
- ข้อเสนอเชิงธุรกิจคือเทงบหลักไปที่ `P0`, ใช้ story พรีเมียมกับ `P2`, และไม่ควรลงงบกาแฟหนักกับ `P1`

---

# 03 | Business Problem

- แบรนด์กาแฟที่มีหน้าร้านมากกว่า 4,000 สาขากำลังขยายจาก `on-premise` ไปสู่ตลาด `RTD` ในร้านสะดวกซื้อ
- การตัดสินใจที่หน้าตู้แช่เกิดในไม่กี่วินาที จึงต้องชนะด้วย message ที่คมกว่าเดิมมาก
- ช่วง `Songkran` เป็น launch window สำคัญ แต่ถ้าสื่อสารผิดกลุ่มจะเผางบเร็วมาก
- คำถามหลักไม่ใช่แค่ “คนชอบไหม” แต่คือ “ใครมีโอกาสลองจริง และต้องกระตุ้นด้วยอะไร”

---

# 04 | Business Questions

- ใครคือกลุ่มที่มีแนวโน้ม `ลองแน่นอน`, `อาจจะลอง`, และ `ไม่ลอง`
- คุณสมบัติสินค้าอะไรเป็นตัวผลักการตัดสินใจ: `value`, `aroma`, `convenience`, `premium`, หรือ `brand trust`
- พฤติกรรมสื่อและบริบทเทศกาลบอกอะไรเกี่ยวกับช่องทาง launch ที่ควรใช้
- เราจะเปลี่ยน insight ให้กลายเป็นเครื่องมือที่ใช้งานจริงได้อย่างไร ไม่ใช่จบแค่กราฟ

---

# 05 | Data Overview

- Source data คือ `data/raw/Case_3_Media_Behavior.csv` จากแบบสอบถามภาษาไทย
- หลังเตรียมข้อมูล ได้ผู้ตอบที่ใช้วิเคราะห์ได้ `181 คน`
- หลัง cleaning และ feature engineering มีคอลัมน์ที่ใช้งานได้ `120 ฟีเจอร์`
- แถวที่มี target พร้อมใช้สำหรับ supervised มี `118 คน`
- ตัวแปรครอบคลุม `demographic`, `media behavior`, `coffee/tea preference`, และ `RTD familiarity`

---

# 06 | Data Explore: Demographics

- กลุ่มตัวอย่างเป็น `ผู้หญิง 125/181 = 69%` และ `ผู้ชาย 54/181 = 30%`
- ช่วงอายุหลักคือ `30-39 ปี = 71 คน (39%)` รองลงมาคือ `23-29 ปี = 47 คน (26%)`
- อาชีพหลักคือ `พนักงานบริษัทเอกชน 120 คน (66%)`
- ภาพรวมจึงใกล้กับกลุ่ม `urban working adults` ซึ่งสอดคล้องกับสินค้า RTD ที่ต้องซื้อเร็ว หยิบง่าย ดื่มง่าย
- Visual: `outputs/demographic_gender.png`, `outputs/demographic_age.png`, `outputs/demographic_occupation.png`

---

# 07 | Data Explore: Early Behavioral Signals

- คุณสมบัติสินค้าที่ได้คะแนนเฉลี่ยสูงคือ `fresh-brew taste = 4.08`, `aroma = 4.05`, `convenience = 3.94`, `smoothness = 3.92`
- อิทธิพลจาก `friends/family = 4.10` สูงกว่า `celebrity = 1.79` ชัดเจน
- Insight แรกคือ RTD ขายด้วย `ประสบการณ์การดื่ม + ความคุ้มค่า + social proof` มากกว่าการใช้ celeb อย่างเดียว
- ถ้าจะสื่อสารช่วง launch ควรขาย “กลิ่น, รส, ดื่มง่าย, คุ้มราคา” มากกว่า message เชิงภาพลักษณ์ลอยๆ
- Visual: `outputs/distribution_analysis.png`, `outputs/likert_by_target.png`, `outputs/high_value_segments.png`

---

# 08 | System Diagram

```text
data/raw/Case_3_Media_Behavior.csv
  -> Data Cleaning
  -> media_behavior_cleaned.csv + column_mapping.json
  -> Feature Selection + EDA
  -> Unsupervised Clustering
  -> Global Supervised Model
  -> Per-cluster Drivers
  -> Next.js Web Dashboard
```

- ทุก stage เขียน artifact ของตัวเองให้ stage ถัดไปอ่านต่อได้
- Frontend อ่าน `JSON/CSV` แบบ static จึงไม่ต้องพึ่ง Python backend ตอน deploy

---

# 09 | Data Cleaning

- เปลี่ยนชื่อคอลัมน์ไทยเป็นอังกฤษเพื่อให้ query และ train model ได้ง่ายขึ้น
- normalize จังหวัด, parse timestamp, และจัดรูปแบบคำตอบหลายตัวเลือกให้สม่ำเสมอ
- แปลง Likert text เป็นตัวเลข `1-5` เพื่อให้ใช้กับสถิติและโมเดลได้
- mask คำตอบที่ขัดกันเชิงตรรกะเพื่อลด noise และลดโอกาส target leakage
- สร้าง `customer_segment` และบันทึก dictionary ชื่อคอลัมน์ไว้ใน `data/processed/column_mapping.json`
- Reference: `src/data_cleaning/data_cleaning.py`

---

# 10 | Data Cleaning Output and Target Design

| Target class | Count | Share |
|---|---:|---:|
| ไม่ลอง | 25 | 21.2% |
| อาจจะลอง | 76 | 64.4% |
| ลองแน่นอน | 17 | 14.4% | 

- เราเก็บ target เป็น `3 classes` เพราะ `อาจจะลอง` มีความหมายเชิงธุรกิจต่างจาก `ไม่ลอง`
- ข้อมูลมี imbalance ชัด จึงใช้ `class_weight="balanced"` แทนการ oversample
- Metric หลักของ supervised จึงต้องดู `macro F1` มากกว่า accuracy
- Visual: `outputs/target_distribution.png`, `outputs/imbalance_summary.png`

---

# 11 | Feature Selection Method

- ใช้ `ANOVA F-test` เทียบทุกฟีเจอร์กับ target 3 คลาส
- สำหรับ categorical จะ one-hot ก่อน แล้วค่อย dedupe กลับเป็น source variable เดิม
- เก็บเฉพาะฟีเจอร์ที่ `p <= 0.05` เพื่อลด noise และลด overfit
- จากฟีเจอร์ที่ significant ทั้งหมด เราเลือก top source variables เพื่อส่งต่อเข้า global supervised model
- Visual: `outputs/feature_selection.png`, `outputs/cohens_d_features.png`

---

# 12 | Feature Selection Results

| Feature | F-score | Business meaning |
|---|---:|---|
| No regular RTD coffee brand | 15.61 | ตัวลบแรงสุดของการลองแน่นอน |
| Perceived value | 7.87 | คนที่มองว่าคุ้มค่ามีโอกาสลองสูงขึ้น |
| Aroma preference | 6.81 | กลิ่นเป็นสัญญาณคุณภาพสำคัญ |
| RTD tea brand = Orishi Gold | 6.77 | สายพร้อมดื่มเดิมมีแนวโน้มลองมากกว่า |
| Daily online usage = 1-2 hr/day | 6.64 | segment ย่อยที่แยกจากกลุ่มอาจจะลองได้ชัด |

- สรุปง่ายๆ คือ `brand familiarity`, `value`, และ `aroma` เป็นแกนหลักของการตัดสินใจ
- ฟีเจอร์ที่ significant มีมากกว่า 5 ตัว แต่ global model เลือกใช้เฉพาะตัวที่แรงสุดเพื่อคุมความเสี่ยง overfit จาก sample size ที่เล็ก

---

# 13 | Unsupervised Approach

- เป้าหมายของ unsupervised คือแบ่งลูกค้าโดยไม่ใช้ target เพื่อหากลุ่มที่ data “จับเอง”
- ใช้ฟีเจอร์ด้านความชอบกาแฟ/ชาและพฤติกรรมรวม `19 ตัว` แล้วทำ `StandardScaler`
- ใช้ `PCA` เพื่อฉายภาพลง 2 มิติสำหรับการมอง pattern แต่ไม่ได้ใช้ PCA ในการ cluster จริง
- เลือก `K-Means` เป็นตัวหลัก และใช้ `DBSCAN` กับ `Isolation Forest` เป็นตัวช่วยดู density กับ anomaly
- Visual: `outputs/elbow_method.png`, `outputs/dbscan_kdistance.png`, `outputs/clustering_comparison.png`

---

# 14 | Unsupervised Results

- K-Means เลือกที่ `K = 3` โดยดูจาก elbow, silhouette, และความหมายเชิงธุรกิจ
- ค่า `silhouette = 0.30` และ PCA อธิบายได้ `PC1 = 31.4%`, `PC2 = 12.8%`
- ขนาดแต่ละกลุ่มคือ `126`, `10`, และ `45` คน หรือประมาณ `70%`, `6%`, `25%`
- โครงสร้างที่ได้แปลเป็นแผนการตลาดได้จริง ไม่ได้จบแค่ cluster id
- Visual: `outputs/customer_clusters_pca.png`, `outputs/persona_cluster_size.png`

---

# 15 | Persona Translation

| Persona | Size | Key traits | Try rate |
|---|---:|---|---:|
| P0 สายกาแฟตัวจริง | 126 | กลิ่น 4.21, รสใกล้กาแฟสด 4.36, intensity 3.93 | 15.3% |
| P1 สายไม่กาแฟ | 10 | คะแนนเกือบทุกมิติต่ำกว่า 2 | 10.0% |
| P2 สายพรีเมียม | 45 | premium 4.61, brand trust 4.47, packaging 4.53 | 13.9% |

- `P0` คือกลุ่ม mass target ที่ใกล้เคียง RTD coffee launch มากที่สุด
- `P1` ไม่ใช่กลุ่มเป้าหมายของ coffee RTD และควรเก็บไว้เป็น watchlist หรือ tea/wellness opportunity
- `P2` ไม่ได้ใหญ่ที่สุด แต่สำคัญเพราะยอมตอบสนองต่อ premium cue และ story ของแบรนด์
- Visual: `outputs/persona_radar.png`, `outputs/persona_heatmap.png`

---

# 16 | Supervised Design: Global Prediction Model

- เป้าหมายของ global supervised คือทำนายว่า respondent จะอยู่ในคลาส `ไม่ลอง / อาจจะลอง / ลองแน่นอน`
- ฟีเจอร์ที่ใช้จริงใน global model มี 5 ตัว: `coffee_value`, `coffee_aroma`, `most_freq_rtd_brand`, `most_freq_rtd_tea_brand`, `dur_online`
- Preprocessing คือ `impute -> scale numeric -> one-hot categorical -> classifier`
- เปรียบเทียบ `Logistic Regression` กับ `Gradient Boosting`
- ประเมินด้วย `5-fold stratified CV` และ `20% stratified holdout`

---

# 17 | Supervised Results: Global Model Performance

| Model | CV F1 macro | CV ROC-AUC | Holdout F1 macro | Holdout ROC-AUC |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.616 | 0.797 | 0.459 | 0.805 |
| Gradient Boosting | 0.604 | 0.785 | 0.322 | 0.758 |

- `Logistic Regression` ชนะด้วย `CV F1 macro` และยังอธิบาย coefficient ได้ตรงกับ business use case
- ถึง `Gradient Boosting` จะมี holdout accuracy สูงกว่าเล็กน้อย แต่แยกคลาส `ลองแน่นอน` ได้แย่กว่า
- Insight สำคัญคือโมเดลนี้เหมาะกับ `prioritization` และ `what-if analysis` มากกว่าการ auto-approve แบบ production เต็มรูปแบบ
- Visual: `outputs/supervised_model_comparison.png`, `outputs/supervised_confusion_matrix.png`, `outputs/supervised_roc_curve.png`

---

# 18 | Supervised Results: Per-Persona Drivers

- Global model ตอบว่า `ใครน่าจะลอง`; per-cluster model ตอบว่า `แต่ละ persona ถูกขับด้วยอะไร`
- `P0` ถ้าจะดันไปสู่ `ลองแน่นอน` ตัวขับแรงสุดคือ `Nutrition +0.55` และ `Aroma +0.54`
- `P2` ถ้าจะดันไปสู่ `ลองแน่นอน` ตัวขับแรงสุดคือ `Aroma +0.75`, `Value +0.63`, `Packaging +0.36`
- `P1` ยังไม่ฟิตโมเดลแยก เพราะมีแค่ `n = 10` และคนที่ตอบ `ลองแน่นอน` เพียง 1 คน
- ข้อสรุปคือ message เดียวใช้กับทุก persona ไม่ได้
- Reference: `outputs/cluster_supervised.json`, `src/web/components/PerClusterDrivers.tsx`

---

# 19 | Web Dashboard

- Frontend สร้างด้วย `Next.js 14 + Tailwind + Recharts` และอ่าน `JSON/CSV` แบบ static
- Dashboard มีครบทั้ง `Cleaning story`, `Feature selection`, `Personas`, `Per-cluster drivers`, `Predictor`, และ `Marketing plan`
- Live predictor คำนวณบน client จาก coefficient ที่ export มาแล้ว จึง demo ได้โดยไม่ต้องมี backend model server
- Artifact หลักที่หน้าเว็บใช้คือ `dashboard_data.json`, `cluster_supervised.json`, `supervised_metrics.json`
- Demo path: `src/web/components/*`, deploy ได้ด้วย Docker จาก `src/web/README.docker.md`

---

# 20 | Recommendations and Next Steps

- ลงงบเปิดตัวกาแฟ RTD แบบ `60% -> P0`, `30% -> P2`, `10% -> P1/watchlist` ตาม logic ที่ทีมทำไว้ใน dashboard
- Message กลางของ launch ควรขาย `กลิ่น`, `ความคุ้มค่า`, และ `ประสบการณ์เหมือนกาแฟสด`; สำหรับ `P2` ให้เพิ่ม `packaging + trusted brand story`
- Activation ช่วงสงกรานต์ควรใช้ `OOH ใกล้ร้านสะดวกซื้อ + short-form video + sampling` มากกว่า celebrity-led campaign
- ระยะถัดไปควรเก็บข้อมูลเพิ่ม โดยเฉพาะคลาส `ลองแน่นอน` เพื่อยกระดับ model จาก decision support ไปสู่ production scoring
- Closing line: โปรเจกต์นี้ไม่ได้จบที่ insight แต่ไปถึง dashboard ที่หยิบไปใช้คุยกับ business และ demo ได้ทันที
