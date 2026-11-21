from django.db import models

class MROAuditTrail(models.Model):
    ACTION_CHOICES = [
        ('SIGN_OFF', 'Airworthiness Sign-off & Release to Service'),
        ('INSPECTION_STAMP', 'Digital Stamp Placed on Job Card'),
        ('STATUS_CHANGE', 'Work Order / Aircraft Status Updated'),
        ('STOCK_ISSUE', 'Critical Spare Part Issued from Stores'),
        ('ERP_TRANSACTION', 'Dispatched Purchase Order to Enterprise ERP'),
        ('AD_CERTIFIED', 'Regulatory Compliance Certified'),
        ('SECURITY_LOGIN', 'User Logged into MRO Terminal'),
    ]

    MODULE_CHOICES = [
        ('PLANNING', 'Planning & Scheduling'),
        ('WORK_ORDERS', 'Work Order Management'),
        ('FLEET', 'Fleet & Ground Equipment'),
        ('INVENTORY', 'Parts Inventory'),
        ('EXECUTION', 'Execution & AMM Documentation'),
        ('COMPLIANCE', 'Airworthiness Compliance'),
        ('SUPPLY_CHAIN', 'ERP & Supply Chain'),
        ('MOBILE_FIELD', 'Field Mobile Operations'),
        ('PREDICTIVE', 'Predictive Diagnostics'),
        ('SECURITY', 'Security & Administration'),
    ]

    user_name = models.CharField(max_length=100, default='Lead Eng. Rajesh Sharma')
    user_role = models.CharField(max_length=60, default='Certifying Engineer (B1/B2)')
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES, default='STATUS_CHANGE')
    target_module = models.CharField(max_length=30, choices=MODULE_CHOICES, default='WORK_ORDERS')
    entity_reference = models.CharField(max_length=100, help_text="e.g. WO-2026-401 or VT-FFX")
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'MRO Audit Trail'
        verbose_name_plural = 'MRO Audit Trail Records'

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.user_name} -> {self.action_type} on {self.entity_reference}"


class MROUserProfile(models.Model):
    ROLE_CHOICES = [
        ('MAINT_MANAGER', 'Base Maintenance Operations Director'),
        ('CHIEF_ENGINEER', 'Chief Certifying Engineer (DGCA/FAA/EASA)'),
        ('LINE_TECHNICIAN', 'Line Maintenance Technician'),
        ('QUALITY_AUDITOR', 'Quality Assurance & Regulatory Auditor'),
        ('STOREKEEPER', 'Materials & Avionics Storekeeper'),
        ('FLEET_PLANNER', 'Fleet Maintenance Planner'),
    ]

    username = models.CharField(max_length=60, unique=True)
    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='CHIEF_ENGINEER')
    license_stamp_no = models.CharField(max_length=50, blank=True, default='AME-DGCA-6012')
    department = models.CharField(max_length=100, default='Airframe & Powerplant Base MRO')
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
