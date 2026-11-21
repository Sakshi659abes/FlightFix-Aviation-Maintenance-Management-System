from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import PartCategory, SparePart, InventoryTransaction
from .serializers import PartCategorySerializer, SparePartSerializer, InventoryTransactionSerializer

class PartCategoryViewSet(viewsets.ModelViewSet):
    queryset = PartCategory.objects.all()
    serializer_class = PartCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

class SparePartViewSet(viewsets.ModelViewSet):
    queryset = SparePart.objects.all().select_related('category')
    serializer_class = SparePartSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['part_number', 'description', 'storage_bin_location', 'category__name']
    ordering_fields = ['part_number', 'quantity_on_hand', 'unit_cost_usd']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_parts = SparePart.objects.filter(quantity_on_hand__lte=F('minimum_safety_stock'))
        serializer = self.get_serializer(low_stock_parts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        part = self.get_object()
        qty = int(request.data.get('quantity', 0))
        txn_type = request.data.get('transaction_type', 'ISSUE_WORK_ORDER')
        ref = request.data.get('reference_order', '')
        user = request.data.get('performed_by', 'Field Technician')
        notes = request.data.get('notes', '')

        if txn_type in ['ISSUE_WORK_ORDER', 'SCRAP_DISPOSAL']:
            if part.quantity_on_hand < qty:
                return Response({'error': f'Insufficient stock! Current stock: {part.quantity_on_hand}'}, status=status.HTTP_400_BAD_REQUEST)
            part.quantity_on_hand -= qty
        else: # RECEIVE_PO, RETURN_TO_STORE, CYCLE_ADJUSTMENT
            part.quantity_on_hand += qty

        part.save()

        txn = InventoryTransaction.objects.create(
            spare_part=part,
            transaction_type=txn_type,
            quantity=qty,
            reference_order=ref,
            performed_by=user,
            notes=notes
        )

        return Response({
            'message': f'Stock updated. New balance: {part.quantity_on_hand}',
            'new_quantity': part.quantity_on_hand,
            'transaction_id': txn.id
        })

class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.all().select_related('spare_part')
    serializer_class = InventoryTransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['spare_part__part_number', 'reference_order', 'performed_by', 'transaction_type']
    ordering_fields = ['timestamp']
