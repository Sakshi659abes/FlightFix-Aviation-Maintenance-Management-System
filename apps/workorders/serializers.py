from rest_framework import serializers
from .models import WorkOrder, WorkOrderTask, LaborLog

class WorkOrderTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WorkOrderTask
        fields = '__all__'

class LaborLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborLog
        fields = '__all__'

class WorkOrderSerializer(serializers.ModelSerializer):
    tasks = WorkOrderTaskSerializer(many=True, read_only=True)
    labor_logs = LaborLogSerializer(many=True, read_only=True)
    aircraft_tail = serializers.CharField(source='aircraft.tail_number', read_only=True)
    aircraft_model = serializers.CharField(source='aircraft.model', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WorkOrder
        fields = '__all__'
