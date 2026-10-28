# Datasets Directory: Livestock Health Monitoring

This directory contains reference datasets and documentation for training and evaluating livestock disease risk estimation models.

---

## 1. Dataset Policy

In accordance with responsible machine learning engineering and animal health privacy:

1. **Synthetic Demonstration Data:** The dataset included in `datasets/sample/livestock_disease_dataset.csv` is a reproducible, synthetic reference dataset generated according to verified physiological parameters published by the **Food and Agriculture Organization (FAO)** and the **Merck Veterinary Manual**.
2. **No Proprietary Farmer PII:** No private commercial farm records or confidential livestock registry identifiers are tracked or committed.
3. **Reproducibility:** The sample dataset can be regenerated at any time using `python ml/train_model.py` with reproducible random seeds.

---

## 2. Incorporating Field Clinical Data

To train models on empirical clinical trial or veterinary clinic data:

1. Replace or supplement `livestock_disease_dataset.csv` ensuring columns strictly adhere to `ml/feature_schema.json`.
2. Ensure records represent authorized de-identified veterinary case histories.
3. Re-run `python ml/train_model.py` to produce updated model weights in `models/`.
