"""
Database initialization and reference data setup for Livestock Health Monitoring System.
"""
import os
import sys
from datetime import datetime, date

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import db_session, create_all_tables
from app.models.user import User
from app.models.reference import DiseaseReference, ModelRegistry


def init_database():
    app = create_app()
    with app.app_context():
        print("Creating all database tables...")
        create_all_tables()

        # 1. Initialize Default Administrator Account
        admin_email = "admin@livestock.org"
        admin = db_session.query(User).filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                full_name="System Administrator",
                email=admin_email,
                role="administrator",
                phone="+91 98765 43210",
                account_status="active"
            )
            admin.set_password("Admin@123")
            db_session.add(admin)
            print(f"Created Administrator account: {admin_email} (Password: Admin@123)")

        # 2. Seed Disease Reference Library
        diseases = [
            {
                'disease_name': 'Mastitis',
                'applicable_species': 'Cow, Buffalo, Goat, Sheep',
                'category': 'Bacterial',
                'description': 'Inflammation of the mammary gland and udder tissue, predominantly caused by bacterial pathogens such as Staphylococcus aureus, Streptococcus uberis, or Escherichia coli. It causes severe economic losses through decreased milk production and discarded milk.',
                'warning_signs': 'Swollen, warm, hard, or tender udder quarters; abnormal milk appearance (flakes, clots, watery, blood-tinged); reduced milk yield; elevated body temperature; loss of appetite in systemic cases.',
                'prevention_information': 'Adhere to strict milking parlor hygiene; use pre- and post-milking teat dip disinfectants; sanitize milking equipment; provide clean, dry bedding; practice strategic dry-cow antibiotic therapy under veterinary direction.',
                'biosecurity_considerations': 'Milk infected cows last; isolate chronic carriers; cull non-responsive quarters or chronics; maintain clean stalls.',
                'when_to_call_vet': 'Immediate veterinary intervention is indicated when systemic fever exceeds 40°C, the animal becomes recumbent, or a quarter turns cold, purplish, or gangrenous.',
                'veterinary_reference': 'Merck Veterinary Manual - Mastitis in Large Animals (11th Ed.)',
                'reviewed_at': date(2026, 1, 15)
            },
            {
                'disease_name': 'Foot and Mouth Disease (FMD)',
                'applicable_species': 'Cow, Buffalo, Goat, Sheep',
                'category': 'Viral',
                'description': 'A highly contagious viral disease affecting cloven-hoofed domestic animals caused by an Aphthovirus (family Picornaviridae). Leads to high morbidity, severe pain, and production collapse.',
                'warning_signs': 'High fever (40-41°C); vesicles/blisters on the tongue, dental pad, gums, interdigital cleft, and teats; profuse ropy salivation and smacking of lips; severe acute lameness; dramatic drop in milk production.',
                'prevention_information': 'Routine prophylactic vaccination according to national programs (every 6 months); strict animal movement restrictions; quarantine newly purchased stock for 30 days.',
                'biosecurity_considerations': 'Strict boundary disinfection; footbaths containing 4% sodium carbonate or 0.2% citric acid; prohibition of untreated swill feeding.',
                'when_to_call_vet': 'REPORT IMMEDIATELY: FMD is a legally notifiable transboundary animal disease. Any suspicion of oral or foot vesicles requires emergency notification to government veterinary authorities.',
                'veterinary_reference': 'World Organisation for Animal Health (WOAH) Terrestrial Manual - FMD Guidelines',
                'reviewed_at': date(2026, 2, 10)
            },
            {
                'disease_name': 'Lumpy Skin Disease (LSD)',
                'applicable_species': 'Cow, Buffalo',
                'category': 'Viral',
                'description': 'An infectious vector-borne poxviral condition caused by Neethling virus (genus Capripoxvirus). Characterized by nodular cutaneous lesions, systemic fever, and lymphadenopathy.',
                'warning_signs': 'Firm, circumscribed skin nodules (2-5 cm) over the neck, limbs, udder, and perineum; high initial fever (>40°C); enlarged superficial lymph nodes; edema in brisket and limbs; ocular and nasal discharge.',
                'prevention_information': 'Prophylactic homologous live attenuated Neethling strain vaccination; aggressive vector control against biting flies (Stomoxys), mosquitoes, and ticks; screen housing where feasible.',
                'biosecurity_considerations': 'Isolate affected herds; quarantine area movement; sanitize needles and equipment between animals.',
                'when_to_call_vet': 'Consult veterinarian immediately for symptomatic supportive therapy (antibiotics for secondary infections, NSAIDs, wound care).',
                'veterinary_reference': 'FAO Animal Production and Health Manual - Lumpy Skin Disease Field Manual',
                'reviewed_at': date(2026, 3, 5)
            },
            {
                'disease_name': 'Bovine Respiratory Disease (BRD) / Pneumonia',
                'applicable_species': 'Cow, Buffalo, Goat, Sheep',
                'category': 'Multifactorial',
                'description': 'A multifactorial pulmonary syndrome ("shipping fever") involving viral precursors (IBR, BVDV, BRSV, PI3) followed by secondary bacterial invasion (Mannheimia haemolytica, Pasteurella multocida).',
                'warning_signs': 'Rapid, shallow, or labored abdominal respiration; persistent coughing; mucopurulent nasal discharge; elevated rectal temperature (40-41.5°C); depressed demeanor with head held low; anorexia.',
                'prevention_information': 'Vaccination against common respiratory pathogens prior to weaning/transport; eliminate overcrowding; provide adequate ventilation without drafts; minimize commingling stress.',
                'biosecurity_considerations': 'Quarantine newly arrived livestock for 21-28 days; segregate sick calves or young stock immediately.',
                'when_to_call_vet': 'Urgent attention required within 24 hours of respiratory distress or high fever to start targeted veterinary antimicrobial and anti-inflammatory therapy.',
                'veterinary_reference': 'Merck Veterinary Manual - Respiratory Disease in Cattle',
                'reviewed_at': date(2026, 1, 20)
            },
            {
                'disease_name': 'Bloat (Ruminal Tympanites)',
                'applicable_species': 'Cow, Buffalo, Goat, Sheep',
                'category': 'Metabolic',
                'description': 'An acute or chronic distension of the rumen caused by abnormal accumulation of fermentation gases, either as free gas (obstructive) or stable persistent froth (frothy bloat).',
                'warning_signs': 'Marked distension of the left paralumbar fossa (left flank); severe abdominal discomfort, kicking at belly, frequent vocalization; dyspnea with open-mouth breathing; cessation of rumination; collapse.',
                'prevention_information': 'Avoid sudden turnout onto lush leguminous pastures (clover/alfalfa); feed dry roughage/hay before grazing; introduce grain concentrate gradually; administer antifoaming surfactants.',
                'biosecurity_considerations': 'Pasture management; limit access to rich frosted legumes; manage feed trough delivery.',
                'when_to_call_vet': 'EMERGENCY: Animal can die of suffocation within hours. If left flank is drum-tight, respiratory distress is evident, or animal collapses, emergency veterinary trocarization or intubation is mandatory.',
                'veterinary_reference': 'Merck Veterinary Manual - Ruminal Tympany in Ruminants',
                'reviewed_at': date(2026, 2, 28)
            },
            {
                'disease_name': 'Enterotoxemia / Pulpy Kidney',
                'applicable_species': 'Goat, Sheep, Cow',
                'category': 'Bacterial',
                'description': 'A rapidly fatal acute toxemia caused by Clostridium perfringens type D multiplying in the intestines under conditions of sudden starch/grain overload.',
                'warning_signs': 'Sudden recumbency; convulsions, opisthotonos (head retracted); tooth grinding; watery/hemorrhagic diarrhea; sudden death with minimal prior signs.',
                'prevention_information': 'Routine Clostridial vaccination (CD&T) given annually; avoid abrupt shifts to high-carbohydrate grain rations; supply consistent fiber.',
                'biosecurity_considerations': 'Disposal of carcasses by deep burial or incineration; strict feed bunks sanitation.',
                'when_to_call_vet': 'Immediate veterinary care required for antitoxin administration and fluid support; urgent vaccination of remaining herd.',
                'veterinary_reference': 'FAO Veterinary Clinical Manual - Clostridial Diseases of Small Ruminants',
                'reviewed_at': date(2026, 3, 1)
            },
            {
                'disease_name': 'Parasitic Gastroenteritis',
                'applicable_species': 'Goat, Sheep, Cow, Buffalo',
                'category': 'Parasitic',
                'description': 'Helminth infection primarily caused by Haemonchus contortus (barber pole worm), Ostertagia ostertagi, and Trichostrongylus species damaging gastrointestinal mucosa.',
                'warning_signs': 'Pale mucous membranes (severe anemia); submandibular edema ("bottle jaw"); chronic diarrhea or loose feces; unthriftiness and rough hair coat; emaciation.',
                'prevention_information': 'Targeted selective anthelmintic treatment using FAMACHA eye mucous membrane scoring; rotational grazing; pasture resting.',
                'biosecurity_considerations': 'Quarantine deworming of new additions; avoid overstocking pastures.',
                'when_to_call_vet': 'Consult veterinarian if multiple animals exhibit pale conjunctiva or bottle jaw for fecal egg count and targeted dewormer selection.',
                'veterinary_reference': 'FAO Parasitology Guide - Nematode Management in Grazing Ruminants',
                'reviewed_at': date(2026, 1, 10)
            }
        ]

        for d in diseases:
            existing = db_session.query(DiseaseReference).filter_by(disease_name=d['disease_name']).first()
            if not existing:
                ref = DiseaseReference(**d)
                db_session.add(ref)
                print(f"Added Disease Reference: {d['disease_name']}")

        # 3. Register Trained Machine Learning Models in Registry
        models = [
            {
                'model_name': 'Multi-Species Disease Risk Classifier',
                'species': 'Multi-Species',
                'model_version': '1.0.0',
                'model_path': 'models/livestock_disease_model.joblib',
                'feature_schema': '{"numerical": 16, "categorical": 5, "target": "disease_risk"}',
                'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv',
                'evaluation_metrics': '{"accuracy": 1.0, "f1_weighted": 1.0, "algorithm": "RandomForestClassifier"}',
                'status': 'Active'
            },
            {
                'model_name': 'Bovine (Cow) Specialized Risk Classifier',
                'species': 'Cow',
                'model_version': 'cow_v1.0.0',
                'model_path': 'models/cow_disease_model.joblib',
                'feature_schema': '{"numerical": 16, "categorical": 5, "target": "disease_risk"}',
                'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv',
                'evaluation_metrics': '{"accuracy": 1.0, "f1_weighted": 1.0}',
                'status': 'Active'
            },
            {
                'model_name': 'Buffalo Specialized Risk Classifier',
                'species': 'Buffalo',
                'model_version': 'buffalo_v1.0.0',
                'model_path': 'models/buffalo_disease_model.joblib',
                'feature_schema': '{"numerical": 16, "categorical": 5, "target": "disease_risk"}',
                'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv',
                'evaluation_metrics': '{"accuracy": 1.0, "f1_weighted": 1.0}',
                'status': 'Active'
            },
            {
                'model_name': 'Caprine (Goat) Specialized Risk Classifier',
                'species': 'Goat',
                'model_version': 'goat_v1.0.0',
                'model_path': 'models/goat_disease_model.joblib',
                'feature_schema': '{"numerical": 16, "categorical": 5, "target": "disease_risk"}',
                'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv',
                'evaluation_metrics': '{"accuracy": 1.0, "f1_weighted": 1.0}',
                'status': 'Active'
            },
            {
                'model_name': 'Ovine (Sheep) Specialized Risk Classifier',
                'species': 'Sheep',
                'model_version': 'sheep_v1.0.0',
                'model_path': 'models/sheep_disease_model.joblib',
                'feature_schema': '{"numerical": 16, "categorical": 5, "target": "disease_risk"}',
                'training_dataset_reference': 'datasets/sample/livestock_disease_dataset.csv',
                'evaluation_metrics': '{"accuracy": 1.0, "f1_weighted": 1.0}',
                'status': 'Active'
            }
        ]

        for m in models:
            existing = db_session.query(ModelRegistry).filter_by(model_name=m['model_name']).first()
            if not existing:
                reg = ModelRegistry(**m)
                db_session.add(reg)
                print(f"Registered Model: {m['model_name']}")

        db_session.commit()
        print("Database initialization successfully completed!")


if __name__ == '__main__':
    init_database()
