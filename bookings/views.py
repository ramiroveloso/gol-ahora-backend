# pyrefly: ignore [missing-import]
from rest_framework import viewsets, status, views
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework.permissions import IsAuthenticated
# pyrefly: ignore [missing-import]
from rest_framework.exceptions import ValidationError
# pyrefly: ignore [missing-import]
from django.db.models import Q
from datetime import datetime

from .models import Reserva, ClaseEntrenamiento, Asistencia
from finance.models import Cobro
from fields.models import Cancha
from .serializers import ReservaSerializer, ClaseEntrenamientoSerializer, AsistenciaSerializer
from gol_ahora_back.utils import EpochMillisecondsField


class ReservaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Reservas.
    Incluye validación de solapamiento y deudas del usuario.
    """
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def perform_create(self, serializer):
        usuario = serializer.validated_data.get('usuario')
        cancha = serializer.validated_data.get('cancha')
        fecha_reserva = serializer.validated_data.get('fecha_reserva')
        hora_inicio = serializer.validated_data.get('hora_inicio')
        hora_fin = serializer.validated_data.get('hora_fin')

        # 1. Verificar deudas pendientes (Cobros no aprobados)
        deudas = Cobro.objects.filter(usuario=usuario).exclude(estado_pago=Cobro.EstadoPago.APROBADO)
        if deudas.exists():
            raise ValidationError({"detail": "El usuario posee deudas pendientes y no puede realizar nuevas reservas."})

        # 2. Verificar solapamiento
        solapamiento = Reserva.objects.filter(
            cancha=cancha,
            fecha_reserva=fecha_reserva,
            estado__in=[Reserva.EstadoReserva.PENDIENTE, Reserva.EstadoReserva.CONFIRMADA]
        ).filter(
            Q(hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio)
        ).exists()

        if solapamiento:
            raise ValidationError({"detail": "La cancha ya se encuentra reservada en el horario solicitado."})

        serializer.save()


class ClaseEntrenamientoViewSet(viewsets.ModelViewSet):
    queryset = ClaseEntrenamiento.objects.all()
    serializer_class = ClaseEntrenamientoSerializer


class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer


class DisponibilidadView(views.APIView):
    """
    Endpoint para consultar la disponibilidad de canchas en una fecha.
    Espera query params: ?fecha=<epoch_ms>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_ms = request.query_params.get('fecha')
        if not fecha_ms:
            return Response({"detail": "Debe proveer el parámetro 'fecha' en milisegundos."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Reutilizamos el field para parsear
            parser = EpochMillisecondsField()
            fecha = parser.to_internal_value(fecha_ms).date()
        except Exception:
            return Response({"detail": "Formato de fecha inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar todas las reservas de ese día que estén confirmadas o pendientes
        reservas_del_dia = Reserva.objects.filter(
            fecha_reserva__date=fecha,
            estado__in=[Reserva.EstadoReserva.PENDIENTE, Reserva.EstadoReserva.CONFIRMADA]
        )

        canchas_data = []
        for cancha in Cancha.objects.filter(activa=True, estado_disponibilidad=True):
            reservas_cancha = reservas_del_dia.filter(cancha=cancha)
            horarios_ocupados = [
                {
                    "hora_inicio": parser.to_representation(r.hora_inicio),
                    "hora_fin": parser.to_representation(r.hora_fin)
                } for r in reservas_cancha
            ]
            canchas_data.append({
                "cancha_id": cancha.id,
                "numero": cancha.numero,
                "tipo_cancha": cancha.tipo_cancha,
                "horarios_ocupados": horarios_ocupados
            })

        return Response(canchas_data)
