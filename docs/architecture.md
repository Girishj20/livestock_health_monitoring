# System Architecture: Livestock Health Monitoring and Disease Risk Assessment System

This document outlines the high-level architecture, module decomposition, request lifecycle, security framework, and data flow of the **Livestock Health Monitoring System**.

---

## 1. High-Level Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                                  CLIENT LAYER                                     |
|             HTML5 / CSS3 / Vanilla JavaScript / Bootstrap 5 / Chart.js            |
|       Responsive Web Interface (Desktop, Laptop, Tablet, Mobile Browser)          |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP / HTTPS Requests (Session Cookie + CSRF)
                                          v
+-----------------------------------------------------------------------------------+
|                                   FLASK BACKEND                                   |
|                                                                                   |
|  [ Authentication & RBAC ]           [ Application Factory: create_app() ]        |
|  - Session Regeneration              - Blueprints Registration                    |
|  - Farm-Level Isolation Filters      - Context Processors                         |
|  - CSRF Token Validation             - Custom Error Handlers                      |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                             ROUTING BLUEPRINTS                              |  |
|  |  auth_bp         dashboard_bp   animals_bp      observations_bp             |  |
|  |  predictions_bp  veterinary_bp  vaccinations_bp notifications_bp            |  |
|  |  farms_bp        reports_bp     disease_bp      admin_bp        settings_bp |  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                               SERVICE LAYER                                 |  |
|  |  - AnimalService: Herd CRUD & state reconciliation                          |  |
|  |  - HealthObservationService: Physiological parameter validation             |  |
|  |  - ValidationService: FAO/Merck clinical range checks & critical triggers    |  |
|  |  - PredictionService: Feature alignment, ML inference, safety overrides     |  |
|  |  - VeterinaryRecordService: Formal diagnoses, clinical findings, Rx courses |  |
|  |  - VaccinationService: Due date calculations & booster alerts               |  |
|  |  - NotificationService: In-app stakeholder broadcast & status tracking      |  |
|  |  - ReportService: Dossier compilation, CSV streaming & ReportLab PDF export |  |
|  +-----------------------------------------------------------------------------+  |
+-------------------+-----------------------------------------+---------------------+
                    |                                         |
                    | Scikit-Learn Pipelines (.joblib)        | SQLAlchemy 2.0 ORM
                    v                                         v
+---------------------------------------+  +----------------------------------------+
|       MACHINE LEARNING ENGINE         |  |             PERSISTENCE LAYER          |
|                                       |  |                                        |
|  - ColumnTransformer Preprocessing    |  |  SQLite Database (Local Dev / Portable)|
|    * StandardScaler (16 Numericals)   |  |  MySQL / MariaDB (Production Ready)    |
|    * OneHotEncoder (5 Categoricals)   |  |                                        |
|  - Calibrated Random Forest Classifiers|  |  13 Relational Tables:                 |
|    * Multi-Species Unified Model      |  |  users, farms, farm_memberships,       |
|    * Cow Specialized Model            |  |  animals, health_observations,         |
|    * Buffalo Specialized Model        |  |  disease_assessments, veterinary_visits|
|    * Goat Specialized Model           |  |  medications, vaccinations,            |
|    * Sheep Specialized Model          |  |  notifications, disease_reference,     |
|  - Clinical Safety Override Rule      |  |  model_registry, audit_logs            |
+---------------------------------------+  +----------------------------------------+
```

---

## 2. Core Subsystems

### A. Presentation Layer (Frontend)
- **Bootstrap 5 & Custom CSS:** Built with a light theme, soft neutrals, and subtle glassmorphic elevation cards (`.glass-card`).
- **Accessible Indicators:** Uses text labels and dual visual icons alongside colors (`.badge-status`) so color-blind users can instantly distinguish status tiers:
  - `Normal` (Green + check)
  - `Monitoring Required` (Blue + info)
  - `Attention Required` (Amber + warning)
  - `Urgent Veterinary Attention` (Red + pulsing bell)
  - `Prediction Unavailable` (Gray + dash)
- **Interactive Visualizations:** Chart.js powers dynamic herd species breakdown doughnuts, triage distribution bar charts, and historical vital signs line plots with dual y-axes (temperature vs respiratory rate).

### B. Routing & Service Layer (Backend)
- **Application Factory Pattern:** `create_app()` instantiates the Flask application with isolated configuration profiles (`development`, `testing`, `production`).
- **Separation of Concerns:** Route handlers only manage request parsing, authorization guards, and template rendering. All business logic, range evaluations, statistical calculations, and database mutations are encapsulated within dedicated services (`AnimalService`, `HealthObservationService`, `PredictionService`, etc.).
- **Scoped Thread-Safe ORM:** Pure SQLAlchemy 2.0 with thread-local `scoped_session` managed through `@app.teardown_appcontext`.

### C. Machine Learning Inference Pipeline
- **Trusted Model Loading:** Models are loaded strictly from the controlled `models/` directory using Joblib.
- **Strict Preprocessing Alignment:** All inference runs through an identical `sklearn.pipeline.Pipeline` preserving the exact feature ordering and scaling fitted during model training.
- **Clinical Safety Override:** A statistical score is never allowed to override acute clinical symptoms. If an animal exhibits recumbency, acute bloat, or severe dyspnea, the system enforces `Urgent Veterinary Attention` and flags `urgency_override=True`.

---

## 3. Security and Multi-Tenant Farm Isolation

1. **Role-Based Access Control (RBAC):** Users are categorized into Farmer, Farm Manager, Veterinarian, and Administrator.
2. **Farm-Level Isolation:** Every animal query is scoped by farm membership (`verify_farm_access`). A farmer can never view, update, or predict risk for livestock belonging to another owner.
3. **Session Hardening:** Session IDs are regenerated upon login to prevent session fixation. Cookies have `HttpOnly=True` and `SameSite='Lax'`.
4. **CSRF Protection:** Cryptographic tokens are issued per session and verified on all mutating HTTP requests (POST, PUT, DELETE).
5. **Audit Trail:** Critical operations (`CREATE_ANIMAL`, `RUN_PREDICTION`, `RECORD_VET_VISIT`, `UPDATE_USER_STATUS`) are permanently recorded in `audit_logs`.
