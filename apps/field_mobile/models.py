from django.db import models
from apps.fleet.models import Aircraft

class FieldInspection(models.Model):
    INSPECTION_TYPES = [
        ('RAMP_TRANSIT_CHECK', 'Ramp Transit Check (Between Turnarounds)'),
        ('WALKAROUND_EXTERIOR', '360° Exterior Airframe Walkaround'),
        ('TIRE_BRAKE_PRESSURE', 'Landing Gear, Tire & Brake Wear Check'),
        ('ENGINE_INLET_FAN', 'Engine Cowling & Fan Blade Visual Check'),
    ]

    STATUS_CHOICES = [
        ('IN_PROGRESS', 'Active On Hangar / Ramp'),
        ('SUBMITTED', 'Submitted to Base MRO'),
        ('SYNCED_TO_CORE_MRO', 'Fully Synced with Work Orders'),
    ]

    inspection_id = models.CharField(max_length=40, unique=True, db_index=True)
    aircraft = models.ForeignKey(Aircraft, related_name='field_inspections', on_delete=models.CASCADE)
    technician_name = models.CharField(max_length=100, default='Line Tech Rahul Sen')
    technician_badge = models.CharField(max_length=50, default='AME-DEL-2940')
    stand_bay_location = models.CharField(max_length=100, default='Terminal 3 - Bay Stand 24')
    
    inspection_type = models.CharField(max_length=35, choices=INSPECTION_TYPES, default='RAMP_TRANSIT_CHECK')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='IN_PROGRESS')
    findings_summary = models.TextField(blank=True, default='')
    
    tire_pressure_psi = models.FloatField(default=205.0)
    oil_level_quarts = models.FloatField(default=18.5)
    battery_voltage_vdc = models.FloatField(default=28.2)
    
    has_photo_evidence = models.BooleanField(default=True)
    gps_coordinates = models.CharField(max_length=100, default='28.5562° N, 77.1000° E')
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.inspection_id}] {self.aircraft.tail_number} - {self.get_inspection_type_display()}"


class QuickDiscrepancyLog(models.Model):
    ZONE_CHOICES = [
        ('NOSE_RADOME', 'Zone 1: Nose & Radome'),
        ('PORT_WING', 'Zone 2: Port (Left) Wing & Slats'),
        ('STBD_WING', 'Zone 3: Starboard (Right) Wing'),
        ('POWERPLANT_1', 'Zone 4: Left CFM LEAP-1B Turbofan'),
        ('POWERPLANT_2', 'Zone 5: Right CFM LEAP-1B Turbofan'),
        ('LANDING_GEAR', 'Zone 6: Main & Nose Landing Gear'),
        ('EMPENNAGE_TAIL', 'Zone 7: Vertical Fin & Horizontal Stabilizer'),
    ]

    field_inspection = models.ForeignKey(FieldInspection, related_name='discrepancies', on_delete=models.CASCADE)
    aircraft_zone = models.CharField(max_length=30, choices=ZONE_CHOICES, default='LANDING_GEAR')
    snag_description = models.CharField(max_length=255)
    severity = models.CharField(max_length=20, default='ROUTINE')
    action_taken_on_ramp = models.TextField(blank=True, default='')
    resolved_on_ramp = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.aircraft_zone}: {self.snag_description}"


class OfflineSyncRecord(models.Model):
    device_id = models.CharField(max_length=100)
    device_model = models.CharField(max_length=100, default='Panasonic Toughbook MRO Edition')
    sync_action = models.CharField(max_length=100)
    payload_snapshot = models.TextField()
    sync_status = models.CharField(max_length=20, default='SYNCED')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} - {self.sync_action} ({self.sync_status})"
