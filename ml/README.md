# Machine Learning Module: Livestock Disease Risk Assessment

This directory contains the machine learning pipelines, feature definitions, training routines, and evaluation procedures for the **Livestock Health Monitoring System**.

---

## 1. Clinical & Architectural Philosophy

Automated assessments are **decision-support and early-warning estimates**, not clinical diagnoses. The system adheres to strict veterinary safety guidelines:

1. **Urgent Clinical Overrides:** When an animal exhibits life-threatening symptoms (e.g., severe dyspnea, acute ruminal tympany/bloat, recumbency, convulsions, severe hemorrhage), the system flags **Urgent Veterinary Attention** immediately, overriding any statistical model output.
2. **Species-Specific Parameterization:** Physiological baselines differ significantly between bovine (Cows, Buffaloes) and small ruminants (Goats, Sheep). Preprocessing and model selection explicitly preserve these boundaries.
3. **Calibrated Probabilities:** Confidence outputs are derived from ensemble class probabilities and explicitly marked as model estimates rather than definitive medical certainty.

---

## 2. Supported Species and Conditions

### Supported Species
- **Cow (Cattle)**
- **Buffalo**
- **Goat**
- **Sheep**

### Target Classes & Risk Tiers
| Condition | Clinical Category | Assigned Risk Tier |
| :--- | :--- | :--- |
| **Healthy / Normal** | Physiological Baseline | Normal |
| **Mastitis** | Udder Inflammation (Bacterial) | Moderate |
| **Foot & Mouth Disease (FMD)** | Contagious Aphthous Fever (Viral) | High |
| **Bovine Respiratory Disease (BRD) / Pneumonia** | Bronchopneumonia (Multifactorial) | High |
| **Lumpy Skin Disease (LSD)** | Capripoxvirus Dermatopathy | High |
| **Bloat (Ruminal Tympanites)** | Acute Ruminal Distension | Critical |
| **Enterotoxemia / GI Infection** | Clostridial / Enteric Disorder | High |
| **Parasitic Gastroenteritis** | Nematode / Helminth Infestation | Moderate |

---

## 3. Feature Schema

- **Numerical Features (16):**
  - `age_months`: Age in completed months.
  - `weight_kg`: Animal weight in kilograms.
  - `temperature_c`: Rectal temperature (°C).
  - `heart_rate_bpm`: Heart rate (beats per minute).
  - `respiratory_rate_bpm`: Respiratory rate (breaths per minute).
  - `milk_production_drop_pct`: Percentage drop in daily milk yield (0-100%).
  - `body_condition_score`: Standard BCS from 1.0 (emaciated) to 5.0 (obese).
  - Binary symptom indicator flags (`fever_flag`, `coughing_flag`, `nasal_discharge_flag`, `diarrhea_flag`, `lameness_flag`, `swelling_flag`, `skin_lesions_flag`, `bloat_distension_flag`, `abnormal_milk_flag`).

- **Categorical Features (5):**
  - `species`: `['Cow', 'Buffalo', 'Goat', 'Sheep']`
  - `food_intake`: `['Normal', 'Reduced', 'Anorexic', 'Increased']`
  - `water_intake`: `['Normal', 'Reduced', 'Excessive', 'None']`
  - `rumination`: `['Normal', 'Reduced', 'Absent', 'N/A']`
  - `walking_activity`: `['Normal', 'Sluggish', 'Lame', 'Staggering', 'Recumbent']`

---

## 4. How to Train and Evaluate Models

To train the models and generate evaluation metrics:

```powershell
python ml/train_model.py
```

To view comprehensive performance diagnostics (confusion matrix, precision, recall, balanced accuracy):

```powershell
python ml/evaluate_model.py
```

To run a standalone sample inference check:

```powershell
python ml/predict.py
```
