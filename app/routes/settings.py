from flask import Blueprint, render_template
from app.utils.security import login_required
from app.services.validation_service import VETERINARY_REFERENCE_RANGES, CRITICAL_SYMPTOMS

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/settings')
@login_required
def index():
    return render_template(
        'settings/index.html',
        reference_ranges=VETERINARY_REFERENCE_RANGES,
        critical_symptoms=CRITICAL_SYMPTOMS
    )
