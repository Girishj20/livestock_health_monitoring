import os
import json
from datetime import datetime
from app.extensions import db_session
from app.models.animal import Animal
from app.models.disease_assessment import DiseaseAssessment
from app.services.validation_service import ValidationService, CRITICAL_SYMPTOMS
from app.services.notification_service import NotificationService
from ml.predict import predict_disease_risk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RECOMMENDED_ACTIONS = {
    'Healthy / Normal': [
        "Continue routine feeding, hydration, and clean housing management.",
        "Maintain regular vaccination and deworming schedules.",
        "Observe normal behavioral cycles and rumination daily."
    ],
    'Mastitis': [
        "Isolate animal during milking to prevent cross-contamination.",
        "Perform California Mastitis Test (CMT) or somatic cell count.",
        "Apply warm udder compresses and strip quarter if recommended by vet.",
        "Seek immediate veterinary consultation for targeted antibiotic or anti-inflammatory prescription."
    ],
    'Foot and Mouth Disease (FMD)': [
        "IMMEDIATELY QUARANTINE animal in strict bio-secure isolation.",
        "Notify attending veterinarian and relevant local animal husbandry department immediately.",
        "Disinfect premises with approved virucidal agent (e.g., sodium carbonate or citric acid solution).",
        "Provide soft feed, clean water, and supportive antiseptic mouth/hoof washes as directed by vet."
    ],
    'Bovine Respiratory Disease / Pneumonia': [
        "Move animal to a well-ventilated, dry, and draft-free shelter.",
        "Minimize stress and avoid moving or transporting the animal.",
        "Contact veterinarian promptly for auscultation and prescription of antimicrobial/NSAID therapy.",
        "Monitor rectal temperature every 6 to 12 hours."
    ],
    'Lumpy Skin Disease (LSD)': [
        "Isolate affected animal in insect-proof quarters (mosquito and vector control).",
        "Apply topical antiseptics and fly repellents to open skin nodules.",
        "Administer clean, palatable soft forage and electrolytes.",
        "Consult veterinarian for supportive therapy and fever management."
    ],
    'Bloat (Tympanites)': [
        "EMERGENCY: Contact veterinarian immediately.",
        "Keep animal standing with head elevated; walk gently if possible.",
        "Do not allow animal to lie down.",
        "Prepare stomach tube or veterinary trocar under professional guidance if acute asphyxia threatens."
    ],
    'Enterotoxemia / GI Infection': [
        "Withhold rich concentrate feeds; provide fresh clean water and electrolyte solution.",
        "Isolate animal to avoid spread of enteric pathogens.",
        "Call veterinarian immediately for fluid resuscitation and specific antitoxin or antibacterial protocol."
    ],
    'Parasitic Gastroenteritis': [
        "Collect fecal sample for veterinary egg count (McMaster flotation).",
        "Consult veterinarian for appropriate broad-spectrum anthelmintic (dewormer) selection.",
        "Improve pasture rotation and hygiene to break parasite life cycle."
    ]
}


