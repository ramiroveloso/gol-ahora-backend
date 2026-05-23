# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import ReservaViewSet, ClaseEntrenamientoViewSet, AsistenciaViewSet, DisponibilidadView

router = DefaultRouter()
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'clases', ClaseEntrenamientoViewSet, basename='clase')
router.register(r'asistencia', AsistenciaViewSet, basename='asistencia')

urlpatterns = [
    path('disponibilidad/', DisponibilidadView.as_view(), name='disponibilidad'),
    path('', include(router.urls)),
]
