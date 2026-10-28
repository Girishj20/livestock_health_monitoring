import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db_session
from app.models.animal import Animal
from app.models.disease_assessment import DiseaseAssessment
from app.services.animal_service import AnimalService
from app.services.prediction_service import PredictionService
from app.services.validation_service import KNOWN_SYMPTOMS
from app.utils.security import login_required, get_current_user, validate_csrf, verify_animal_access
from app.utils.helpers import log_audit

predictions_bp = Blueprint('predictions', __name__)


@predictions_bp.route('/predictions/workspace')
@login_required
def workspace():
    user = get_current_user()
    animals = AnimalService.get_animals(user)

    animal_id = request.args.get('animal_id')
    selected_animal = None
    latest_obs = None

    if animal_id:
        try:
            target_id = int(animal_id)
            if verify_animal_access(user, target_id, required_level='view'):
                selected_animal = db_session.get(Animal, target_id)
                if selected_animal:
                    latest_obs = selected_animal.latest_observation
        except (ValueError, TypeError):
            pass

    return render_template(
        'predictions/workspace.html',
        animals=animals,
        selected_animal=selected_animal,
        latest_obs=latest_obs,
        known_symptoms=KNOWN_SYMPTOMS
    )


@predictions_bp.route('/predictions/run', methods=['POST'])
@login_required
def run():
    validate_csrf()
    user = get_current_user()

    animal_id = request.form.get('animal_id')
    if not animal_id:
        flash("Please select an animal for assessment.", "danger")
        return redirect(url_for('predictions.workspace'))

    try:
        target_id = int(animal_id)
    except ValueError:
        flash("Invalid animal ID.", "danger")
        return redirect(url_for('predictions.workspace'))

    if not verify_animal_access(user, target_id, required_level='view'):
        flash("Unauthorized animal access.", "danger")
        return redirect(url_for('predictions.workspace'))

    symptoms = request.form.getlist('symptoms')
    other_symptom = request.form.get('other_symptom', '').strip()
    if other_symptom:
        symptoms.append(other_symptom)

    obs_dict = {
        'temperature_c': request.form.get('temperature_c'),
        'heart_rate_bpm': request.form.get('heart_rate_bpm'),
        'respiratory_rate_bpm': request.form.get('respiratory_rate_bpm'),
        'weight_kg': request.form.get('weight_kg'),
        'food_intake': request.form.get('food_intake', 'Normal'),
        'water_intake': request.form.get('water_intake', 'Normal'),
        'walking_activity': request.form.get('walking_activity', 'Normal'),
        'rumination': request.form.get('rumination', 'Normal'),
        'milk_production_drop_pct': request.form.get('milk_production_drop_pct', 0.0),
        'body_condition_score': request.form.get('body_condition_score', 3.0),
        'symptoms': symptoms
    }

    try:
        result = PredictionService.run_assessment(target_id, user.id, obs_dict)
        log_audit(actor=user, action='RUN_PREDICTION', entity_type='DiseaseAssessment', entity_id=result['assessment_id'], details=f"Predicted: {result['predicted_class']}")
        flash(f"Risk assessment completed: {result['predicted_class']} ({result['risk_level']} Risk)", "info")
        return redirect(url_for('predictions.detail', id=result['assessment_id']))
    except Exception as e:
        flash(f"Assessment error: {str(e)}", "danger")
        return redirect(url_for('predictions.workspace', animal_id=target_id))


@predictions_bp.route('/predictions/<int:id>')
@login_required
def detail(id):
    user = get_current_user()
    assessment = db_session.get(DiseaseAssessment, id)
    if not assessment:
        flash("Assessment record not found.", "danger")
        return redirect(url_for('dashboard.index'))

    if not verify_animal_access(user, assessment.animal_id, required_level='view'):
        flash("Access unauthorized.", "danger")
        return redirect(url_for('dashboard.index'))

    # Retrieve recommended steps for class
    from app.services.prediction_service import RECOMMENDED_ACTIONS
    recommended_steps = RECOMMENDED_ACTIONS.get(assessment.predicted_class, [
        "Monitor animal closely and consult a qualified veterinary doctor.",
        "Record vital signs twice daily."
    ])

    return render_template(
        'predictions/detail.html',
        assessment=assessment,
        animal=assessment.animal,
        recommended_steps=recommended_steps
    )


@predictions_bp.route('/predictions/history')
@login_required
def history():
    user = get_current_user()
    animals = AnimalService.get_animals(user)
    animal_ids = [a.id for a in animals]

    assessments = []
    if animal_ids:
        assessments = db_session.query(DiseaseAssessment)\
            .filter(DiseaseAssessment.animal_id.in_(animal_ids))\
            .order_by(DiseaseAssessment.created_at.desc()).limit(100).all()

    return render_template('predictions/history.html', assessments=assessments)
