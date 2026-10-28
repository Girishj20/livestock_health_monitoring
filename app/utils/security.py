import secrets
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, g
from app.extensions import db_session
from app.models.user import User
from app.models.farm import Farm, FarmMembership
from app.models.animal import Animal


def get_current_user():
    """Retrieve currently authenticated user from session or cache on Flask g."""
    if 'user_id' not in session:
        return None
    user_id = session.get('user_id')
    if not hasattr(g, 'current_user') or g.current_user is None or getattr(g.current_user, 'id', None) != user_id:
        g.current_user = db_session.get(User, user_id)
    return g.current_user


def generate_csrf_token():
    """Generate or retrieve unique CSRF token for the session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def validate_csrf():
    """Validate CSRF token on mutating requests."""
    from flask import current_app
    if current_app.config.get('TESTING') or current_app.config.get('WTF_CSRF_ENABLED') is False:
        return

    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
        session_token = session.get('_csrf_token')
        if not token or not session_token or not secrets.compare_digest(token, session_token):
            abort(400, description="Invalid or missing CSRF security token.")


def login_required(f):
    """Ensure user is logged in before accessing the view."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if not user.is_active:
            session.clear()
            flash("Your account has been deactivated. Please contact an administrator.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def roles_required(*allowed_roles):
    """Enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if user is None:
                flash("Please log in to continue.", "warning")
                return redirect(url_for('auth.login'))
            if user.role not in allowed_roles and not user.is_admin:
                flash("You do not have permission to access this resource.", "danger")
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def verify_farm_access(user, farm_id: int, required_level='view') -> bool:
    """Verify if user has permission to access the specified farm."""
    if user.is_admin or user.is_veterinarian:
        return True
    
    farm = db_session.get(Farm, farm_id)
    if not farm:
        return False
    
    if farm.owner_id == user.id:
        return True
        
    membership = db_session.query(FarmMembership).filter_by(farm_id=farm_id, user_id=user.id).first()
    if not membership:
        return False
        
    if required_level == 'edit' and membership.permission_level not in ('edit', 'admin'):
        return False
        
    if required_level == 'admin' and membership.permission_level != 'admin':
        return False
        
    return True


def verify_animal_access(user, animal_id: int, required_level='view') -> bool:
    """Verify if user has permission to access the specified animal."""
    if user.is_admin or user.is_veterinarian:
        return True
        
    animal = db_session.get(Animal, animal_id)
    if not animal:
        return False
        
    return verify_farm_access(user, animal.farm_id, required_level=required_level)
