from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db_session
from app.models.farm import Farm, FarmMembership
from app.models.user import User
from app.utils.security import login_required, get_current_user, validate_csrf, verify_farm_access
from app.utils.helpers import log_audit

farms_bp = Blueprint('farms', __name__)


@farms_bp.route('/farms')
@login_required
def index():
    user = get_current_user()
    if user.is_admin:
        farms = db_session.query(Farm).all()
    else:
        owned = user.owned_farms
        member = [m.farm for m in user.farm_memberships]
        farms = list({f.id: f for f in (owned + member)}.values())

    return render_template('farms/index.html', farms=farms)


@farms_bp.route('/farms/create', methods=['GET', 'POST'])
@login_required
def create():
    user = get_current_user()
    if request.method == 'POST':
        validate_csrf()
        farm_name = request.form.get('farm_name', '').strip()
        location = request.form.get('location', '').strip()
        farm_type = request.form.get('farm_type', 'Dairy')

        if not farm_name:
            flash("Farm name is required.", "danger")
            return render_template('farms/create.html')

        farm = Farm(
            farm_name=farm_name,
            owner_id=user.id,
            location=location,
            farm_type=farm_type,
            status='active'
        )
        db_session.add(farm)
        db_session.commit()

        log_audit(actor=user, action='CREATE_FARM', entity_type='Farm', entity_id=farm.id, details=farm_name)
        flash(f"Farm '{farm.farm_name}' created successfully!", "success")
        return redirect(url_for('farms.detail', id=farm.id))

    return render_template('farms/create.html')


@farms_bp.route('/farms/<int:id>')
@login_required
def detail(id):
    user = get_current_user()
    if not verify_farm_access(user, id, required_level='view'):
        flash("Unauthorized farm access.", "danger")
        return redirect(url_for('farms.index'))

    farm = db_session.get(Farm, id)
    if not farm:
        flash("Farm not found.", "danger")
        return redirect(url_for('farms.index'))

    animals = farm.animals
    total_animals = len(animals)
    cow_count = sum(1 for a in animals if a.species == 'Cow')
    buffalo_count = sum(1 for a in animals if a.species == 'Buffalo')
    goat_count = sum(1 for a in animals if a.species == 'Goat')
    sheep_count = sum(1 for a in animals if a.species == 'Sheep')

    normal_count = sum(1 for a in animals if a.health_status == 'Normal')
    attention_count = sum(1 for a in animals if a.health_status in ('Attention Required', 'Urgent Veterinary Attention'))

    return render_template(
        'farms/detail.html',
        farm=farm,
        animals=animals,
        total_animals=total_animals,
        cow_count=cow_count,
        buffalo_count=buffalo_count,
        goat_count=goat_count,
        sheep_count=sheep_count,
        normal_count=normal_count,
        attention_count=attention_count
    )


@farms_bp.route('/farms/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = get_current_user()
    if not verify_farm_access(user, id, required_level='admin'):
        flash("Unauthorized farm edit permissions.", "danger")
        return redirect(url_for('farms.detail', id=id))

    farm = db_session.get(Farm, id)
    if not farm:
        flash("Farm not found.", "danger")
        return redirect(url_for('farms.index'))

    if request.method == 'POST':
        validate_csrf()
        farm.farm_name = request.form.get('farm_name', farm.farm_name).strip()
        farm.location = request.form.get('location', farm.location).strip()
        farm.farm_type = request.form.get('farm_type', farm.farm_type)
        farm.status = request.form.get('status', farm.status)

        db_session.commit()
        log_audit(actor=user, action='UPDATE_FARM', entity_type='Farm', entity_id=farm.id)
        flash("Farm details updated.", "success")
        return redirect(url_for('farms.detail', id=farm.id))

    return render_template('farms/edit.html', farm=farm)
