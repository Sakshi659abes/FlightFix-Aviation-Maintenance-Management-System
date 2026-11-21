from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.fleet.models import Aircraft
from .models import FieldInspection, QuickDiscrepancyLog

class FieldMobileModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aircraft = Aircraft.objects.create(
            tail_number='VT-MOB01',
            model='Boeing 737-800',
            serial_number='SN-MOB-550',
            manufacturer='Boeing'
        )
        self.inspection = FieldInspection.objects.create(
            inspection_id='FINSP-TEST-01',
            aircraft=self.aircraft,
            technician_name='Line Tech Vikram',
            inspection_type='RAMP_TRANSIT_CHECK',
            status='IN_PROGRESS'
        )
        self.discrepancy = QuickDiscrepancyLog.objects.create(
            field_inspection=self.inspection,
            aircraft_zone='LANDING_GEAR',
            snag_description='Nose tire tread wear within 1mm limit',
            severity='ROUTINE'
        )

    def test_field_inspection_creation(self):
        self.assertEqual(self.inspection.inspection_id, 'FINSP-TEST-01')
        self.assertEqual(self.inspection.discrepancies.count(), 1)

    def test_complete_inspection_api(self):
        response = self.client.post(
            f'/api/v1/field/inspections/{self.inspection.id}/complete_inspection/',
            {'findings_summary': 'Tire inspected, approved for flight AI-101.'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inspection.refresh_from_db()
        self.assertEqual(self.inspection.status, 'SYNCED_TO_CORE_MRO')

    def test_sync_offline_batch_api(self):
        response = self.client.post(
            '/api/v1/field/inspections/sync_offline_batch/',
            {'device_id': 'TAB-RAMP-09', 'batch_records': [{'step': 1, 'action': 'o-ring check'}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SUCCESS')
