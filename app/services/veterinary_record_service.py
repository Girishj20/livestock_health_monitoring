from datetime import datetime
from app.extensions import db_session
from app.models.animal import Animal
from app.models.veterinary import VeterinaryVisit, Medication
from app.services.notification_service import NotificationService


class VeterinaryRecordService:
    """Manages clinical veterinary visit records, official veterinary diagnoses, and prescribed treatments."""

    @staticmethod
    def record_visit(animal_id: int, reason: str, visit_date=None, veterinarian_id=None,
                     vet_name=None, clinical_findings=None, veterinarian_diagnosis=None,
                     treatment_notes=None, follow_up_date=None, outcome_notes=None) -> VeterinaryVisit:
        """Create and persist an official veterinary clinical consultation record."""
        animal = db_session.get(Animal, animal_id)
        if not animal:
            raise ValueError(f"Animal #{animal_id} not found.")

        if visit_date is None:
            visit_date = datetime.utcnow()

        visit = VeterinaryVisit(
            animal_id=animal_id,
            veterinarian_id=veterinarian_id,
            vet_name=vet_name,
            visit_date=visit_date,
            reason=reason,
            clinical_findings=clinical_findings,
            veterinarian_diagnosis=veterinarian_diagnosis,
            treatment_notes=treatment_notes,
            follow_up_date=follow_up_date,
            outcome_notes=outcome_notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(visit)
        db_session.commit()

        # If follow-up date is set, schedule notification reminder
        if follow_up_date:
            NotificationService.notify_farm_stakeholders(
                farm_id=animal.farm_id,
                title=f"Veterinary Follow-Up Scheduled: {animal.animal_tag}",
                message=f"Follow-up visit due on {follow_up_date.strftime('%Y-%m-%d')} for reason: {reason}",
                priority='Medium',
                notification_type='Vet Follow-up',
                animal_id=animal.id,
                link_url=f"/animals/{animal.id}"
            )

        return visit

    @staticmethod
    def add_medication(animal_id: int, medication_name: str, dosage_instructions: str,
                       start_date, end_date=None, visit_id=None, prescribing_vet=None) -> Medication:
        """Record prescribed medication and dosage."""
        med = Medication(
            animal_id=animal_id,
            veterinary_visit_id=visit_id,
            medication_name=medication_name,
            dosage_instructions=dosage_instructions,
            start_date=start_date,
            end_date=end_date,
            prescribing_veterinarian=prescribing_vet,
            status='Active',
            created_at=datetime.utcnow()
        )
        db_session.add(med)
        db_session.commit()
        return med
