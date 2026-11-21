# ✈️ FlightFix: Enhancing Aircraft Maintenance Efficiency

> **Enterprise-Grade Aviation MRO (Maintenance, Repair, and Overhaul) Management System**  
> *Developed with Django, Django REST Framework, HTML/CSS/JavaScript, and Supabase PostgreSQL.*

---

## 📋 Project Overview

**FlightFix** is a comprehensive, end-to-end digital aerospace maintenance management platform engineered to maximize aircraft fleet availability, eliminate Aircraft-on-Ground (AOG) downtime, maintain regulatory airworthiness compliance (DGCA CAR 145 / FAA Part 145 / EASA Part 145), and automate maintenance workflows across hangars, line stations, and parts inventory.

This project covers all **10 Modules** specified in the curriculum requirements with **Data Entities (Django Models)**, **REST APIs (Django REST Framework ViewSets)**, **Responsive UI Screens**, and **Automated Unit Tests**.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla ES6+), Chart.js | Responsive aerospace HUD command center, real-time KPI graphs, interactive modal forms, table search filters, and simulated mobile field technician interface. |
| **Backend** | Python 3.13+, Django 5.x / 6.x | Modular architectural structure, ORM data modelling, business logic validation, state transitions, security, and session management. |
| **API** | Django REST Framework (DRF) | RESTful API endpoints with pagination, ordering, search filtering, and custom actions (`release_to_service`, `adjust_stock`, `stamp_technician`, `sync_erp`). |
| **Database** | Supabase PostgreSQL / SQLite3 fallback | Production-grade relational database storing fleet entities, work orders, telemetry readings, and audit trails. Seamless fallback to local SQLite when offline. |

---

## 📦 Modular Architecture: The 10 Modules

Each module is structured as an independent, decoupled Django application with its own `models.py`, `serializers.py`, `views.py`, `urls.py`, and `tests.py`:

```
flightfix_project/
├── manage.py
├── flightfix/                   # Core Django project settings & main router
│   ├── settings.py              # Supabase PostgreSQL + CORS + DRF configuration
│   ├── urls.py                  # API v1 router and frontend routes
│   └── views.py                 # Unified Dashboard view
├── apps/
│   ├── planning/                # Module 1: Maintenance Planning and Scheduling
│   ├── workorders/              # Module 2: Work Order Management
│   ├── fleet/                   # Module 3: Aircraft and Equipment Management
│   ├── inventory/               # Module 4: Spare Parts Inventory Management
│   ├── execution/               # Module 5: Maintenance Execution and Documentation
│   ├── compliance/              # Module 6: Compliance Management
│   ├── supplychain/             # Module 7: ERP and Supply Chain Integration
│   ├── field_mobile/            # Module 8: Mobile App Module for Field Technicians
│   ├── analytics/               # Module 9: Fleet Reliability & Predictive Diagnostics
│   └── audit_security/          # Module 10: Security, Audit Trail & System Roles
├── static/                      # Custom CSS (aerospace theme) and JS controllers
└── templates/                   # Clean HTML templates (Glassmorphic Command Center)
```

---

### Detailed Module Specifications

#### 1. Maintenance Planning and Scheduling (`apps.planning`)
- **Entities:** `MaintenanceSchedule`, `HangarBay`
- **Features:** Calendar booking for hangar slots (HB-01, HB-02), scheduled check interval tracking (A-Check, B-Check, C-Check, D-Check, Line Transits), lead engineer assignment, priority classification.
- **Key API:** `/api/v1/planning/schedules/`, `/api/v1/planning/schedules/calendar_stats/`

#### 2. Work Order Management (`apps.workorders`)
- **Entities:** `WorkOrder`, `WorkOrderTask`, `LaborLog`
- **Features:** Automated job order creation, step-by-step task tracking, AMM cross-referencing, man-hour calculation, and digital Certificate of Release to Service (CRS) signing.
- **Key API:** `/api/v1/workorders/orders/`, `/api/v1/workorders/orders/{id}/release_to_service/`, `/api/v1/workorders/orders/metrics/`

#### 3. Aircraft and Equipment Management (`apps.fleet`)
- **Entities:** `Aircraft`, `AircraftSubsystem`, `GroundEquipment`
- **Features:** Complete aircraft registry (Boeing 737-800, Airbus A320neo, B787-9 Dreamliner, A321neo), total flight hours/cycles, status indicators (Operational, In Maintenance, AOG), subsystem health scores, and Ground Power Unit (GPU) / hydraulic cart calibration status.
- **Key API:** `/api/v1/fleet/aircraft/`, `/api/v1/fleet/aircraft/summary/`, `/api/v1/fleet/ground-equipment/`

#### 4. Spare Parts Inventory Management (`apps.inventory`)
- **Entities:** `SparePart`, `PartCategory`, `InventoryTransaction`
- **Features:** Stock on-hand vs. minimum safety levels, storage bin location mapping (`ZONE-A/RACK-02/BIN-11`), rotable/consumable classification, automated stock issuance, and low-stock alerts.
- **Key API:** `/api/v1/inventory/parts/`, `/api/v1/inventory/parts/{id}/adjust_stock/`, `/api/v1/inventory/parts/low_stock/`

