from rest_framework import serializers
from .models import HangarBay, MaintenanceSchedule

class HangarBaySerializer(serializers.ModelSerializer):
    class Meta:
        model = HangarBay
        fields = '__all__'

class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    aircraft_tail = serializers.CharField(source='aircraft.tail_number', read_only=True)
    aircraft_model = serializers.CharField(source='aircraft.model', read_only=True)
    hangar_bay_code = serializers.CharField(source='hangar_bay.bay_code', read_only=True)
    check_type_display = serializers.CharField(source='get_check_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'
