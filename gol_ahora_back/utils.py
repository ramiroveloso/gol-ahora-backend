from datetime import datetime, timezone
from rest_framework import serializers


class EpochMillisecondsField(serializers.Field):
    """
    Serializa DateTimeField de Django como epoch milliseconds (entero).
    Deserializa epoch milliseconds (entero) a un objeto datetime de Django (UTC).
    """

    def to_representation(self, value):
        if not value:
            return None
        return int(value.timestamp() * 1000)

    def to_internal_value(self, data):
        if not data:
            return None
        try:
            return datetime.fromtimestamp(int(data) / 1000, tz=timezone.utc)
        except (ValueError, TypeError):
            raise serializers.ValidationError('Formato epoch milliseconds inválido.')
