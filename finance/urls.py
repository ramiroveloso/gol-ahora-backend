# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import DescuentoViewSet, CobroViewSet, ReciboPagoViewSet

router = DefaultRouter()
router.register(r'descuentos', DescuentoViewSet, basename='descuento')
router.register(r'cobros', CobroViewSet, basename='cobro')
router.register(r'recibos', ReciboPagoViewSet, basename='recibo')

urlpatterns = [
    path('', include(router.urls)),
]
