from rest_framework import serializers
from .models import AirworthinessDirective, AircraftADCompliance, ServiceBulletin, TechnicianLicense

class AirworthinessDirectiveSerializer(serializers.ModelSerializer):
    authority_display = serializers.CharField(source='get_issuing_authority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AirworthinessDirective
        fields = '__all__'

class AircraftADComplianceSerializer(serializers.ModelSerializer):
    aircraft_tail = serializers.CharField(source='aircraft.tail_number', read_only=True)
    ad_number = serializers.CharField(source='directive.ad_number', read_only=True)
    ad_title = serializers.CharField(source='directive.title', read_only=True)

    class Meta:
        model = AircraftADCompliance
        fields = '__all__'

class ServiceBulletinSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = ServiceBulletin
        fields = '__all__'

class TechnicianLicenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = TechnicianLicense
        fields = '__all__'
