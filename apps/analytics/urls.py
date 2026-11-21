from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelemetrySensorReadingViewSet, PredictiveAlertViewSet, FleetKPIMetricViewSet

router = DefaultRouter()
router.register(r'telemetry', TelemetrySensorReadingViewSet, basename='telemetry')
router.register(r'alerts', PredictiveAlertViewSet, basename='alerts')
router.register(r'kpis', FleetKPIMetricViewSet, basename='kpis')

urlpatterns = [
    path('', include(router.urls)),
]
