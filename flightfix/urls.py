"""
FlightFix URL Configuration
Routing for all 10 MRO Modules and Frontend Dashboard
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Unified Web Frontend
    path('', dashboard_view, name='dashboard'),
    
    # 10 Module REST APIs (DRF v1)
    path('api/v1/planning/', include('apps.planning.urls')),           # Module 1
    path('api/v1/workorders/', include('apps.workorders.urls')),       # Module 2
    path('api/v1/fleet/', include('apps.fleet.urls')),                 # Module 3
    path('api/v1/inventory/', include('apps.inventory.urls')),         # Module 4
    path('api/v1/execution/', include('apps.execution.urls')),         # Module 5
    path('api/v1/compliance/', include('apps.compliance.urls')),       # Module 6
    path('api/v1/supplychain/', include('apps.supplychain.urls')),     # Module 7
    path('api/v1/field/', include('apps.field_mobile.urls')),          # Module 8
    path('api/v1/analytics/', include('apps.analytics.urls')),         # Module 9
    path('api/v1/audit/', include('apps.audit_security.urls')),        # Module 10
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
