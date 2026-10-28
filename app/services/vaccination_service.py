from datetime import datetime, date, timedelta
from app.extensions import db_session
from app.models.animal import Animal
from app.models.vaccination import Vaccination
from app.services.notification_service import NotificationService


class VaccinationService:
    """Manages vaccination schedules, deworming, batch tracking, and due date reminders."""

    @staticmethod
    def record_vaccination(animal_id: int, vaccine_name: str, vaccination_date: date,
                           next_due_date: date = None, administered_by: str = None,
                           batch_reference: str = None, status: str = 'Completed',
                           notes: str = None) -> Vaccination:
        """Record or schedule a vaccination."""
        animal = db_session.get(Animal, animal_id)
        if not animal:
            raise ValueError(f"Animal #{animal_id} not found.")

        vacc = Vaccination(
            animal_id=animal_id,
            vaccine_name=vaccine_name,
            vaccination_date=vaccination_date,
            next_due_date=next_due_date,
            administered_by=administered_by,
            batch_reference=batch_reference,
            status=status,
            notes=notes,
            created_at=datetime.utcnow()
        )
        db_session.add(vacc)
        db_session.commit()

        # If next due date is scheduled, create reminder
        if next_due_date and status in ('Completed', 'Upcoming'):
            NotificationService.notify_farm_stakeholders(
                farm_id=animal.farm_id,
                title=f"Vaccine Scheduled: {vaccine_name} for {animal.animal_tag}",
                message=f"Booster/Next dose scheduled for {next_due_date.strftime('%Y-%m-%d')}.",
                priority='Medium',
                notification_type='Vaccine Reminder',
                animal_id=animal.id,
                link_url=f"/vaccinations"
            )

        return vacc

    @staticmethod
    def get_upcoming_vaccinations(user, days=30):
        """Retrieve vaccinations due within the next N days or currently overdue."""
        today = date.today()
        target_date = today + timedelta(days=days)

        query = db_session.query(Vaccination).join(Animal)

        if not (user.is_admin or user.is_veterinarian):
            owned_farm_ids = [f.id for f in user.owned_farms]
            member_farm_ids = [m.farm_id for m in user.farm_memberships]
            allowed_farm_ids = list(set(owned_farm_ids + member_farm_ids))
            if not allowed_farm_ids:
                return []
            query = query.filter(Animal.farm_id.in_(allowed_farm_ids))

        # Filter by next_due_date in range or overdue
        query = query.filter(
            Vaccination.next_due_date != None,
            Vaccination.next_due_date <= target_date,
            Vaccination.status.in_(['Upcoming', 'Due Today', 'Overdue'])
        )

        return query.order_by(Vaccination.next_due_date.asc()).all()
