from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AirworthinessDirectiveViewSet,
    AircraftADComplianceViewSet,
    ServiceBulletinViewSet,
    TechnicianLicenseViewSet
)

router = DefaultRouter()
router.register(r'directives', AirworthinessDirectiveViewSet, basename='directives')
router.register(r'fleet-compliance', AircraftADComplianceViewSet, basename='fleet-compliance')
router.register(r'service-bulletins', ServiceBulletinViewSet, basename='service-bulletins')
router.register(r'licenses', TechnicianLicenseViewSet, basename='licenses')

urlpatterns = [
    path('', include(router.urls)),
]
