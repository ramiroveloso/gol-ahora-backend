# pyrefly: ignore [missing-import]
from django.urls import path, include
# pyrefly: ignore [missing-import]
from rest_framework.routers import DefaultRouter
from .views import (
    CompetenciaViewSet,
    EquipoViewSet,
    InscripcionViewSet,
    PartidoViewSet,
    ReglamentoView,
    ResultadoView,
)

router = DefaultRouter()
router.register(r'competencias', CompetenciaViewSet, basename='competencia')
router.register(r'equipos', EquipoViewSet, basename='equipo')

urlpatterns = [
    # ── Reglamento (1:1 con competencia) ──────────────────────────────────────
    path(
        'competencias/<int:competencia_pk>/reglamento/',
        ReglamentoView.as_view(),
        name='competencia-reglamento',
    ),

    # ── Inscripciones ─────────────────────────────────────────────────────────
    path(
        'competencias/<int:competencia_pk>/inscripciones/',
        InscripcionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='competencia-inscripciones-list',
    ),
    path(
        'competencias/<int:competencia_pk>/inscripciones/<int:pk>/',
        InscripcionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='competencia-inscripciones-detail',
    ),

    # ── Partidos / Fixture ────────────────────────────────────────────────────
    path(
        'competencias/<int:competencia_pk>/partidos/',
        PartidoViewSet.as_view({'get': 'list'}),
        name='competencia-partidos-list',
    ),
    path(
        'competencias/<int:competencia_pk>/partidos/<int:pk>/',
        PartidoViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='competencia-partidos-detail',
    ),

    # ── Resultado de un partido ───────────────────────────────────────────────
    path(
        'partidos/<int:partido_pk>/resultado/',
        ResultadoView.as_view(),
        name='partido-resultado',
    ),

    # ── Router (incluye CompetenciaViewSet con /generar-fixture/ y /cambiar-estado/) ──
    path('', include(router.urls)),
]
