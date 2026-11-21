from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet, WorkOrderTaskViewSet, LaborLogViewSet

router = DefaultRouter()
router.register(r'orders', WorkOrderViewSet, basename='work-orders')
router.register(r'tasks', WorkOrderTaskViewSet, basename='tasks')
router.register(r'labor-logs', LaborLogViewSet, basename='labor-logs')

urlpatterns = [
    path('', include(router.urls)),
]
