from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, jsonify
from app.extensions import db_session
from app.models.animal import Animal
from app.models.health_observation import HealthObservation
from app.models.disease_assessment import DiseaseAssessment
from app.models.veterinary import VeterinaryVisit
from app.models.vaccination import Vaccination
from app.models.notification import Notification
from app.utils.security import login_required, get_current_user
from app.services.animal_service import AnimalService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def root():
    user = get_current_user()
    if user:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('dashboard.landing'))


@dashboard_bp.route('/landing')
def landing():
    return render_template('dashboard/landing.html')


@dashboard_bp.route('/dashboard')
@login_required
def index():
    user = get_current_user()
    animals = AnimalService.get_animals(user)

    total_animals = len(animals)
    cow_count = sum(1 for a in animals if a.species == 'Cow')
    buffalo_count = sum(1 for a in animals if a.species == 'Buffalo')
    goat_count = sum(1 for a in animals if a.species == 'Goat')
    sheep_count = sum(1 for a in animals if a.species == 'Sheep')

    # Status counts
    normal_count = sum(1 for a in animals if a.health_status == 'Normal')
    monitoring_count = sum(1 for a in animals if a.health_status == 'Monitoring Required')
    attention_count = sum(1 for a in animals if a.health_status == 'Attention Required')
    urgent_count = sum(1 for a in animals if a.health_status == 'Urgent Veterinary Attention')
    unknown_count = sum(1 for a in animals if a.health_status == 'Prediction Unavailable')

    # Animals needing attention
    attention_animals = [a for a in animals if a.health_status in ('Attention Required', 'Urgent Veterinary Attention')]

    # Recent observations
    animal_ids = [a.id for a in animals]
    recent_observations = []
    recent_assessments = []
    upcoming_vaccinations = []
    upcoming_visits = []

    if animal_ids:
        recent_observations = db_session.query(HealthObservation)\
            .filter(HealthObservation.animal_id.in_(animal_ids))\
            .order_by(HealthObservation.observed_at.desc()).limit(6).all()

        recent_assessments = db_session.query(DiseaseAssessment)\
            .filter(DiseaseAssessment.animal_id.in_(animal_ids))\
            .order_by(DiseaseAssessment.created_at.desc()).limit(6).all()

        today = date.today()
        upcoming_vaccinations = db_session.query(Vaccination)\
            .filter(Vaccination.animal_id.in_(animal_ids))\
            .filter(Vaccination.next_due_date != None)\
            .filter(Vaccination.next_due_date >= today)\
            .order_by(Vaccination.next_due_date.asc()).limit(5).all()

        upcoming_visits = db_session.query(VeterinaryVisit)\
            .filter(VeterinaryVisit.animal_id.in_(animal_ids))\
            .filter(VeterinaryVisit.follow_up_date != None)\
            .filter(VeterinaryVisit.follow_up_date >= today)\
            .order_by(VeterinaryVisit.follow_up_date.asc()).limit(5).all()

    # Chart data
    species_chart_data = {
        'labels': ['Cattle (Cow)', 'Buffalo', 'Goat', 'Sheep'],
        'values': [cow_count, buffalo_count, goat_count, sheep_count]
    }

    health_chart_data = {
        'labels': ['Normal', 'Monitoring Required', 'Attention Required', 'Urgent Vet Care'],
        'values': [normal_count, monitoring_count, attention_count, urgent_count]
    }

    return render_template(
        'dashboard/index.html',
        total_animals=total_animals,
        cow_count=cow_count,
        buffalo_count=buffalo_count,
        goat_count=goat_count,
        sheep_count=sheep_count,
        normal_count=normal_count,
        monitoring_count=monitoring_count,
        attention_count=attention_count,
        urgent_count=urgent_count,
        unknown_count=unknown_count,
        attention_animals=attention_animals,
        recent_observations=recent_observations,
        recent_assessments=recent_assessments,
        upcoming_vaccinations=upcoming_vaccinations,
        upcoming_visits=upcoming_visits,
        species_chart_data=species_chart_data,
        health_chart_data=health_chart_data
    )