class PredictionService:
    """Manages ML inference, snapshot persistence, and clinical safety guardrails."""

    @staticmethod
    def run_assessment(animal_id: int, user_id: int, observation_dict: dict) -> dict:
        """
        Execute prediction pipeline for an animal.
        Applies feature extraction, model inference, safety overrides, and persistence.
        """
        animal = db_session.get(Animal, animal_id)
        if not animal:
            raise ValueError(f"Animal #{animal_id} not found.")

        # Extract symptoms list
        symptoms = observation_dict.get('symptoms', [])
        if isinstance(symptoms, str):
            symptoms = [s.strip() for s in symptoms.split(',') if s.strip()]

        # Check for urgent clinical override
        urgent_flag = any(s in CRITICAL_SYMPTOMS for s in symptoms)
        temp = observation_dict.get('temperature_c')
        hr = observation_dict.get('heart_rate_bpm')
        rr = observation_dict.get('respiratory_rate_bpm')
        vitals_eval = ValidationService.validate_vital_signs(animal.species, temp, hr, rr)
        if vitals_eval['is_critical']:
            urgent_flag = True

        # Build feature vector
        features = {
            'species': animal.species,
            'age_months': animal.estimated_age_months or 36,
            'weight_kg': float(observation_dict.get('weight_kg') or animal.weight_kg or 400.0),
            'temperature_c': float(temp) if temp not in (None, '') else 38.6,
            'heart_rate_bpm': float(hr) if hr not in (None, '') else 65.0,
            'respiratory_rate_bpm': float(rr) if rr not in (None, '') else 25.0,
            'food_intake': observation_dict.get('food_intake', 'Normal'),
            'water_intake': observation_dict.get('water_intake', 'Normal'),
            'rumination': observation_dict.get('rumination', 'Normal'),
            'walking_activity': observation_dict.get('walking_activity', 'Normal'),
            'milk_production_drop_pct': float(observation_dict.get('milk_production_drop_pct') or 0.0),
            'body_condition_score': float(observation_dict.get('body_condition_score') or 3.0),
            'fever_flag': 1 if ('Fever or elevated temperature' in symptoms or vitals_eval['is_abnormal']) else 0,
            'coughing_flag': 1 if 'Coughing' in symptoms else 0,
            'nasal_discharge_flag': 1 if 'Nasal discharge' in symptoms else 0,
            'diarrhea_flag': 1 if 'Diarrhea' in symptoms else 0,
            'lameness_flag': 1 if ('Lameness' in symptoms or observation_dict.get('walking_activity') == 'Lame') else 0,
            'swelling_flag': 1 if 'Swelling / Udder heat' in symptoms else 0,
            'skin_lesions_flag': 1 if 'Skin lesions / Pox nodules' in symptoms else 0,
            'bloat_distension_flag': 1 if ('Bloat / Distension' in symptoms or 'Acute Bloat / Severe Abdominal Distension' in symptoms) else 0,
            'abnormal_milk_flag': 1 if 'Reduced milk production' in symptoms else 0
        }

        # Run inference
        inference = predict_disease_risk(features)

        predicted_class = inference.get('predicted_class', 'Healthy / Normal')
        risk_level = inference.get('risk_level', 'Normal')
        confidence = inference.get('confidence', 0.0)
        probabilities = inference.get('probabilities', {})
        model_version = inference.get('model_version', '1.0.0')

        # Safety override rule
        if urgent_flag:
            risk_level = 'Critical'
            if predicted_class == 'Healthy / Normal':
                predicted_class = 'Urgent Veterinary Attention Required'

        # Compile list of abnormal observations detected
        abnormal_features = []
        if vitals_eval['warnings']:
            abnormal_features.extend(vitals_eval['warnings'])
        if features['food_intake'] != 'Normal':
            abnormal_features.append(f"Abnormal food intake: {features['food_intake']}")
        if features['rumination'] != 'Normal':
            abnormal_features.append(f"Abnormal rumination: {features['rumination']}")
        if features['walking_activity'] != 'Normal':
            abnormal_features.append(f"Abnormal mobility: {features['walking_activity']}")
        for s in symptoms:
            abnormal_features.append(f"Reported symptom: {s}")

        recommended_steps = RECOMMENDED_ACTIONS.get(predicted_class, [
            "Monitor animal closely and consult a qualified veterinary doctor.",
            "Record vital signs twice daily."
        ])

        # Persist Assessment
        assessment = DiseaseAssessment(
            animal_id=animal_id,
            initiated_by=user_id,
            model_name=f"{animal.species} Disease Risk Classifier",
            model_version=model_version,
            input_snapshot=json.dumps(features),
            predicted_class=predicted_class,
            prediction_scores=json.dumps(probabilities),
            data_quality_status='Complete' if not vitals_eval['warnings'] else 'Warning',
            assessment_status='Completed',
            risk_level=risk_level,
            urgency_override=urgent_flag,
            created_at=datetime.utcnow()
        )
        db_session.add(assessment)
        db_session.commit()

        # Update animal health status if this is higher priority
        if risk_level in ('High', 'Critical'):
            animal.health_status = 'Urgent Veterinary Attention' if risk_level == 'Critical' else 'Attention Required'
            db_session.commit()
            
            # Send Notification
            NotificationService.notify_farm_stakeholders(
                farm_id=animal.farm_id,
                title=f"Disease Risk Alert: {animal.species} [{animal.animal_tag}]",
                message=f"Model assessment estimated risk of {predicted_class} (Tier: {risk_level}, Confidence: {confidence}%).",
                priority='Urgent' if risk_level == 'Critical' else 'High',
                notification_type='ML Risk Alert',
                animal_id=animal.id,
                link_url=f"/predictions/{assessment.id}"
            )

        return {
            'assessment_id': assessment.id,
            'animal_tag': animal.animal_tag,
            'species': animal.species,
            'predicted_class': predicted_class,
            'risk_level': risk_level,
            'confidence': confidence,
            'probabilities': probabilities,
            'urgency_override': urgent_flag,
            'model_version': model_version,
            'abnormal_features': abnormal_features,
            'recommended_steps': recommended_steps,
            'timestamp': assessment.created_at.strftime('%Y-%m-%d %H:%M'),
            'disclaimer': (
                "Automated assessments are informational and do not confirm a disease. "
                "Consult a qualified veterinarian for diagnosis and treatment. "
                "Seek urgent veterinary care when severe or rapidly worsening symptoms are observed."
            )
        }
