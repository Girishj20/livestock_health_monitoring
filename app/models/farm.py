from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class Farm(Base):
    __tablename__ = 'farms'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_name: Mapped[str] = mapped_column(String(150), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    farm_type: Mapped[str] = mapped_column(String(50), default='Dairy', nullable=False)  # Dairy, Pastoral, Mixed, Breeding
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False)  # active, inactive
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship('User', back_populates='owned_farms', foreign_keys=[owner_id])
    memberships = relationship('FarmMembership', back_populates='farm', cascade='all, delete-orphan')
    animals = relationship('Animal', back_populates='farm', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'farm_name': self.farm_name,
            'owner_id': self.owner_id,
            'location': self.location,
            'farm_type': self.farm_type,
            'status': self.status,
            'animal_count': len(self.animals) if self.animals else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Farm id={self.id} name='{self.farm_name}'>"


class FarmMembership(Base):
    __tablename__ = 'farm_memberships'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey('farms.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    permission_level: Mapped[str] = mapped_column(String(30), default='view', nullable=False)  # view, edit, admin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    farm = relationship('Farm', back_populates='memberships')
    user = relationship('User', back_populates='farm_memberships')

    def __repr__(self):
        return f"<FarmMembership farm_id={self.farm_id} user_id={self.user_id} permission='{self.permission_level}'>"
