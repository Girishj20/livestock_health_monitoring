from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db_session
from app.models.animal import Animal
from app.services.animal_service import AnimalService
from app.services.health_observation_service import HealthObservationService
from app.services.validation_service import KNOWN_SYMPTOMS, ValidationService
from app.utils.security import login_required, get_current_user, validate_csrf, verify_animal_access
from app.utils.helpers import log_audit

observations_bp = Blueprint('observations', __name__)


@observations_bp.route('/observations/record', methods=['GET', 'POST'])
@login_required
def record():
    user = get_current_user()
    animals = AnimalService.get_animals(user)

    animal_id = request.args.get('animal_id')
    selected_animal = None
    if animal_id:
        try:
            selected_animal = db_session.get(Animal, int(animal_id))
        except (ValueError, TypeError):
            pass

    if request.method == 'POST':
        validate_csrf()
        target_animal_id = request.form.get('animal_id')
        if not target_animal_id:
            flash("Please select an animal.", "danger")
            return render_template('observations/record.html', animals=animals, known_symptoms=KNOWN_SYMPTOMS)

        try:
            target_id = int(target_animal_id)
        except ValueError:
            flash("Invalid animal ID.", "danger")
            return redirect(url_for('observations.record'))

        if not verify_animal_access(user, target_id, required_level='edit'):
            flash("You do not have permission to record observations for this animal.", "danger")
            return redirect(url_for('animals.index'))

        animal = db_session.get(Animal, target_id)
        observed_at_str = request.form.get('observed_at')
        observed_at = datetime.utcnow()
        if observed_at_str:
            try:
                observed_at = datetime.strptime(observed_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        temp = request.form.get('temperature_c')
        hr = request.form.get('heart_rate_bpm')
        rr = request.form.get('respiratory_rate_bpm')
        weight = request.form.get('weight_kg')
        food = request.form.get('food_intake', 'Normal')
        water = request.form.get('water_intake', 'Normal')
        walking = request.form.get('walking_activity', 'Normal')
        grazing = request.form.get('grazing_activity', 'Normal')
        rumination = request.form.get('rumination', 'Normal')
        resting = request.form.get('resting_behavior', 'Normal')
        milk = request.form.get('milk_production')
        bcs = request.form.get('body_condition_score')
        symptoms = request.form.getlist('symptoms')
        other_symptom = request.form.get('other_symptom', '').strip()
        if other_symptom:
            symptoms.append(other_symptom)

        notes = request.form.get('additional_notes', '').strip()
        data_source = request.form.get('data_source', 'manual')

        try:
            obs = HealthObservationService.record_observation(
                animal_id=animal.id,
                recorded_by_user_id=user.id,
                temperature_c=temp,
                heart_rate_bpm=hr,
                respiratory_rate_bpm=rr,
                weight_kg=weight,
                food_intake=food,
                water_intake=water,
                walking_activity=walking,
                grazing_activity=grazing,
                rumination=rumination,
                resting_behavior=resting,
                milk_production=milk,
                body_condition_score=bcs,
                symptoms_list=symptoms,
                additional_notes=notes,
                data_source=data_source,
                observed_at=observed_at
            )

            log_audit(actor=user, action='RECORD_HEALTH_OBSERVATION', entity_type='HealthObservation', entity_id=obs.id, details=f"Animal: {animal.animal_tag}")
            flash(f"Health observation successfully recorded for {animal.animal_tag}!", "success")
            return redirect(url_for('animals.detail', id=animal.id))
        except Exception as e:
            flash(f"Error saving observation: {str(e)}", "danger")

    # Species reference ranges for the form's helper tooltips
    ranges = ValidationService.get_species_ranges(selected_animal.species if selected_animal else 'Cow')

    return render_template(
        'observations/record.html',
        animals=animals,
        selected_animal=selected_animal,
        known_symptoms=KNOWN_SYMPTOMS,
        reference_ranges=ranges
    )


@observations_bp.route('/api/observations/vitals/<int:id>')
@login_required
def api_vitals(id):
    user = get_current_user()
    if not verify_animal_access(user, id, required_level='view'):
        return jsonify({'error': 'Unauthorized'}), 403

    trends = HealthObservationService.get_vital_trends(id)
    return jsonify(trends)
