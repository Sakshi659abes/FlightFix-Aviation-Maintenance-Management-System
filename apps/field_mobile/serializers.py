from rest_framework import serializers
from .models import FieldInspection, QuickDiscrepancyLog, OfflineSyncRecord

class QuickDiscrepancyLogSerializer(serializers.ModelSerializer):
    zone_display = serializers.CharField(source='get_aircraft_zone_display', read_only=True)

    class Meta:
        model = QuickDiscrepancyLog
        fields = '__all__'

class FieldInspectionSerializer(serializers.ModelSerializer):
    discrepancies = QuickDiscrepancyLogSerializer(many=True, read_only=True)
    aircraft_tail = serializers.CharField(source='aircraft.tail_number', read_only=True)
    aircraft_model = serializers.CharField(source='aircraft.model', read_only=True)
    inspection_type_display = serializers.CharField(source='get_inspection_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FieldInspection
        fields = '__all__'

class OfflineSyncRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfflineSyncRecord
        fields = '__all__'
