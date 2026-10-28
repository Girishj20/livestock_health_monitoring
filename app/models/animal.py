from datetime import datetime, date
from sqlalchemy import Integer, String, Float, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class Animal(Base):
    __tablename__ = 'animals'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey('farms.id'), nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    animal_tag: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    animal_name: Mapped[str] = mapped_column(String(100), nullable=True)
    species: Mapped[str] = mapped_column(String(30), nullable=False, index=True)  # Cow, Buffalo, Goat, Sheep
    breed: Mapped[str] = mapped_column(String(100), nullable=True)
    sex: Mapped[str] = mapped_column(String(10), default='Female', nullable=False)  # Female, Male
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    estimated_age_months: Mapped[int] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    production_purpose: Mapped[str] = mapped_column(String(50), default='Dairy', nullable=False)
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='Active', nullable=False)  # Active, Sick, Quarantine, Sold, Deceased, Archived
    health_status: Mapped[str] = mapped_column(String(50), default='Normal', nullable=False)  # Normal, Monitoring Required, Attention Required, Urgent Veterinary Attention, Prediction Unavailable
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    farm = relationship('Farm', back_populates='animals')
    owner = relationship('User', back_populates='animals', foreign_keys=[owner_id])
    health_observations = relationship('HealthObservation', back_populates='animal', cascade='all, delete-orphan', order_by='desc(HealthObservation.observed_at)')
    disease_assessments = relationship('DiseaseAssessment', back_populates='animal', cascade='all, delete-orphan', order_by='desc(DiseaseAssessment.created_at)')
    veterinary_visits = relationship('VeterinaryVisit', back_populates='animal', cascade='all, delete-orphan', order_by='desc(VeterinaryVisit.visit_date)')
    medications = relationship('Medication', back_populates='animal', cascade='all, delete-orphan')
    vaccinations = relationship('Vaccination', back_populates='animal', cascade='all, delete-orphan', order_by='desc(Vaccination.vaccination_date)')
    notifications = relationship('Notification', back_populates='animal', cascade='all, delete-orphan')

    @property
    def age_display(self) -> str:
        if self.estimated_age_months:
            years = self.estimated_age_months // 12
            months = self.estimated_age_months % 12
            if years > 0:
                return f"{years}y {months}m" if months > 0 else f"{years} yrs"
            return f"{months} mos"
        elif self.date_of_birth:
            diff_days = (date.today() - self.date_of_birth).days
            months = int(diff_days / 30.4375)
            years = months // 12
            rem_months = months % 12
            if years > 0:
                return f"{years}y {rem_months}m" if rem_months > 0 else f"{years} yrs"
            return f"{months} mos"
        return "Unknown"

    @property
    def latest_observation(self):
        return self.health_observations[0] if self.health_observations else None

    @property
    def latest_assessment(self):
        return self.disease_assessments[0] if self.disease_assessments else None

    @property
    def health_badge_class(self) -> str:
        mapping = {
            'Normal': 'success',
            'Monitoring Required': 'info',
            'Attention Required': 'warning',
            'Urgent Veterinary Attention': 'danger',
            'Prediction Unavailable': 'secondary'
        }
        return mapping.get(self.health_status, 'secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'animal_tag': self.animal_tag,
            'animal_name': self.animal_name,
            'species': self.species,
            'breed': self.breed,
            'sex': self.sex,
            'age_display': self.age_display,
            'weight_kg': self.weight_kg,
            'status': self.status,
            'health_status': self.health_status,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Animal id={self.id} tag='{self.animal_tag}' species='{self.species}'>"
