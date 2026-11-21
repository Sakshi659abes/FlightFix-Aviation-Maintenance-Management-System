from django.db import models

class Aircraft(models.Model):
    STATUS_CHOICES = [
        ('OPERATIONAL', 'Operational'),
        ('IN_MAINTENANCE', 'In Maintenance'),
        ('AOG', 'Aircraft on Ground (AOG)'),
        ('RESERVE', 'Reserve'),
    ]

    tail_number = models.CharField(max_length=20, unique=True, db_index=True)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100)
    total_flight_hours = models.FloatField(default=0.0)
    total_flight_cycles = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPERATIONAL')
    current_location = models.CharField(max_length=100, default='DEL - Indira Gandhi Intl')
    manufacture_date = models.DateField(null=True, blank=True)
    last_inspection_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tail_number']
        verbose_name = 'Aircraft'
        verbose_name_plural = 'Aircraft Fleet'

    def __str__(self):
        return f"{self.tail_number} ({self.model}) - {self.get_status_display()}"


class AircraftSubsystem(models.Model):
    HEALTH_CHOICES = [
        ('EXCELLENT', 'Excellent (90-100%)'),
        ('GOOD', 'Good (75-89%)'),
        ('MONITOR', 'Needs Monitoring (50-74%)'),
        ('CRITICAL', 'Critical Alert (<50%)'),
    ]

    aircraft = models.ForeignKey(Aircraft, related_name='subsystems', on_delete=models.CASCADE)
    system_name = models.CharField(max_length=120)  # e.g., Turbofan Engine #1, Hydraulic Green System, APU
    health_status = models.CharField(max_length=20, choices=HEALTH_CHOICES, default='GOOD')
    health_score = models.IntegerField(default=95)
    last_tested_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.aircraft.tail_number} - {self.system_name} ({self.health_score}%)"


class GroundEquipment(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('IN_USE', 'In Use on Ramp/Hangar'),
        ('CALIBRATION_DUE', 'Calibration Due'),
        ('MAINTENANCE', 'Out of Service'),
    ]

    equipment_tag = models.CharField(max_length=50, unique=True)
    equipment_type = models.CharField(max_length=100) # GPU, Hydraulic Cart, Aircraft Tug, Digital Torque Meter
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    calibration_due_date = models.DateField(null=True, blank=True)
    assigned_hangar = models.CharField(max_length=100, default='Hangar Bay 1 - Line Maint')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['equipment_tag']

    def __str__(self):
        return f"[{self.equipment_tag}] {self.equipment_type} - {self.status}"
