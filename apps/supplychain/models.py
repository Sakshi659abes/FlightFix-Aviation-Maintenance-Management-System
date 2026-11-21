from django.db import models

class VendorSupplier(models.Model):
    vendor_code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    oem_type = models.CharField(max_length=100, default='OEM Tier-1 Parts Distributor')
    contact_email = models.EmailField()
    phone = models.CharField(max_length=30)
    country = models.CharField(max_length=50, default='United States')
    rating_score = models.FloatField(default=4.8)
    is_faa_easa_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vendor_code} - {self.name}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft Requisition'),
        ('SUBMITTED_ERP', 'Dispatched to Enterprise ERP (SAP/Oracle)'),
        ('IN_TRANSIT', 'Shipped / In-Transit (Air Cargo)'),
        ('CUSTOMS_HOLD', 'Customs Clearance at DEL Gateway'),
        ('RECEIVED', 'Goods Inspected & Stocked in Stores'),
        ('CANCELLED', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=40, unique=True, db_index=True)
    vendor = models.ForeignKey(VendorSupplier, related_name='purchase_orders', on_delete=models.CASCADE)
    erp_system_ref = models.CharField(max_length=80, blank=True, default='SAP-MRO-PO-99120', help_text="Enterprise ERP integration reference ID")
    
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    total_amount_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED_ERP')
    
    shipping_carrier = models.CharField(max_length=100, default='FedEx Aerospace Critical')
    air_waybill_number = models.CharField(max_length=80, blank=True, default='AWB-774-902189')
    customs_declaration_no = models.CharField(max_length=80, blank=True, default='IN-DEL-BOE-2026-441')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"[{self.po_number}] {self.vendor.name} - ${self.total_amount_usd} ({self.status})"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    part_number = models.CharField(max_length=80)
    description = models.CharField(max_length=255)
    quantity_ordered = models.IntegerField(default=1)
    quantity_received = models.IntegerField(default=0)
    unit_cost_usd = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)

    def __str__(self):
        return f"{self.part_number} x {self.quantity_ordered} for {self.purchase_order.po_number}"
