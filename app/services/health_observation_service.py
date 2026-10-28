import json
from datetime import datetime
from app.extensions import db_session
from app.models.animal import Animal
from app.models.health_observation import HealthObservation
from app.services.validation_service import ValidationService
from app.services.animal_service import AnimalService
from app.services.notification_service import NotificationService


class HealthObservationService:
    """Handles recording, validation, alerting, and trend analysis for health observations."""

    @staticmethod
    def record_observation(animal_id: int, recorded_by_user_id: int,
                           temperature_c=None, heart_rate_bpm=None,
                           respiratory_rate_bpm=None, weight_kg=None,
                           food_intake='Normal', water_intake='Normal',
                           walking_activity='Normal', grazing_activity='Normal',
                           rumination='Normal', resting_behavior='Normal',
                           milk_production=None, body_condition_score=None,
                           symptoms_list=None, additional_notes=None,
                           data_source='manual', observed_at=None) -> HealthObservation:
        """Create, validate, and store a new clinical observation."""
        animal = db_session.get(Animal, animal_id)
        if not animal:
            raise ValueError(f"Animal #{animal_id} not found.")

        if observed_at is None:
            observed_at = datetime.utcnow()

        if symptoms_list is None:
            symptoms_list = []

        # Validate vitals
        validation = ValidationService.validate_vital_signs(
            animal.species,
            temperature=temperature_c,
            heart_rate=heart_rate_bpm,
            respiratory_rate=respiratory_rate_bpm
        )

        obs = HealthObservation(
            animal_id=animal_id,
            recorded_by=recorded_by_user_id,
            observed_at=observed_at,
            temperature_c=float(temperature_c) if temperature_c not in (None, '') else None,
            heart_rate_bpm=float(heart_rate_bpm) if heart_rate_bpm not in (None, '') else None,
            respiratory_rate_bpm=float(respiratory_rate_bpm) if respiratory_rate_bpm not in (None, '') else None,
            weight_kg=float(weight_kg) if weight_kg not in (None, '') else animal.weight_kg,
            food_intake=food_intake or 'Normal',
            water_intake=water_intake or 'Normal',
            walking_activity=walking_activity or 'Normal',
            grazing_activity=grazing_activity or 'Normal',
            rumination=rumination or 'Normal',
            resting_behavior=resting_behavior or 'Normal',
            milk_production=float(milk_production) if milk_production not in (None, '') else None,
            body_condition_score=float(body_condition_score) if body_condition_score not in (None, '') else None,
            symptoms=json.dumps(symptoms_list),
            additional_notes=additional_notes,
            data_source=data_source,
            created_at=datetime.utcnow()
        )
        db_session.add(obs)

        # Update animal weight if provided
        if weight_kg not in (None, ''):
            animal.weight_kg = float(weight_kg)

        db_session.commit()

        # Update animal overall status
        new_status = AnimalService.refresh_animal_health_status(animal_id)

        # Alert farm stakeholders if critical or urgent
        if validation['is_critical'] or new_status == 'Urgent Veterinary Attention':
            alert_title = f"Urgent Health Warning: {animal.species} [{animal.animal_tag}]"
            alert_msg = f"Critical indicators observed on {observed_at.strftime('%Y-%m-%d %H:%M')}: " + "; ".join(validation['warnings'] + symptoms_list)
            NotificationService.notify_farm_stakeholders(
                farm_id=animal.farm_id,
                title=alert_title,
                message=alert_msg,
                priority='Urgent',
                notification_type='Vital Warning',
                animal_id=animal.id,
                link_url=f"/animals/{animal.id}"
            )
        elif validation['is_abnormal'] or new_status in ('Attention Required', 'Monitoring Required'):
            alert_title = f"Health Alert: {animal.species} [{animal.animal_tag}]"
            alert_msg = f"Abnormal status [{new_status}]: " + "; ".join(validation['warnings'] + symptoms_list)
            NotificationService.notify_farm_stakeholders(
                farm_id=animal.farm_id,
                title=alert_title,
                message=alert_msg,
                priority='High',
                notification_type='Vital Warning',
                animal_id=animal.id,
                link_url=f"/animals/{animal.id}"
            )

        return obs

    @staticmethod
    def get_vital_trends(animal_id: int, limit=15) -> dict:
        """Extract chronological data points for Chart.js vitals graph."""
        observations = db_session.query(HealthObservation)\
            .filter_by(animal_id=animal_id)\
            .order_by(HealthObservation.observed_at.asc())\
            .limit(limit).all()

        dates = []
        temperatures = []
        heart_rates = []
        respiratory_rates = []

        for o in observations:
            dates.append(o.observed_at.strftime('%m/%d %H:%M'))
            temperatures.append(o.temperature_c if o.temperature_c is not None else None)
            heart_rates.append(o.heart_rate_bpm if o.heart_rate_bpm is not None else None)
            respiratory_rates.append(o.respiratory_rate_bpm if o.respiratory_rate_bpm is not None else None)

        return {
            'labels': dates,
            'temperatures': temperatures,
            'heart_rates': heart_rates,
            'respiratory_rates': respiratory_rates
        }
