# pyrefly: ignore [missing-import]
from rest_framework import viewsets, status, views
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework.permissions import IsAuthenticated, AllowAny
# pyrefly: ignore [missing-import]
from django.contrib.auth import authenticate, login, logout
# pyrefly: ignore [missing-import]
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Usuario, Profesor
from .serializers import UsuarioSerializer, UsuarioCreateSerializer, ProfesorSerializer, LoginSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios.
    El DELETE hace un borrado lógico (RF-BACK-005).
    """
    queryset = Usuario.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        # Borrado lógico
        usuario = self.get_object()
        usuario.activo = False
        usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfesorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listado de profesores. Solo lectura.
    """
    queryset = Profesor.objects.all()
    serializer_class = ProfesorSerializer


class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user:
            login(request, user)
            return Response(UsuarioSerializer(user).data)
        
        return Response(
            {"detail": "Credenciales inválidas"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class GetCSRFToken(views.APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, format=None):
        return Response({'detail': 'CSRF cookie set'})
