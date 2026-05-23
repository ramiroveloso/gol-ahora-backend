# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Cancha


class CanchaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancha
        fields = '__all__'
