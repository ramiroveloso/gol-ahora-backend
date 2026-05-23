# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Reserva, ClaseEntrenamiento, Asistencia
from gol_ahora_back.utils import EpochMillisecondsField


class ReservaSerializer(serializers.ModelSerializer):
    fecha_reserva = EpochMillisecondsField()
    hora_inicio = EpochMillisecondsField()
    hora_fin = EpochMillisecondsField()

    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ['estado', 'created_at', 'updated_at']


class AsistenciaSerializer(serializers.ModelSerializer):
    fecha = EpochMillisecondsField(read_only=True)

    class Meta:
        model = Asistencia
        fields = '__all__'


class ClaseEntrenamientoSerializer(serializers.ModelSerializer):
    horario = EpochMillisecondsField()
    asistencias = AsistenciaSerializer(many=True, read_only=True)

    class Meta:
        model = ClaseEntrenamiento
        fields = '__all__'
