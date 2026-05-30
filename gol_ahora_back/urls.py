"""
URL configuration for gol_ahora_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# CONFIGURACIÓN DE MARCA PARA EL DJANGO ADMIN:
admin.site.site_header = "Administración Gol Ahora"  # El título dorado grande arriba de todo
admin.site.site_title = "Gol Ahora Admin"            # El texto que aparece en la pestaña del navegador
admin.site.index_title = "Panel de Control"          # El subtítulo dentro de la página principal del admin


urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/auth/', include('authentication.urls')),
    path('api/fields/', include('fields.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/finance/', include('finance.urls')),
    
    # Swagger UI endpoints
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
