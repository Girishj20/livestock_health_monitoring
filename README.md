# Livestock Health Monitoring and Disease Risk Assessment System

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.0-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Pytest](https://img.shields.io/badge/Tests-17%20Passed-success)](https://pytest.org/)

A full-stack web application designed for farmers, dairy producers, farm managers, and veterinary professionals to maintain digital livestock health records, observe vital signs, evaluate disease risks using calibrated Machine Learning pipelines, and streamline clinical veterinary consultations.

---

## 1. Project Title and Overview

The **Livestock Health Monitoring System** is a centralized platform designed to track animal welfare across dairy and pastoral herds. By recording vital signs (rectal temperature, heart rate, respiration rate, rumination, feeding intake) and clinical symptoms, the system provides early disease risk estimations, maintains longitudinal medical records, tracks vaccination schedules, and alerts stakeholders to life-threatening conditions.

---

## 2. Problem Statement

Livestock such as cows, buffaloes, goats, and sheep are the financial backbone of dairy farming, agriculture, and rural livelihoods. In traditional farming practices:
- **Delayed Intervention:** Early subclinical fevers and rumination drops often go unnoticed during visual inspections until cattle collapse or milk yields drop significantly.
- **Lost Paper Records:** Immunization dates, previous antibiotic regimens, and medical diagnoses recorded in paper registers are frequently misplaced.
- **Inadequate Farm Privacy:** Multi-tenant cooperatives lack digital systems ensuring individual herd privacy and strict role-based access.

---

## 3. Objectives

- Maintain complete digital records for individual livestock animals.
- Monitor vital signs and behavioral markers against species-specific physiological reference ranges.
- Provide machine-learning-assisted disease risk estimations with calibrated probabilities.
- Generate downloadable PDF and printable health dossiers.
- Track vaccination schedules, pending boosters, and overdue care.
- Enforce emergency clinical overrides when life-threatening symptoms are detected.
- Implement multi-tenant farm-level access control and session security.

---

## 4. Key Features

- **Personalized Analytics Dashboard:** Live herd demographics, species breakdowns, triage status, and care reminders.
- **Animal Herd Registry (Full CRUD):** Identification tag management, breed, age, sex, weight, production purpose, and photographs.
- **Structured Health Observation Recording:** Standardized recording of temperature, pulse, respiration, food/water intake, rumination, mobility, and symptom checkboxes.
- **Machine Learning Disease Risk Workspace:** Species-specific Random Forest classification models for Cows, Buffaloes, Goats, and Sheep.
- **Clinical Urgency Safety Override:** Critical signs (acute bloat, dyspnea, recumbency, hyperthermia > 41°C) automatically escalate to Urgent Veterinary Attention.
- **Official Veterinary Medical Records:** Distinct consultation records, confirmed diagnoses, and prescribed medication regimens.
- **Vaccination & Preventive Care Scheduler:** Immunization tracking with dynamic statuses (`Upcoming`, `Due Today`, `Overdue`, `Completed`).
- **In-App Persistent Alerts:** Real-time surveillance warnings and scheduled reminders with live unread badge counters.
- **Evidence-Based Disease Library:** Verified reference guides covering Mastitis, FMD, LSD, BRD, Bloat, Enterotoxemia, and Parasites.
- **Dossier & Report Generator:** Downloadable physical PDF dossiers via ReportLab and CSV exports.
- **System Administration Console:** RBAC management, model registry catalog, disk storage checks, and immutable security audit logs.

---

## 5. Supported Animal Species

| Species | Physiological Normal Temp | Normal Heart Rate | Normal Resp Rate | Optimal BCS |
| :--- | :--- | :--- | :--- | :--- |
| **Cow (Cattle)** | 38.0 - 39.3 °C | 48 - 84 bpm | 24 - 40 breaths/min | 2.5 - 3.75 |
| **Buffalo** | 37.5 - 39.0 °C | 40 - 70 bpm | 15 - 30 breaths/min | 2.5 - 3.75 |
| **Goat** | 38.5 - 40.0 °C | 70 - 120 bpm | 15 - 30 breaths/min | 2.5 - 3.5 |
| **Sheep** | 38.5 - 40.0 °C | 70 - 100 bpm | 16 - 34 breaths/min | 2.5 - 3.5 |

---

## 6. Technology Stack

- **Backend:** Python (3.11 / 3.12), Flask 3.1.3, Werkzeug 3.1.9, Pandas 2.x, NumPy 2.x.
- **Database:** Pure SQLAlchemy 2.0 ORM with thread-local scoped sessions (SQLite default, MySQL/MariaDB compatible).
- **Machine Learning:** Scikit-Learn 1.9.0 (Ensemble Random Forest), Joblib 1.5.3 (Serialization).
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Chart.js 4.4.2.
- **Reporting:** ReportLab 5.1.0 (PDF compilation), CSV streaming.
- **Testing:** Pytest 9.1.1.

---

## 7. System Architecture

The architecture enforces a strict layered separation:
1. **Client Layer:** Responsive HTML5 templates styled with subtle glassmorphism and dual color/text indicators for accessibility.
2. **Controller Layer:** 13 Flask Blueprints managing routing, authentication guards, and CSRF protection.
3. **Service Layer:** Business logic encapsulated in `AnimalService`, `HealthObservationService`, `ValidationService`, `PredictionService`, `VeterinaryRecordService`, `VaccinationService`, `NotificationService`, and `ReportService`.
4. **Machine Learning Layer:** Scikit-Learn pipelines combining continuous feature scalers, categorical encoders, and trained Random Forest classifiers.
5. **Persistence Layer:** 13 relational tables linked by foreign keys and cascade rules.

For complete architectural diagrams, see [`docs/architecture.md`](docs/architecture.md).

---

## 8. Project Folder Structure

```
livestock-health-monitoring/
│
├── app.py                     # Main application runner
├── config.py                  # Environment configurations (Dev, Test, Prod)
├── requirements.txt           # Verified runtime dependencies
├── .env.example               # Safe environment configuration template
├── .gitignore                 # Excludes local databases, .env, and uploads
├── .gitattributes             # Line ending normalization
├── LICENSE                    # MIT License
├── README.md                  # Comprehensive project documentation
│
├── app/
│   ├── __init__.py            # Application factory (create_app)
│   ├── extensions.py          # SQLAlchemy 2.0 scoped session and engine setup
│   ├── models/                # 13 Relational database entities
│   │   ├── user.py            # User credentials & RBAC
│   │   ├── farm.py            # Farm & FarmMembership models
│   │   ├── animal.py          # Animal herd entity & health status
│   │   ├── health_observation.py  # Vitals, rumination & symptoms
│   │   ├── disease_assessment.py  # ML prediction snapshots
│   │   ├── veterinary.py      # VeterinaryVisit & Medication models
│   │   ├── vaccination.py     # Immunizations & due date tracking
│   │   ├── notification.py    # In-app alert entities
│   │   └── reference.py       # DiseaseReference, ModelRegistry, AuditLog
│   ├── routes/                # Modular route blueprints
│   ├── services/              # Encapsulated business & clinical services
│   ├── utils/                 # Security decorators, CSRF & image helpers
│   ├── static/                # CSS, client JavaScript & animal uploads
│   └── templates/             # Jinja2 layouts and 15 feature views
│
├── ml/
│   ├── train_model.py         # Model training script
│   ├── evaluate_model.py      # Model evaluation & confusion matrix
│   ├── predict.py             # Inference engine
│   ├── feature_schema.json    # Feature definitions
│   └── README.md              # ML module documentation
│
├── models/                    # Serialized .joblib model files
├── datasets/sample/           # Clinically grounded reference dataset
├── instance/                  # Local SQLite storage (.gitignore tracked)
├── scripts/
│   ├── init_db.py             # Database creation & reference data seeding
│   └── seed_demo_data.py      # Realistic multi-species demo records
├── tests/                     # 17 automated Pytest suites
└── docs/                      # Technical documentation & BCA Viva guide
```

---

## 9. Screenshots & Visual Interface

| Interface | Description |
| :--- | :--- |
| **Landing Page** | Value proposition, physiological baselines, and portal registration. |
| **Main Dashboard** | Live database metrics, species doughnut chart, and triage distribution. |
| **Animal Health Profile**| Demographics, latest vitals, interactive Chart.js trend plot, and care tabs. |
| **Record Vitals Form** | Input rectal temperature, heart rate, respiration, rumination, and symptoms. |
| **ML Risk Workspace** | Pre-loaded parameters, model version indicator, and probability breakdown. |
| **Medical Dossier** | Printable and PDF exportable veterinary medical history dossier. |

---

## 10. Database Setup

The application uses SQLite by default for simple local setup. To initialize tables and populate baseline disease libraries:

```powershell
python scripts/init_db.py
```

To configure MySQL or MariaDB in production, set `DATABASE_URL` in your `.env` file:
```ini
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/livestock_health_monitoring
```

---

## 11. Python Virtual Environment Setup

Open PowerShell or Terminal in the project root:

```powershell
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate on Linux / macOS
source .venv/bin/activate
```

---

## 12. Dependency Installation

Upgrade pip and install the locked runtime dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 13. Environment Variable Setup

Copy the template `.env.example` to create your local `.env`:

```powershell
Copy-Item .env.example .env
```

Ensure `.env` contains safe configuration parameters:
```ini
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=local-dev-secret-key-livestock-2026
DATABASE_URL=sqlite:///instance/livestock_health.db
MODEL_DIR=models
```

---

## 14. How to Run the Application

Start the local Flask development server:

```powershell
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 15. How to Initialize the Database

Run the database setup script to create all 13 tables, register trained models, and populate reference guides:

```powershell
python scripts/init_db.py
```

---

## 16. How to Create Demonstration Accounts

To seed comprehensive sample data (Cows, Buffaloes, Goats, Sheep, vitals, vet visits, and vaccines):

```powershell
python scripts/seed_demo_data.py
```

### Pre-configured Demonstration Accounts

| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Farmer** | `farmer@greenpastures.com` | `Farmer@123` | Own herds & farm records |
| **Veterinarian** | `vet@animalcare.org` | `Doctor@123` | Clinical consults & official diagnoses |
| **Farm Manager** | `manager@dairyhub.com` | `Manager@123` | Farm operations & health recording |
| **Administrator** | `admin@livestock.org` | `Admin@123` | System-wide users, audit logs & models |

---

## 17. How to Configure Trained Model Files

Pre-trained Scikit-Learn model artifacts are located in `models/`:
- `models/livestock_disease_model.joblib`
- `models/cow_disease_model.joblib`
- `models/buffalo_disease_model.joblib`
- `models/goat_disease_model.joblib`
- `models/sheep_disease_model.joblib`

The application automatically loads the appropriate model based on the selected animal's species.

---

## 18. How to Run Tests

Execute the automated test suite using `pytest`:

```powershell
python -m pytest tests -v
```

Expected output:
```
tests/test_animals.py::test_create_animal_success PASSED
tests/test_animals.py::test_duplicate_tag_rejected_on_same_farm PASSED
tests/test_animals.py::test_update_animal PASSED
tests/test_animals.py::test_animal_search_and_filter PASSED
tests/test_auth.py::test_password_hashing PASSED
tests/test_auth.py::test_user_registration PASSED
tests/test_auth.py::test_user_login_and_logout PASSED
tests/test_auth.py::test_protected_routes_redirect_unauthenticated PASSED
tests/test_health_observations.py::test_validation_service_normal_vitals PASSED
tests/test_health_observations.py::test_validation_service_critical_temperature PASSED
tests/test_health_observations.py::test_record_observation_updates_animal_status PASSED
tests/test_health_observations.py::test_urgent_symptoms_trigger_immediate_urgency PASSED
tests/test_permissions.py::test_cross_farm_data_isolation PASSED
tests/test_permissions.py::test_admin_and_vet_cross_access PASSED
tests/test_permissions.py::test_admin_console_rbac PASSED
tests/test_predictions.py::test_prediction_execution_and_snapshot PASSED
tests/test_predictions.py::test_prediction_emergency_override_on_acute_symptoms PASSED

====================== 17 passed in 13.33s ======================
```

---

## 19. How to Train and Evaluate a Model

To re-train all models and regenerate evaluation metrics:

```powershell
python ml/train_model.py
```

To view per-class performance diagnostics and confusion matrices:

```powershell
python ml/evaluate_model.py
```

---

## 20. Sample Dataset Policy

- The sample dataset in `datasets/sample/livestock_disease_dataset.csv` is synthetically generated according to verified physiological parameters published by the **Food and Agriculture Organization (FAO)** and the **Merck Veterinary Manual**.
- No confidential farmer PII or commercial farm registry records are included.

---

## 21. Privacy and Security Notes

- **Multi-Tenant Farm Isolation:** Enforced on all animal queries; farmers can never access other farms' livestock dossiers.
- **Session Protection:** Session regeneration on authentication prevents session fixation.
- **CSRF Defense:** Session-bound cryptographic tokens validated on all mutating requests.
- **Audit Trail:** Critical actions logged in `audit_logs` table.
- **File Upload Safeguards:** Secure UUID renaming, extension whitelisting (PNG, JPG, WEBP), and 16 MB limit.

---

## 22. Medical Disclaimer

> **VETERINARY MEDICAL DISCLAIMER:**
> Automated assessments generated by this software are informational probability estimates intended for decision-support and early-warning monitoring. They do NOT constitute confirmed diagnoses or licensed veterinary prescriptions. Consult a qualified, registered veterinary doctor for diagnosis, treatment, and medication administration. Severe or rapidly deteriorating symptoms must trigger immediate emergency veterinary care regardless of model outputs.

---

## 23. Known Limitations

- Model predictions are based on statistical feature patterns and should be verified with clinical physical examinations.
- IoT live sensor integration requires external MQTT or REST ingestion endpoints.
- SMS/Email notifications require configuration of external gateway credentials (Twilio / SendGrid).

---

## 24. Future Enhancements

- Ingestion pipelines for wearable rumination and temperature sensor ear tags.
- Offline-first Progressive Web App (PWA) support with background synchronization for remote rural areas.
- Integration with government livestock identification registries (e.g. INAPH / Bharat Pashudhan).

---

## 25. License and Acknowledgements

This project is licensed under the **MIT License** - see the [`LICENSE`](LICENSE) file for details.

Grounded in veterinary medicine literature from the **Food and Agriculture Organization (FAO)** and the **Merck Veterinary Manual (11th Edition)**.
