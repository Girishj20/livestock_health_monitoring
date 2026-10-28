import os
from flask import Flask, render_template, g, session
from config import config_by_name
from app.extensions import init_db, create_all_tables
from app.utils.security import generate_csrf_token, get_current_user
from app.services.notification_service import NotificationService


def create_app(config_name=None):
    """Application factory for Livestock Health Monitoring System."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    config_cls = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_cls)

    # Initialize extensions and database
    init_db(app)

    with app.app_context():
        # Ensure all models are imported and tables created
        from app import models as app_models
        create_all_tables()
        
        # Auto-seed initial reference data and demo accounts if needed (e.g. On Vercel /tmp)
        from app.utils.auto_seeder import ensure_initial_seed
        ensure_initial_seed()

    # Context processors for all Jinja templates
    @app.context_processor
    def inject_global_template_vars():
        user = get_current_user()
        unread_count = 0
        if user:
            try:
                unread_count = NotificationService.get_unread_count(user.id)
            except Exception:
                unread_count = 0

        return {
            'csrf_token': generate_csrf_token(),
            'current_user': user,
            'unread_notifications_count': unread_count,
            'app_name': 'Livestock Health Monitoring System'
        }

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.animals import animals_bp
    from app.routes.observations import observations_bp
    from app.routes.predictions import predictions_bp
    from app.routes.veterinary import veterinary_bp
    from app.routes.vaccinations import vaccinations_bp
    from app.routes.notifications import notifications_bp
    from app.routes.farms import farms_bp
    from app.routes.reports import reports_bp
    from app.routes.disease_library import disease_library_bp
    from app.routes.admin import admin_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(animals_bp)
    app.register_blueprint(observations_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(veterinary_bp)
    app.register_blueprint(vaccinations_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(farms_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(disease_library_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(settings_bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html', error=error), 500

    return app