#### 5. Maintenance Execution and Documentation (`apps.execution`)
- **Entities:** `JobCardExecution`, `DefectReport`
- **Features:** Aircraft Maintenance Manual (AMM) compliance sign-offs, digital AME technician stamps, Quality Control inspector stamps, and pilot/mechanic discrepancy logbooks (PIREP/MAREP) with Minimum Equipment List (MEL) deferrals.
- **Key API:** `/api/v1/execution/job-cards/`, `/api/v1/execution/job-cards/{id}/stamp_technician/`, `/api/v1/execution/defects/{id}/rectify/`

#### 6. Compliance Management (`apps.compliance`)
- **Entities:** `AirworthinessDirective`, `AircraftADCompliance`, `ServiceBulletin`, `TechnicianLicense`
- **Features:** Regulatory mandate tracking (FAA, EASA, DGCA), recurring inspection thresholds, aircraft compliance certification, OEM Service Bulletins, and AME license validity monitoring.
- **Key API:** `/api/v1/compliance/directives/`, `/api/v1/compliance/directives/compliance_summary/`, `/api/v1/compliance/fleet-compliance/{id}/certify_compliance/`

#### 7. ERP and Supply Chain Integration (`apps.supplychain`)
- **Entities:** `VendorSupplier`, `PurchaseOrder`, `PurchaseOrderItem`
- **Features:** OEM vendor registry (Boeing Distribution, Safran Landing Systems), purchase orders, SAP/Oracle ERP system synchronization, Air Waybill (AWB) freight tracking, and customs clearance status.
- **Key API:** `/api/v1/supplychain/purchase-orders/`, `/api/v1/supplychain/purchase-orders/{id}/sync_erp_status/`, `/api/v1/supplychain/purchase-orders/procurement_metrics/`

#### 8. Mobile App Module for Field Technicians (`apps.field_mobile`)
- **Entities:** `FieldInspection`, `QuickDiscrepancyLog`, `OfflineSyncRecord`
- **Features:** Handheld terminal emulator for line mechanics on the ramp, quick walkaround snag logging, tire pressure & engine oil level telemetry, and simulated offline-to-cloud batch sync.
- **Key API:** `/api/v1/field/inspections/`, `/api/v1/field/inspections/{id}/complete_inspection/`, `/api/v1/field/inspections/sync_offline_batch/`

#### 9. Fleet Reliability & Predictive Diagnostics (`apps.analytics`)
- **Entities:** `TelemetrySensorReading`, `PredictiveAlert`, `FleetKPIMetric`
- **Features:** Live telemetry sensors (EGT margin, vibration harmonic, hydraulic pressure), AI-driven anomaly detection, failure probability scores, Dispatch Reliability %, MTBF, and MTTR KPI dashboards.
- **Key API:** `/api/v1/analytics/alerts/`, `/api/v1/analytics/alerts/{id}/acknowledge/`, `/api/v1/analytics/kpis/live_kpis/`

#### 10. Security, Audit Trail & System Roles (`apps.audit_security`)
- **Entities:** `MROAuditTrail`, `MROUserProfile`
- **Features:** Comprehensive regulatory audit trail capturing all CRS releases, digital stamps, and stock adjustments with IP address and timestamp; role-based profiles (Chief Engineer, Line Technician, QA Auditor, Storekeeper).
- **Key API:** `/api/v1/audit/logs/`, `/api/v1/audit/logs/recent_activities/`, `/api/v1/audit/users/active_roles/`

---

## 🚀 How to Run the Project

### 1. Prerequisites
- Python 3.10+ installed
- Git (optional)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Connect to Supabase PostgreSQL (Optional)
Open the `.env` file and insert your Supabase connection string:
```ini
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```
*(If `DATABASE_URL` is left blank, the application automatically runs on local SQLite without needing internet access or remote database credentials).*

### 4. Run Migrations & Seed Data
```bash
# Apply database schemas across all 10 modules
python manage.py migrate

# Populate realistic aviation data
python manage.py seed_flightfix_data
```

### 5. Run Automated Tests
```bash
python manage.py test
```
*Output: 32 tests run across all 10 modules with 100% success rate.*

### 6. Start the Local Server
```bash
python manage.py runserver 8000
```
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```
You can also access the Django Admin panel at:
```
http://127.0.0.1:8000/admin/
```

---

## 📊 Evaluation & College Viva Highlights

1. **Why Django + Django REST Framework?**
   - Django provides an enterprise ORM with relational integrity between aircraft, work orders, and parts. DRF allows seamless decoupled REST APIs that power the modern single-page dashboard.
2. **How does Supabase integrate?**
   - Supabase PostgreSQL provides cloud-hosted high-availability PostgreSQL. FlightFix dynamically parses `DATABASE_URL` via `dj-database-url` with SSL support, while providing transparent local SQLite fallback.
3. **What makes this project realistic?**
   - Uses genuine aviation standards: FAA/EASA/DGCA Airworthiness Directives, Aircraft Maintenance Manual (AMM) references, MEL (Minimum Equipment List) dispatch criteria, and CRS (Certificate of Release to Service) sign-off workflows.
