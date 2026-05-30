from django.shortcuts import render

# Create your views here.
# pyrefly: ignore [missing-import]
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Competencia
from .serializers import CompetenciaSerializer

class CompetenciaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que expone las competencias.
    Filtra para mostrar solo en las que el usuario logueado participa.
    """
    serializer_class = CompetenciaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Si es un administrador, permitimos ver todas para gestionar
        if user.is_staff or user.rol == 'ADMIN':
            return Competencia.objects.all()
            
        # Para los clientes, filtramos las competencias donde su usuario está en la lista de participantes
        return Competencia.objects.filter(participantes=user, activa=True)