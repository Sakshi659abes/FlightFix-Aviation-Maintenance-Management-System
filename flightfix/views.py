from django.shortcuts import render
from django.views.generic import TemplateView
from apps.fleet.models import Aircraft
from apps.workorders.models import WorkOrder
from apps.planning.models import MaintenanceSchedule
from apps.inventory.models import SparePart
from apps.compliance.models import AirworthinessDirective
from apps.analytics.models import PredictiveAlert, FleetKPIMetric

def dashboard_view(request):
    """
    Main FlightFix Unified Aviation MRO Operations Command Center.
    Loads real-time metrics across all 10 modules.
    """
    context = {
        'page_title': 'FlightFix MRO | Unified Aerospace Operations Command Center',
        'aircraft_count': Aircraft.objects.count(),
        'operational_count': Aircraft.objects.filter(status='OPERATIONAL').count(),
        'maintenance_count': Aircraft.objects.filter(status='IN_MAINTENANCE').count(),
        'aog_count': Aircraft.objects.filter(status='AOG').count(),
        'open_wo_count': WorkOrder.objects.exclude(status='CLOSED_RELEASED').count(),
        'upcoming_schedules_count': MaintenanceSchedule.objects.filter(status='SCHEDULED').count(),
        'low_stock_parts_count': SparePart.objects.filter(quantity_on_hand__lte=5).count(),
        'mandatory_ads_count': AirworthinessDirective.objects.filter(status='MANDATORY_OPEN').count(),
        'active_predictive_alerts': PredictiveAlert.objects.filter(status='ACTIVE').count(),
    }
    return render(request, 'dashboard.html', context)
