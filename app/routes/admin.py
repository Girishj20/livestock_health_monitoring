import os
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.extensions import db_session, get_engine
from app.models.user import User
from app.models.farm import Farm
from app.models.animal import Animal
from app.models.health_observation import HealthObservation
from app.models.disease_assessment import DiseaseAssessment
from app.models.reference import AuditLog, ModelRegistry
from app.utils.security import login_required, roles_required, get_current_user, validate_csrf
from app.utils.helpers import log_audit

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
@login_required
@roles_required('administrator')
def index():
    user_count = db_session.query(User).count()
    farm_count = db_session.query(Farm).count()
    animal_count = db_session.query(Animal).count()
    obs_count = db_session.query(HealthObservation).count()
    assessment_count = db_session.query(DiseaseAssessment).count()
    vet_count = db_session.query(User).filter_by(role='veterinarian').count()

    recent_logs = db_session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()

    return render_template(
        'admin/index.html',
        user_count=user_count,
        farm_count=farm_count,
        animal_count=animal_count,
        obs_count=obs_count,
        assessment_count=assessment_count,
        vet_count=vet_count,
        recent_logs=recent_logs
    )


@admin_bp.route('/admin/users')
@login_required
@roles_required('administrator')
def users():
    all_users = db_session.query(User).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/admin/users/<int:id>/status', methods=['POST'])
@login_required
@roles_required('administrator')
def user_status(id):
    validate_csrf()
    current_admin = get_current_user()
    user = db_session.get(User, id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.users'))

    if user.id == current_admin.id:
        flash("You cannot suspend your own administrative account.", "warning")
        return redirect(url_for('admin.users'))

    new_status = request.form.get('status')
    new_role = request.form.get('role')

    if new_status in ('active', 'suspended'):
        user.account_status = new_status

    if new_role in ('farmer', 'veterinarian', 'farm_manager', 'administrator'):
        user.role = new_role

    db_session.commit()
    log_audit(actor=current_admin, action='UPDATE_USER_STATUS', entity_type='User', entity_id=user.id, details=f"Status: {new_status}, Role: {new_role}")
    flash(f"User {user.email} updated successfully.", "success")
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/audit-logs')
@login_required
@roles_required('administrator')
def audit_logs():
    logs = db_session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(150).all()
    return render_template('admin/audit_logs.html', logs=logs)


@admin_bp.route('/admin/models')
@login_required
@roles_required('administrator')
def models():
    models_list = db_session.query(ModelRegistry).all()
    return render_template('admin/models.html', models=models_list)


@admin_bp.route('/admin/system-health')
@login_required
@roles_required('administrator')
def system_health():
    # Database check
    db_ok = False
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(db_session.query(User.id).limit(1).statement)
        db_ok = True
    except Exception:
        db_ok = False

    # Models check
    models_dir = current_app.config['MODEL_DIR']
    models_exist = os.path.exists(models_dir) and any(f.endswith('.joblib') for f in os.listdir(models_dir))

    # Disk usage
    total, used, free = shutil.disk_usage(".")
    disk_free_gb = round(free / (2**30), 2)

    return render_template(
        'admin/system_health.html',
        db_ok=db_ok,
        models_ok=models_exist,
        disk_free_gb=disk_free_gb,
        models_dir=models_dir
    )
