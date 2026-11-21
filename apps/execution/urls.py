from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobCardExecutionViewSet, DefectReportViewSet

router = DefaultRouter()
router.register(r'job-cards', JobCardExecutionViewSet, basename='job-cards')
router.register(r'defects', DefectReportViewSet, basename='defects')

urlpatterns = [
    path('', include(router.urls)),
]
