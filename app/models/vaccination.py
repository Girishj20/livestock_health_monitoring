from datetime import datetime, date
from sqlalchemy import Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class Vaccination(Base):
    __tablename__ = 'vaccinations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey('animals.id'), nullable=False, index=True)
    vaccine_name: Mapped[str] = mapped_column(String(150), nullable=False)
    vaccination_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=True)
    administered_by: Mapped[str] = mapped_column(String(120), nullable=True)
    batch_reference: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='Completed', nullable=False)  # Upcoming, Due Today, Overdue, Completed, Cancelled
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    animal = relationship('Animal', back_populates='vaccinations')

    @property
    def computed_status(self) -> str:
        """Dynamically evaluate status based on next_due_date if marked as scheduled/upcoming."""
        if self.status in ('Completed', 'Cancelled'):
            return self.status
        if not self.next_due_date:
            return self.status
            
        today = date.today()
        if self.next_due_date < today:
            return 'Overdue'
        elif self.next_due_date == today:
            return 'Due Today'
        return 'Upcoming'

    @property
    def status_badge_class(self) -> str:
        mapping = {
            'Completed': 'success',
            'Upcoming': 'primary',
            'Due Today': 'warning',
            'Overdue': 'danger',
            'Cancelled': 'secondary'
        }
        return mapping.get(self.computed_status, 'secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'vaccine_name': self.vaccine_name,
            'vaccination_date': self.vaccination_date.strftime('%Y-%m-%d') if self.vaccination_date else None,
            'next_due_date': self.next_due_date.strftime('%Y-%m-%d') if self.next_due_date else None,
            'administered_by': self.administered_by,
            'batch_reference': self.batch_reference,
            'status': self.computed_status,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<Vaccination id={self.id} animal_id={self.animal_id} vaccine='{self.vaccine_name}'>"
