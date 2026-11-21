from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.fleet.models import Aircraft
from .models import PredictiveAlert, FleetKPIMetric

class AnalyticsModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aircraft = Aircraft.objects.create(
            tail_number='VT-ANL01',
            model='Boeing 787-9 Dreamliner',
            serial_number='SN-ANL-787',
            manufacturer='Boeing'
        )
        self.alert = PredictiveAlert.objects.create(
            alert_id='PRED-ALT-01',
            aircraft=self.aircraft,
            component_name='Center Hydraulic Primary Electric Pump',
            predicted_failure_probability_pct=91.4,
            severity='CRITICAL',
            recommended_action='Replace pump filter assembly within 48 flight hours.'
        )
        self.kpi = FleetKPIMetric.objects.create(
            fleet_dispatch_reliability_pct=99.5,
            mean_time_between_failures_hours=440.0,
            mean_time_to_repair_hours=3.8
        )

    def test_alert_creation(self):
        self.assertEqual(self.alert.alert_id, 'PRED-ALT-01')
        self.assertEqual(self.alert.status, 'ACTIVE')

    def test_acknowledge_alert_api(self):
        response = self.client.post(
            f'/api/v1/analytics/alerts/{self.alert.id}/acknowledge/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'ACKNOWLEDGED')

    def test_live_kpis_api(self):
        response = self.client.get('/api/v1/analytics/kpis/live_kpis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['dispatch_reliability'], 99.5)
