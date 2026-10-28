"""
Validation Service for Livestock Health Monitoring System.
Grounded in veterinary standards (Merck Veterinary Manual & FAO guidelines).
Provides species-specific physiological reference intervals, measurement validation,
and clinical urgency detection.
"""

# Species-specific reference thresholds
VETERINARY_REFERENCE_RANGES = {
    'Cow': {
        'temperature': {'min_normal': 38.0, 'max_normal': 39.3, 'min_critical': 37.0, 'max_critical': 40.5, 'unit': '°C'},
        'heart_rate': {'min_normal': 48.0, 'max_normal': 84.0, 'min_critical': 38.0, 'max_critical': 110.0, 'unit': 'bpm'},
        'respiratory_rate': {'min_normal': 24.0, 'max_normal': 40.0, 'min_critical': 12.0, 'max_critical': 60.0, 'unit': 'breaths/min'},
        'bcs_range': {'min': 1.0, 'max': 5.0, 'optimal_min': 2.5, 'optimal_max': 3.75}
    },
    'Buffalo': {
        'temperature': {'min_normal': 37.5, 'max_normal': 39.0, 'min_critical': 36.5, 'max_critical': 40.2, 'unit': '°C'},
        'heart_rate': {'min_normal': 40.0, 'max_normal': 70.0, 'min_critical': 32.0, 'max_critical': 95.0, 'unit': 'bpm'},
        'respiratory_rate': {'min_normal': 15.0, 'max_normal': 30.0, 'min_critical': 10.0, 'max_critical': 50.0, 'unit': 'breaths/min'},
        'bcs_range': {'min': 1.0, 'max': 5.0, 'optimal_min': 2.5, 'optimal_max': 3.75}
    },
    'Goat': {
        'temperature': {'min_normal': 38.5, 'max_normal': 40.0, 'min_critical': 37.2, 'max_critical': 41.0, 'unit': '°C'},
        'heart_rate': {'min_normal': 70.0, 'max_normal': 120.0, 'min_critical': 50.0, 'max_critical': 145.0, 'unit': 'bpm'},
        'respiratory_rate': {'min_normal': 15.0, 'max_normal': 30.0, 'min_critical': 10.0, 'max_critical': 50.0, 'unit': 'breaths/min'},
        'bcs_range': {'min': 1.0, 'max': 5.0, 'optimal_min': 2.5, 'optimal_max': 3.5}
    },
    'Sheep': {
        'temperature': {'min_normal': 38.5, 'max_normal': 40.0, 'min_critical': 37.2, 'max_critical': 41.0, 'unit': '°C'},
        'heart_rate': {'min_normal': 70.0, 'max_normal': 100.0, 'min_critical': 45.0, 'max_critical': 135.0, 'unit': 'bpm'},
        'respiratory_rate': {'min_normal': 16.0, 'max_normal': 34.0, 'min_critical': 10.0, 'max_critical': 55.0, 'unit': 'breaths/min'},
        'bcs_range': {'min': 1.0, 'max': 5.0, 'optimal_min': 2.5, 'optimal_max': 3.5}
    }
}

# Critical symptoms that automatically trigger urgent veterinary attention
CRITICAL_SYMPTOMS = {
    'Recumbent / Unable to Stand',
    'Severe Respiratory Distress',
    'Acute Bloat / Severe Abdominal Distension',
    'High Fever (>41°C)',
    'Hemorrhagic Diarrhea / Blood in Stool',
    'Convulsions / Neurological Signs',
    'Severe Hemorrhage',
    'Acute Mastitis with Systemic Shock',
    'Rapid Dehydration / Sunken Eyes',
    'Unresponsive / Comatose'
}

# Standard symptom catalog
KNOWN_SYMPTOMS = [
    'Reduced appetite',
    'Fever or elevated temperature',
    'Coughing',
    'Nasal discharge',
    'Diarrhea',
    'Abnormal breathing',
    'Lameness',
    'Swelling / Udder heat',
    'Skin lesions / Pox nodules',
    'Reduced milk production',
    'Bloat / Distension',
    'Recumbent / Unable to Stand',
    'Severe Respiratory Distress',
    'Acute Bloat / Severe Abdominal Distension',
    'Hemorrhagic Diarrhea / Blood in Stool',
    'Unusual / Depressed behavior'
]


