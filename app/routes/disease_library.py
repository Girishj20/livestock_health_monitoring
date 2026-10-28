from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db_session
from app.models.reference import DiseaseReference
from app.utils.security import login_required

disease_library_bp = Blueprint('disease_library', __name__)


@disease_library_bp.route('/disease-library')
def index():
    species_filter = request.args.get('species', 'All')
    category_filter = request.args.get('category', 'All')
    search = request.args.get('search', '').strip()

    query = db_session.query(DiseaseReference).filter_by(status='active')

    if species_filter != 'All':
        query = query.filter(DiseaseReference.applicable_species.ilike(f"%{species_filter}%"))

    if category_filter != 'All':
        query = query.filter_by(category=category_filter)

    if search:
        query = query.filter(DiseaseReference.disease_name.ilike(f"%{search}%"))

    diseases = query.order_by(DiseaseReference.disease_name.asc()).all()

    return render_template(
        'disease_library/index.html',
        diseases=diseases,
        selected_species=species_filter,
        selected_category=category_filter,
        search=search
    )


@disease_library_bp.route('/disease-library/<int:id>')
def detail(id):
    disease = db_session.get(DiseaseReference, id)
    if not disease:
        flash("Disease reference entry not found.", "warning")
        return redirect(url_for('disease_library.index'))

    return render_template('disease_library/detail.html', disease=disease)
