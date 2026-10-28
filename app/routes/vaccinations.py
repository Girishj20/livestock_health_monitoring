from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db_session
from app.models.animal import Animal
from app.models.vaccination import Vaccination
from app.services.animal_service import AnimalService
from app.services.vaccination_service import VaccinationService
from app.utils.security import login_required, get_current_user, validate_csrf, verify_animal_access
from app.utils.helpers import log_audit

vaccinations_bp = Blueprint('vaccinations', __name__)


@vaccinations_bp.route('/vaccinations')
@login_required
def index():
    user = get_current_user()
    animals = AnimalService.get_animals(user)
    animal_ids = [a.id for a in animals]

    all_vaccinations = []
    if animal_ids:
        all_vaccinations = db_session.query(Vaccination)\
            .filter(Vaccination.animal_id.in_(animal_ids))\
            .order_by(Vaccination.vaccination_date.desc()).all()

    # Partition by status
    upcoming = [v for v in all_vaccinations if v.computed_status in ('Upcoming', 'Due Today', 'Overdue')]
    completed = [v for v in all_vaccinations if v.status == 'Completed']

    return render_template(
        'vaccinations/index.html',
        upcoming=upcoming,
        completed=completed,
        animals=animals
    )


@vaccinations_bp.route('/vaccinations/record', methods=['GET', 'POST'])
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
        vaccine_name = request.form.get('vaccine_name', '').strip()
        vac_date_str = request.form.get('vaccination_date')
        next_due_str = request.form.get('next_due_date')
        admin_by = request.form.get('administered_by', '').strip()
        batch_ref = request.form.get('batch_reference', '').strip()
        status = request.form.get('status', 'Completed')
        notes = request.form.get('notes', '').strip()

        if not target_animal_id or not vaccine_name or not vac_date_str:
            flash("Animal, Vaccine Name, and Vaccination Date are required.", "danger")
            return render_template('vaccinations/record.html', animals=animals, selected_animal=selected_animal)

        try:
            target_id = int(target_animal_id)
        except ValueError:
            flash("Invalid animal ID.", "danger")
            return redirect(url_for('vaccinations.record'))

        if not verify_animal_access(user, target_id, required_level='edit'):
            flash("Unauthorized animal access.", "danger")
            return redirect(url_for('vaccinations.index'))

        vac_date = datetime.strptime(vac_date_str, '%Y-%m-%d').date()
        next_due = None
        if next_due_str:
            try:
                next_due = datetime.strptime(next_due_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        vacc = VaccinationService.record_vaccination(
            animal_id=target_id,
            vaccine_name=vaccine_name,
            vaccination_date=vac_date,
            next_due_date=next_due,
            administered_by=admin_by or user.full_name,
            batch_reference=batch_ref,
            status=status,
            notes=notes
        )

        log_audit(actor=user, action='RECORD_VACCINATION', entity_type='Vaccination', entity_id=vacc.id, details=f"Vaccine: {vaccine_name}")
        flash(f"Vaccination record for {vaccine_name} saved successfully.", "success")
        return redirect(url_for('vaccinations.index'))

    return render_template('vaccinations/record.html', animals=animals, selected_animal=selected_animal)


@vaccinations_bp.route('/vaccinations/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    validate_csrf()
    user = get_current_user()
    vacc = db_session.get(Vaccination, id)
    if not vacc:
        flash("Record not found.", "danger")
        return redirect(url_for('vaccinations.index'))

    if not verify_animal_access(user, vacc.animal_id, required_level='edit'):
        flash("Unauthorized action.", "danger")
        return redirect(url_for('vaccinations.index'))

    new_status = request.form.get('status', 'Completed')
    if new_status in ('Completed', 'Cancelled', 'Upcoming'):
        vacc.status = new_status
        db_session.commit()
        log_audit(actor=user, action='UPDATE_VACCINE_STATUS', entity_type='Vaccination', entity_id=vacc.id, details=f"Status: {new_status}")
        flash("Vaccination status updated.", "info")

    return redirect(url_for('vaccinations.index'))
