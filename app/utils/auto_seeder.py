from datetime import datetime, date, timedelta
from app.extensions import db_session
from app.models.user import User
from app.models.reference import DiseaseReference, ModelRegistry
from app.models.farm import Farm, FarmMembership
from app.models.animal import Animal
from app.models.health_observation import HealthObservation
from app.models.vaccination import Vaccination

def ensure_initial_seed():
    """Ensure database has reference diseases, ML registry, and demo accounts/animals."""
    try:
        user_count = db_session.query(User).count()
        if user_count > 0:
            return

        # 1. Admin
        admin = User(
            full_name="System Administrator",
            email="admin@livestock.org",
            role="administrator",
            phone="+91 98765 43210",
            account_status="active"
        )
        admin.set_password("Admin@123")
        db_session.add(admin)

        # 2. Farmer
        farmer = User(
            full_name="Ramesh Kumar (Farmer)",
            email="farmer@greenpastures.com",
            role="farmer",
            phone="+91 98111 22334",
            account_status="active"
        )
        farmer.set_password("Farmer@123")
        db_session.add(farmer)

        # 3. Veterinarian
        vet = User(
            full_name="Dr. Anjali Sharma (Veterinarian)",
            email="vet@animalcare.org",
            role="veterinarian",
            phone="+91 98222 33445",
            account_status="active"
        )
        vet.set_password("Doctor@123")
        db_session.add(vet)
        db_session.commit()

        # 4. Disease References
        diseases = [
            {
                'disease_name': 'Mastitis',
                'applicable_species': 'Cow, Buffalo, Goat, Sheep',
                'category': 'Bacterial',
                'description': 'Inflammation of the mammary gland and udder tissue, predominantly bacterial.',
                'warning_signs': 'Swollen, warm, hard, or tender udder quarters; abnormal milk; elevated body temperature.',
                'prevention_information': 'Strict milking parlor hygiene; teat dip disinfectants; clean bedding.',
                'biosecurity_considerations': 'Milk infected cows last; isolate chronic carriers.',
                'when_to_call_vet': 'When fever exceeds 40°C, animal becomes recumbent, or quarter turns gangrenous.',
                'veterinary_reference': 'Merck Veterinary Manual - Mastitis in Large Animals',
                'reviewed_at': date(2026, 1, 15)
            },
            {
                'disease_name': 'Foot and Mouth Disease (FMD)',
                'applicable_species': 'Cow, Buffalo, Goat, Sheep',
                'category': 'Viral',
                'description': 'Highly contagious viral disease affecting cloven-hoofed domestic animals.',
                'warning_signs': 'High fever (40-41°C); vesicles/blisters on tongue, gums, feet; ropy salivation; lameness.',
                'prevention_information': 'Routine prophylactic vaccination every 6 months; animal movement control.',
                'biosecurity_considerations': 'Strict boundary disinfection; 4% sodium carbonate footbaths.',
                'when_to_call_vet': 'REPORT IMMEDIATELY: Notifiable transboundary animal disease.',
                'veterinary_reference': 'WOAH Terrestrial Manual - FMD Guidelines',
                'reviewed_at': date(2026, 2, 10)
            },
            {
                'disease_name': 'Lumpy Skin Disease (LSD)',
                'applicable_species': 'Cow, Buffalo',
                'category': 'Viral',
                'description': 'Vector-borne poxviral condition with nodular cutaneous lesions.',
                'warning_signs': 'Firm skin nodules (2-5 cm) over neck, limbs, udder; fever (>40°C); enlarged lymph nodes.',
                'prevention_information': 'Annual live-attenuated homologous LSD or goat pox vaccine; vector control.',
                'biosecurity_considerations': 'Vector netting; quarantine new animals.',
                'when_to_call_vet': 'Immediate reporting upon observing generalized nodular eruptions.',
                'veterinary_reference': 'FAO Manual on Lumpy Skin Disease for Veterinarians',
                'reviewed_at': date(2026, 1, 20)
            },
            {
                'disease_name': 'Bovine Brucellosis',
                'applicable_species': 'Cow, Buffalo',
                'category': 'Bacterial',
                'description': 'Chronic infectious bacterial disease causing abortion in late pregnancy.',
                'warning_signs': 'Late gestation abortion (7-8 months); retained placenta; severe metritis.',
                'prevention_information': 'Vaccinate female calves (4-8 months) with Brucella abortus Strain 19; test and segregate.',
                'biosecurity_considerations': 'ZOONOTIC: Causes undulant fever in humans. Always wear gloves.',
                'when_to_call_vet': 'Any abortion storm in dairy herds requires immediate serological testing.',
                'veterinary_reference': 'CDC / WHO Guidelines for Brucellosis Prevention',
                'reviewed_at': date(2026, 1, 5)
            }
        ]
        for d in diseases:
            db_session.add(DiseaseReference(**d))

        # 5. Model Registry
        models = [
            {'model_name': 'Multi-Species Disease Risk Classifier', 'species': 'Multi-Species', 'model_version': '1.0.0', 'model_path': 'models/livestock_disease_model.joblib', 'feature_schema': '{"numerical": 16, "categorical": 5}', 'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv', 'evaluation_metrics': '{"accuracy": 1.0}', 'status': 'Active'},
            {'model_name': 'Bovine (Cow) Specialized Risk Classifier', 'species': 'Cow', 'model_version': 'cow_v1.0.0', 'model_path': 'models/cow_disease_model.joblib', 'feature_schema': '{"numerical": 16, "categorical": 5}', 'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv', 'evaluation_metrics': '{"accuracy": 1.0}', 'status': 'Active'},
            {'model_name': 'Buffalo Specialized Risk Classifier', 'species': 'Buffalo', 'model_version': 'buffalo_v1.0.0', 'model_path': 'models/buffalo_disease_model.joblib', 'feature_schema': '{"numerical": 16, "categorical": 5}', 'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv', 'evaluation_metrics': '{"accuracy": 1.0}', 'status': 'Active'},
            {'model_name': 'Caprine (Goat) Specialized Risk Classifier', 'species': 'Goat', 'model_version': 'goat_v1.0.0', 'model_path': 'models/goat_disease_model.joblib', 'feature_schema': '{"numerical": 16, "categorical": 5}', 'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv', 'evaluation_metrics': '{"accuracy": 1.0}', 'status': 'Active'},
            {'model_name': 'Ovine (Sheep) Specialized Risk Classifier', 'species': 'Sheep', 'model_version': 'sheep_v1.0.0', 'model_path': 'models/sheep_disease_model.joblib', 'feature_schema': '{"numerical": 16, "categorical": 5}', 'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv', 'evaluation_metrics': '{"accuracy": 1.0}', 'status': 'Active'}
        ]
        for m in models:
            db_session.add(ModelRegistry(**m))
        db_session.commit()

        # 6. Farm & Animals
        farm = Farm(
            name="Green Pastures Dairy",
            code="FARM-GPD-01",
            location="Karnal District, Haryana",
            description="Specialized dairy farming cluster focusing on indigenous Gir cows and Murrah buffaloes.",
            owner_id=farmer.id
        )
        db_session.add(farm)
        db_session.flush()

        membership = FarmMembership(farm_id=farm.id, user_id=farmer.id, role="owner")
        db_session.add(membership)

        vet_membership = FarmMembership(farm_id=farm.id, user_id=vet.id, role="veterinarian")
        db_session.add(vet_membership)

        animals_data = [
            {'tag_id': 'COW-GIR-0101', 'name': 'Gauri', 'species': 'Cow', 'breed': 'Gir', 'sex': 'Female', 'date_of_birth': date(2021, 5, 12), 'weight_kg': 465.0, 'production_purpose': 'Dairy', 'current_health_status': 'Normal'},
            {'tag_id': 'COW-HF-0102', 'name': 'Lakshmi', 'species': 'Cow', 'breed': 'Holstein Friesian', 'sex': 'Female', 'date_of_birth': date(2022, 2, 18), 'weight_kg': 580.0, 'production_purpose': 'Dairy', 'current_health_status': 'Attention Required'},
            {'tag_id': 'BUF-MUR-0201', 'name': 'Shyamali', 'species': 'Buffalo', 'breed': 'Murrah', 'sex': 'Female', 'date_of_birth': date(2020, 8, 25), 'weight_kg': 610.0, 'production_purpose': 'Dairy', 'current_health_status': 'Monitoring Required'},
            {'tag_id': 'GOT-JAM-0301', 'name': 'Raja', 'species': 'Goat', 'breed': 'Jamnapari', 'sex': 'Male', 'date_of_birth': date(2023, 1, 10), 'weight_kg': 68.0, 'production_purpose': 'Breeding', 'current_health_status': 'Normal'},
            {'tag_id': 'SHP-MER-0401', 'name': 'Nandi', 'species': 'Sheep', 'breed': 'Merino', 'sex': 'Female', 'date_of_birth': date(2023, 4, 15), 'weight_kg': 52.0, 'production_purpose': 'Wool', 'current_health_status': 'Normal'}
        ]

        created_animals = []
        for ad in animals_data:
            animal = Animal(
                farm_id=farm.id,
                owner_id=farmer.id,
                **ad
            )
            db_session.add(animal)
            created_animals.append(animal)
        db_session.flush()

        # 7. Sample Observations
        obs1 = HealthObservation(
            animal_id=created_animals[0].id,
            recorded_by_user_id=farmer.id,
            observed_at=datetime.utcnow() - timedelta(hours=3),
            temperature=38.6,
            heart_rate=64,
            respiratory_rate=22,
            weight=465.0,
            mucous_membrane_status='Normal',
            body_condition_score=3.5,
            appetite_status='Normal',
            rumination_status='Normal',
            mobility_status='Normal',
            eye_discharge='None',
            nasal_discharge='None',
            feces_consistency='Normal',
            fever_status='Normal',
            health_urgency_level='Normal',
            clinical_notes='Animal alert, active, eating well and ruminating regularly.'
        )
        db_session.add(obs1)

        # 8. Sample Vaccination
        vac1 = Vaccination(
            animal_id=created_animals[0].id,
            administered_by_user_id=vet.id,
            vaccine_name='FMD Quadrivalent Oil Adjuvant',
            target_disease='Foot and Mouth Disease',
            dose_administered='3 ml',
            batch_number='FMD-2025-BATCH09',
            administered_date=date(2025, 11, 15),
            next_due_date=date(2026, 5, 15),
            status='Completed'
        )
        db_session.add(vac1)

        db_session.commit()
    except Exception as e:
        db_session.rollback()
