import os
import uuid
from flask import request
from werkzeug.utils import secure_filename
from app.extensions import db_session
from app.models.reference import AuditLog


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Validate file extension against allowed set."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_image(file_storage, target_folder: str, allowed_extensions: set = None) -> str:
    """Safely validate and save uploaded image with unique UUID name."""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        
    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename, allowed_extensions):
        raise ValueError("Invalid image file extension. Allowed: PNG, JPG, JPEG, WEBP.")
        
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(target_folder, exist_ok=True)
    full_path = os.path.join(target_folder, unique_filename)
    file_storage.save(full_path)
    
    # Return path relative to static/
    return f"uploads/animals/{unique_filename}"


def log_audit(actor=None, action: str = "", entity_type: str = "", entity_id: int = None, details: str = ""):
    """Record an action in the system audit logs."""
    try:
        actor_id = actor.id if actor else None
        actor_name = actor.full_name if actor else "System"
        ip_addr = request.remote_addr if request else "127.0.0.1"
        
        audit = AuditLog(
            actor_id=actor_id,
            actor_name=actor_name,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_addr
        )
        db_session.add(audit)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        # Fail silently for audit logging to not block main operation
        print(f"Audit log error: {e}")