class ValidationService:
    """Provides clinical range validations and urgent criteria evaluation."""

    @staticmethod
    def get_species_ranges(species: str) -> dict:
        """Retrieve species physiological reference ranges, defaulting to Cow if unknown."""
        return VETERINARY_REFERENCE_RANGES.get(species, VETERINARY_REFERENCE_RANGES['Cow'])

    @staticmethod
    def validate_vital_signs(species: str, temperature=None, heart_rate=None, respiratory_rate=None) -> dict:
        """
        Validate vital signs against species thresholds.
        Returns dictionary of evaluations, flags, and warnings.
        """
        ranges = ValidationService.get_species_ranges(species)
        evaluations = {
            'temperature_status': 'Normal',
            'heart_rate_status': 'Normal',
            'respiratory_rate_status': 'Normal',
            'warnings': [],
            'is_critical': False,
            'is_abnormal': False
        }

        # Temperature evaluation
        if temperature is not None:
            try:
                temp = float(temperature)
                t_ref = ranges['temperature']
                if temp < 30.0 or temp > 45.0:
                    evaluations['warnings'].append(f"Temperature value {temp}°C is physically implausible. Please verify input.")
                elif temp >= t_ref['max_critical'] or temp <= t_ref['min_critical']:
                    evaluations['temperature_status'] = 'Critical'
                    evaluations['is_critical'] = True
                    evaluations['is_abnormal'] = True
                    evaluations['warnings'].append(f"Critical temperature alert: {temp}°C (Normal: {t_ref['min_normal']}-{t_ref['max_normal']}°C)")
                elif temp > t_ref['max_normal'] or temp < t_ref['min_normal']:
                    evaluations['temperature_status'] = 'Abnormal'
                    evaluations['is_abnormal'] = True
                    evaluations['warnings'].append(f"Abnormal temperature: {temp}°C (Normal: {t_ref['min_normal']}-{t_ref['max_normal']}°C)")
            except (ValueError, TypeError):
                evaluations['warnings'].append("Invalid temperature format.")

        # Heart rate evaluation
        if heart_rate is not None:
            try:
                hr = float(heart_rate)
                hr_ref = ranges['heart_rate']
                if hr < 20 or hr > 250:
                    evaluations['warnings'].append(f"Heart rate value {hr} bpm is outside plausible physiological limits.")
                elif hr >= hr_ref['max_critical'] or hr <= hr_ref['min_critical']:
                    evaluations['heart_rate_status'] = 'Critical'
                    evaluations['is_critical'] = True
                    evaluations['is_abnormal'] = True
                    evaluations['warnings'].append(f"Critical heart rate alert: {hr} bpm (Normal: {hr_ref['min_normal']}-{hr_ref['max_normal']} bpm)")
                elif hr > hr_ref['max_normal'] or hr < hr_ref['min_normal']:
                    evaluations['heart_rate_status'] = 'Abnormal'
                    evaluations['is_abnormal'] = True
                    evaluations['warnings'].append(f"Abnormal heart rate: {hr} bpm (Normal: {hr_ref['min_normal']}-{hr_ref['max_normal']} bpm)")
            except (ValueError, TypeError):
                evaluations['warnings'].append("Invalid heart rate format.")

        # Respiratory rate evaluation
        if respiratory_rate is not None:
            try:
                rr = float(respiratory_rate)
                rr_ref = ranges['respiratory_rate']
                if rr < 5 or rr > 140:
                    evaluations['warnings'].append(f"Respiratory rate {rr} breaths/min is outside plausible limits.")
                elif rr >= rr_ref['max_critical'] or rr <= rr_ref['min_critical']:
                    evaluations['respiratory_rate_status'] = 'Critical'
                    evaluations['is_critical'] = True
                    evaluations['is_abnormal'] = True
                    evaluations['warnings'].append(f"Critical respiratory rate alert: {rr} breaths/min (Normal: {rr_ref['min_normal']}-{rr_ref['max_normal']} breaths/min)")
                elif rr > rr_ref['max_normal'] or rr < rr_ref['min_normal']:
                    evaluations['respiratory_rate_status'] = 'Abnormal'
                    evaluations['is_abnormal'] = True
                    evaluations['warnings'].append(f"Abnormal respiratory rate: {rr} breaths/min (Normal: {rr_ref['min_normal']}-{rr_ref['max_normal']} breaths/min)")
            except (ValueError, TypeError):
                evaluations['warnings'].append("Invalid respiratory rate format.")

        return evaluations

    @staticmethod
    def evaluate_overall_health_status(species: str, observation_data: dict) -> str:
        """
        Determine transparent health status following clinical protocol:
        - Normal
        - Monitoring Required
        - Attention Required
        - Urgent Veterinary Attention
        - Prediction Unavailable (if data is insufficient)
        """
        temp = observation_data.get('temperature_c')
        hr = observation_data.get('heart_rate_bpm')
        rr = observation_data.get('respiratory_rate_bpm')
        symptoms = observation_data.get('symptoms', [])
        food_intake = observation_data.get('food_intake', 'Normal')
        walking = observation_data.get('walking_activity', 'Normal')
        rumination = observation_data.get('rumination', 'Normal')

        # Check for insufficient data
        if temp is None and hr is None and rr is None and not symptoms and food_intake == 'Normal':
            return 'Prediction Unavailable'

        # Rule 1: Check Critical Symptoms (Immediate urgent override)
        for s in symptoms:
            if s in CRITICAL_SYMPTOMS:
                return 'Urgent Veterinary Attention'

        # Rule 2: Check Critical Vitals
        vitals_eval = ValidationService.validate_vital_signs(species, temp, hr, rr)
        if vitals_eval['is_critical']:
            return 'Urgent Veterinary Attention'

        # Rule 3: Check recumbency or inability to walk
        if walking in ('Recumbent', 'Staggering'):
            return 'Urgent Veterinary Attention'

        # Rule 4: Check Attention Required (multiple abnormal signs or high fever/symptoms)
        abnormality_score = 0
        if vitals_eval['is_abnormal']:
            abnormality_score += 2
        if food_intake in ('Anorexic', 'Reduced'):
            abnormality_score += 1
        if rumination in ('Absent', 'Reduced'):
            abnormality_score += 1
        if walking in ('Lame', 'Sluggish'):
            abnormality_score += 1
        abnormality_score += len(symptoms)

        if abnormality_score >= 3:
            return 'Attention Required'
        elif abnormality_score >= 1:
            return 'Monitoring Required'

        return 'Normal'
