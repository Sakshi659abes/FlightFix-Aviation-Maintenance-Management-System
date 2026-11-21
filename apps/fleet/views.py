from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Aircraft, AircraftSubsystem, GroundEquipment
from .serializers import AircraftSerializer, AircraftSubsystemSerializer, GroundEquipmentSerializer

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all().prefetch_related('subsystems')
    serializer_class = AircraftSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tail_number', 'model', 'serial_number', 'manufacturer', 'status']
    ordering_fields = ['tail_number', 'total_flight_hours', 'status', 'created_at']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        total = Aircraft.objects.count()
        operational = Aircraft.objects.filter(status='OPERATIONAL').count()
        in_maintenance = Aircraft.objects.filter(status='IN_MAINTENANCE').count()
        aog = Aircraft.objects.filter(status='AOG').count()
        fleet_readiness = round((operational / total * 100), 1) if total > 0 else 100
        return Response({
            'total_aircraft': total,
            'operational': operational,
            'in_maintenance': in_maintenance,
            'aog': aog,
            'fleet_readiness_pct': fleet_readiness
        })

class AircraftSubsystemViewSet(viewsets.ModelViewSet):
    queryset = AircraftSubsystem.objects.all()
    serializer_class = AircraftSubsystemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['system_name', 'health_status']

class GroundEquipmentViewSet(viewsets.ModelViewSet):
    queryset = GroundEquipment.objects.all()
    serializer_class = GroundEquipmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['equipment_tag', 'equipment_type', 'status', 'assigned_hangar']
