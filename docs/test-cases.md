# Quality Assurance & Test Cases: Livestock Health Monitoring System

This document outlines the automated and functional test suite covering authentication, animal herd management, physiological vital validations, machine learning predictions, and role-based access control.

---

## 1. Test Suite Summary

- **Framework:** `pytest` (v9.1.1)
- **Database Engine for Testing:** Isolated In-Memory SQLite (`sqlite:///:memory:`)
- **Total Test Cases:** 17 Passed (100% Success Rate)

---

## 2. Test Cases Specification

### Suite 1: Authentication & User Management (`tests/test_auth.py`)

| Test ID | Test Function | Objective | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-AUTH-01** | `test_password_hashing` | Verify secure password hashing and verification | Hash is non-reversible; correct password validates | **PASSED** |
| **TC-AUTH-02** | `test_user_registration` | Register a new farmer account with farm | Account created in DB with encrypted password | **PASSED** |
| **TC-AUTH-03** | `test_user_login_and_logout` | Authenticate valid user and terminate session | Session created on login, cleared on logout | **PASSED** |
| **TC-AUTH-04** | `test_protected_routes_redirect_unauthenticated` | Unauthenticated access to `/dashboard` & `/animals` | HTTP 302 redirect to `/login` | **PASSED** |

---

### Suite 2: Animal Herd Management (`tests/test_animals.py`)

| Test ID | Test Function | Objective | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-ANIM-01** | `test_create_animal_success` | Register a new cow with vital defaults | Animal saved with `Normal` initial health status | **PASSED** |
| **TC-ANIM-02** | `test_duplicate_tag_rejected_on_same_farm` | Attempt duplicate ear tag on same farm | Raises `ValueError` preventing duplicate tag | **PASSED** |
| **TC-ANIM-03** | `test_update_animal` | Modify animal weight, name, and status | Fields updated and `updated_at` refreshed | **PASSED** |
| **TC-ANIM-04** | `test_animal_search_and_filter` | Query animals by keyword and species filter | Returns matching animals belonging to user's farm | **PASSED** |

---

### Suite 3: Physiological Vitals & Urgency Detection (`tests/test_health_observations.py`)

| Test ID | Test Function | Objective | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-OBS-01** | `test_validation_service_normal_vitals` | Test normal Cow vitals against reference range | No warnings; `is_critical=False`, `is_abnormal=False` | **PASSED** |
| **TC-OBS-02** | `test_validation_service_critical_temperature` | Test critical fever (>40.5°C in cattle) | `temperature_status='Critical'`, `is_critical=True` | **PASSED** |
| **TC-OBS-03** | `test_record_observation_updates_animal_status` | Log fever + coughing for a normal animal | Animal status auto-transitions to `Attention Required` | **PASSED** |
| **TC-OBS-04** | `test_urgent_symptoms_trigger_immediate_urgency` | Log recumbency or acute bloat | Status transitions to `Urgent Veterinary Attention`; Urgent notification created | **PASSED** |

---

### Suite 4: Machine Learning Inference & Safety (`tests/test_predictions.py`)

| Test ID | Test Function | Objective | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-ML-01** | `test_prediction_execution_and_snapshot` | Run ML inference on mastitis presentation | Predicts `Mastitis`, stores input snapshot in DB | **PASSED** |
| **TC-ML-02** | `test_prediction_emergency_override_on_acute_symptoms` | Evaluate ML output with severe acute bloat | Flags `urgency_override=True`, `risk_level='Critical'` | **PASSED** |

---

### Suite 5: Data Isolation & Permissions (`tests/test_permissions.py`)

| Test ID | Test Function | Objective | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-SEC-01** | `test_cross_farm_data_isolation` | Verify Farmer 1 cannot access Farmer 2's herd | Access denied; prevents unauthorized URL manipulation | **PASSED** |
| **TC-SEC-02** | `test_admin_and_vet_cross_access` | Verify Doctor & Admin can review clinical records | Allowed universal view access for clinical supervision | **PASSED** |
| **TC-SEC-03** | `test_admin_console_rbac` | Enforce admin-only access on `/admin` | Farmer redirected to `/dashboard`; Admin granted 200 OK | **PASSED** |

---

## 3. How to Run the Tests

```powershell
python -m pytest tests -v
```
