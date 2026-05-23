# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import CanchaViewSet

router = DefaultRouter()
router.register(r'canchas', CanchaViewSet, basename='cancha')

urlpatterns = [
    path('', include(router.urls)),
]
