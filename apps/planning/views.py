from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import HangarBay, MaintenanceSchedule
from .serializers import HangarBaySerializer, MaintenanceScheduleSerializer

class HangarBayViewSet(viewsets.ModelViewSet):
    queryset = HangarBay.objects.all()
    serializer_class = HangarBaySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['bay_code', 'name', 'status']

class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSchedule.objects.all().select_related('aircraft', 'hangar_bay')
    serializer_class = MaintenanceScheduleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['schedule_id', 'aircraft__tail_number', 'aircraft__model', 'check_type', 'status', 'lead_engineer']
    ordering_fields = ['scheduled_start', 'priority', 'status']

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        schedule = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(MaintenanceSchedule.STATUS_CHOICES):
            schedule.status = new_status
            schedule.save()
            return Response({'message': f'Status updated to {new_status}', 'status': schedule.status})
        return Response({'error': 'Invalid status choice'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def calendar_stats(self, request):
        total = MaintenanceSchedule.objects.count()
        upcoming = MaintenanceSchedule.objects.filter(status='SCHEDULED').count()
        active = MaintenanceSchedule.objects.filter(status='IN_PROGRESS').count()
        completed = MaintenanceSchedule.objects.filter(status='COMPLETED').count()
        return Response({
            'total_events': total,
            'scheduled': upcoming,
            'in_progress': active,
            'completed': completed
        })
