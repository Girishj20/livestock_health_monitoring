from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default='farmer', nullable=False)  # farmer, veterinarian, farm_manager, administrator
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    account_status: Mapped[str] = mapped_column(String(20), default='active', nullable=False)  # active, suspended, pending
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owned_farms = relationship('Farm', back_populates='owner', cascade='all, delete-orphan', foreign_keys='Farm.owner_id')
    farm_memberships = relationship('FarmMembership', back_populates='user', cascade='all, delete-orphan')
    animals = relationship('Animal', back_populates='owner', foreign_keys='Animal.owner_id')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    audit_logs = relationship('AuditLog', back_populates='actor', foreign_keys='AuditLog.actor_id')

    def set_password(self, password: str):
        """Hash and store user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify plain password against stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == 'administrator'

    @property
    def is_veterinarian(self) -> bool:
        return self.role == 'veterinarian'

    @property
    def is_farm_manager(self) -> bool:
        return self.role in ('farm_manager', 'administrator')

    @property
    def is_active(self) -> bool:
        return self.account_status == 'active'

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'account_status': self.account_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"
