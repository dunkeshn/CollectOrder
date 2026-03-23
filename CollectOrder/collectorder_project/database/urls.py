# urls.py (в приложении)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'stores', views.StoreViewSet)
router.register(r'inventory', views.StoreInventoryViewSet, basename='inventory')
router.register(r'users', views.UserViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-items', views.OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path('', include(router.urls)),
]