from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date

from apps.fleet.models import Aircraft, AircraftSubsystem, GroundEquipment
from apps.planning.models import HangarBay, MaintenanceSchedule
from apps.workorders.models import WorkOrder, WorkOrderTask, LaborLog
from apps.inventory.models import PartCategory, SparePart, InventoryTransaction
from apps.execution.models import JobCardExecution, DefectReport
from apps.compliance.models import AirworthinessDirective, AircraftADCompliance, ServiceBulletin, TechnicianLicense
from apps.supplychain.models import VendorSupplier, PurchaseOrder, PurchaseOrderItem
from apps.field_mobile.models import FieldInspection, QuickDiscrepancyLog, OfflineSyncRecord
from apps.analytics.models import TelemetrySensorReading, PredictiveAlert, FleetKPIMetric
from apps.audit_security.models import MROAuditTrail, MROUserProfile

class Command(BaseCommand):
    help = 'Seeds realistic, high-fidelity aviation MRO data across all 10 FlightFix modules'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting FlightFix Aviation Data Seeding..."))
        now = timezone.now()
        today = date.today()

        # 1. FLEET (Module 3)
        self.stdout.write("- Seeding Aircraft Fleet and Ground Equipment...")
        ac1, _ = Aircraft.objects.get_or_create(
            tail_number='VT-FFX',
            defaults={
                'model': 'Boeing 737-800NG',
                'serial_number': 'MSN-37255',
                'manufacturer': 'The Boeing Company',
                'total_flight_hours': 14250.4,
                'total_flight_cycles': 8920,
                'status': 'OPERATIONAL',
                'current_location': 'DEL - Hangar Bay 1',
                'manufacture_date': today - timedelta(days=2200),
                'last_inspection_date': today - timedelta(days=12)
            }
        )

        ac2, _ = Aircraft.objects.get_or_create(
            tail_number='VT-SKY',
            defaults={
                'model': 'Airbus A320neo',
                'serial_number': 'MSN-10492',
                'manufacturer': 'Airbus SAS',
                'total_flight_hours': 6820.2,
                'total_flight_cycles': 4150,
                'status': 'IN_MAINTENANCE',
                'current_location': 'DEL - Hangar Bay 2 (Heavy MRO)',
                'manufacture_date': today - timedelta(days=1100),
                'last_inspection_date': today - timedelta(days=2)
            }
        )

        ac3, _ = Aircraft.objects.get_or_create(
            tail_number='VT-GLO',
            defaults={
                'model': 'Boeing 787-9 Dreamliner',
                'serial_number': 'MSN-60144',
                'manufacturer': 'The Boeing Company',
                'total_flight_hours': 11400.0,
                'total_flight_cycles': 2400,
                'status': 'OPERATIONAL',
                'current_location': 'BOM - Chhatrapati Shivaji Maharaj Intl',
                'manufacture_date': today - timedelta(days=1600),
                'last_inspection_date': today - timedelta(days=20)
            }
        )

        ac4, _ = Aircraft.objects.get_or_create(
            tail_number='VT-AOG',
            defaults={
                'model': 'Airbus A321neo',
                'serial_number': 'MSN-11208',
                'manufacturer': 'Airbus SAS',
                'total_flight_hours': 3450.8,
                'total_flight_cycles': 2120,
                'status': 'AOG',
                'current_location': 'DEL - Ramp Stand 34',
                'manufacture_date': today - timedelta(days=700),
                'last_inspection_date': today - timedelta(days=1)
            }
        )

        # Subsystems
        AircraftSubsystem.objects.get_or_create(
            aircraft=ac1, system_name='CFM56-7B Turbofan Engine #1 (Port)',
            defaults={'health_status': 'EXCELLENT', 'health_score': 96, 'last_tested_date': today - timedelta(days=10)}
        )
        AircraftSubsystem.objects.get_or_create(
            aircraft=ac1, system_name='Hydraulic System A & B Power Units',
            defaults={'health_status': 'GOOD', 'health_score': 88, 'last_tested_date': today - timedelta(days=10)}
        )
        AircraftSubsystem.objects.get_or_create(
            aircraft=ac2, system_name='Pratt & Whitney PW1100G Engine #2',
            defaults={'health_status': 'MONITOR', 'health_score': 68, 'last_tested_date': today - timedelta(days=2), 'notes': 'Vibration harmonic elevated near 80% N1'}
        )
        AircraftSubsystem.objects.get_or_create(
            aircraft=ac4, system_name='Main Landing Gear Actuator Assembly',
            defaults={'health_status': 'CRITICAL', 'health_score': 42, 'last_tested_date': today - timedelta(days=1), 'notes': 'Hydraulic fluid seal leakage exceeding dispatch limits'}
        )

        # Ground Equipment
        GroundEquipment.objects.get_or_create(equipment_tag='GPU-DEL-01', defaults={'equipment_type': 'Ground Power Unit 90kVA 400Hz', 'status': 'AVAILABLE', 'assigned_hangar': 'Hangar Bay 1'})
        GroundEquipment.objects.get_or_create(equipment_tag='HYD-CART-04', defaults={'equipment_type': 'Dual-System Hydraulic Test Rig (3000 PSI)', 'status': 'IN_USE', 'assigned_hangar': 'Hangar Bay 2'})
        GroundEquipment.objects.get_or_create(equipment_tag='TUG-AERO-09', defaults={'equipment_type': 'Electric Aircraft Pushback Tug (400kN)', 'status': 'AVAILABLE', 'assigned_hangar': 'Terminal Ramp Area'})

        # 2. PLANNING & SCHEDULING (Module 1)
        self.stdout.write("- Seeding Maintenance Planning & Schedules...")
        bay1, _ = HangarBay.objects.get_or_create(bay_code='HB-01', defaults={'name': 'Line Maintenance Express Bay 1', 'facility_location': 'DEL East Apron', 'status': 'OCCUPIED'})
        bay2, _ = HangarBay.objects.get_or_create(bay_code='HB-02', defaults={'name': 'Heavy MRO Dock Bay 2', 'facility_location': 'DEL MRO Complex', 'status': 'OCCUPIED'})
        bay3, _ = HangarBay.objects.get_or_create(bay_code='HB-03', defaults={'name': 'Avionics & Paint Refit Bay 3', 'facility_location': 'DEL South Apron', 'status': 'AVAILABLE'})

        sch1, _ = MaintenanceSchedule.objects.get_or_create(
            schedule_id='SCH-2026-A01',
            defaults={
                'aircraft': ac1,
                'check_type': 'A_CHECK',
                'hangar_bay': bay1,
                'scheduled_start': now - timedelta(hours=6),
                'scheduled_end': now + timedelta(hours=18),
                'interval_hours': 500,
                'lead_engineer': 'Chief Eng. Rajesh Sharma',
                'status': 'IN_PROGRESS',
                'priority': 'ROUTINE',
                'task_scope_summary': 'Scheduled 500-hr A-Check inspection: engine oil filter replacement, flight control rigging verification, emergency lighting test.'
            }
        )

        sch2, _ = MaintenanceSchedule.objects.get_or_create(
            schedule_id='SCH-2026-C04',
            defaults={
                'aircraft': ac2,
                'check_type': 'C_CHECK',
                'hangar_bay': bay2,
                'scheduled_start': now - timedelta(days=2),
                'scheduled_end': now + timedelta(days=5),
                'interval_hours': 3500,
                'lead_engineer': 'Sr. Inspector Sunita Menon',
                'status': 'IN_PROGRESS',
                'priority': 'URGENT',
                'task_scope_summary': 'Heavy Base C-Check: Structural NDT eddy current testing, cabin pressure hull integrity test, landing gear retraction cycle check.'
            }
        )

        sch3, _ = MaintenanceSchedule.objects.get_or_create(
            schedule_id='SCH-2026-LIN-99',
            defaults={
                'aircraft': ac4,
                'check_type': 'LINE_INSPECTION',
                'hangar_bay': bay1,
                'scheduled_start': now - timedelta(hours=2),
                'scheduled_end': now + timedelta(hours=8),
                'interval_hours': 100,
                'lead_engineer': 'Lead Mechanic Vikram Joshi',
                'status': 'IN_PROGRESS',
                'priority': 'CRITICAL_AOG',
                'task_scope_summary': 'AOG Rectification: Main Landing Gear actuator seal leakage emergency repair and return-to-service validation.'
            }
        )

        # 3. WORK ORDER MANAGEMENT (Module 2)
        self.stdout.write("- Seeding Work Orders and Tasks...")
        wo1, _ = WorkOrder.objects.get_or_create(
            work_order_no='WO-2026-AOG-01',
            defaults={
                'aircraft': ac4,
                'title': 'AOG: Main Landing Gear Actuator Seal High-Pressure Hydraulic Leak',
                'description': 'Discrepancy reported during post-flight inspection. Hydraulic seal extrusion detected on left MLG retract actuator cylinder. Replace seal kit and perform leak check at 3,000 PSI.',
                'order_type': 'UNSCHEDULED_DEFECT',
                'priority': 'CRITICAL_AOG',
                'status': 'IN_PROGRESS',
                'assigned_team': 'Rapid Response AOG Hydraulics Team',
                'estimated_man_hours': 14.0,
                'actual_man_hours': 6.5
            }
        )

        wo2, _ = WorkOrder.objects.get_or_create(
            work_order_no='WO-2026-CHK-102',
            defaults={
                'aircraft': ac1,
                'schedule': sch1,
                'title': 'Boeing 737NG Scheduled A-Check Inspection Pack',
                'description': 'Execution of Routine A-Check task cards in accordance with Boeing MPD 24-00-00 and airline AMP rev 14.',
                'order_type': 'SCHEDULED_CHECK',
                'priority': 'MEDIUM',
                'status': 'IN_PROGRESS',
                'assigned_team': 'Hangar Line Crew Alpha',
                'estimated_man_hours': 36.0,
                'actual_man_hours': 18.0
            }
        )

        wo3, _ = WorkOrder.objects.get_or_create(
            work_order_no='WO-2026-REL-088',
            defaults={
                'aircraft': ac3,
                'title': 'B787-9 Bleed Air PRSOV Pressure Sensor Calibration',
                'description': 'Scheduled instrument calibration and BITE test completed. All parameters within OEM flight envelope.',
                'order_type': 'SCHEDULED_CHECK',
                'priority': 'ROUTINE',
                'status': 'CLOSED_RELEASED',
                'assigned_team': 'Avionics Specialists Team',
                'estimated_man_hours': 6.0,
                'actual_man_hours': 5.5,
                'sign_off_engineer': 'Eng. Amit K. Verma (AME DGCA B2)',
                'certificate_of_release': 'CRS-DEL-B787-2026-088',
                'released_to_service': True,
                'closed_at': now - timedelta(days=1)
            }
        )

        WorkOrderTask.objects.get_or_create(
            work_order=wo1, task_code='TSK-AOG-01',
            defaults={'description': 'De-pressurize Green Hydraulic System and install safety landing gear locks', 'amm_reference': 'AMM 32-00-01', 'technician_assigned': 'Arjun Nair', 'status': 'COMPLETED', 'is_critical': True}
        )
        WorkOrderTask.objects.get_or_create(
            work_order=wo1, task_code='TSK-AOG-02',
            defaults={'description': 'Extract leaking MLG actuator gland seal assembly and inspect cylinder bore', 'amm_reference': 'AMM 32-31-05', 'technician_assigned': 'Vikram Joshi', 'status': 'IN_PROGRESS', 'is_critical': True}
        )
        WorkOrderTask.objects.get_or_create(
            work_order=wo1, task_code='TSK-AOG-03',
            defaults={'description': 'Install OEM seal kit P/N SK-MLG-774 and torque gland nut to 120 lbf.ft', 'amm_reference': 'AMM 32-31-06', 'technician_assigned': 'Vikram Joshi', 'status': 'PENDING', 'is_critical': True}
        )

        LaborLog.objects.get_or_create(
            work_order=wo1, technician_name='Vikram Joshi',
            defaults={'hours_worked': 4.0, 'work_performed': 'Removed actuator lower pin and extracted damaged backup ring.'}
        )

        # 4. SPARE PARTS INVENTORY (Module 4)
        self.stdout.write("- Seeding Spare Parts Inventory...")
        cat_hyd, _ = PartCategory.objects.get_or_create(code='CAT-HYD', defaults={'name': 'Hydraulics & Flight Controls', 'description': 'Pumps, actuators, valves, and high-pressure hose assemblies'})
        cat_eng, _ = PartCategory.objects.get_or_create(code='CAT-ENG', defaults={'name': 'Engine & Powerplant Spares', 'description': 'Turbofan blades, igniters, fuel nozzles, starter generators'})
        cat_av, _ = PartCategory.objects.get_or_create(code='CAT-AV', defaults={'name': 'Avionics & Sensors', 'description': 'Pitot probes, angle-of-attack sensors, TCAS antennas, radar transceivers'})
        cat_hard, _ = PartCategory.objects.get_or_create(code='CAT-HARD', defaults={'name': 'Airframe Hardware & Seal Kits', 'description': 'Aerospace O-rings, titanium fasteners, safety wire'})

        part1, _ = SparePart.objects.get_or_create(
            part_number='SK-MLG-774',
            defaults={
                'description': 'A320/A321 MLG Retraction Actuator OEM Seal Kit',
                'category': cat_hyd,
                'quantity_on_hand': 2,
                'minimum_safety_stock': 4,
                'reorder_quantity': 6,
                'unit_of_measure': 'KIT',
                'unit_cost_usd': 1480.00,
                'storage_bin_location': 'ZONE-B / RACK-04 / BIN-12',
                'condition': 'NEW_OEM',
                'shelf_life_controlled': True,
                'expiry_date': today + timedelta(days=600)
            }
        )

        part2, _ = SparePart.objects.get_or_create(
            part_number='CFM-BLD-7701',
            defaults={
                'description': 'CFM56-7B Stage 1 Titanium Fan Blade (Matched Pair)',
                'category': cat_eng,
                'serial_number_tracked': True,
                'quantity_on_hand': 8,
                'minimum_safety_stock': 2,
                'reorder_quantity': 4,
                'unit_of_measure': 'SET',
                'unit_cost_usd': 8950.00,
                'storage_bin_location': 'ZONE-A / HEAVY-ROT-01',
                'condition': 'NEW_OEM'
            }
        )

        part3, _ = SparePart.objects.get_or_create(
            part_number='PITOT-COLL-900',
            defaults={
                'description': 'Heated Pitot-Static Probe Head (FAA/EASA TSO-C16a)',
                'category': cat_av,
                'serial_number_tracked': True,
                'quantity_on_hand': 3,
                'minimum_safety_stock': 2,
                'reorder_quantity': 5,
                'unit_of_measure': 'EA',
                'unit_cost_usd': 3420.00,
                'storage_bin_location': 'ZONE-C / AVIONICS-CAGE-09',
                'condition': 'OVERHAULED'
            }
        )

        part4, _ = SparePart.objects.get_or_create(
            part_number='ORING-AERO-014',
            defaults={
                'description': 'Viton High-Temperature O-Ring Pack (Size AS568-014)',
                'category': cat_hard,
                'quantity_on_hand': 85,
                'minimum_safety_stock': 20,
                'reorder_quantity': 50,
                'unit_of_measure': 'EA',
                'unit_cost_usd': 12.50,
                'storage_bin_location': 'ZONE-D / FASTENERS-BIN-33',
                'condition': 'NEW_OEM'
            }
        )

        InventoryTransaction.objects.get_or_create(
            spare_part=part1,
            reference_order='WO-2026-AOG-01',
            transaction_type='ISSUE_WORK_ORDER',
            defaults={'quantity': 1, 'performed_by': 'Storekeeper Ankit Verma', 'notes': 'Issued to AOG Ramp team with Certificate of Conformity'}
        )

        # 5. EXECUTION & DOCUMENTATION (Module 5)
        self.stdout.write("- Seeding Job Cards & Defect Reports...")
        JobCardExecution.objects.get_or_create(
            work_order=wo1,
            job_card_no='JC-32-31-01',
            step_number=1,
            defaults={
                'step_instruction': 'Verify ground safety gear pins installed on all three landing gears. Connect GPU and verify hydraulic pressure is zero.',
                'amm_clause_reference': 'AMM 32-00-00 Page 201',
                'technician_name': 'Arjun Nair',
                'technician_stamp': 'DGCA-AME-8812',
                'is_completed': True,
                'completed_at': now - timedelta(hours=3),
                'inspector_name': 'Lead Insp. Sunita Menon',
                'inspector_stamp': 'QC-DEL-77',
                'is_inspected': True,
                'inspected_at': now - timedelta(hours=2)
            }
        )

        JobCardExecution.objects.get_or_create(
            work_order=wo1,
            job_card_no='JC-32-31-02',
            step_number=2,
            defaults={
                'step_instruction': 'Clean actuator gland area using solvent MIL-PRF-680. Unfasten retaining collar and extract old seal pack.',
                'amm_clause_reference': 'AMM 32-31-02 Page 405',
                'technician_name': 'Vikram Joshi',
                'technician_stamp': 'AME-DGCA-B1-4019',
                'is_completed': True,
                'completed_at': now - timedelta(hours=1)
            }
        )

        DefectReport.objects.get_or_create(
            defect_log_number='DEF-2026-0941',
            defaults={
                'aircraft': ac4,
                'work_order': wo1,
                'report_source': 'MAREP',
                'title': 'Left MLG Retract Cylinder Fluid Leakage Exceeds 5 Drops/Min Limit',
                'discrepancy_details': 'Ramp transit check revealed red Skydrol hydraulic fluid pooling around left MLG bay door. Actuator shaft wetness confirmed.',
                'severity': 'AOG',
                'flight_sector': 'AI-308 CCU-DEL',
                'mel_reference': 'Non-MEL item (Airframe primary flight gear)',
                'status': 'OPEN',
                'reported_by': 'Line Mechanic Rahul Sen'
            }
        )

        DefectReport.objects.get_or_create(
            defect_log_number='DEF-2026-0920',
            defaults={
                'aircraft': ac1,
                'report_source': 'PIREP',
                'title': 'Cockpit Right Audio Control Panel (ACP) Intermittent Static in VHF-2',
                'discrepancy_details': 'First Officer reported background hash on VHF-2 reception during descent into DEL.',
                'severity': 'MINOR_MEL',
                'flight_sector': 'AI-805 BLR-DEL',
                'mel_reference': 'MEL 23-51-01 (Category C - 10 Calendar Days Dispatch)',
                'status': 'DEFERRED_MEL',
                'reported_by': 'Capt. K. Nambiar',
                'rectification_action': 'Deferred under MEL 23-51-01. Placed caution placard on FO ACP.'
            }
        )

        # 6. COMPLIANCE MANAGEMENT (Module 6)
        self.stdout.write("- Seeding Airworthiness Directives & Licenses...")
        ad1, _ = AirworthinessDirective.objects.get_or_create(
            ad_number='DGCA-AD-2026-08',
            defaults={
                'issuing_authority': 'DGCA',
                'title': 'Boeing 737NG Horizontal Stabilizer Trim Actuator Inspection',
                'applicable_models': 'Boeing 737-700, 737-800, 737-900ER',
                'effective_date': today - timedelta(days=60),
                'compliance_deadline': today + timedelta(days=45),
                'is_recurring': True,
                'repeat_interval_flight_hours': 1200,
                'action_required': 'Measure backlash and thread wear on jackscrew ball nut assembly using Boeing tool ST-990.',
                'status': 'MANDATORY_OPEN'
            }
        )

        ad2, _ = AirworthinessDirective.objects.get_or_create(
            ad_number='EASA-AD-2025-0219R1',
            defaults={
                'issuing_authority': 'EASA',
                'title': 'Airbus A320neo Family Engine Cowl Latch Modification',
                'applicable_models': 'Airbus A319neo, A320neo, A321neo',
                'effective_date': today - timedelta(days=180),
                'compliance_deadline': today + timedelta(days=20),
                'is_recurring': False,
                'action_required': 'Install redesigned ergonomic latch flag kit as per Airbus SB A320-71-1074.',
                'status': 'MANDATORY_OPEN'
            }
        )

        AircraftADCompliance.objects.get_or_create(
            aircraft=ac1, directive=ad1,
            defaults={'is_complied': False, 'next_due_date': today + timedelta(days=45)}
        )

        ServiceBulletin.objects.get_or_create(
            sb_number='BOEING-SB-737-24A1144',
            defaults={
                'oem_manufacturer': 'The Boeing Company',
                'title': 'Electrical Power - IDG Feeder Cable Terminal Lug Inspection and Clamp Upgrade',
                'category': 'ALERT',
                'release_date': today - timedelta(days=40),
                'summary': 'Inspection of Integrated Drive Generator feeder wiring to prevent chafing in pylon area.',
                'is_incorporated': True
            }
        )

        TechnicianLicense.objects.get_or_create(
            license_number='AME-DGCA-B1-7712',
            defaults={
                'technician_name': 'Chief Eng. Rajesh Sharma',
                'category': 'B1_MECHANICAL',
                'authorized_aircraft_ratings': 'Boeing 737NG/MAX, Airbus A320neo (CFM LEAP-1A / CFM56)',
                'expiry_date': today + timedelta(days=720),
                'is_active': True
            }
        )

        # 7. ERP & SUPPLY CHAIN (Module 7)
        self.stdout.write("- Seeding ERP Suppliers & Purchase Orders...")
        vnd1, _ = VendorSupplier.objects.get_or_create(
            vendor_code='VND-BOEING-DIST',
            defaults={
                'name': 'Boeing Global Distribution Services Inc.',
                'oem_type': 'OEM Direct Airframe Parts',
                'contact_email': 'apac-orders@boeingdistribution.com',
                'phone': '+1-206-544-5000',
                'country': 'United States',
                'rating_score': 4.95,
                'is_faa_easa_approved': True
            }
        )

        vnd2, _ = VendorSupplier.objects.get_or_create(
            vendor_code='VND-SAFRAN-AERO',
            defaults={
                'name': 'Safran Landing Systems Services India',
                'oem_type': 'Landing Gear & Brake Specialist',
                'contact_email': 'spares@safrangroup.com',
                'phone': '+91-124-490-8800',
                'country': 'France / India',
                'rating_score': 4.88,
                'is_faa_easa_approved': True
            }
        )

        po1, _ = PurchaseOrder.objects.get_or_create(
            po_number='PO-2026-ERP-9912',
            defaults={
                'vendor': vnd2,
                'erp_system_ref': 'SAP-ECC-PO-8840192',
                'expected_delivery_date': today + timedelta(days=2),
                'total_amount_usd': 5920.00,
                'status': 'IN_TRANSIT',
                'shipping_carrier': 'FedEx Aerospace Critical Rush',
                'air_waybill_number': 'AWB-FDX-7719-2044',
                'customs_declaration_no': 'BOE-DEL-AIR-2026-449'
            }
        )

        PurchaseOrderItem.objects.get_or_create(
            purchase_order=po1,
            part_number='SK-MLG-774',
            defaults={'description': 'A320/A321 MLG Actuator OEM Seal Kits', 'quantity_ordered': 4, 'quantity_received': 0, 'unit_cost_usd': 1480.00}
        )

        # 8. FIELD MOBILE TECHNICIAN (Module 8)
        self.stdout.write("- Seeding Field Mobile Inspections...")
        insp1, _ = FieldInspection.objects.get_or_create(
            inspection_id='FINSP-DEL-2026-088',
            defaults={
                'aircraft': ac4,
                'technician_name': 'Rahul Sen',
                'technician_badge': 'AME-DEL-2940',
                'stand_bay_location': 'DEL Terminal 3 - Stand 34',
                'inspection_type': 'RAMP_TRANSIT_CHECK',
                'status': 'IN_PROGRESS',
                'findings_summary': 'Found excessive hydraulic fluid weeping from MLG bay. Reported to MCC. AOG declared.',
                'tire_pressure_psi': 204.0,
                'oil_level_quarts': 17.8,
                'battery_voltage_vdc': 28.4,
                'gps_coordinates': '28.5562° N, 77.1000° E (DEL T3 Apron)'
            }
        )

        QuickDiscrepancyLog.objects.get_or_create(
            field_inspection=insp1,
            aircraft_zone='LANDING_GEAR',
            defaults={'snag_description': 'Skydrol puddle 12cm diameter under port MLG wheel well', 'severity': 'AOG', 'action_taken_on_ramp': 'Isolated hydraulic brake accumulator and cordoned off stand.'}
        )

        OfflineSyncRecord.objects.get_or_create(
            device_id='PANASONIC-MRO-TAB-04',
            defaults={'device_model': 'Panasonic Toughbook G2 Rugged', 'sync_action': 'RAMP_AUDIT_BATCH_UPLOAD', 'payload_snapshot': '{"records": 4, "photos": 2, "timestamp": "2026-11-20T14:30"}', 'sync_status': 'SYNCED'}
        )

        # 9. PREDICTIVE ANALYTICS & HEALTH (Module 9)
        self.stdout.write("- Seeding Telemetry & Predictive Failure Alerts...")
        TelemetrySensorReading.objects.get_or_create(
            aircraft=ac2,
            subsystem_name='PW1100G Port Turbofan #1',
            parameter_name='Exhaust Gas Temperature (EGT) Margin °C',
            defaults={'sensor_value': 28.5, 'nominal_min': 25.0, 'nominal_max': 90.0, 'is_anomaly': False}
        )
        TelemetrySensorReading.objects.get_or_create(
            aircraft=ac2,
            subsystem_name='PW1100G Starboard Turbofan #2',
            parameter_name='N1 Low Pressure Rotor Vibration Index',
            defaults={'sensor_value': 1.85, 'nominal_min': 0.1, 'nominal_max': 1.2, 'is_anomaly': True}
        )

        PredictiveAlert.objects.get_or_create(
            alert_id='PRED-ALT-7704',
            defaults={
                'aircraft': ac2,
                'component_name': 'PW1100G Engine #2 Bearing #3 Vibration Harmonic',
                'predicted_failure_probability_pct': 87.2,
                'predicted_failure_window': 'Next 45 Flight Hours',
                'severity': 'CRITICAL',
                'recommended_action': 'Perform borescope inspection of #3 bearing compartment and analyze magnetic chip detector for metallic debris.',
                'status': 'ACTIVE'
            }
        )

        PredictiveAlert.objects.get_or_create(
            alert_id='PRED-ALT-7705',
            defaults={
                'aircraft': ac1,
                'component_name': 'Green System Hydraulic Engine Driven Pump (EDP)',
                'predicted_failure_probability_pct': 64.0,
                'predicted_failure_window': 'Next 120 Flight Hours',
                'severity': 'WARNING',
                'recommended_action': 'Pressure output decaying during high rudder deflection demand. Inspect case drain filter.',
                'status': 'ACKNOWLEDGED'
            }
        )

        FleetKPIMetric.objects.get_or_create(
            id=1,
            defaults={
                'fleet_dispatch_reliability_pct': 99.4,
                'mean_time_between_failures_hours': 438.5,
                'mean_time_to_repair_hours': 4.1,
                'active_aog_incidents': 1,
                'maintenance_cost_per_flight_hour_usd': 274.20,
                'predictive_early_catch_count': 26
            }
        )

        # 10. AUDIT TRAIL & SYSTEM ROLES (Module 10)
        self.stdout.write("- Seeding Audit Logs & User Roles...")
        MROUserProfile.objects.get_or_create(
            username='rsharma_chief',
            defaults={
                'full_name': 'Chief Eng. Rajesh Sharma',
                'email': 'rajesh.sharma@flightfix.aero',
                'role': 'CHIEF_ENGINEER',
                'license_stamp_no': 'AME-DGCA-B1-7712',
                'department': 'Hangar 1 Line & Base Maintenance'
            }
        )
        MROUserProfile.objects.get_or_create(
            username='smenon_qa',
            defaults={
                'full_name': 'Inspector Sunita Menon',
                'email': 'sunita.menon@flightfix.aero',
                'role': 'QUALITY_AUDITOR',
                'license_stamp_no': 'DGCA-QC-INSP-04',
                'department': 'Quality Assurance & Regulatory Safety'
            }
        )
        MROUserProfile.objects.get_or_create(
            username='rsen_field',
            defaults={
                'full_name': 'Line Tech Rahul Sen',
                'email': 'rahul.sen@flightfix.aero',
                'role': 'LINE_TECHNICIAN',
                'license_stamp_no': 'AME-DEL-2940',
                'department': 'Ramp Line Operations'
            }
        )

        MROAuditTrail.objects.get_or_create(
            entity_reference='WO-2026-AOG-01',
            action_type='STATUS_CHANGE',
            defaults={
                'user_name': 'Rahul Sen',
                'user_role': 'Line Maintenance Technician',
                'target_module': 'WORK_ORDERS',
                'ip_address': '192.168.1.104',
                'details': 'Declared AOG status on aircraft VT-AOG following hydraulic seal blowout on port MLG.'
            }
        )
        MROAuditTrail.objects.get_or_create(
            entity_reference='PO-2026-ERP-9912',
            action_type='ERP_TRANSACTION',
            defaults={
                'user_name': 'Storekeeper Ankit Verma',
                'user_role': 'Materials & Avionics Storekeeper',
                'target_module': 'SUPPLY_CHAIN',
                'ip_address': '192.168.1.45',
                'details': 'Dispatched emergency rush procurement order to Safran Landing Systems via SAP ERP gateway.'
            }
        )
        MROAuditTrail.objects.get_or_create(
            entity_reference='WO-2026-REL-088',
            action_type='SIGN_OFF',
            defaults={
                'user_name': 'Chief Eng. Rajesh Sharma',
                'user_role': 'Certifying Engineer (B1/B2)',
                'target_module': 'WORK_ORDERS',
                'ip_address': '192.168.1.12',
                'details': 'Issued Certificate of Release to Service (CRS) CRS-DEL-B787-2026-088 for Boeing 787 VT-GLO.'
            }
        )

        self.stdout.write(self.style.SUCCESS("FlightFix data successfully seeded across all 10 modules!"))
