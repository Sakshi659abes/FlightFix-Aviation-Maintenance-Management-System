from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AircraftViewSet, AircraftSubsystemViewSet, GroundEquipmentViewSet

router = DefaultRouter()
router.register(r'aircraft', AircraftViewSet, basename='aircraft')
router.register(r'subsystems', AircraftSubsystemViewSet, basename='subsystems')
router.register(r'ground-equipment', GroundEquipmentViewSet, basename='ground-equipment')

urlpatterns = [
    path('', include(router.urls)),
]
