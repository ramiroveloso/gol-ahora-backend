# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Descuento, Cobro, ReciboPago
from gol_ahora_back.utils import EpochMillisecondsField


class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = '__all__'


class ReciboPagoSerializer(serializers.ModelSerializer):
    fecha_emision = EpochMillisecondsField(read_only=True)

    class Meta:
        model = ReciboPago
        fields = '__all__'


class CobroSerializer(serializers.ModelSerializer):
    fecha_cobro = EpochMillisecondsField(read_only=True)
    recibo = ReciboPagoSerializer(read_only=True)

    class Meta:
        model = Cobro
        fields = '__all__'
