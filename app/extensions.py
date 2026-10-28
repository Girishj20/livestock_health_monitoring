"""
Database extensions and ORM initialization for Livestock Health Monitoring System.
Uses pure SQLAlchemy 2.0 with thread-local scoped sessions.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy database models."""
    pass


# Global thread-safe scoped session
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
_engine = None


def init_db(app):
    """Initialize database engine, bind session, and configure app teardown."""
    global _engine
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    # Configure SQLite-specific engine arguments if applicable
    engine_kwargs = {"echo": False, "future": True}
    if db_uri.startswith('sqlite:'):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        
    _engine = create_engine(db_uri, **engine_kwargs)
    db_session.configure(bind=_engine)
    
    # Attach engine to Base metadata
    Base.metadata.bind = _engine
    
    # Automatically release session at end of request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
        
    return _engine


def get_engine():
    """Retrieve active SQLAlchemy engine."""
    return _engine


def create_all_tables():
    """Create all registered database tables."""
    if _engine is not None:
        Base.metadata.create_all(bind=_engine)
