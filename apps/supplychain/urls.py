from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorSupplierViewSet, PurchaseOrderViewSet, PurchaseOrderItemViewSet

router = DefaultRouter()
router.register(r'vendors', VendorSupplierViewSet, basename='vendors')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')
router.register(r'order-items', PurchaseOrderItemViewSet, basename='order-items')

urlpatterns = [
    path('', include(router.urls)),
]
