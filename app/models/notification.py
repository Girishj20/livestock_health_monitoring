from datetime import datetime
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    animal_id: Mapped[int] = mapped_column(Integer, ForeignKey('animals.id'), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default='Medium', nullable=False)  # Low, Medium, High, Urgent
    notification_type: Mapped[str] = mapped_column(String(50), default='General', nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    link_url: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='notifications')
    animal = relationship('Animal', back_populates='notifications')

    @property
    def priority_badge_class(self) -> str:
        mapping = {
            'Low': 'info',
            'Medium': 'secondary',
            'High': 'warning',
            'Urgent': 'danger'
        }
        return mapping.get(self.priority, 'secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'link_url': self.link_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }

    def __repr__(self):
        return f"<Notification id={self.id} user_id={self.user_id} title='{self.title}'>"
