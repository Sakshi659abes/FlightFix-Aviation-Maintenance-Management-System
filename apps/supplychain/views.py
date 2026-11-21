from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VendorSupplier, PurchaseOrder, PurchaseOrderItem
from .serializers import VendorSupplierSerializer, PurchaseOrderSerializer, PurchaseOrderItemSerializer

class VendorSupplierViewSet(viewsets.ModelViewSet):
    queryset = VendorSupplier.objects.all()
    serializer_class = VendorSupplierSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['vendor_code', 'name', 'country', 'oem_type']

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().select_related('vendor').prefetch_related('items')
    serializer_class = PurchaseOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['po_number', 'vendor__name', 'erp_system_ref', 'status', 'air_waybill_number']
    ordering_fields = ['order_date', 'total_amount_usd', 'status']

    @action(detail=True, methods=['post'])
    def sync_erp_status(self, request, pk=None):
        po = self.get_object()
        new_status = request.data.get('status', 'IN_TRANSIT')
        tracking = request.data.get('air_waybill_number', po.air_waybill_number)
        
        po.status = new_status
        po.air_waybill_number = tracking
        if new_status == 'RECEIVED':
            po.actual_delivery_date = timezone.now().date()
            for item in po.items.all():
                item.quantity_received = item.quantity_ordered
                item.save()
        po.save()

        return Response({
            'message': f'ERP Synchronized: PO {po.po_number} status updated to {po.get_status_display()}',
            'status': po.status,
            'erp_system_ref': po.erp_system_ref
        })

    @action(detail=False, methods=['get'])
    def procurement_metrics(self, request):
        total_pos = PurchaseOrder.objects.count()
        in_transit = PurchaseOrder.objects.filter(status='IN_TRANSIT').count()
        customs = PurchaseOrder.objects.filter(status='CUSTOMS_HOLD').count()
        received = PurchaseOrder.objects.filter(status='RECEIVED').count()
        return Response({
            'total_purchase_orders': total_pos,
            'in_transit_air_cargo': in_transit,
            'customs_hold': customs,
            'received_and_stocked': received
        })

class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderItem.objects.all().select_related('purchase_order')
    serializer_class = PurchaseOrderItemSerializer
