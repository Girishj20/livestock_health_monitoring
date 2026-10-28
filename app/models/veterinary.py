from datetime import datetime, date
from sqlalchemy import Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class VeterinaryVisit(Base):
    __tablename__ = 'veterinary_visits'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey('animals.id'), nullable=False, index=True)
    veterinarian_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    vet_name: Mapped[str] = mapped_column(String(120), nullable=True)
    visit_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    clinical_findings: Mapped[str] = mapped_column(Text, nullable=True)
    veterinarian_diagnosis: Mapped[str] = mapped_column(String(255), nullable=True)
    treatment_notes: Mapped[str] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date] = mapped_column(Date, nullable=True)
    outcome_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    animal = relationship('Animal', back_populates='veterinary_visits')
    veterinarian = relationship('User', foreign_keys=[veterinarian_id])
    medications = relationship('Medication', back_populates='visit', cascade='all, delete-orphan')

    @property
    def attending_doctor(self) -> str:
        if self.veterinarian:
            return f"Dr. {self.veterinarian.full_name}"
        return self.vet_name or "Attending Veterinarian"

    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'vet_name': self.attending_doctor,
            'visit_date': self.visit_date.strftime('%Y-%m-%d %H:%M') if self.visit_date else None,
            'reason': self.reason,
            'clinical_findings': self.clinical_findings,
            'veterinarian_diagnosis': self.veterinarian_diagnosis,
            'treatment_notes': self.treatment_notes,
            'follow_up_date': self.follow_up_date.strftime('%Y-%m-%d') if self.follow_up_date else None,
            'outcome_notes': self.outcome_notes
        }

    def __repr__(self):
        return f"<VeterinaryVisit id={self.id} animal_id={self.animal_id} date={self.visit_date}>"


class Medication(Base):
    __tablename__ = 'medications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey('animals.id'), nullable=False, index=True)
    veterinary_visit_id: Mapped[int] = mapped_column(Integer, ForeignKey('veterinary_visits.id'), nullable=True)
    medication_name: Mapped[str] = mapped_column(String(150), nullable=False)
    dosage_instructions: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    prescribing_veterinarian: Mapped[str] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='Active', nullable=False)  # Active, Completed, Discontinued
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    animal = relationship('Animal', back_populates='medications')
    visit = relationship('VeterinaryVisit', back_populates='medications')

    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'medication_name': self.medication_name,
            'dosage_instructions': self.dosage_instructions,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'prescribing_veterinarian': self.prescribing_veterinarian,
            'status': self.status
        }

    def __repr__(self):
        return f"<Medication id={self.id} animal_id={self.animal_id} name='{self.medication_name}'>"
