from rest_framework import serializers
from .models import Aircraft, AircraftSubsystem, GroundEquipment

class AircraftSubsystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftSubsystem
        fields = '__all__'

class AircraftSerializer(serializers.ModelSerializer):
    subsystems = AircraftSubsystemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Aircraft
        fields = '__all__'

class GroundEquipmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = GroundEquipment
        fields = '__all__'
