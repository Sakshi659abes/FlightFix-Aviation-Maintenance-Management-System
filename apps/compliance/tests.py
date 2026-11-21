from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from apps.fleet.models import Aircraft
from .models import AirworthinessDirective, AircraftADCompliance

class ComplianceModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aircraft = Aircraft.objects.create(
            tail_number='VT-CMP01',
            model='Airbus A320neo',
            serial_number='SN-CMP-110',
            manufacturer='Airbus'
        )
        self.ad = AirworthinessDirective.objects.create(
            ad_number='DGCA-AD-2026-09',
            issuing_authority='DGCA',
            title='Pratt & Whitney PW1100G High Pressure Turbine Disk Inspection',
            applicable_models='Airbus A320neo',
            effective_date=timezone.now().date(),
            compliance_deadline=timezone.now().date() + timedelta(days=30),
            action_required='Ultrasonic inspection of stage 1 and 2 HPT disks.'
        )
        self.compliance_record = AircraftADCompliance.objects.create(
            aircraft=self.aircraft,
            directive=self.ad,
            is_complied=False
        )

    def test_ad_creation(self):
        self.assertEqual(self.ad.ad_number, 'DGCA-AD-2026-09')
        self.assertEqual(self.ad.status, 'MANDATORY_OPEN')

    def test_compliance_summary_api(self):
        response = self.client.get('/api/v1/compliance/directives/compliance_summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_directives'], 1)

    def test_certify_compliance_api(self):
        response = self.client.post(
            f'/api/v1/compliance/fleet-compliance/{self.compliance_record.id}/certify_compliance/',
            {'certifying_engineer': 'Eng. R. Sen', 'compliance_method': 'UT scan done SAT'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.compliance_record.refresh_from_db()
        self.assertTrue(self.compliance_record.is_complied)
