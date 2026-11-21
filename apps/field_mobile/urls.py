from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FieldInspectionViewSet, QuickDiscrepancyLogViewSet, OfflineSyncRecordViewSet

router = DefaultRouter()
router.register(r'inspections', FieldInspectionViewSet, basename='inspections')
router.register(r'discrepancies', QuickDiscrepancyLogViewSet, basename='discrepancies')
router.register(r'sync-records', OfflineSyncRecordViewSet, basename='sync-records')

urlpatterns = [
    path('', include(router.urls)),
]
