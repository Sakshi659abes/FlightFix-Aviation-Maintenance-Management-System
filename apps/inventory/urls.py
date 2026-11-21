from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartCategoryViewSet, SparePartViewSet, InventoryTransactionViewSet

router = DefaultRouter()
router.register(r'categories', PartCategoryViewSet, basename='categories')
router.register(r'parts', SparePartViewSet, basename='parts')
router.register(r'transactions', InventoryTransactionViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
]
