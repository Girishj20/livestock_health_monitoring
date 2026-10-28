import io
import csv
from datetime import datetime, date
from app.extensions import db_session
from app.models.animal import Animal
from app.models.farm import Farm
from app.models.health_observation import HealthObservation
from app.models.disease_assessment import DiseaseAssessment
from app.models.veterinary import VeterinaryVisit
from app.models.vaccination import Vaccination
from app.services.animal_service import AnimalService

# Try importing reportlab safely
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportService:
    """Generates health reports, herd analytics, CSV exports, and downloadable PDF dossiers."""

    @staticmethod
    def get_animal_summary(animal_id: int) -> dict:
        """Collect comprehensive medical dossier for a single animal."""
        animal = db_session.get(Animal, animal_id)
        if not animal:
            raise ValueError(f"Animal #{animal_id} not found.")

        return {
            'animal': animal,
            'observations': animal.health_observations[:20],
            'assessments': animal.disease_assessments[:10],
            'veterinary_visits': animal.veterinary_visits[:10],
            'medications': animal.medications,
            'vaccinations': animal.vaccinations,
            'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        }

    @staticmethod
    def export_animals_to_csv(user, farm_id=None) -> str:
        """Export animals visible to user into CSV format."""
        animals = AnimalService.get_animals(user, farm_id=farm_id)
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Animal Tag', 'Name', 'Species', 'Breed', 'Sex',
            'Age', 'Weight (kg)', 'Purpose', 'Status', 'Health Status', 'Farm'
        ])

        for a in animals:
            writer.writerow([
                a.animal_tag,
                a.animal_name or '',
                a.species,
                a.breed or '',
                a.sex,
                a.age_display,
                a.weight_kg or '',
                a.production_purpose,
                a.status,
                a.health_status,
                a.farm.farm_name if a.farm else ''
            ])

        return output.getvalue()

    @staticmethod
    def export_observations_to_csv(user, animal_id=None) -> str:
        """Export health observation records to CSV."""
        query = db_session.query(HealthObservation).join(Animal)

        if not (user.is_admin or user.is_veterinarian):
            owned_farm_ids = [f.id for f in user.owned_farms]
            member_farm_ids = [m.farm_id for m in user.farm_memberships]
            allowed_farm_ids = list(set(owned_farm_ids + member_farm_ids))
            query = query.filter(Animal.farm_id.in_(allowed_farm_ids))

        if animal_id:
            query = query.filter(HealthObservation.animal_id == animal_id)

        records = query.order_by(HealthObservation.observed_at.desc()).limit(1000).all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            'Observation ID', 'Animal Tag', 'Species', 'Observed At',
            'Temperature (°C)', 'Heart Rate (bpm)', 'Resp Rate (bpm)', 'Weight (kg)',
            'Food Intake', 'Rumination', 'Mobility', 'Milk (L)', 'BCS', 'Symptoms', 'Notes'
        ])

        for r in records:
            writer.writerow([
                r.id,
                r.animal.animal_tag if r.animal else '',
                r.animal.species if r.animal else '',
                r.observed_at.strftime('%Y-%m-%d %H:%M') if r.observed_at else '',
                r.temperature_c or '',
                r.heart_rate_bpm or '',
                r.respiratory_rate_bpm or '',
                r.weight_kg or '',
                r.food_intake or '',
                r.rumination or '',
                r.walking_activity or '',
                r.milk_production or '',
                r.body_condition_score or '',
                ", ".join(r.symptoms_list),
                r.additional_notes or ''
            ])

        return output.getvalue()

    @staticmethod
    def generate_pdf_report(animal_id: int) -> bytes:
        """Generate formatted PDF health dossier using ReportLab."""
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("ReportLab library is not installed.")

        data = ReportService.get_animal_summary(animal_id)
        animal = data['animal']

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1b4332'),
            spaceAfter=12
        )
        story.append(Paragraph(f"Livestock Health Dossier: {animal.species} [{animal.animal_tag}]", title_style))
        story.append(Paragraph(f"Report Generated: {data['generated_at']}", styles['Normal']))
        story.append(Spacer(1, 14))

        # Animal Info Table
        info_data = [
            ["Tag Number:", animal.animal_tag, "Name:", animal.animal_name or "N/A"],
            ["Species:", animal.species, "Breed:", animal.breed or "N/A"],
            ["Sex:", animal.sex, "Age:", animal.age_display],
            ["Weight:", f"{animal.weight_kg} kg" if animal.weight_kg else "N/A", "Health Status:", animal.health_status],
            ["Farm:", animal.farm.farm_name if animal.farm else "N/A", "Management Status:", animal.status]
        ]
        info_table = Table(info_data, colWidths=[90, 180, 90, 180])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 18))

        # Recent Observations Section
        story.append(Paragraph("Recent Clinical Observations", styles['Heading2']))
        if data['observations']:
            obs_headers = ["Date & Time", "Temp (°C)", "Heart (bpm)", "Resp (bpm)", "Food", "Symptoms"]
            obs_rows = [obs_headers]
            for o in data['observations'][:8]:
                obs_rows.append([
                    o.observed_at.strftime('%Y-%m-%d %H:%M'),
                    str(o.temperature_c) if o.temperature_c else '-',
                    str(o.heart_rate_bpm) if o.heart_rate_bpm else '-',
                    str(o.respiratory_rate_bpm) if o.respiratory_rate_bpm else '-',
                    o.food_intake or '-',
                    ", ".join(o.symptoms_list[:3]) or 'None'
                ])
            obs_table = Table(obs_rows, colWidths=[90, 60, 65, 65, 70, 190])
            obs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4)
            ]))
            story.append(obs_table)
        else:
            story.append(Paragraph("No health observations recorded yet.", styles['Normal']))

        story.append(Spacer(1, 18))

        # Veterinary Notice / Disclaimer
        disclaimer_text = (
            "<b>VETERINARY MEDICAL DISCLAIMER:</b> This report is generated by the Livestock Health Monitoring System "
            "as a digital tracking and decision-support tool. Automated risk scores are estimates and not official "
            "veterinary diagnoses. Always consult a licensed veterinarian for definitive treatment."
        )
        story.append(Paragraph(disclaimer_text, ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#495057'))))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
