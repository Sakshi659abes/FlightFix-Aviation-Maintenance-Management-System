from django.db import models

class PartCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.code} - {self.name}"


class SparePart(models.Model):
    CONDITION_CHOICES = [
        ('NEW_OEM', 'Factory New (OEM Certified)'),
        ('OVERHAULED', 'Overhauled with EASA/FAA Form 1'),
        ('SERVICEABLE', 'Serviceable Tested'),
        ('UNSERVICEABLE', 'Unserviceable / Core Return Pending'),
    ]

    UNIT_CHOICES = [
        ('EA', 'Each'),
        ('SET', 'Set'),
        ('KIT', 'Maintenance Kit'),
        ('LTR', 'Liters'),
        ('MTR', 'Meters'),
    ]

    part_number = models.CharField(max_length=80, unique=True, db_index=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(PartCategory, on_delete=models.SET_NULL, null=True, related_name='parts')
    
    serial_number_tracked = models.BooleanField(default=False)
    shelf_life_controlled = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)
    
    quantity_on_hand = models.IntegerField(default=0)
    minimum_safety_stock = models.IntegerField(default=5)
    reorder_quantity = models.IntegerField(default=10)
    
    unit_of_measure = models.CharField(max_length=10, choices=UNIT_CHOICES, default='EA')
    unit_cost_usd = models.DecimalField(max_digits=12, decimal_places=2, default=150.00)
    storage_bin_location = models.CharField(max_length=100, default='ZONE-A/RACK-02/BIN-11')
    lead_time_days = models.IntegerField(default=7)
    condition = models.CharField(max_length=25, choices=CONDITION_CHOICES, default='NEW_OEM')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['part_number']
        verbose_name = 'Spare Part'
        verbose_name_plural = 'Spare Parts'

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.minimum_safety_stock

    def __str__(self):
        return f"[{self.part_number}] {self.description} (Stock: {self.quantity_on_hand})"


class InventoryTransaction(models.Model):
    TXN_TYPES = [
        ('RECEIVE_PO', 'Goods Receipt from Purchase Order'),
        ('ISSUE_WORK_ORDER', 'Issue to Hangar Work Order'),
        ('RETURN_TO_STORE', 'Return of Serviceable Core/Surplus'),
        ('SCRAP_DISPOSAL', 'Scrapped / Condemned'),
        ('CYCLE_ADJUSTMENT', 'Physical Audit Adjustment'),
    ]

    spare_part = models.ForeignKey(SparePart, related_name='transactions', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=30, choices=TXN_TYPES)
    quantity = models.IntegerField()
    reference_order = models.CharField(max_length=80, blank=True, default='') # WO-xxx or PO-xxx
    performed_by = models.CharField(max_length=100, default='Storekeeper Vikram')
    notes = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} x {self.spare_part.part_number} by {self.performed_by}"
