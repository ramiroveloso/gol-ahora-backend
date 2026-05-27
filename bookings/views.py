# pyrefly: ignore [missing-import]
from rest_framework import viewsets, status, views
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework.permissions import IsAuthenticated, AllowAny
# pyrefly: ignore [missing-import]
from rest_framework.exceptions import ValidationError
# pyrefly: ignore [missing-import]
from rest_framework.decorators import action  # <-- Importamos el decorador para rutas personalizadas
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
        
        # Recuperamos los datos crudos del request para parsearlos de forma segura si vienen en milisegundos
        parser = EpochMillisecondsField()
        raw_fecha = self.request.data.get('fecha_reserva')
        raw_inicio = self.request.data.get('hora_inicio')
        raw_fin = self.request.data.get('hora_fin')

        try:
            # Si vienen como milisegundos de React, los transformamos al tipo nativo de Python, sino usamos el fallback del serializer
            fecha_reserva = parser.to_internal_value(raw_fecha).date() if str(raw_fecha).isdigit() else serializer.validated_data.get('fecha_reserva')
            hora_inicio = parser.to_internal_value(raw_inicio) if str(raw_inicio).isdigit() else serializer.validated_data.get('hora_inicio')
            hora_fin = parser.to_internal_value(raw_fin) if str(raw_fin).isdigit() else serializer.validated_data.get('hora_fin')
        except Exception:
            raise ValidationError({"detail": "Los campos de fecha u hora no tienen un formato de milisegundos válido."})

        # 1. Verificar deudas pendientes (Cobros no aprobados)
        deudas = Cobro.objects.filter(usuario=usuario).exclude(estado_pago=Cobro.EstadoPago.APROBADO)
        if deudas.exists():
            raise ValidationError({"detail": "El usuario posee deudas pendientes y no puede realizar nuevas reservas."})

        # 2. Verificar solapamiento
        solapamiento = Reserva.objects.filter(
            cancha=cancha,
            estado__in=[Reserva.EstadoReserva.PENDIENTE, Reserva.EstadoReserva.CONFIRMADA]
        ).filter(
            Q(fecha_reserva__date=fecha_reserva) & Q(hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio)
        ).exists()

        if solapamiento:
            raise ValidationError({"detail": "La cancha ya se encuentra reservada en el horario solicitado."})

        # Guardamos inyectando los valores transformados de forma segura
        serializer.save(fecha_reserva=fecha_reserva, hora_inicio=hora_inicio, hora_fin=hora_fin)

    @action(detail=True, methods=['post'], url_path='cambiar_estado', permission_classes=[AllowAny])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint personalizado para confirmar el pago y cambiar el estado de la reserva.
        Machea con: POST /api/bookings/reservas/<id>/cambiar_estado/
        """
        reserva = self.get_object()
        nuevo_estado = request.data.get('estado')

        if not nuevo_estado:
            return Response({"detail": "Debe proveer el campo 'estado'."}, status=status.HTTP_400_BAD_REQUEST)

        # Validamos que el estado ingresado coincida con los que maneja el modelo
        if nuevo_estado not in [Reserva.EstadoReserva.PENDIENTE, Reserva.EstadoReserva.CONFIRMADA, Reserva.EstadoReserva.CANCELADA]:
            return Response({"detail": "Estado de reserva inválido."}, status=status.HTTP_400_BAD_REQUEST)

        reserva.estado = nuevo_estado
        reserva.save()

        serializer = self.get_serializer(reserva)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    permission_classes = [AllowAny]  # <-- Liberado para consulta pública del calendario desde React

    def get(self, request):
        fecha_ms = request.query_params.get('fecha')
        if not fecha_ms:
            return Response({"detail": "Debe proveer el parámetro 'fecha' en milisegundos."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            parser = EpochMillisecondsField()
            fecha = parser.to_internal_value(fecha_ms).date()
        except Exception:
            return Response({"detail": "Formato de fecha inválido."}, status=status.HTTP_400_BAD_REQUEST)

        reservas_del_dia = Reserva.objects.filter(
            fecha_reserva__date=fecha,
            estado__in=[Reserva.EstadoReserva.PENDIENTE, Reserva.EstadoReserva.CONFIRMADA]
        )

        canchas_data = []
        for cancha in Cancha.objects.filter(activa=True, estado_disponibilidad=True):
            reservas_cancha = reservas_del_dia.filter(cancha=cancha)
            horarios_ocupados = [
                {
                    "num_reserva": r.id,  # Agregamos metadata por si React la necesita
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
