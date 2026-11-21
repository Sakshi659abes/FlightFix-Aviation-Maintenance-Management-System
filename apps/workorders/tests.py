from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.fleet.models import Aircraft
from .models import WorkOrder, WorkOrderTask

class WorkOrderModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aircraft = Aircraft.objects.create(
            tail_number='VT-WO01',
            model='Boeing 737 MAX 8',
            serial_number='SN-MAX-901',
            manufacturer='Boeing',
            status='IN_MAINTENANCE'
        )
        self.work_order = WorkOrder.objects.create(
            work_order_no='WO-2026-TEST-01',
            aircraft=self.aircraft,
            title='Hydraulic B-System Pressure Valve Inspection',
            description='Check leakage rate and actuator seal compliance.',
            order_type='UNSCHEDULED_DEFECT',
            priority='HIGH',
            status='IN_PROGRESS',
            estimated_man_hours=8.0
        )
        self.task = WorkOrderTask.objects.create(
            work_order=self.work_order,
            task_code='TSK-HYD-01',
            description='Disassemble valve manifold seal',
            amm_reference='AMM 29-10-00',
            technician_assigned='R. Verma',
            status='IN_PROGRESS'
        )

    def test_work_order_creation(self):
        self.assertEqual(self.work_order.work_order_no, 'WO-2026-TEST-01')
        self.assertEqual(self.work_order.tasks.count(), 1)

    def test_work_order_list_api(self):
        response = self.client.get('/api/v1/workorders/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_release_to_service_action(self):
        response = self.client.post(
            f'/api/v1/workorders/orders/{self.work_order.id}/release_to_service/',
            {'sign_off_engineer': 'Eng. K. Mehta', 'crs_code': 'CRS-TEST-999'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.work_order.refresh_from_db()
        self.assertEqual(self.work_order.status, 'CLOSED_RELEASED')
        self.assertTrue(self.work_order.released_to_service)

    def test_work_order_metrics(self):
        response = self.client.get('/api/v1/workorders/orders/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_work_orders'], 1)
