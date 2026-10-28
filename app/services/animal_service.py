from datetime import datetime, date
from sqlalchemy import or_
from app.extensions import db_session
from app.models.animal import Animal
from app.models.farm import Farm, FarmMembership
from app.services.validation_service import ValidationService


class AnimalService:
    """Manages animal lifecycle, registration, queries, and health status updates."""

    @staticmethod
    def get_animal(animal_id: int) -> Animal:
        return db_session.get(Animal, animal_id)

    @staticmethod
    def get_animals(user, search_query=None, species=None, status=None, health_status=None, farm_id=None):
        """Query animals visible to user with optional filters."""
        query = db_session.query(Animal)

        # Enforce role-based data isolation
        if not (user.is_admin or user.is_veterinarian):
            # Farmer / Manager: Only animals belonging to their owned farms or member farms
            owned_farm_ids = [f.id for f in user.owned_farms]
            member_farm_ids = [m.farm_id for m in user.farm_memberships]
            allowed_farm_ids = list(set(owned_farm_ids + member_farm_ids))
            if not allowed_farm_ids:
                return []
            query = query.filter(Animal.farm_id.in_(allowed_farm_ids))

        # Apply search and filters
        if farm_id:
            query = query.filter(Animal.farm_id == farm_id)

        if species and species != 'All':
            query = query.filter(Animal.species == species)

        if status and status != 'All':
            query = query.filter(Animal.status == status)

        if health_status and health_status != 'All':
            query = query.filter(Animal.health_status == health_status)

        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    Animal.animal_tag.ilike(term),
                    Animal.animal_name.ilike(term),
                    Animal.breed.ilike(term)
                )
            )

        return query.order_by(Animal.updated_at.desc()).all()

    @staticmethod
    def create_animal(farm_id: int, owner_id: int, animal_tag: str, species: str,
                      animal_name=None, breed=None, sex='Female', date_of_birth=None,
                      estimated_age_months=None, weight_kg=None, production_purpose='Dairy',
                      image_path=None, notes=None) -> Animal:
        """Register a new animal."""
        # Check duplicate tag within same farm
        existing = db_session.query(Animal).filter_by(farm_id=farm_id, animal_tag=animal_tag).first()
        if existing:
            raise ValueError(f"An animal with tag '{animal_tag}' already exists on this farm.")

        animal = Animal(
            farm_id=farm_id,
            owner_id=owner_id,
            animal_tag=animal_tag.strip().upper(),
            animal_name=animal_name.strip() if animal_name else None,
            species=species,
            breed=breed.strip() if breed else None,
            sex=sex,
            date_of_birth=date_of_birth,
            estimated_age_months=estimated_age_months,
            weight_kg=weight_kg,
            production_purpose=production_purpose,
            image_path=image_path,
            status='Active',
            health_status='Normal',
            notes=notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(animal)
        db_session.commit()
        return animal

    @staticmethod
    def update_animal(animal_id: int, **kwargs) -> Animal:
        """Update animal profile details."""
        animal = db_session.get(Animal, animal_id)
        if not animal:
            raise ValueError(f"Animal #{animal_id} not found.")

        for key, val in kwargs.items():
            if hasattr(animal, key) and key not in ('id', 'created_at'):
                setattr(animal, key, val)

        animal.updated_at = datetime.utcnow()
        db_session.commit()
        return animal

    @staticmethod
    def refresh_animal_health_status(animal_id: int) -> str:
        """Recalculate and update the overall health status of an animal from latest records."""
        animal = db_session.get(Animal, animal_id)
        if not animal:
            return 'Normal'

        latest_obs = animal.latest_observation
        if not latest_obs:
            animal.health_status = 'Normal'
            db_session.commit()
            return 'Normal'

        obs_dict = {
            'temperature_c': latest_obs.temperature_c,
            'heart_rate_bpm': latest_obs.heart_rate_bpm,
            'respiratory_rate_bpm': latest_obs.respiratory_rate_bpm,
            'food_intake': latest_obs.food_intake,
            'walking_activity': latest_obs.walking_activity,
            'rumination': latest_obs.rumination,
            'symptoms': latest_obs.symptoms_list
        }

        new_status = ValidationService.evaluate_overall_health_status(animal.species, obs_dict)
        animal.health_status = new_status
        db_session.commit()
        return new_status
