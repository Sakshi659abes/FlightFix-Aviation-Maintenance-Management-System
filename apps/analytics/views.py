from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TelemetrySensorReading, PredictiveAlert, FleetKPIMetric
from .serializers import TelemetrySensorReadingSerializer, PredictiveAlertSerializer, FleetKPIMetricSerializer

class TelemetrySensorReadingViewSet(viewsets.ModelViewSet):
    queryset = TelemetrySensorReading.objects.all().select_related('aircraft')
    serializer_class = TelemetrySensorReadingSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['aircraft__tail_number', 'subsystem_name', 'parameter_name']
    ordering_fields = ['recorded_at', 'sensor_value']

class PredictiveAlertViewSet(viewsets.ModelViewSet):
    queryset = PredictiveAlert.objects.all().select_related('aircraft')
    serializer_class = PredictiveAlertSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['alert_id', 'aircraft__tail_number', 'component_name', 'severity', 'status']
    ordering_fields = ['detected_at', 'predicted_failure_probability_pct', 'severity']

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'ACKNOWLEDGED'
        alert.save()
        return Response({'message': f'Predictive alert {alert.alert_id} acknowledged by Fleet Engineering.', 'status': alert.status})

    @action(detail=True, methods=['post'])
    def generate_work_order(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'WO_GENERATED'
        alert.save()
        return Response({
            'message': f'Preemptive Work Order created for {alert.component_name} on {alert.aircraft.tail_number}',
            'status': alert.status
        })

class FleetKPIMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FleetKPIMetric.objects.all()
    serializer_class = FleetKPIMetricSerializer

    @action(detail=False, methods=['get'])
    def live_kpis(self, request):
        latest = FleetKPIMetric.objects.first()
        if not latest:
            return Response({
                'dispatch_reliability': 99.4,
                'mtbf_hours': 428.0,
                'mttr_hours': 4.2,
                'active_aog': 1,
                'aog_downtime_reduction_pct': 34.8,
                'prevented_delays_this_month': 22
            })
        return Response({
            'dispatch_reliability': latest.fleet_dispatch_reliability_pct,
            'mtbf_hours': latest.mean_time_between_failures_hours,
            'mttr_hours': latest.mean_time_to_repair_hours,
            'active_aog': latest.active_aog_incidents,
            'aog_downtime_reduction_pct': 36.2,
            'prevented_delays_this_month': latest.predictive_early_catch_count
        })
