from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import AirworthinessDirective, AircraftADCompliance, ServiceBulletin, TechnicianLicense
from .serializers import (
    AirworthinessDirectiveSerializer,
    AircraftADComplianceSerializer,
    ServiceBulletinSerializer,
    TechnicianLicenseSerializer
)

class AirworthinessDirectiveViewSet(viewsets.ModelViewSet):
    queryset = AirworthinessDirective.objects.all()
    serializer_class = AirworthinessDirectiveSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ad_number', 'title', 'applicable_models', 'issuing_authority', 'status']
    ordering_fields = ['compliance_deadline', 'status']

    @action(detail=False, methods=['get'])
    def compliance_summary(self, request):
        total_ads = AirworthinessDirective.objects.count()
        complied = AirworthinessDirective.objects.filter(status='COMPLIED').count()
        open_mandatory = AirworthinessDirective.objects.filter(status='MANDATORY_OPEN').count()
        rate = round((complied / total_ads * 100), 1) if total_ads > 0 else 100.0
        return Response({
            'total_directives': total_ads,
            'complied': complied,
            'open_mandatory': open_mandatory,
            'compliance_rate_pct': rate
        })

class AircraftADComplianceViewSet(viewsets.ModelViewSet):
    queryset = AircraftADCompliance.objects.all().select_related('aircraft', 'directive')
    serializer_class = AircraftADComplianceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['aircraft__tail_number', 'directive__ad_number']

    @action(detail=True, methods=['post'])
    def certify_compliance(self, request, pk=None):
        record = self.get_object()
        engineer = request.data.get('certifying_engineer', 'Lead Inspector R. Sen')
        method = request.data.get('compliance_method', 'Replaced part as per SB revision 2 and verified ground ops.')
        
        record.is_complied = True
        record.complied_date = timezone.now().date()
        record.certifying_engineer = engineer
        record.compliance_method = method
        record.save()

        return Response({
            'message': f'Directive {record.directive.ad_number} certified for aircraft {record.aircraft.tail_number}',
            'is_complied': True
        })

class ServiceBulletinViewSet(viewsets.ModelViewSet):
    queryset = ServiceBulletin.objects.all()
    serializer_class = ServiceBulletinSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['sb_number', 'title', 'oem_manufacturer']

class TechnicianLicenseViewSet(viewsets.ModelViewSet):
    queryset = TechnicianLicense.objects.all()
    serializer_class = TechnicianLicenseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['technician_name', 'license_number', 'category']
