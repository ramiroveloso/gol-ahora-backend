# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import CanchaViewSet, CanchaDisponibilidadView

router = DefaultRouter()
router.register(r'canchas', CanchaViewSet, basename='cancha')

urlpatterns = [
    path('canchas/<int:pk>/disponibilidad/', CanchaDisponibilidadView.as_view(), name='cancha-disponibilidad'),
    path('', include(router.urls)),
]
