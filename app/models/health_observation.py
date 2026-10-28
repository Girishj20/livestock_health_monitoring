import json
from datetime import datetime
from sqlalchemy import Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class HealthObservation(Base):
    __tablename__ = 'health_observations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey('animals.id'), nullable=False, index=True)
    recorded_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Vital signs
    temperature_c: Mapped[float] = mapped_column(Float, nullable=True)
    heart_rate_bpm: Mapped[float] = mapped_column(Float, nullable=True)
    respiratory_rate_bpm: Mapped[float] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Behavioral indicators
    food_intake: Mapped[str] = mapped_column(String(30), nullable=True)  # Normal, Reduced, Anorexic, Increased
    water_intake: Mapped[str] = mapped_column(String(30), nullable=True)  # Normal, Reduced, Excessive, None
    walking_activity: Mapped[str] = mapped_column(String(30), nullable=True)  # Normal, Sluggish, Lame, Staggering, Recumbent
    grazing_activity: Mapped[str] = mapped_column(String(30), nullable=True)  # Normal, Reduced, Not Grazing, N/A
    rumination: Mapped[str] = mapped_column(String(30), nullable=True)  # Normal, Reduced, Absent, N/A
    resting_behavior: Mapped[str] = mapped_column(String(30), nullable=True)  # Normal, Restless, Lethargic, Isolated
    milk_production: Mapped[float] = mapped_column(Float, nullable=True)
    body_condition_score: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Symptoms recorded (JSON string of symptom names)
    symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    additional_notes: Mapped[str] = mapped_column(Text, nullable=True)
    data_source: Mapped[str] = mapped_column(String(30), default='manual', nullable=False)  # manual, sensor, veterinary_check
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    animal = relationship('Animal', back_populates='health_observations')
    recorder = relationship('User', foreign_keys=[recorded_by])

    @property
    def symptoms_list(self) -> list:
        if not self.symptoms:
            return []
        try:
            parsed = json.loads(self.symptoms)
            if isinstance(parsed, list):
                return parsed
            return [str(parsed)]
        except Exception:
            return [s.strip() for s in self.symptoms.split(',') if s.strip()]

    def set_symptoms_list(self, symptom_list: list):
        self.symptoms = json.dumps(symptom_list)

    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'observed_at': self.observed_at.strftime('%Y-%m-%d %H:%M') if self.observed_at else None,
            'temperature_c': self.temperature_c,
            'heart_rate_bpm': self.heart_rate_bpm,
            'respiratory_rate_bpm': self.respiratory_rate_bpm,
            'weight_kg': self.weight_kg,
            'food_intake': self.food_intake,
            'water_intake': self.water_intake,
            'walking_activity': self.walking_activity,
            'rumination': self.rumination,
            'milk_production': self.milk_production,
            'body_condition_score': self.body_condition_score,
            'symptoms': self.symptoms_list,
            'additional_notes': self.additional_notes,
            'data_source': self.data_source
        }

    def __repr__(self):
        return f"<HealthObservation id={self.id} animal_id={self.animal_id} observed_at={self.observed_at}>"
