from rest_framework import serializers
from .models import TelemetrySensorReading, PredictiveAlert, FleetKPIMetric

class TelemetrySensorReadingSerializer(serializers.ModelSerializer):
    aircraft_tail = serializers.CharField(source='aircraft.tail_number', read_only=True)

    class Meta:
        model = TelemetrySensorReading
        fields = '__all__'

class PredictiveAlertSerializer(serializers.ModelSerializer):
    aircraft_tail = serializers.CharField(source='aircraft.tail_number', read_only=True)
    aircraft_model = serializers.CharField(source='aircraft.model', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PredictiveAlert
        fields = '__all__'

class FleetKPIMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = FleetKPIMetric
        fields = '__all__'
