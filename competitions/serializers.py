# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Competencia

class CompetenciaSerializer(serializers.ModelSerializer):
    # Al ser un JSONField, Django REST Framework lo serializa automáticamente como objeto
    class Meta:
        model = Competencia
        fields = ['id', 'nombre', 'tipo_competencia', 'activa', 'fixture', 'participantes', 'created_at']