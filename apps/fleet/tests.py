from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Aircraft, AircraftSubsystem, GroundEquipment

class FleetModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aircraft = Aircraft.objects.create(
            tail_number='VT-TEST1',
            model='Airbus A320neo',
            serial_number='SN-98210',
            manufacturer='Airbus',
            total_flight_hours=1450.5,
            total_flight_cycles=820,
            status='OPERATIONAL'
        )
        self.subsystem = AircraftSubsystem.objects.create(
            aircraft=self.aircraft,
            system_name='CFM LEAP-1A Engine',
            health_status='EXCELLENT',
            health_score=98
        )
        self.equipment = GroundEquipment.objects.create(
            equipment_tag='GPU-901',
            equipment_type='Ground Power Unit (GPU)',
            status='AVAILABLE'
        )

    def test_aircraft_creation(self):
        self.assertEqual(self.aircraft.tail_number, 'VT-TEST1')
        self.assertEqual(self.aircraft.status, 'OPERATIONAL')

    def test_aircraft_api_list(self):
        response = self.client.get('/api/v1/fleet/aircraft/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated or unpaginated response
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)

    def test_aircraft_summary_api(self):
        response = self.client.get('/api/v1/fleet/aircraft/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_aircraft'], 1)
        self.assertEqual(response.data['operational'], 1)

    def test_ground_equipment_api(self):
        response = self.client.get('/api/v1/fleet/ground-equipment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
