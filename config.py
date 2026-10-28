import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-livestock-health-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Check if running in Vercel or similar serverless container
    IS_VERCEL = bool(os.environ.get('VERCEL'))
    
    if IS_VERCEL:
        INSTANCE_PATH = '/tmp'
        default_db = 'sqlite:////tmp/livestock_health.db'
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
        default_db = f"sqlite:///{os.path.join(INSTANCE_PATH, 'livestock_health.db')}"
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'animals')

    os.makedirs(INSTANCE_PATH, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    raw_db_url = os.environ.get('DATABASE_URL', default_db)
    if raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = raw_db_url
    
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    
    # Machine Learning Models Directory
    MODEL_DIR = os.path.join(BASE_DIR, os.environ.get('MODEL_DIR', 'models'))
    
    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get('PERMANENT_SESSION_LIFETIME_DAYS', 7)))
    
    # Feature toggles
    SEED_SAMPLE_DATA = os.environ.get('SEED_SAMPLE_DATA', '1') == '1'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    # In-memory SQLite database for lightning fast, isolated test execution
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # Ensure a real secret key is enforced in production with a secure fallback
    SECRET_KEY = os.environ.get('SECRET_KEY', 'livestock-production-secret-key-2026')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
