import pytest
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import db_session, Base, get_engine
from app.models.user import User
from app.models.farm import Farm
from app.models.animal import Animal


@pytest.fixture(scope='session')
def app():
    """Create and configure a testing Flask application."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def client(app):
    """Provide a test client with a clean database for each test function."""
    with app.app_context():
        # Create all tables
        engine = get_engine()
        Base.metadata.create_all(bind=engine)

        yield app.test_client()

        # Teardown: rollback and drop tables
        db_session.remove()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_users(client):
    """Seed test users with different roles."""
    admin = User(full_name="Admin Test", email="admin@test.org", role="administrator", account_status="active")
    admin.set_password("Admin@123")

    farmer1 = User(full_name="Farmer One", email="farmer1@test.org", role="farmer", account_status="active")
    farmer1.set_password("Farmer@123")

    farmer2 = User(full_name="Farmer Two", email="farmer2@test.org", role="farmer", account_status="active")
    farmer2.set_password("Farmer@123")

    vet = User(full_name="Vet Test", email="vet@test.org", role="veterinarian", account_status="active")
    vet.set_password("Doctor@123")

    db_session.add_all([admin, farmer1, farmer2, vet])
    db_session.commit()

    return {
        'admin': admin,
        'farmer1': farmer1,
        'farmer2': farmer2,
        'vet': vet
    }


@pytest.fixture
def test_farm_and_animal(auth_users):
    """Seed a sample farm and animal belonging to farmer1."""
    f1 = auth_users['farmer1']
    farm = Farm(farm_name="Test Valley Farm", owner_id=f1.id, location="Test District", farm_type="Dairy")
    db_session.add(farm)
    db_session.commit()

    animal = Animal(
        farm_id=farm.id,
        owner_id=f1.id,
        animal_tag="TEST-COW-01",
        animal_name="Daisy",
        species="Cow",
        breed="Jersey",
        sex="Female",
        estimated_age_months=36,
        weight_kg=430.0,
        production_purpose="Dairy",
        status="Active",
        health_status="Normal"
    )
    db_session.add(animal)
    db_session.commit()

    return {
        'farm': farm,
        'animal': animal
    }
