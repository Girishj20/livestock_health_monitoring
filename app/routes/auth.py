from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.extensions import db_session
from app.models.user import User
from app.models.farm import Farm
from app.utils.security import login_required, get_current_user, validate_csrf
from app.utils.helpers import log_audit

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if get_current_user():
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        validate_csrf()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'farmer')
        phone = request.form.get('phone', '').strip()
        farm_name = request.form.get('farm_name', '').strip()
        farm_location = request.form.get('farm_location', '').strip()

        if not full_name or not email or not password:
            flash("Full name, email, and password are required.", "danger")
            return render_template('auth/register.html', full_name=full_name, email=email, phone=phone, farm_name=farm_name)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('auth/register.html', full_name=full_name, email=email, phone=phone, farm_name=farm_name)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('auth/register.html', full_name=full_name, email=email, phone=phone, farm_name=farm_name)

        existing = db_session.query(User).filter_by(email=email).first()
        if existing:
            flash("An account with this email address already exists.", "danger")
            return render_template('auth/register.html', full_name=full_name, phone=phone, farm_name=farm_name)

        # Allowable roles for public registration
        if role not in ('farmer', 'veterinarian', 'farm_manager'):
            role = 'farmer'

        user = User(
            full_name=full_name,
            email=email,
            role=role,
            phone=phone,
            account_status='active'
        )
        user.set_password(password)
        db_session.add(user)
        db_session.commit()

        # If user is a farmer/manager and specified a farm name, create their default farm
        if role in ('farmer', 'farm_manager') and farm_name:
            farm = Farm(
                farm_name=farm_name,
                owner_id=user.id,
                location=farm_location,
                farm_type='Dairy'
            )
            db_session.add(farm)
            db_session.commit()

        log_audit(actor=user, action='USER_REGISTER', entity_type='User', entity_id=user.id, details=f"Registered as {role}")

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if get_current_user():
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        validate_csrf()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = db_session.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('auth/login.html', email=email)

        if not user.is_active:
            flash("Your account has been deactivated. Please contact an administrator.", "danger")
            return render_template('auth/login.html')

        # Session fixation defense: regenerate session
        session.clear()
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.full_name
        session.permanent = remember

        log_audit(actor=user, action='USER_LOGIN', entity_type='User', entity_id=user.id, details="Successful login")

        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    user = get_current_user()
    if user:
        log_audit(actor=user, action='USER_LOGOUT', entity_type='User', entity_id=user.id, details="User logged out")
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('dashboard.landing'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()

    if request.method == 'POST':
        validate_csrf()
        action = request.form.get('action')

        if action == 'update_info':
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()

            if full_name:
                user.full_name = full_name
                user.phone = phone
                session['user_name'] = full_name
                db_session.commit()
                flash("Profile details updated successfully.", "success")

        elif action == 'change_password':
            current_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_pass = request.form.get('confirm_password', '')

            if not user.check_password(current_pass):
                flash("Current password is incorrect.", "danger")
            elif len(new_pass) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new_pass != confirm_pass:
                flash("New passwords do not match.", "danger")
            else:
                user.set_password(new_pass)
                db_session.commit()
                log_audit(actor=user, action='PASSWORD_CHANGE', entity_type='User', entity_id=user.id)
                flash("Password changed successfully.", "success")

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', user=user)
