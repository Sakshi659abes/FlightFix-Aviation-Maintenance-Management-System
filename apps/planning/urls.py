from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HangarBayViewSet, MaintenanceScheduleViewSet

router = DefaultRouter()
router.register(r'hangar-bays', HangarBayViewSet, basename='hangar-bays')
router.register(r'schedules', MaintenanceScheduleViewSet, basename='schedules')

urlpatterns = [
    path('', include(router.urls)),
]
