from django.db import models
from apps.fleet.models import Aircraft
from apps.workorders.models import WorkOrder

class JobCardExecution(models.Model):
    work_order = models.ForeignKey(WorkOrder, related_name='job_cards', on_delete=models.CASCADE)
    job_card_no = models.CharField(max_length=50)
    step_number = models.IntegerField(default=1)
    step_instruction = models.TextField()
    amm_clause_reference = models.CharField(max_length=100, default='AMM 32-41-00 Page 401')
    
    technician_name = models.CharField(max_length=100, blank=True, default='')
    technician_stamp = models.CharField(max_length=50, blank=True, default='', help_text="AME Stamp Number")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    inspector_name = models.CharField(max_length=100, blank=True, default='')
    inspector_stamp = models.CharField(max_length=50, blank=True, default='', help_text="Quality Inspector Stamp")
    is_inspected = models.BooleanField(default=False)
    inspected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"{self.job_card_no} Step {self.step_number}: {'DONE' if self.is_completed else 'PENDING'}"


class DefectReport(models.Model):
    REPORT_SOURCE = [
        ('PIREP', 'Pilot In-Flight Report (PIREP)'),
        ('MAREP', 'Maintenance Ground Snag (MAREP)'),
        ('INSPECTION', 'Periodic Audit / Heavy Check Finding'),
    ]

    SEVERITY_LEVELS = [
        ('AOG', 'AOG - Grounds Aircraft Immediately'),
        ('MAJOR', 'Major Defect - Rectify Before Next Sector'),
        ('MINOR_MEL', 'Minor - Dispatch under MEL Allowance'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open Discrepancy'),
        ('DEFERRED_MEL', 'Deferred under MEL (Item Category C/D)'),
        ('RECTIFIED', 'Rectified and Signed Off'),
    ]

    aircraft = models.ForeignKey(Aircraft, related_name='defect_reports', on_delete=models.CASCADE)
    work_order = models.ForeignKey(WorkOrder, null=True, blank=True, related_name='defects', on_delete=models.SET_NULL)
    
    report_source = models.CharField(max_length=20, choices=REPORT_SOURCE, default='PIREP')
    defect_log_number = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=200)
    discrepancy_details = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='MAJOR')
    
    flight_sector = models.CharField(max_length=50, default='AI-402 BOM-DEL')
    mel_reference = models.CharField(max_length=60, blank=True, default='', help_text="e.g. MEL 21-31-01 (Cabin Air Valve)")
    rectification_action = models.TextField(blank=True, default='')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    reported_by = models.CharField(max_length=100, default='Capt. R. Kapoor')
    rectified_by = models.CharField(max_length=100, blank=True, default='')
    assigned_engineer = models.CharField(max_length=100, blank=True, default='')
    expected_start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    manager_notes = models.TextField(blank=True, default='')
    
    date_reported = models.DateTimeField(auto_now_add=True)
    date_rectified = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_reported']

    def __str__(self):
        return f"[{self.defect_log_number}] {self.aircraft.tail_number} - {self.title} ({self.status})"
