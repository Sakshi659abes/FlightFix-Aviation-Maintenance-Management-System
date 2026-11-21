from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import MROAuditTrail, MROUserProfile

class AuditSecurityModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_profile = MROUserProfile.objects.create(
            username='rsharma_ame',
            full_name='Chief Eng. Rajesh Sharma',
            email='rajesh.sharma@flightfix.aero',
            role='CHIEF_ENGINEER',
            license_stamp_no='AME-DGCA-B1-9921',
            department='Heavy Maintenance Hangar 2'
        )
        self.audit = MROAuditTrail.objects.create(
            user_name='Chief Eng. Rajesh Sharma',
            user_role='Certifying Engineer (B1/B2)',
            action_type='SIGN_OFF',
            target_module='WORK_ORDERS',
            entity_reference='WO-2026-TEST',
            details='Released aircraft to service following engine cowl inspection.'
        )

    def test_audit_log_creation(self):
        self.assertEqual(self.audit.entity_reference, 'WO-2026-TEST')
        self.assertEqual(self.audit.action_type, 'SIGN_OFF')

    def test_recent_activities_api(self):
        response = self.client.get('/api/v1/audit/logs/recent_activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_active_roles_api(self):
        response = self.client.get('/api/v1/audit/users/active_roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
