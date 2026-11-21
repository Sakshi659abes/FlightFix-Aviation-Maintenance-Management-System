from django.db import models
from apps.fleet.models import Aircraft

class HangarBay(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Hangar Maintenance'),
    ]

    bay_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    facility_location = models.CharField(max_length=100, default='DEL Hangar Complex')
    max_aircraft_category = models.CharField(max_length=50, default='Wide-Body (CAT E/F)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

    class Meta:
        ordering = ['bay_code']

    def __str__(self):
        return f"{self.bay_code} - {self.name} ({self.status})"


class MaintenanceSchedule(models.Model):
    CHECK_TYPES = [
        ('A_CHECK', 'A-Check (Every 400-600 Flight Hours)'),
        ('B_CHECK', 'B-Check (Every 6-8 Months)'),
        ('C_CHECK', 'C-Check (Heavy Maintenance - 20-24 Months)'),
        ('D_CHECK', 'D-Check (Comprehensive Structural Overhaul)'),
        ('LINE_INSPECTION', 'Daily / Transit Line Inspection'),
        ('MODIFICATION', 'Avionics / Cabin Retrofit'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('ROUTINE', 'Routine Planned'),
        ('URGENT', 'Urgent Operational Requirement'),
        ('CRITICAL_AOG', 'Critical AOG (Aircraft on Ground)'),
    ]

    schedule_id = models.CharField(max_length=30, unique=True, db_index=True)
    aircraft = models.ForeignKey(Aircraft, related_name='maintenance_schedules', on_delete=models.CASCADE)
    check_type = models.CharField(max_length=30, choices=CHECK_TYPES, default='A_CHECK')
    hangar_bay = models.ForeignKey(HangarBay, null=True, blank=True, on_delete=models.SET_NULL, related_name='scheduled_aircraft')
    
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    interval_hours = models.IntegerField(default=500, help_text="Target flight hours for check")
    interval_cycles = models.IntegerField(default=300, help_text="Target flight cycles")
    
    lead_engineer = models.CharField(max_length=100, default='Chief Eng. Rajesh Sharma (EASA/DGCA B1)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='ROUTINE')
    task_scope_summary = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_start']
        verbose_name = 'Maintenance Schedule'
        verbose_name_plural = 'Maintenance Schedules'

    def __str__(self):
        return f"[{self.schedule_id}] {self.aircraft.tail_number} - {self.get_check_type_display()} ({self.status})"
