"""
Inference script for Livestock Health Monitoring System.
Provides reproducible prediction routines, feature alignment, and clinical safety wrappers.
"""

import os
import json
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
SCHEMA_PATH = os.path.join(BASE_DIR, 'ml', 'feature_schema.json')


def load_model(species: str = None):
    """Load species-specific model if available, otherwise fallback to unified model."""
    if species:
        species_model = os.path.join(MODELS_DIR, f"{species.lower()}_disease_model.joblib")
        if os.path.exists(species_model):
            return joblib.load(species_model), f"{species.lower()}_v1.0.0"
            
    unified_model = os.path.join(MODELS_DIR, "livestock_disease_model.joblib")
    if os.path.exists(unified_model):
        return joblib.load(unified_model), "unified_v1.0.0"
        
    return None, None


def predict_disease_risk(input_features: dict) -> dict:
    """
    Execute model inference safely.
    Validates input features, aligns schema, and provides safety boundaries.
    """
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Feature schema not found at {SCHEMA_PATH}")

    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)

    species = input_features.get('species', 'Cow')
    model, model_ver = load_model(species)

    if model is None:
        return {
            'status': 'error',
            'message': 'No trained machine learning model found. Run ml/train_model.py first.',
            'predicted_class': 'Prediction Unavailable',
            'risk_level': 'Normal',
            'confidence': 0.0,
            'probabilities': {}
        }

    # Prepare single row DataFrame conforming to feature schema
    num_cols = schema['numerical_features']
    cat_cols = schema['categorical_features']
    all_cols = num_cols + cat_cols

    row_data = {}
    for col in all_cols:
        val = input_features.get(col)
        if val is None:
            # Set sensible defaults if missing
            if col in ('fever_flag', 'coughing_flag', 'nasal_discharge_flag', 'diarrhea_flag',
                        'lameness_flag', 'swelling_flag', 'skin_lesions_flag', 'bloat_distension_flag',
                        'abnormal_milk_flag'):
                row_data[col] = 0
            elif col == 'milk_production_drop_pct':
                row_data[col] = 0.0
            elif col == 'body_condition_score':
                row_data[col] = 3.0
            elif col in ('food_intake', 'water_intake', 'rumination', 'walking_activity'):
                row_data[col] = 'Normal'
            elif col == 'species':
                row_data[col] = species
            else:
                row_data[col] = 0.0
        else:
            row_data[col] = val

    df_input = pd.DataFrame([row_data])[all_cols]

    # Predict
    pred_class = model.predict(df_input)[0]
    
    # Probabilities
    probs = {}
    confidence = 0.0
    if hasattr(model, 'predict_proba'):
        try:
            proba_arr = model.predict_proba(df_input)[0]
            classes = model.classes_
            for cls_name, p in zip(classes, proba_arr):
                probs[cls_name] = round(float(p), 4)
            confidence = round(float(max(proba_arr)) * 100, 1)
        except Exception:
            pass

    risk_mapping = schema.get('risk_mapping', {})
    risk_level = risk_mapping.get(pred_class, 'Moderate')

    return {
        'status': 'success',
        'predicted_class': pred_class,
        'risk_level': risk_level,
        'confidence': confidence,
        'probabilities': probs,
        'model_version': model_ver
    }


if __name__ == '__main__':
    # Simple test run
    test_sample = {
        'species': 'Cow',
        'age_months': 36,
        'weight_kg': 480.0,
        'temperature_c': 40.2,
        'heart_rate_bpm': 88.0,
        'respiratory_rate_bpm': 36.0,
        'food_intake': 'Reduced',
        'water_intake': 'Normal',
        'rumination': 'Reduced',
        'walking_activity': 'Normal',
        'milk_production_drop_pct': 45.0,
        'body_condition_score': 3.2,
        'fever_flag': 1,
        'coughing_flag': 0,
        'nasal_discharge_flag': 0,
        'diarrhea_flag': 0,
        'lameness_flag': 0,
        'swelling_flag': 1,
        'skin_lesions_flag': 0,
        'bloat_distension_flag': 0,
        'abnormal_milk_flag': 1
    }
    res = predict_disease_risk(test_sample)
    print("Test inference result:")
    print(json.dumps(res, indent=2))
