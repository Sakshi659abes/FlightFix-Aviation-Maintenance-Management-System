from django.db import models
from apps.fleet.models import Aircraft

class TelemetrySensorReading(models.Model):
    aircraft = models.ForeignKey(Aircraft, related_name='telemetry_readings', on_delete=models.CASCADE)
    subsystem_name = models.CharField(max_length=100) # e.g., Turbofan #1, Hydraulic Green, APU
    parameter_name = models.CharField(max_length=100) # EGT Margin °C, N1 Vibration, Oil Pressure PSI
    sensor_value = models.FloatField()
    nominal_min = models.FloatField(default=0.0)
    nominal_max = models.FloatField(default=100.0)
    is_anomaly = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.aircraft.tail_number} [{self.parameter_name}]: {self.sensor_value} (Anomaly: {self.is_anomaly})"


class PredictiveAlert(models.Model):
    SEVERITY_LEVELS = [
        ('CRITICAL', 'Critical - Imminent Failure (<48 hrs)'),
        ('WARNING', 'Warning - Degradation Trend Detected'),
        ('ADVISORY', 'Advisory - Schedule Inspection at Next Check'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active Alert'),
        ('ACKNOWLEDGED', 'Acknowledged by Engineering'),
        ('WO_GENERATED', 'Preemptive Work Order Generated'),
        ('RESOLVED', 'Resolved & Component Restored'),
    ]

    alert_id = models.CharField(max_length=40, unique=True)
    aircraft = models.ForeignKey(Aircraft, related_name='predictive_alerts', on_delete=models.CASCADE)
    component_name = models.CharField(max_length=120)
    predicted_failure_probability_pct = models.FloatField(default=85.0)
    predicted_failure_window = models.CharField(max_length=80, default='Next 35 Flight Hours')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='WARNING')
    recommended_action = models.TextField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='ACTIVE')
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"[{self.alert_id}] {self.aircraft.tail_number}: {self.component_name} ({self.predicted_failure_probability_pct}%)"


class FleetKPIMetric(models.Model):
    metric_date = models.DateField(auto_now_add=True)
    fleet_dispatch_reliability_pct = models.FloatField(default=99.2)
    mean_time_between_failures_hours = models.FloatField(default=412.5)
    mean_time_to_repair_hours = models.FloatField(default=4.8)
    active_aog_incidents = models.IntegerField(default=1)
    maintenance_cost_per_flight_hour_usd = models.FloatField(default=285.50)
    predictive_early_catch_count = models.IntegerField(default=18)

    class Meta:
        ordering = ['-metric_date']

    def __str__(self):
        return f"Fleet KPI {self.metric_date}: Dispatch {self.fleet_dispatch_reliability_pct}%"
