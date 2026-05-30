from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from competitions.views import CompetenciaViewSet

# CONFIGURACIÓN DE MARCA PARA EL DJANGO ADMIN
admin.site.site_header = "Administración Gol Ahora"
admin.site.site_title = "Gol Ahora Admin"
admin.site.index_title = "Panel de Control"

# 1. Configuración del Router para ViewSets (Competiciones)
router = DefaultRouter()
router.register(r'competitions', CompetenciaViewSet, basename='competencia')

# 2. Lista ÚNICA de Patrones de URL
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints manuales de las aplicaciones
    path('api/auth/', include('authentication.urls')),
    path('api/fields/', include('fields.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/finance/', include('finance.urls')),  # <-- ¡Recuperado!
    
    # API endpoints automáticos del Router (Incluye /api/competitions/)
    path('api/', include(router.urls)),
    
    # Swagger UI / Documentación de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
