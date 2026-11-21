from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MROAuditTrail, MROUserProfile
from .serializers import MROAuditTrailSerializer, MROUserProfileSerializer

class MROAuditTrailViewSet(viewsets.ModelViewSet):
    queryset = MROAuditTrail.objects.all()
    serializer_class = MROAuditTrailSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user_name', 'action_type', 'target_module', 'entity_reference', 'details']
    ordering_fields = ['timestamp', 'action_type', 'target_module']

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        recent = MROAuditTrail.objects.all()[:15]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)

class MROUserProfileViewSet(viewsets.ModelViewSet):
    queryset = MROUserProfile.objects.all()
    serializer_class = MROUserProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'full_name', 'role', 'department', 'license_stamp_no']

    @action(detail=False, methods=['get'])
    def active_roles(self, request):
        users = MROUserProfile.objects.filter(is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
