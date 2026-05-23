# pyrefly: ignore [missing-import]
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cancha
from .serializers import CanchaSerializer


class CanchaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Canchas.
    Permite filtrar por tipo_cancha (RF-BACK-010).
    """
    queryset = Cancha.objects.all()
    serializer_class = CanchaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo_cancha', 'superficie', 'estado_disponibilidad']
