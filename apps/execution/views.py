from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JobCardExecution, DefectReport
from .serializers import JobCardExecutionSerializer, DefectReportSerializer

class JobCardExecutionViewSet(viewsets.ModelViewSet):
    queryset = JobCardExecution.objects.all().select_related('work_order')
    serializer_class = JobCardExecutionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['job_card_no', 'step_instruction', 'technician_name', 'technician_stamp']

    @action(detail=True, methods=['post'])
    def stamp_technician(self, request, pk=None):
        card = self.get_object()
        tech_name = request.data.get('technician_name', 'Tech. Arjun V.')
        stamp = request.data.get('technician_stamp', 'AME-DGCA-7741')
        
        card.technician_name = tech_name
        card.technician_stamp = stamp
        card.is_completed = True
        card.completed_at = timezone.now()
        card.save()

        return Response({
            'message': f'Step {card.step_number} digitally stamped by technician {tech_name}',
            'is_completed': True,
            'technician_stamp': stamp
        })

    @action(detail=True, methods=['post'])
    def stamp_inspector(self, request, pk=None):
        card = self.get_object()
        insp_name = request.data.get('inspector_name', 'Lead Inspector K. Verma')
        stamp = request.data.get('inspector_stamp', 'QC-DEL-890')
        
        card.inspector_name = insp_name
        card.inspector_stamp = stamp
        card.is_inspected = True
        card.inspected_at = timezone.now()
        card.save()

        return Response({
            'message': f'Step {card.step_number} verified and stamped by inspector {insp_name}',
            'is_inspected': True,
            'inspector_stamp': stamp
        })

class DefectReportViewSet(viewsets.ModelViewSet):
    queryset = DefectReport.objects.all().select_related('aircraft', 'work_order')
    serializer_class = DefectReportSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['defect_log_number', 'title', 'aircraft__tail_number', 'severity', 'status']
    ordering_fields = ['date_reported', 'severity', 'status']

    @action(detail=True, methods=['post'])
    def rectify(self, request, pk=None):
        defect = self.get_object()
        action_text = request.data.get('rectification_action', 'Replaced faulty transducer and carried out BITE test SAT.')
        engineer = request.data.get('rectified_by', 'Sr. Avionics Eng. Ananya Roy')
        
        defect.status = 'RECTIFIED'
        defect.rectification_action = action_text
        defect.rectified_by = engineer
        defect.date_rectified = timezone.now()
        defect.save()

        return Response({
            'message': f'Defect {defect.defect_log_number} rectified and closed.',
            'status': defect.status
        })
