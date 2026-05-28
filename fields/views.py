# pyrefly: ignore [missing-import]
from rest_framework import viewsets, status, views
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Cancha
from .serializers import CanchaSerializer, ReservaResumenSerializer
from bookings.models import Reserva
from gol_ahora_back.utils import EpochMillisecondsField
from rest_framework.permissions import AllowAny


class CanchaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Canchas.
    Permite filtrar por tipo_cancha (RF-BACK-010).
    """
    queryset = Cancha.objects.all()
    serializer_class = CanchaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo_cancha', 'superficie', 'estado_disponibilidad']


class CanchaDisponibilidadView(views.APIView):
    """
    Devuelve la información de una cancha junto con todas sus reservas
    activas (PENDIENTE / CONFIRMADA) para un día determinado.

    GET /api/fields/canchas/<pk>/disponibilidad/?dia=<epoch_ms>
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        # 1. Obtener la cancha (404 automático si no existe)
        cancha = get_object_or_404(Cancha, pk=pk)

        # 2. Validar query param "dia"
        dia_ms = request.query_params.get('dia')
        if not dia_ms:
            return Response(
                {"detail": "Debe proveer el parámetro 'dia' en milisegundos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parser = EpochMillisecondsField()
            dia_dt = parser.to_internal_value(dia_ms)
            dia_date = dia_dt.date()
        except Exception:
            return Response(
                {"detail": "Formato de fecha inválido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Filtrar reservas activas de esa cancha en ese día
        reservas = Reserva.objects.filter(
            cancha=cancha,
            fecha_reserva__date=dia_date,
            estado__in=[
                Reserva.EstadoReserva.PENDIENTE,
                Reserva.EstadoReserva.CONFIRMADA,
            ],
        ).order_by('hora_inicio')

        # 4. Serializar y responder
        cancha_data = CanchaSerializer(cancha).data
        reservas_data = ReservaResumenSerializer(reservas, many=True).data

        return Response({
            "cancha": cancha_data,
            "dia": int(dia_ms),
            "reservas": reservas_data,
        })
