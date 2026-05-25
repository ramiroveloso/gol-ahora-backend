# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, ProfesorViewSet, LoginView, LogoutView, GetCSRFToken

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'profesores', ProfesorViewSet, basename='profesor')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('csrf/', GetCSRFToken.as_view(), name='csrf'),
]
