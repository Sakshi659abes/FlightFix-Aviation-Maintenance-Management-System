from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import VendorSupplier, PurchaseOrder, PurchaseOrderItem

class SupplyChainModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vendor = VendorSupplier.objects.create(
            vendor_code='VND-BOEING-01',
            name='Boeing Global Distribution Services',
            contact_email='orders@boeingdistribution.com',
            phone='+1-800-555-0199',
            country='USA'
        )
        self.po = PurchaseOrder.objects.create(
            po_number='PO-2026-TEST-77',
            vendor=self.vendor,
            expected_delivery_date=timezone.now().date() + timedelta(days=5),
            total_amount_usd=14500.00,
            status='SUBMITTED_ERP'
        )
        self.item = PurchaseOrderItem.objects.create(
            purchase_order=self.po,
            part_number='BLD-FAN-7701',
            description='Titanium Fan Blade Set',
            quantity_ordered=4,
            unit_cost_usd=3625.00
        )

    def test_po_creation(self):
        self.assertEqual(self.po.po_number, 'PO-2026-TEST-77')
        self.assertEqual(self.po.items.count(), 1)

    def test_procurement_metrics(self):
        response = self.client.get('/api/v1/supplychain/purchase-orders/procurement_metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_purchase_orders'], 1)

    def test_sync_erp_status(self):
        response = self.client.post(
            f'/api/v1/supplychain/purchase-orders/{self.po.id}/sync_erp_status/',
            {'status': 'IN_TRANSIT', 'air_waybill_number': 'AWB-TEST-999'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.po.refresh_from_db()
        self.assertEqual(self.po.status, 'IN_TRANSIT')
        self.assertEqual(self.po.air_waybill_number, 'AWB-TEST-999')
