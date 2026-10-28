from flask import Blueprint, render_template, request, Response, flash, redirect, url_for
from app.extensions import db_session
from app.models.animal import Animal
from app.models.farm import Farm
from app.services.animal_service import AnimalService
from app.services.report_service import ReportService
from app.utils.security import login_required, get_current_user, verify_animal_access

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
@login_required
def index():
    user = get_current_user()
    animals = AnimalService.get_animals(user)
    farms = user.owned_farms if not user.is_admin else db_session.query(Farm).all()

    return render_template('reports/index.html', animals=animals, farms=farms)


@reports_bp.route('/reports/animal/<int:id>')
@login_required
def animal_report(id):
    user = get_current_user()
    if not verify_animal_access(user, id, required_level='view'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('reports.index'))

    data = ReportService.get_animal_summary(id)
    return render_template('reports/animal_report.html', **data)


@reports_bp.route('/reports/animal/<int:id>/pdf')
@login_required
def animal_pdf(id):
    user = get_current_user()
    if not verify_animal_access(user, id, required_level='view'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('reports.index'))

    try:
        pdf_bytes = ReportService.generate_pdf_report(id)
        animal = db_session.get(Animal, id)
        filename = f"health_report_{animal.animal_tag}_{animal.species}.pdf"
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        flash(f"PDF generation error: {str(e)}", "danger")
        return redirect(url_for('reports.animal_report', id=id))


@reports_bp.route('/reports/export/animals-csv')
@login_required
def export_animals():
    user = get_current_user()
    farm_id = request.args.get('farm_id')
    if farm_id:
        try:
            farm_id = int(farm_id)
        except ValueError:
            farm_id = None

    csv_data = ReportService.export_animals_to_csv(user, farm_id=farm_id)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename="livestock_animals.csv"'}
    )


@reports_bp.route('/reports/export/observations-csv')
@login_required
def export_observations():
    user = get_current_user()
    animal_id = request.args.get('animal_id')
    if animal_id:
        try:
            animal_id = int(animal_id)
        except ValueError:
            animal_id = None

    csv_data = ReportService.export_observations_to_csv(user, animal_id=animal_id)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename="health_observations.csv"'}
    )
