from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MROAuditTrailViewSet, MROUserProfileViewSet

router = DefaultRouter()
router.register(r'logs', MROAuditTrailViewSet, basename='audit-logs')
router.register(r'users', MROUserProfileViewSet, basename='mro-users')

urlpatterns = [
    path('', include(router.urls)),
]
