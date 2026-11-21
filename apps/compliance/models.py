from django.db import models
from apps.fleet.models import Aircraft

class AirworthinessDirective(models.Model):
    AUTHORITY_CHOICES = [
        ('FAA', 'Federal Aviation Administration (FAA)'),
        ('EASA', 'European Union Aviation Safety Agency (EASA)'),
        ('DGCA', 'Directorate General of Civil Aviation (DGCA India)'),
        ('TCCA', 'Transport Canada Civil Aviation (TCCA)'),
    ]

    STATUS_CHOICES = [
        ('MANDATORY_OPEN', 'Mandatory - Pending Compliance'),
        ('COMPLIED', 'Complied & Certified'),
        ('SUPERSEDED', 'Superseded by Newer Directive'),
        ('TERMINATING_ACTION', 'Terminating Modification Done'),
    ]

    ad_number = models.CharField(max_length=60, unique=True, db_index=True)
    issuing_authority = models.CharField(max_length=20, choices=AUTHORITY_CHOICES, default='DGCA')
    title = models.CharField(max_length=255)
    applicable_models = models.CharField(max_length=150, help_text="e.g. Boeing 737-800, Airbus A320neo")
    
    effective_date = models.DateField()
    compliance_deadline = models.DateField()
    is_recurring = models.BooleanField(default=False)
    repeat_interval_flight_hours = models.IntegerField(default=0, help_text="Hours between repeat inspections if recurring")
    
    action_required = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='MANDATORY_OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['compliance_deadline']

    def __str__(self):
        return f"[{self.ad_number}] {self.title} ({self.status})"


class AircraftADCompliance(models.Model):
    aircraft = models.ForeignKey(Aircraft, related_name='ad_compliances', on_delete=models.CASCADE)
    directive = models.ForeignKey(AirworthinessDirective, related_name='fleet_compliances', on_delete=models.CASCADE)
    complied_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    certifying_engineer = models.CharField(max_length=120, blank=True, default='')
    compliance_method = models.TextField(blank=True, default='')
    is_complied = models.BooleanField(default=False)

    class Meta:
        unique_together = ('aircraft', 'directive')

    def __str__(self):
        return f"{self.aircraft.tail_number} -> {self.directive.ad_number}: {'COMPLIED' if self.is_complied else 'PENDING'}"


class ServiceBulletin(models.Model):
    CATEGORY_CHOICES = [
        ('ALERT', 'Alert / Safety Critical'),
        ('RECOMMENDED', 'Manufacturer Recommended'),
        ('OPTIONAL', 'Optional Improvement / Mod'),
    ]

    sb_number = models.CharField(max_length=80, unique=True)
    oem_manufacturer = models.CharField(max_length=100) # Boeing, CFM International, Collins
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='RECOMMENDED')
    release_date = models.DateField()
    summary = models.TextField()
    is_incorporated = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.sb_number}] {self.title}"


class TechnicianLicense(models.Model):
    CATEGORY_CHOICES = [
        ('B1_MECHANICAL', 'Category B1 (Airframe, Powerplant & Systems)'),
        ('B2_AVIONICS', 'Category B2 (Avionics, Electrical & Instruments)'),
        ('A_LINE', 'Category A (Line Maintenance Certifying Mechanic)'),
        ('C_BASE', 'Category C (Base Maintenance Certifying Engineer)'),
    ]

    technician_name = models.CharField(max_length=120)
    license_number = models.CharField(max_length=60, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='B1_MECHANICAL')
    authorized_aircraft_ratings = models.CharField(max_length=200, default='Boeing 737NG, Airbus A320 Family')
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.technician_name} ({self.license_number}) - {self.category}"
