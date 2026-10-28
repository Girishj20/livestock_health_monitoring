"""
Realistic demonstration data seeder for Livestock Health Monitoring System.
Grounded in authentic livestock care, realistic animal tags, clinical conditions, and schedules.
"""
import os
import sys
import json
from datetime import datetime, date, timedelta

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import db_session
from app.models.user import User
from app.models.farm import Farm, FarmMembership
from app.models.animal import Animal
from app.models.health_observation import HealthObservation
from app.models.disease_assessment import DiseaseAssessment
from app.models.veterinary import VeterinaryVisit, Medication
from app.models.vaccination import Vaccination
from app.models.notification import Notification
from app.services.animal_service import AnimalService


def seed_demo_data():
    app = create_app()
    with app.app_context():
        print("Seeding demonstration data...")

        # 1. Create Demo Users
        users_config = [
            {
                'email': 'farmer@greenpastures.com',
                'full_name': 'Ramesh Kumar (Farmer)',
                'role': 'farmer',
                'password': 'Farmer@123',
                'phone': '+91 98111 22334'
            },
            {
                'email': 'vet@animalcare.org',
                'full_name': 'Anjali Sharma (Veterinarian)',
                'role': 'veterinarian',
                'password': 'Doctor@123',
                'phone': '+91 98222 33445'
            },
            {
                'email': 'manager@dairyhub.com',
                'full_name': 'Vikram Singh (Farm Manager)',
                'role': 'farm_manager',
                'password': 'Manager@123',
                'phone': '+91 98333 44556'
            }
        ]

        created_users = {}
        for ucfg in users_config:
            u = db_session.query(User).filter_by(email=ucfg['email']).first()
            if not u:
                u = User(
                    full_name=ucfg['full_name'],
                    email=ucfg['email'],
                    role=ucfg['role'],
                    phone=ucfg['phone'],
                    account_status='active'
                )
                u.set_password(ucfg['password'])
                db_session.add(u)
                db_session.commit()
                print(f"Created user: {ucfg['email']}")
            created_users[ucfg['email']] = u

        farmer = created_users['farmer@greenpastures.com']
        vet = created_users['vet@animalcare.org']
        manager = created_users['manager@dairyhub.com']

        # 2. Create Farms
        farm1 = db_session.query(Farm).filter_by(farm_name='Green Pastures Dairy Farm').first()
        if not farm1:
            farm1 = Farm(
                farm_name='Green Pastures Dairy Farm',
                owner_id=farmer.id,
                location='Karnal, Haryana, India',
                farm_type='Dairy',
                status='active'
            )
            db_session.add(farm1)
            db_session.commit()
            print(f"Created Farm: {farm1.farm_name}")

            # Assign manager membership
            mem = FarmMembership(
                farm_id=farm1.id,
                user_id=manager.id,
                permission_level='admin'
            )
            db_session.add(mem)
            db_session.commit()

        farm2 = db_session.query(Farm).filter_by(farm_name='Highland Ruminant Ranch').first()
        if not farm2:
            farm2 = Farm(
                farm_name='Highland Ruminant Ranch',
                owner_id=farmer.id,
                location='Jaipur, Rajasthan, India',
                farm_type='Mixed',
                status='active'
            )
            db_session.add(farm2)
            db_session.commit()
            print(f"Created Farm: {farm2.farm_name}")

        # 3. Create Sample Animals
        animals_spec = [
            # Cows
            {
                'farm_id': farm1.id,
                'animal_tag': 'COW-101',
                'animal_name': 'Kamdhenu',
                'species': 'Cow',
                'breed': 'Holstein-Friesian Cross',
                'sex': 'Female',
                'estimated_age_months': 48,
                'weight_kg': 540.0,
                'production_purpose': 'Dairy',
                'status': 'Active',
                'health_status': 'Normal',
                'notes': 'High-yield milch cow, second lactation.'
            },
            {
                'farm_id': farm1.id,
                'animal_tag': 'COW-102',
                'animal_name': 'Gauri',
                'species': 'Cow',
                'breed': 'Jersey',
                'sex': 'Female',
                'estimated_age_months': 36,
                'weight_kg': 420.0,
                'production_purpose': 'Dairy',
                'status': 'Active',
                'health_status': 'Attention Required',
                'notes': 'Showing signs of left hindquarter udder swelling.'
            },
            {
                'farm_id': farm1.id,
                'animal_tag': 'COW-103',
                'animal_name': 'Radha',
                'species': 'Cow',
                'breed': 'Sahiwal',
                'sex': 'Female',
                'estimated_age_months': 60,
                'weight_kg': 480.0,
                'production_purpose': 'Dairy',
                'status': 'Active',
                'health_status': 'Normal',
                'notes': 'Indigenous breed, heat tolerant, healthy.'
            },
            # Buffaloes
            {
                'farm_id': farm1.id,
                'animal_tag': 'BUF-201',
                'animal_name': 'Murrah Queen',
                'species': 'Buffalo',
                'breed': 'Murrah',
                'sex': 'Female',
                'estimated_age_months': 54,
                'weight_kg': 610.0,
                'production_purpose': 'Dairy',
                'status': 'Active',
                'health_status': 'Urgent Veterinary Attention',
                'notes': 'Sudden acute abdominal distension and discomfort observed after rich concentrate feeding.'
            },
            {
                'farm_id': farm1.id,
                'animal_tag': 'BUF-202',
                'animal_name': 'Kalyani',
                'species': 'Buffalo',
                'breed': 'Nili-Ravi',
                'sex': 'Female',
                'estimated_age_months': 42,
                'weight_kg': 570.0,
                'production_purpose': 'Dairy',
                'status': 'Active',
                'health_status': 'Normal',
                'notes': 'Steady daily production of 14 liters.'
            },
            # Goats
            {
                'farm_id': farm2.id,
                'animal_tag': 'GT-301',
                'animal_name': 'Champa',
                'species': 'Goat',
                'breed': 'Beetal',
                'sex': 'Female',
                'estimated_age_months': 24,
                'weight_kg': 42.0,
                'production_purpose': 'Dairy',
                'status': 'Active',
                'health_status': 'Monitoring Required',
                'notes': 'Mild coughing and nasal clear discharge observed in the morning.'
            },
            {
                'farm_id': farm2.id,
                'animal_tag': 'GT-302',
                'animal_name': 'Sultan',
                'species': 'Goat',
                'breed': 'Boer Cross',
                'sex': 'Male',
                'estimated_age_months': 18,
                'weight_kg': 68.0,
                'production_purpose': 'Breeding',
                'status': 'Active',
                'health_status': 'Normal',
                'notes': 'Active breeding buck, excellent body condition.'
            },
            # Sheep
            {
                'farm_id': farm2.id,
                'animal_tag': 'SH-401',
                'animal_name': 'Bella',
                'species': 'Sheep',
                'breed': 'Dorper',
                'sex': 'Female',
                'estimated_age_months': 28,
                'weight_kg': 52.0,
                'production_purpose': 'Meat',
                'status': 'Active',
                'health_status': 'Attention Required',
                'notes': 'Pale conjunctiva and loose stool; suspected internal parasites.'
            },
            {
                'farm_id': farm2.id,
                'animal_tag': 'SH-402',
                'animal_name': 'Rambo',
                'species': 'Sheep',
                'breed': 'Marwari',
                'sex': 'Male',
                'estimated_age_months': 36,
                'weight_kg': 65.0,
                'production_purpose': 'Wool',
                'status': 'Active',
                'health_status': 'Normal',
                'notes': 'Recently sheared; robust appetite.'
            }
        ]

        saved_animals = {}
        for aspec in animals_spec:
            a = db_session.query(Animal).filter_by(animal_tag=aspec['animal_tag']).first()
            if not a:
                a = Animal(
                    farm_id=aspec['farm_id'],
                    owner_id=farmer.id,
                    animal_tag=aspec['animal_tag'],
                    animal_name=aspec['animal_name'],
                    species=aspec['species'],
                    breed=aspec['breed'],
                    sex=aspec['sex'],
                    estimated_age_months=aspec['estimated_age_months'],
                    weight_kg=aspec['weight_kg'],
                    production_purpose=aspec['production_purpose'],
                    status=aspec['status'],
                    health_status=aspec['health_status'],
                    notes=aspec['notes'],
                    created_at=datetime.utcnow() - timedelta(days=60)
                )
                db_session.add(a)
                db_session.commit()
                print(f"Created Animal: {a.animal_tag} ({a.species})")
            saved_animals[aspec['animal_tag']] = a

        # 4. Create Observations and Timeline Records
        now = datetime.utcnow()

        # COW-101 (Healthy Baseline)
        obs_c101 = HealthObservation(
            animal_id=saved_animals['COW-101'].id,
            recorded_by=farmer.id,
            observed_at=now - timedelta(hours=4),
            temperature_c=38.6,
            heart_rate_bpm=64.0,
            respiratory_rate_bpm=28.0,
            weight_kg=540.0,
            food_intake='Normal',
            water_intake='Normal',
            walking_activity='Normal',
            rumination='Normal',
            milk_production=22.5,
            body_condition_score=3.5,
            symptoms=json.dumps([]),
            additional_notes='Calm, chewing cud normally, full milk letdown.',
            data_source='manual'
        )
        db_session.add(obs_c101)

        # COW-102 (Mastitis Case)
        obs_c102 = HealthObservation(
            animal_id=saved_animals['COW-102'].id,
            recorded_by=farmer.id,
            observed_at=now - timedelta(hours=3),
            temperature_c=39.9,
            heart_rate_bpm=86.0,
            respiratory_rate_bpm=34.0,
            weight_kg=420.0,
            food_intake='Reduced',
            water_intake='Normal',
            walking_activity='Normal',
            rumination='Reduced',
            milk_production=9.0,
            body_condition_score=3.0,
            symptoms=json.dumps(['Swelling / Udder heat', 'Reduced milk production', 'Fever or elevated temperature']),
            additional_notes='Left rear quarter hard and hot. Clots observed in foremilk.',
            data_source='manual'
        )
        db_session.add(obs_c102)

        # BUF-201 (Bloat Emergency)
        obs_b201 = HealthObservation(
            animal_id=saved_animals['BUF-201'].id,
            recorded_by=manager.id,
            observed_at=now - timedelta(hours=1),
            temperature_c=38.9,
            heart_rate_bpm=92.0,
            respiratory_rate_bpm=48.0,
            weight_kg=610.0,
            food_intake='Anorexic',
            water_intake='None',
            walking_activity='Recumbent / Unable to Stand',
            rumination='Absent',
            milk_production=0.0,
            body_condition_score=3.5,
            symptoms=json.dumps(['Acute Bloat / Severe Abdominal Distension', 'Severe Respiratory Distress', 'Recumbent / Unable to Stand']),
            additional_notes='EMERGENCY: Left paralumbar fossa drum-tight. Animal in respiratory distress.',
            data_source='manual'
        )
        db_session.add(obs_b201)

        # GT-301 (Respiratory Case)
        obs_g301 = HealthObservation(
            animal_id=saved_animals['GT-301'].id,
            recorded_by=farmer.id,
            observed_at=now - timedelta(hours=5),
            temperature_c=40.4,
            heart_rate_bpm=110.0,
            respiratory_rate_bpm=38.0,
            weight_kg=42.0,
            food_intake='Reduced',
            water_intake='Normal',
            walking_activity='Sluggish',
            rumination='Normal',
            body_condition_score=3.0,
            symptoms=json.dumps(['Coughing', 'Nasal discharge', 'Fever or elevated temperature']),
            additional_notes='Serous nasal discharge, frequent dry cough.',
            data_source='manual'
        )
        db_session.add(obs_g301)

        # SH-401 (Parasitic Case)
        obs_s401 = HealthObservation(
            animal_id=saved_animals['SH-401'].id,
            recorded_by=farmer.id,
            observed_at=now - timedelta(hours=6),
            temperature_c=38.9,
            heart_rate_bpm=94.0,
            respiratory_rate_bpm=26.0,
            weight_kg=52.0,
            food_intake='Reduced',
            water_intake='Normal',
            walking_activity='Sluggish',
            rumination='Normal',
            body_condition_score=2.0,
            symptoms=json.dumps(['Diarrhea', 'Unusual / Depressed behavior']),
            additional_notes='Submandibular edema (bottle jaw) noted; conjunctiva markedly pale.',
            data_source='manual'
        )
        db_session.add(obs_s401)

        db_session.commit()

        # 5. Seed Machine Learning Assessments
        ass_c102 = DiseaseAssessment(
            animal_id=saved_animals['COW-102'].id,
            initiated_by=farmer.id,
            model_name='Cow Disease Risk Classifier',
            model_version='cow_v1.0.0',
            input_snapshot=json.dumps({
                'species': 'Cow', 'temperature_c': 39.9, 'heart_rate_bpm': 86.0,
                'swelling_flag': 1, 'abnormal_milk_flag': 1, 'fever_flag': 1
            }),
            predicted_class='Mastitis',
            prediction_scores=json.dumps({'Mastitis': 0.88, 'Healthy / Normal': 0.04, 'FMD': 0.08}),
            data_quality_status='Complete',
            assessment_status='Completed',
            risk_level='Moderate',
            urgency_override=False,
            created_at=now - timedelta(hours=3)
        )
        db_session.add(ass_c102)

        ass_b201 = DiseaseAssessment(
            animal_id=saved_animals['BUF-201'].id,
            initiated_by=manager.id,
            model_name='Buffalo Specialized Risk Classifier',
            model_version='buffalo_v1.0.0',
            input_snapshot=json.dumps({
                'species': 'Buffalo', 'temperature_c': 38.9, 'bloat_distension_flag': 1,
                'walking_activity': 'Recumbent'
            }),
            predicted_class='Bloat (Tympanites)',
            prediction_scores=json.dumps({'Bloat (Tympanites)': 0.95, 'Enterotoxemia': 0.05}),
            data_quality_status='Complete',
            assessment_status='Completed',
            risk_level='Critical',
            urgency_override=True,
            created_at=now - timedelta(hours=1)
        )
        db_session.add(ass_b201)

        db_session.commit()

        # 6. Seed Veterinary Consultation & Prescriptions
        visit1 = VeterinaryVisit(
            animal_id=saved_animals['COW-102'].id,
            veterinarian_id=vet.id,
            vet_name='Dr. Anjali Sharma',
            visit_date=now - timedelta(days=1),
            reason='Acute left rear quarter mastitis consultation',
            clinical_findings='Rectal temp 39.9°C. Marked erythema and edema on left rear teat. California Mastitis Test strongly positive (3+).',
            veterinarian_diagnosis='Acute Clinical Coliform Mastitis',
            treatment_notes='Intramammary antibiotic infusion administered. Prescribed supportive anti-inflammatory therapy. Milk quarter stripped every 3 hours.',
            follow_up_date=date.today() + timedelta(days=2),
            outcome_notes='Monitoring quarter texture and temperature daily.'
        )
        db_session.add(visit1)
        db_session.commit()

        med1 = Medication(
            animal_id=saved_animals['COW-102'].id,
            veterinary_visit_id=visit1.id,
            medication_name='Ceftiofur Sodium (Intramammary Infusion)',
            dosage_instructions='Infuse one syringe into affected quarter every 24 hours for 3 days after milking.',
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=2),
            prescribing_veterinarian='Dr. Anjali Sharma',
            status='Active'
        )
        db_session.add(med1)

        med2 = Medication(
            animal_id=saved_animals['COW-102'].id,
            veterinary_visit_id=visit1.id,
            medication_name='Meloxicam (Oral Susp. / Injectable)',
            dosage_instructions='0.5 mg/kg once daily for pain and anti-inflammatory relief.',
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=2),
            prescribing_veterinarian='Dr. Anjali Sharma',
            status='Active'
        )
        db_session.add(med2)

        # 7. Seed Vaccinations
        vacs = [
            {
                'animal_id': saved_animals['COW-101'].id,
                'vaccine_name': 'FMD Oil Adjuvant Vaccine (Raksha-Ovac)',
                'vaccination_date': date.today() - timedelta(days=150),
                'next_due_date': date.today() + timedelta(days=30),
                'administered_by': 'Dr. Anjali Sharma',
                'batch_reference': 'FMD-2025-BATCH-44',
                'status': 'Upcoming',
                'notes': 'Bi-annual prophylactic dose.'
            },
            {
                'animal_id': saved_animals['COW-103'].id,
                'vaccine_name': 'Brucella Abortus S19 Live Vaccine',
                'vaccination_date': date.today() - timedelta(days=365),
                'next_due_date': None,
                'administered_by': 'Veterinary Hospital Karnal',
                'batch_reference': 'BRU-S19-901',
                'status': 'Completed',
                'notes': 'Calfhood vaccination completed.'
            },
            {
                'animal_id': saved_animals['GT-301'].id,
                'vaccine_name': 'PPR Vaccine (Peste des Petits Ruminants)',
                'vaccination_date': date.today() - timedelta(days=300),
                'next_due_date': date.today() - timedelta(days=5),
                'administered_by': 'Dr. Anjali Sharma',
                'batch_reference': 'PPR-LIV-092',
                'status': 'Overdue',
                'notes': 'Annual booster is overdue by 5 days.'
            },
            {
                'animal_id': saved_animals['SH-401'].id,
                'vaccine_name': 'Enterotoxemia (Clostridium perfringens D) Vaccine',
                'vaccination_date': date.today() - timedelta(days=180),
                'next_due_date': date.today(),
                'administered_by': 'Dr. Anjali Sharma',
                'batch_reference': 'ET-VAC-218',
                'status': 'Due Today',
                'notes': 'Pre-monsoon booster due today.'
            }
        ]

        for vcfg in vacs:
            v = Vaccination(**vcfg)
            db_session.add(v)

        # 8. Seed Notifications
        notifs = [
            {
                'user_id': farmer.id,
                'animal_id': saved_animals['BUF-201'].id,
                'title': 'CRITICAL ALERT: Buffalo BUF-201 Bloat Emergency',
                'message': 'Severe abdominal distension and recumbency observed. Immediate veterinary intubation or trocarization required.',
                'priority': 'Urgent',
                'notification_type': 'Vital Warning',
                'link_url': f"/animals/{saved_animals['BUF-201'].id}"
            },
            {
                'user_id': farmer.id,
                'animal_id': saved_animals['COW-102'].id,
                'title': 'Health Alert: Cow COW-102 Mastitis Detected',
                'message': 'High fever (39.9°C) and swollen udder quarter detected. Estimated risk tier: Moderate.',
                'priority': 'High',
                'notification_type': 'ML Risk Alert',
                'link_url': f"/animals/{saved_animals['COW-102'].id}"
            },
            {
                'user_id': farmer.id,
                'animal_id': saved_animals['SH-401'].id,
                'title': 'Vaccination Due Today: SH-401 Enterotoxemia',
                'message': 'Booster dose for Clostridium perfringens Enterotoxemia is scheduled for today.',
                'priority': 'Medium',
                'notification_type': 'Vaccine Reminder',
                'link_url': '/vaccinations'
            },
            {
                'user_id': farmer.id,
                'animal_id': saved_animals['GT-301'].id,
                'title': 'Vaccination Overdue: GT-301 PPR Vaccine',
                'message': 'Peste des Petits Ruminants (PPR) annual booster is 5 days overdue.',
                'priority': 'High',
                'notification_type': 'Vaccine Reminder',
                'link_url': '/vaccinations'
            }
        ]

        for ncfg in notifs:
            n = Notification(**ncfg, is_read=False, created_at=datetime.utcnow() - timedelta(hours=2))
            db_session.add(n)

        db_session.commit()
        print("Successfully seeded realistic livestock demonstration data!")


if __name__ == '__main__':
    seed_demo_data()
