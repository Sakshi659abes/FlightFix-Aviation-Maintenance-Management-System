from rest_framework import serializers
from .models import PartCategory, SparePart, InventoryTransaction

class PartCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PartCategory
        fields = '__all__'

class SparePartSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = SparePart
        fields = '__all__'

class InventoryTransactionSerializer(serializers.ModelSerializer):
    part_number = serializers.CharField(source='spare_part.part_number', read_only=True)
    part_description = serializers.CharField(source='spare_part.description', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = '__all__'
