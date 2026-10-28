from app.services.validation_service import ValidationService
from app.services.health_observation_service import HealthObservationService
from app.models.notification import Notification
from app.extensions import db_session


def test_validation_service_normal_vitals():
    evals = ValidationService.validate_vital_signs(
        species="Cow",
        temperature=38.6,
        heart_rate=65,
        respiratory_rate=28
    )
    assert evals['is_critical'] is False
    assert evals['is_abnormal'] is False
    assert len(evals['warnings']) == 0


def test_validation_service_critical_temperature():
    evals = ValidationService.validate_vital_signs(
        species="Cow",
        temperature=41.2,  # Severe fever above 40.5
        heart_rate=70,
        respiratory_rate=30
    )
    assert evals['is_critical'] is True
    assert evals['temperature_status'] == 'Critical'
    assert any("Critical temperature alert" in w for w in evals['warnings'])


def test_record_observation_updates_animal_status(auth_users, test_farm_and_animal):
    farmer = auth_users['farmer1']
    animal = test_farm_and_animal['animal']

    assert animal.health_status == "Normal"

    # Record observation with high fever and coughing
    obs = HealthObservationService.record_observation(
        animal_id=animal.id,
        recorded_by_user_id=farmer.id,
        temperature_c=40.2,
        heart_rate_bpm=88.0,
        respiratory_rate_bpm=38.0,
        food_intake="Reduced",
        rumination="Reduced",
        symptoms_list=["Coughing", "Fever or elevated temperature"]
    )

    assert obs.id is not None
    assert animal.health_status in ("Attention Required", "Monitoring Required")


def test_urgent_symptoms_trigger_immediate_urgency(auth_users, test_farm_and_animal):
    farmer = auth_users['farmer1']
    animal = test_farm_and_animal['animal']

    obs = HealthObservationService.record_observation(
        animal_id=animal.id,
        recorded_by_user_id=farmer.id,
        temperature_c=38.6,
        food_intake="Anorexic",
        symptoms_list=["Recumbent / Unable to Stand", "Acute Bloat / Severe Abdominal Distension"]
    )

    assert animal.health_status == "Urgent Veterinary Attention"

    # Notification should be generated for the farm owner
    notif = db_session.query(Notification).filter_by(animal_id=animal.id, priority="Urgent").first()
    assert notif is not None
    assert "Urgent" in notif.title or "Critical" in notif.title
