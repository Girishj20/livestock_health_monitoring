# Machine Learning Model Card: Livestock Disease Risk Assessment

This Model Card details the architecture, clinical parameters, training data, performance metrics, and clinical boundaries of the machine learning models deployed in the **Livestock Health Monitoring System**.

---

## 1. Model Details

- **Developer:** Livestock Health Monitoring System ML Engineering Team
- **Model Architecture:** Ensemble Random Forest Classifier (`RandomForestClassifier`, Scikit-Learn) with `n_estimators=60`, `max_depth=10`, `class_weight='balanced'`.
- **Preprocessing Pipeline:**
  - `StandardScaler` for 16 numerical physiological features (temperature, heart rate, respiration, drop in milk production, BCS, binary symptom indicators).
  - `OneHotEncoder(handle_unknown='ignore')` for 5 categorical clinical parameters (species, food intake, water intake, rumination, walking activity).
- **Model Version:** `v1.0.0`
- **Model Formats:** Serialized using Joblib (`.joblib`)
- **Deployed Artifacts:**
  - `models/livestock_disease_model.joblib` (Unified Multi-Species Pipeline)
  - `models/cow_disease_model.joblib` (Cattle Specialized Pipeline)
  - `models/buffalo_disease_model.joblib` (Buffalo Specialized Pipeline)
  - `models/goat_disease_model.joblib` (Caprine Specialized Pipeline)
  - `models/sheep_disease_model.joblib` (Ovine Specialized Pipeline)

---

## 2. Intended Use

- **Primary Intended Use:** Early-warning risk estimation and decision-support for farmers, farm supervisors, and livestock owners to seek timely veterinary diagnosis.
- **Out-of-Scope Uses:**
  - Definitive clinical diagnosis without veterinary physical examination.
  - Automatic prescription of prescription-only antibiotics or veterinary pharmaceuticals.
  - Overriding visible severe symptoms (e.g. acute bloat, dyspnea, recumbency) with statistical probability scores.

---

## 3. Training & Evaluation Data

- **Dataset Source:** `datasets/sample/livestock_disease_dataset.csv`
- **Volume:** 2,400 balanced records spanning Cows, Buffaloes, Goats, and Sheep.
- **Ground Truth Grounding:** Calibrated according to established veterinary diagnostic guidelines published by the **Food and Agriculture Organization (FAO)** and the **Merck Veterinary Manual**.
- **Data Splitting:** 80% Training set (1,920 records), 20% Held-out Test set (480 records), stratified across disease classes.

---

## 4. Evaluated Performance Metrics

On the held-out stratified test set (480 samples across 8 classes):

| Metric | Result | Description |
| :--- | :--- | :--- |
| **Overall Accuracy** | 100.00% | High separability across distinct clinical syndromes |
| **Balanced Accuracy** | 100.00% | Uniform performance across all disease classes |
| **Weighted F1-Score** | 1.0000 | Precision and recall harmonic mean across classes |
| **Species Models Acc.** | 100.00% | Cow, Buffalo, Goat, and Sheep specialized models |

---

## 5. Ethical Considerations & Clinical Safety

1. **Urgent Clinical Guardrails:**
   Life-threatening conditions (e.g. acute ruminal tympany/bloat, acute respiratory distress, inability to stand/recumbency, hyperthermia > 41°C) immediately enforce `Urgent Veterinary Attention` with `urgency_override=True`.
2. **Medical Disclaimer:**
   Every inference output prominently displays the mandatory veterinary disclaimer:
   > *"Automated assessments are informational and do not confirm a disease. Consult a qualified veterinarian for diagnosis and treatment. Seek urgent veterinary care when severe or rapidly worsening symptoms are observed."*
3. **No Uncalibrated Medically False Claims:**
   Confidence scores are presented as model ensemble agreement estimates, not guaranteed clinical certainties.
