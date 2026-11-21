from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import PartCategory, SparePart, InventoryTransaction

class InventoryModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = PartCategory.objects.create(
            name='Hydraulics & Flight Controls',
            code='CAT-HYD',
            description='Hydraulic pumps, valves, and lines'
        )
        self.part = SparePart.objects.create(
            part_number='VALV-HYD-9901',
            description='B-System Isolation Valve Assembly',
            category=self.category,
            quantity_on_hand=15,
            minimum_safety_stock=5,
            unit_cost_usd=850.00
        )

    def test_spare_part_stock(self):
        self.assertEqual(self.part.quantity_on_hand, 15)
        self.assertFalse(self.part.is_low_stock)

    def test_parts_list_api(self):
        response = self.client.get('/api/v1/inventory/parts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_adjust_stock_issue(self):
        response = self.client.post(
            f'/api/v1/inventory/parts/{self.part.id}/adjust_stock/',
            {
                'quantity': 3,
                'transaction_type': 'ISSUE_WORK_ORDER',
                'reference_order': 'WO-2026-TEST',
                'performed_by': 'Mechanic Arjun'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.part.refresh_from_db()
        self.assertEqual(self.part.quantity_on_hand, 12)
        self.assertEqual(InventoryTransaction.objects.count(), 1)
