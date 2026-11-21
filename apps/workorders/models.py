from django.db import models
from apps.fleet.models import Aircraft
from apps.planning.models import MaintenanceSchedule

class WorkOrder(models.Model):
    ORDER_TYPES = [
        ('SCHEDULED_CHECK', 'Scheduled Routine Maintenance'),
        ('UNSCHEDULED_DEFECT', 'Unscheduled Defect Rectification'),
        ('AIRWORTHINESS_DIRECTIVE', 'Airworthiness Directive (AD) Compliance'),
        ('SERVICE_BULLETIN', 'Service Bulletin (SB) Compliance'),
        ('PRE_FLIGHT_SNAG', 'Pre-Flight / Transit Snag'),
    ]

    PRIORITY_CHOICES = [
        ('CRITICAL_AOG', 'Aircraft on Ground (AOG) - Critical'),
        ('HIGH', 'High - Immediate Turnaround'),
        ('MEDIUM', 'Medium - Routine Base MRO'),
        ('ROUTINE', 'Routine - Minor Defect'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open / Draft'),
        ('IN_PROGRESS', 'In Progress'),
        ('AWAITING_PARTS', 'Awaiting Spare Parts'),
        ('INSPECTION_PENDING', 'Work Completed - Inspection Pending'),
        ('CLOSED_RELEASED', 'Closed & Released to Service (CRS)'),
    ]

    work_order_no = models.CharField(max_length=35, unique=True, db_index=True)
    aircraft = models.ForeignKey(Aircraft, related_name='work_orders', on_delete=models.CASCADE)
    schedule = models.ForeignKey(MaintenanceSchedule, null=True, blank=True, related_name='work_orders', on_delete=models.SET_NULL)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    order_type = models.CharField(max_length=35, choices=ORDER_TYPES, default='SCHEDULED_CHECK')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='OPEN')
    
    assigned_team = models.CharField(max_length=120, default='Avionics & Mechanical Line Team A')
    estimated_man_hours = models.FloatField(default=12.0)
    actual_man_hours = models.FloatField(default=0.0)
    
    sign_off_engineer = models.CharField(max_length=120, blank=True, default='')
    certificate_of_release = models.CharField(max_length=100, blank=True, default='', help_text="CRS Reference Number")
    released_to_service = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Work Order'
        verbose_name_plural = 'Work Orders'

    def __str__(self):
        return f"[{self.work_order_no}] {self.aircraft.tail_number} - {self.title} ({self.status})"


class WorkOrderTask(models.Model):
    TASK_STATUS = [
        ('PENDING', 'Pending Assignment'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed & Signed'),
    ]

    work_order = models.ForeignKey(WorkOrder, related_name='tasks', on_delete=models.CASCADE)
    task_code = models.CharField(max_length=30)
    description = models.CharField(max_length=255)
    amm_reference = models.CharField(max_length=80, blank=True, default='AMM 24-00-00', help_text="Aircraft Maintenance Manual reference")
    technician_assigned = models.CharField(max_length=100, blank=True, default='Amit Verma')
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='PENDING')
    is_critical = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_code} - {self.description} ({self.status})"


class LaborLog(models.Model):
    work_order = models.ForeignKey(WorkOrder, related_name='labor_logs', on_delete=models.CASCADE)
    technician_name = models.CharField(max_length=100)
    hours_worked = models.FloatField(default=1.0)
    work_performed = models.TextField()
    date_logged = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.technician_name} - {self.hours_worked} hrs on {self.work_order.work_order_no}"
