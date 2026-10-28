import pytest
from app.models.animal import Animal
from app.services.animal_service import AnimalService
from app.extensions import db_session


def test_create_animal_success(auth_users, test_farm_and_animal):
    farmer = auth_users['farmer1']
    farm = test_farm_and_animal['farm']

    new_animal = AnimalService.create_animal(
        farm_id=farm.id,
        owner_id=farmer.id,
        animal_tag="COW-NEW-99",
        species="Cow",
        breed="Holstein",
        sex="Female",
        estimated_age_months=24,
        weight_kg=480.0
    )

    assert new_animal.id is not None
    assert new_animal.animal_tag == "COW-NEW-99"
    assert new_animal.health_status == "Normal"


def test_duplicate_tag_rejected_on_same_farm(auth_users, test_farm_and_animal):
    farmer = auth_users['farmer1']
    farm = test_farm_and_animal['farm']
    existing = test_farm_and_animal['animal']

    with pytest.raises(ValueError, match="already exists"):
        AnimalService.create_animal(
            farm_id=farm.id,
            owner_id=farmer.id,
            animal_tag=existing.animal_tag,
            species="Cow"
        )


def test_update_animal(test_farm_and_animal):
    animal = test_farm_and_animal['animal']
    updated = AnimalService.update_animal(
        animal.id,
        animal_name="Daisy Updated",
        weight_kg=455.0,
        status="Sick"
    )

    assert updated.animal_name == "Daisy Updated"
    assert updated.weight_kg == 455.0
    assert updated.status == "Sick"


def test_animal_search_and_filter(auth_users, test_farm_and_animal):
    farmer = auth_users['farmer1']
    results = AnimalService.get_animals(farmer, search_query="Daisy")
    assert len(results) == 1
    assert results[0].animal_tag == "TEST-COW-01"

    # Filter by species
    cows = AnimalService.get_animals(farmer, species="Cow")
    assert len(cows) >= 1

    goats = AnimalService.get_animals(farmer, species="Goat")
    assert len(goats) == 0
