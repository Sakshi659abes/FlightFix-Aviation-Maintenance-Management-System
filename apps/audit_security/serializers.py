from rest_framework import serializers
from .models import MROAuditTrail, MROUserProfile

class MROAuditTrailSerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    target_module_display = serializers.CharField(source='get_target_module_display', read_only=True)

    class Meta:
        model = MROAuditTrail
        fields = '__all__'

class MROUserProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = MROUserProfile
        fields = '__all__'
