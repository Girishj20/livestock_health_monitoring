from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db_session
from app.models.animal import Animal
from app.models.veterinary import VeterinaryVisit, Medication
from app.services.animal_service import AnimalService
from app.services.veterinary_record_service import VeterinaryRecordService
from app.utils.security import login_required, get_current_user, validate_csrf, verify_animal_access
from app.utils.helpers import log_audit

veterinary_bp = Blueprint('veterinary', __name__)


@veterinary_bp.route('/veterinary')
@login_required
def index():
    user = get_current_user()
    animals = AnimalService.get_animals(user)
    animal_ids = [a.id for a in animals]

    visits = []
    medications = []
    if animal_ids:
        visits = db_session.query(VeterinaryVisit)\
            .filter(VeterinaryVisit.animal_id.in_(animal_ids))\
            .order_by(VeterinaryVisit.visit_date.desc()).limit(50).all()

        medications = db_session.query(Medication)\
            .filter(Medication.animal_id.in_(animal_ids))\
            .order_by(Medication.created_at.desc()).limit(50).all()

    return render_template('veterinary/index.html', visits=visits, medications=medications, animals=animals)


@veterinary_bp.route('/veterinary/record/<int:animal_id>', methods=['GET', 'POST'])
@login_required
def record(animal_id):
    user = get_current_user()
    if not verify_animal_access(user, animal_id, required_level='edit'):
        flash("Unauthorized animal access.", "danger")
        return redirect(url_for('veterinary.index'))

    animal = AnimalService.get_animal(animal_id)
    if not animal:
        flash("Animal not found.", "danger")
        return redirect(url_for('veterinary.index'))

    if request.method == 'POST':
        validate_csrf()
        reason = request.form.get('reason', '').strip()
        vet_name = request.form.get('vet_name', '').strip()
        clinical_findings = request.form.get('clinical_findings', '').strip()
        veterinarian_diagnosis = request.form.get('veterinarian_diagnosis', '').strip()
        treatment_notes = request.form.get('treatment_notes', '').strip()
        follow_up_str = request.form.get('follow_up_date')

        if not reason:
            flash("Reason for consultation is required.", "danger")
            return render_template('veterinary/record.html', animal=animal)

        follow_up_date = None
        if follow_up_str:
            try:
                follow_up_date = datetime.strptime(follow_up_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        visit = VeterinaryRecordService.record_visit(
            animal_id=animal.id,
            reason=reason,
            veterinarian_id=user.id if user.is_veterinarian else None,
            vet_name=vet_name or (f"Dr. {user.full_name}" if user.is_veterinarian else None),
            clinical_findings=clinical_findings,
            veterinarian_diagnosis=veterinarian_diagnosis,
            treatment_notes=treatment_notes,
            follow_up_date=follow_up_date
        )

        # Handle optional medication attached directly in the form
        med_name = request.form.get('medication_name', '').strip()
        med_dosage = request.form.get('dosage_instructions', '').strip()
        if med_name and med_dosage:
            VeterinaryRecordService.add_medication(
                animal_id=animal.id,
                medication_name=med_name,
                dosage_instructions=med_dosage,
                start_date=visit.visit_date.date(),
                visit_id=visit.id,
                prescribing_vet=visit.attending_doctor
            )

        log_audit(actor=user, action='RECORD_VET_VISIT', entity_type='VeterinaryVisit', entity_id=visit.id, details=f"Diagnosis: {veterinarian_diagnosis}")
        flash(f"Veterinary consultation record saved for {animal.animal_tag}.", "success")
        return redirect(url_for('animals.detail', id=animal.id))

    return render_template('veterinary/record.html', animal=animal)


@veterinary_bp.route('/veterinary/visit/<int:id>')
@login_required
def detail(id):
    user = get_current_user()
    visit = db_session.get(VeterinaryVisit, id)
    if not visit:
        flash("Record not found.", "danger")
        return redirect(url_for('veterinary.index'))

    if not verify_animal_access(user, visit.animal_id, required_level='view'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('veterinary.index'))

    return render_template('veterinary/detail.html', visit=visit, animal=visit.animal)
