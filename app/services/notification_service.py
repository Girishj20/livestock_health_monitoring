from datetime import datetime
from app.extensions import db_session
from app.models.notification import Notification
from app.models.farm import Farm, FarmMembership


class NotificationService:
    """Handles alert creation, notification delivery, and persistence."""

    @staticmethod
    def create_notification(user_id: int, title: str, message: str, priority='Medium', 
                            notification_type='General', animal_id=None, link_url=None) -> Notification:
        """Create and persist a single user notification."""
        notif = Notification(
            user_id=user_id,
            animal_id=animal_id,
            title=title,
            message=message,
            priority=priority,
            notification_type=notification_type,
            link_url=link_url,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db_session.add(notif)
        db_session.commit()
        return notif

    @staticmethod
    def notify_farm_stakeholders(farm_id: int, title: str, message: str, priority='High',
                                 notification_type='Alert', animal_id=None, link_url=None):
        """Broadcast alert to farm owner and all affiliated farm managers/members."""
        farm = db_session.get(Farm, farm_id)
        if not farm:
            return

        recipients = {farm.owner_id}
        members = db_session.query(FarmMembership).filter_by(farm_id=farm_id).all()
        for m in members:
            recipients.add(m.user_id)

        for uid in recipients:
            notif = Notification(
                user_id=uid,
                animal_id=animal_id,
                title=title,
                message=message,
                priority=priority,
                notification_type=notification_type,
                link_url=link_url,
                is_read=False,
                created_at=datetime.utcnow()
            )
            db_session.add(notif)

        db_session.commit()

    @staticmethod
    def get_user_notifications(user_id: int, unread_only=False, limit=25):
        """Retrieve notifications for a user."""
        query = db_session.query(Notification).filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        return db_session.query(Notification).filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        notif = db_session.query(Notification).filter_by(id=notification_id, user_id=user_id).first()
        if notif and not notif.is_read:
            notif.is_read = True
            notif.read_at = datetime.utcnow()
            db_session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id: int):
        db_session.query(Notification).filter_by(user_id=user_id, is_read=False).update({
            Notification.is_read: True,
            Notification.read_at: datetime.utcnow()
        })
        db_session.commit()
