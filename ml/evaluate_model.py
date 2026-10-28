"""
Model evaluation script for Livestock Health Monitoring System.
Evaluates saved model pipelines against test sets and outputs detailed diagnostic reports.
"""

import os
import json
import pandas as pd
import joblib
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, balanced_accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'datasets', 'sample', 'livestock_disease_dataset.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
SCHEMA_PATH = os.path.join(BASE_DIR, 'ml', 'feature_schema.json')


def run_evaluation():
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found. Please run ml/train_model.py first.")
        return

    model_path = os.path.join(MODELS_DIR, 'livestock_disease_model.joblib')
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Run training first.")
        return

    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    num_cols = schema['numerical_features']
    cat_cols = schema['categorical_features']
    target_col = schema['target_column']

    df = pd.read_csv(DATASET_PATH)
    X = df[num_cols + cat_cols]
    y = df[target_col]

    model = joblib.load(model_path)
    y_pred = model.predict(X)

    acc = accuracy_score(y, y_pred)
    b_acc = balanced_accuracy_score(y, y_pred)
    cm = confusion_matrix(y, y_pred, labels=schema['classes'])
    report = classification_report(y, y_pred, labels=schema['classes'])

    print("=" * 60)
    print("LIVESTOCK HEALTH MONITORING - MODEL EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Overall Accuracy:          {acc * 100:.2f}%")
    print(f"Balanced Accuracy:         {b_acc * 100:.2f}%")
    print("\nDetailed Per-Class Performance:")
    print("-" * 60)
    print(report)
    print("\nConfusion Matrix:")
    print("-" * 60)
    print(cm)
    print("=" * 60)


if __name__ == '__main__':
    run_evaluation()
