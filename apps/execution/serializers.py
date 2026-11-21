from rest_framework import serializers
from .models import JobCardExecution, DefectReport

class JobCardExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCardExecution
        fields = '__all__'

class DefectReportSerializer(serializers.ModelSerializer):
    aircraft_tail = serializers.CharField(source='aircraft.tail_number', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    report_source_display = serializers.CharField(source='get_report_source_display', read_only=True)

    class Meta:
        model = DefectReport
        fields = '__all__'
