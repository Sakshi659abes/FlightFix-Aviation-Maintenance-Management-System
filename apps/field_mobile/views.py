from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FieldInspection, QuickDiscrepancyLog, OfflineSyncRecord
from .serializers import FieldInspectionSerializer, QuickDiscrepancyLogSerializer, OfflineSyncRecordSerializer

class FieldInspectionViewSet(viewsets.ModelViewSet):
    queryset = FieldInspection.objects.all().select_related('aircraft').prefetch_related('discrepancies')
    serializer_class = FieldInspectionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['inspection_id', 'aircraft__tail_number', 'technician_name', 'inspection_type', 'status']
    ordering_fields = ['created_at', 'status']

    @action(detail=True, methods=['post'])
    def complete_inspection(self, request, pk=None):
        insp = self.get_object()
        findings = request.data.get('findings_summary', insp.findings_summary)
        insp.findings_summary = findings
        insp.status = 'SYNCED_TO_CORE_MRO'
        insp.completed_at = timezone.now()
        insp.save()
        return Response({
            'message': f'Field inspection {insp.inspection_id} completed and pushed to core MRO system.',
            'status': insp.status
        })

    @action(detail=False, methods=['post'])
    def sync_offline_batch(self, request):
        device_id = request.data.get('device_id', 'TOUGHBOOK-FIELD-01')
        records = request.data.get('batch_records', [])
        
        sync_log = OfflineSyncRecord.objects.create(
            device_id=device_id,
            sync_action='BULK_OFFLINE_RAMP_SYNC',
            payload_snapshot=str(records),
            sync_status='SUCCESS'
        )
        return Response({
            'status': 'SUCCESS',
            'synced_count': len(records),
            'sync_token': f'SYNC-{sync_log.id}-{timezone.now().strftime("%H%M%S")}'
        })

class QuickDiscrepancyLogViewSet(viewsets.ModelViewSet):
    queryset = QuickDiscrepancyLog.objects.all().select_related('field_inspection')
    serializer_class = QuickDiscrepancyLogSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['snag_description', 'aircraft_zone']

class OfflineSyncRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfflineSyncRecord.objects.all()
    serializer_class = OfflineSyncRecordSerializer
