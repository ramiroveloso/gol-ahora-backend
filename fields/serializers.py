# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Cancha
from bookings.models import Reserva
from gol_ahora_back.utils import EpochMillisecondsField


class CanchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancha
        fields = '__all__'


class ReservaResumenSerializer(serializers.ModelSerializer):
    """Serializer liviano para mostrar reservas en la grilla de disponibilidad."""
    hora_inicio = EpochMillisecondsField()
    hora_fin = EpochMillisecondsField()

    class Meta:
        model = Reserva
        fields = ['id', 'hora_inicio', 'hora_fin', 'estado', 'usuario']
