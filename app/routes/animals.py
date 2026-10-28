import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.extensions import db_session
from app.models.animal import Animal
from app.models.farm import Farm
from app.services.animal_service import AnimalService
from app.utils.security import login_required, get_current_user, validate_csrf, verify_animal_access, verify_farm_access
from app.utils.helpers import save_uploaded_image, log_audit

animals_bp = Blueprint('animals', __name__)


@animals_bp.route('/animals')
@login_required
def index():
    user = get_current_user()
    search = request.args.get('search', '').strip()
    species = request.args.get('species', 'All')
    status = request.args.get('status', 'All')
    health_status = request.args.get('health_status', 'All')
    farm_id = request.args.get('farm_id')

    if farm_id:
        try:
            farm_id = int(farm_id)
        except ValueError:
            farm_id = None

    animals = AnimalService.get_animals(
        user,
        search_query=search,
        species=species,
        status=status,
        health_status=health_status,
        farm_id=farm_id
    )

    # User farms for filter dropdown
    farms = user.owned_farms if not user.is_admin else db_session.query(Farm).all()

    return render_template(
        'animals/index.html',
        animals=animals,
        search=search,
        selected_species=species,
        selected_status=status,
        selected_health_status=health_status,
        selected_farm_id=farm_id,
        farms=farms
    )


@animals_bp.route('/animals/register', methods=['GET', 'POST'])
@login_required
def register():
    user = get_current_user()
    user_farms = user.owned_farms if not user.is_admin else db_session.query(Farm).all()

    if not user_farms:
        flash("Please register a farm first before adding animals.", "warning")
        return redirect(url_for('farms.create'))

    if request.method == 'POST':
        validate_csrf()
        farm_id = request.form.get('farm_id')
        animal_tag = request.form.get('animal_tag', '').strip()
        animal_name = request.form.get('animal_name', '').strip()
        species = request.form.get('species')
        breed = request.form.get('breed', '').strip()
        sex = request.form.get('sex', 'Female')
        dob_str = request.form.get('date_of_birth')
        age_months = request.form.get('estimated_age_months')
        weight_kg = request.form.get('weight_kg')
        production_purpose = request.form.get('production_purpose', 'Dairy')
        notes = request.form.get('notes', '').strip()

        if not farm_id or not animal_tag or not species:
            flash("Farm, Tag Number, and Species are mandatory fields.", "danger")
            return render_template('animals/register.html', farms=user_farms)

        try:
            farm_id_int = int(farm_id)
        except ValueError:
            flash("Invalid farm selection.", "danger")
            return render_template('animals/register.html', farms=user_farms)

        if not verify_farm_access(user, farm_id_int, required_level='edit'):
            flash("You do not have permission to add animals to this farm.", "danger")
            return redirect(url_for('animals.index'))

        # Date of birth parsing
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Image upload handling
        image_path = None
        if 'image' in request.files and request.files['image'].filename:
            try:
                image_file = request.files['image']
                upload_dir = current_app.config['UPLOAD_FOLDER']
                image_path = save_uploaded_image(image_file, upload_dir)
            except Exception as e:
                flash(f"Image upload failed: {str(e)}", "warning")

        try:
            animal = AnimalService.create_animal(
                farm_id=farm_id_int,
                owner_id=user.id,
                animal_tag=animal_tag,
                species=species,
                animal_name=animal_name,
                breed=breed,
                sex=sex,
                date_of_birth=dob,
                estimated_age_months=int(age_months) if age_months else None,
                weight_kg=float(weight_kg) if weight_kg else None,
                production_purpose=production_purpose,
                image_path=image_path,
                notes=notes
            )
            log_audit(actor=user, action='CREATE_ANIMAL', entity_type='Animal', entity_id=animal.id, details=f"Tag: {animal.animal_tag}, Species: {animal.species}")
            flash(f"Animal '{animal.animal_tag}' registered successfully!", "success")
            return redirect(url_for('animals.detail', id=animal.id))
        except ValueError as e:
            flash(str(e), "danger")
            return render_template('animals/register.html', farms=user_farms)

    return render_template('animals/register.html', farms=user_farms)


@animals_bp.route('/animals/<int:id>')
@login_required
def detail(id):
    user = get_current_user()
    if not verify_animal_access(user, id, required_level='view'):
        flash("You do not have permission to view this animal's records.", "danger")
        return redirect(url_for('animals.index'))

    animal = AnimalService.get_animal(id)
    if not animal:
        flash("Animal not found.", "danger")
        return redirect(url_for('animals.index'))

    # Load related timeline records
    observations = animal.health_observations[:15]
    assessments = animal.disease_assessments[:10]
    visits = animal.veterinary_visits[:10]
    medications = animal.medications
    vaccinations = animal.vaccinations

    return render_template(
        'animals/detail.html',
        animal=animal,
        observations=observations,
        assessments=assessments,
        visits=visits,
        medications=medications,
        vaccinations=vaccinations
    )


@animals_bp.route('/animals/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = get_current_user()
    if not verify_animal_access(user, id, required_level='edit'):
        flash("You do not have permission to edit this animal.", "danger")
        return redirect(url_for('animals.index'))

    animal = AnimalService.get_animal(id)
    if not animal:
        flash("Animal not found.", "danger")
        return redirect(url_for('animals.index'))

    farms = user.owned_farms if not user.is_admin else db_session.query(Farm).all()

    if request.method == 'POST':
        validate_csrf()
        animal_name = request.form.get('animal_name', '').strip()
        breed = request.form.get('breed', '').strip()
        sex = request.form.get('sex', animal.sex)
        age_months = request.form.get('estimated_age_months')
        weight_kg = request.form.get('weight_kg')
        production_purpose = request.form.get('production_purpose', animal.production_purpose)
        status = request.form.get('status', animal.status)
        notes = request.form.get('notes', '').strip()

        # Image upload
        if 'image' in request.files and request.files['image'].filename:
            try:
                image_file = request.files['image']
                upload_dir = current_app.config['UPLOAD_FOLDER']
                animal.image_path = save_uploaded_image(image_file, upload_dir)
            except Exception as e:
                flash(f"Image upload failed: {str(e)}", "warning")

        AnimalService.update_animal(
            animal.id,
            animal_name=animal_name,
            breed=breed,
            sex=sex,
            estimated_age_months=int(age_months) if age_months else animal.estimated_age_months,
            weight_kg=float(weight_kg) if weight_kg else animal.weight_kg,
            production_purpose=production_purpose,
            status=status,
            notes=notes
        )

        log_audit(actor=user, action='UPDATE_ANIMAL', entity_type='Animal', entity_id=animal.id)
        flash("Animal details updated successfully.", "success")
        return redirect(url_for('animals.detail', id=animal.id))

    return render_template('animals/edit.html', animal=animal, farms=farms)


@animals_bp.route('/animals/<int:id>/archive', methods=['POST'])
@login_required
def archive(id):
    validate_csrf()
    user = get_current_user()
    if not verify_animal_access(user, id, required_level='edit'):
        flash("Permission denied.", "danger")
        return redirect(url_for('animals.index'))

    animal = AnimalService.get_animal(id)
    if animal:
        animal.status = 'Archived'
        db_session.commit()
        log_audit(actor=user, action='ARCHIVE_ANIMAL', entity_type='Animal', entity_id=animal.id)
        flash(f"Animal {animal.animal_tag} has been archived.", "info")

    return redirect(url_for('animals.index'))
