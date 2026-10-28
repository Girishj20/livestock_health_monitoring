import json
from datetime import datetime, date
from sqlalchemy import Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class DiseaseReference(Base):
    __tablename__ = 'disease_reference'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disease_name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    applicable_species: Mapped[str] = mapped_column(String(100), nullable=False)  # Cow, Buffalo, Goat, Sheep, All
    category: Mapped[str] = mapped_column(String(50), default='Bacterial', nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    warning_signs: Mapped[str] = mapped_column(Text, nullable=False)
    prevention_information: Mapped[str] = mapped_column(Text, nullable=False)
    biosecurity_considerations: Mapped[str] = mapped_column(Text, nullable=True)
    when_to_call_vet: Mapped[str] = mapped_column(Text, nullable=False)
    veterinary_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'disease_name': self.disease_name,
            'applicable_species': self.applicable_species,
            'category': self.category,
            'description': self.description,
            'warning_signs': self.warning_signs,
            'prevention_information': self.prevention_information,
            'when_to_call_vet': self.when_to_call_vet,
            'veterinary_reference': self.veterinary_reference,
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d') if self.reviewed_at else None
        }

    def __repr__(self):
        return f"<DiseaseReference id={self.id} name='{self.disease_name}'>"


class ModelRegistry(Base):
    __tablename__ = 'model_registry'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    model_version: Mapped[str] = mapped_column(String(30), nullable=False)
    model_path: Mapped[str] = mapped_column(String(255), nullable=False)
    feature_schema: Mapped[str] = mapped_column(Text, nullable=False)
    training_dataset_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    evaluation_metrics: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='Active', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def metrics_dict(self) -> dict:
        if not self.evaluation_metrics:
            return {}
        try:
            return json.loads(self.evaluation_metrics)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'species': self.species,
            'model_version': self.model_version,
            'model_path': self.model_path,
            'metrics': self.metrics_dict,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

    def __repr__(self):
        return f"<ModelRegistry id={self.id} model='{self.model_name}' version='{self.model_version}'>"


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    actor_name: Mapped[str] = mapped_column(String(120), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    actor = relationship('User', foreign_keys=[actor_id])

    def to_dict(self):
        return {
            'id': self.id,
            'actor_name': self.actor_name,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f"<AuditLog id={self.id} action='{self.action}' entity='{self.entity_type}'>"
