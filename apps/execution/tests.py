from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.fleet.models import Aircraft
from apps.workorders.models import WorkOrder
from .models import JobCardExecution, DefectReport

class ExecutionModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aircraft = Aircraft.objects.create(
            tail_number='VT-EX01',
            model='Airbus A321neo',
            serial_number='SN-EX-401',
            manufacturer='Airbus'
        )
        self.work_order = WorkOrder.objects.create(
            work_order_no='WO-EX-2026',
            aircraft=self.aircraft,
            title='Main Landing Gear Brake Pack Replacement'
        )
        self.job_card = JobCardExecution.objects.create(
            work_order=self.work_order,
            job_card_no='JC-MLG-32-01',
            step_number=1,
            step_instruction='Jack aircraft MLG and de-pressurize hydraulic system.'
        )
        self.defect = DefectReport.objects.create(
            aircraft=self.aircraft,
            defect_log_number='DEF-2026-90',
            title='Left Engine Bleed Air Low Pressure light illuminated',
            discrepancy_details='Engine #1 PRSOV valve cycling during descent.',
            severity='MAJOR'
        )

    def test_job_card_stamping(self):
        response = self.client.post(
            f'/api/v1/execution/job-cards/{self.job_card.id}/stamp_technician/',
            {'technician_name': 'Tech. Dev', 'technician_stamp': 'DGCA-AME-123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job_card.refresh_from_db()
        self.assertTrue(self.job_card.is_completed)
        self.assertEqual(self.job_card.technician_stamp, 'DGCA-AME-123')

    def test_defect_rectify(self):
        response = self.client.post(
            f'/api/v1/execution/defects/{self.defect.id}/rectify/',
            {'rectification_action': 'Replaced pressure transducer', 'rectified_by': 'Eng. Roy'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.defect.refresh_from_db()
        self.assertEqual(self.defect.status, 'RECTIFIED')
