import json
from datetime import datetime
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class DiseaseAssessment(Base):
    __tablename__ = 'disease_assessments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey('animals.id'), nullable=False, index=True)
    initiated_by: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_snapshot: Mapped[str] = mapped_column(Text, nullable=False)  # JSON snapshot of all inputs
    predicted_class: Mapped[str] = mapped_column(String(100), nullable=False)
    prediction_scores: Mapped[str] = mapped_column(Text, nullable=True)  # JSON dictionary of probabilities/scores
    data_quality_status: Mapped[str] = mapped_column(String(50), default='Complete', nullable=False)  # Complete, Imputed, Warning
    assessment_status: Mapped[str] = mapped_column(String(50), default='Completed', nullable=False)  # Completed, Demo Mode, Failed
    risk_level: Mapped[str] = mapped_column(String(50), default='Normal', nullable=False)  # Normal, Low, Moderate, High, Critical
    urgency_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    veterinary_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    animal = relationship('Animal', back_populates='disease_assessments')
    user = relationship('User', foreign_keys=[initiated_by])

    @property
    def input_snapshot_dict(self) -> dict:
        if not self.input_snapshot:
            return {}
        try:
            return json.loads(self.input_snapshot)
        except Exception:
            return {}

    @property
    def prediction_scores_dict(self) -> dict:
        if not self.prediction_scores:
            return {}
        try:
            return json.loads(self.prediction_scores)
        except Exception:
            return {}

    @property
    def risk_badge_class(self) -> str:
        mapping = {
            'Normal': 'success',
            'Low': 'info',
            'Moderate': 'warning',
            'High': 'danger',
            'Critical': 'danger'
        }
        return mapping.get(self.risk_level, 'secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'animal_id': self.animal_id,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'predicted_class': self.predicted_class,
            'prediction_scores': self.prediction_scores_dict,
            'data_quality_status': self.data_quality_status,
            'assessment_status': self.assessment_status,
            'risk_level': self.risk_level,
            'urgency_override': self.urgency_override,
            'veterinary_notes': self.veterinary_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }

    def __repr__(self):
        return f"<DiseaseAssessment id={self.id} animal_id={self.animal_id} pred='{self.predicted_class}' risk='{self.risk_level}'>"
