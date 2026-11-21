from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from apps.fleet.models import Aircraft
from .models import HangarBay, MaintenanceSchedule

class PlanningModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aircraft = Aircraft.objects.create(
            tail_number='VT-PLN01',
            model='Boeing 737-800',
            serial_number='SN-PLN-101',
            manufacturer='Boeing'
        )
        self.bay = HangarBay.objects.create(
            bay_code='HB-01',
            name='Bay 1 Heavy MRO',
            status='AVAILABLE'
        )
        now = timezone.now()
        self.schedule = MaintenanceSchedule.objects.create(
            schedule_id='SCH-2026-001',
            aircraft=self.aircraft,
            check_type='A_CHECK',
            hangar_bay=self.bay,
            scheduled_start=now,
            scheduled_end=now + timedelta(days=2),
            lead_engineer='Chief Eng. Rajesh',
            status='SCHEDULED'
        )

    def test_schedule_creation(self):
        self.assertEqual(self.schedule.schedule_id, 'SCH-2026-001')
        self.assertEqual(self.schedule.aircraft.tail_number, 'VT-PLN01')

    def test_schedules_api_list(self):
        response = self.client.get('/api/v1/planning/schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hangar_bays_api(self):
        response = self.client.get('/api/v1/planning/hangar-bays/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_calendar_stats_api(self):
        response = self.client.get('/api/v1/planning/schedules/calendar_stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_events'], 1)
