from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.notification_service import NotificationService
from app.utils.security import login_required, get_current_user, validate_csrf

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@login_required
def index():
    user = get_current_user()
    notifications = NotificationService.get_user_notifications(user.id, limit=50)
    unread_count = NotificationService.get_unread_count(user.id)
    return render_template('notifications/index.html', notifications=notifications, unread_count=unread_count)


@notifications_bp.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    validate_csrf()
    user = get_current_user()
    NotificationService.mark_as_read(id, user.id)
    next_url = request.args.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    validate_csrf()
    user = get_current_user()
    NotificationService.mark_all_as_read(user.id)
    flash("All notifications marked as read.", "info")
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/api/notifications/unread-count')
@login_required
def unread_count_api():
    user = get_current_user()
    count = NotificationService.get_unread_count(user.id)
    return jsonify({'unread_count': count})
