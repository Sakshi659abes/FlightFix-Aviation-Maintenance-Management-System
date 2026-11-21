from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WorkOrder, WorkOrderTask, LaborLog
from .serializers import WorkOrderSerializer, WorkOrderTaskSerializer, LaborLogSerializer

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().select_related('aircraft', 'schedule').prefetch_related('tasks', 'labor_logs')
    serializer_class = WorkOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['work_order_no', 'title', 'aircraft__tail_number', 'order_type', 'priority', 'status', 'assigned_team']
    ordering_fields = ['created_at', 'priority', 'status', 'estimated_man_hours']

    @action(detail=True, methods=['post'])
    def release_to_service(self, request, pk=None):
        wo = self.get_object()
        engineer = request.data.get('sign_off_engineer', 'Lead Inspector Sunita Menon')
        crs_code = request.data.get('crs_code', f'CRS-DEL-{wo.work_order_no}')
        
        wo.status = 'CLOSED_RELEASED'
        wo.released_to_service = True
        wo.sign_off_engineer = engineer
        wo.certificate_of_release = crs_code
        wo.closed_at = timezone.now()
        wo.save()
        
        # Also update aircraft status if all open WOs are resolved
        aircraft = wo.aircraft
        remaining_aog = aircraft.work_orders.filter(status__in=['OPEN', 'IN_PROGRESS', 'AWAITING_PARTS']).count()
        if remaining_aog == 0 and aircraft.status in ['IN_MAINTENANCE', 'AOG']:
            aircraft.status = 'OPERATIONAL'
            aircraft.save()

        return Response({
            'message': f'Work order {wo.work_order_no} successfully released to service under {crs_code}.',
            'status': wo.status,
            'crs_code': crs_code
        })

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        total = WorkOrder.objects.count()
        open_count = WorkOrder.objects.filter(status='OPEN').count()
        in_progress = WorkOrder.objects.filter(status='IN_PROGRESS').count()
        awaiting_parts = WorkOrder.objects.filter(status='AWAITING_PARTS').count()
        inspection = WorkOrder.objects.filter(status='INSPECTION_PENDING').count()
        released = WorkOrder.objects.filter(status='CLOSED_RELEASED').count()
        aog_orders = WorkOrder.objects.filter(priority='CRITICAL_AOG').exclude(status='CLOSED_RELEASED').count()
        
        return Response({
            'total_work_orders': total,
            'open': open_count,
            'in_progress': in_progress,
            'awaiting_parts': awaiting_parts,
            'inspection_pending': inspection,
            'closed_released': released,
            'active_aog_orders': aog_orders
        })

class WorkOrderTaskViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderTask.objects.all().select_related('work_order')
    serializer_class = WorkOrderTaskSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['task_code', 'description', 'amm_reference', 'status']

class LaborLogViewSet(viewsets.ModelViewSet):
    queryset = LaborLog.objects.all().select_related('work_order')
    serializer_class = LaborLogSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['technician_name', 'work_order__work_order_no']
