from app.services.prediction_service import PredictionService
from app.models.disease_assessment import DiseaseAssessment
from app.extensions import db_session


def test_prediction_execution_and_snapshot(auth_users, test_farm_and_animal):
    farmer = auth_users['farmer1']
    animal = test_farm_and_animal['animal']

    obs_data = {
        'temperature_c': 39.8,
        'heart_rate_bpm': 85.0,
        'respiratory_rate_bpm': 32.0,
        'food_intake': 'Reduced',
        'rumination': 'Reduced',
        'walking_activity': 'Normal',
        'milk_production_drop_pct': 40.0,
        'body_condition_score': 3.2,
        'symptoms': ['Swelling / Udder heat', 'Fever or elevated temperature']
    }

    result = PredictionService.run_assessment(
        animal_id=animal.id,
        user_id=farmer.id,
        observation_dict=obs_data
    )

    assert result['assessment_id'] is not None
    assert result['predicted_class'] != "Prediction Unavailable"
    assert result['risk_level'] in ("Moderate", "High", "Critical")
    assert result['disclaimer'] is not None
    assert len(result['recommended_steps']) > 0

    # Verify database persistence
    asst = db_session.get(DiseaseAssessment, result['assessment_id'])
    assert asst is not None
    assert asst.animal_id == animal.id
    assert asst.model_version is not None
    assert len(asst.input_snapshot) > 10


def test_prediction_emergency_override_on_acute_symptoms(auth_users, test_farm_and_animal):
    farmer = auth_users['farmer1']
    animal = test_farm_and_animal['animal']

    obs_data = {
        'temperature_c': 38.6,
        'food_intake': 'Normal',
        'symptoms': ['Acute Bloat / Severe Abdominal Distension', 'Severe Respiratory Distress']
    }

    result = PredictionService.run_assessment(
        animal_id=animal.id,
        user_id=farmer.id,
        observation_dict=obs_data
    )

    assert result['urgency_override'] is True
    assert result['risk_level'] == 'Critical'
