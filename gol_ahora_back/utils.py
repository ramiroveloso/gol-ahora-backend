from datetime import datetime, time, timezone
from rest_framework import serializers
from django.utils import timezone as django_timezone


class EpochMillisecondsField(serializers.Field):
    """
    Serializa DateTimeField y DateField de Django como epoch milliseconds (entero).
    Deserializa epoch milliseconds (entero) a un objeto datetime de Django (UTC).
    """

    def to_representation(self, value):
        if not value:
            return None
        
        # Si es un objeto date puro (no tiene el método timestamp), lo convertimos
        # a datetime combinándolo con hora 00:00 y asignándole la zona horaria UTC
        if not hasattr(value, 'timestamp') and hasattr(value, 'year'):
            value = django_timezone.make_aware(datetime.combine(value, time.min), django_timezone.utc)
            
        return int(value.timestamp() * 1000)

    def to_internal_value(self, data):
        if not data:
            return None
        try:
            return datetime.fromtimestamp(int(data) / 1000, tz=timezone.utc)
        except (ValueError, TypeError):
            raise serializers.ValidationError('Formato epoch milliseconds inválido.')