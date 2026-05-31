# pyrefly: ignore [missing-import]
from rest_framework import viewsets, status, views
# pyrefly: ignore [missing-import]
from rest_framework.decorators import action
# pyrefly: ignore [missing-import]
from rest_framework.response import Response
# pyrefly: ignore [missing-import]
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import random

from .models import (
    Competencia, Equipo, MiembroEquipo,
    Reglamento, Inscripcion, Partido, Resultado,
)
from .serializers import (
    CompetenciaSerializer, CompetenciaListSerializer,
    EquipoSerializer, EquipoListSerializer,
    MiembroEquipoSerializer,
    InscripcionSerializer,
    ReglamentoSerializer,
    PartidoSerializer,
    ResultadoSerializer,
)
from .permissions import IsAdministrador, IsAdminOrReadOnly, IsCapitanOrReadOnly


# ─── Helpers del bracket ──────────────────────────────────────────────────────

RONDAS_8 = [Partido.Ronda.CUARTOS, Partido.Ronda.SEMIFINAL, Partido.Ronda.FINAL]
RONDAS_16 = [Partido.Ronda.OCTAVOS, Partido.Ronda.CUARTOS, Partido.Ronda.SEMIFINAL, Partido.Ronda.FINAL]

PARTIDOS_POR_RONDA = {
    Partido.Ronda.OCTAVOS: 8,
    Partido.Ronda.CUARTOS: 4,
    Partido.Ronda.SEMIFINAL: 2,
    Partido.Ronda.FINAL: 1,
}


def _generar_bracket(competencia, equipos):
    """
    Genera todos los partidos del bracket de eliminación directa.
    - equipos: lista de objetos Equipo (8 o 16, ya mezclados al azar)
    Retorna la lista de Partido creados.
    """
    total = len(equipos)
    rondas = RONDAS_8 if total == 8 else RONDAS_16

    partidos_creados = {}  # ronda -> [Partido]

    for ronda in rondas:
        n = PARTIDOS_POR_RONDA[ronda]
        partidos_ronda = []
        for num in range(1, n + 1):
            partido = Partido.objects.create(
                competencia=competencia,
                ronda=ronda,
                numero_partido=num,
            )
            partidos_ronda.append(partido)
        partidos_creados[ronda] = partidos_ronda

    # Asignar equipos a la primera ronda
    primera_ronda = rondas[0]
    primeros = partidos_creados[primera_ronda]
    for i, partido in enumerate(primeros):
        partido.equipo_local = equipos[i * 2]
        partido.equipo_visitante = equipos[i * 2 + 1]
        partido.save()

    # Enlazar partido_siguiente entre rondas
    for idx in range(len(rondas) - 1):
        ronda_actual = rondas[idx]
        ronda_siguiente = rondas[idx + 1]
        partidos_actual = partidos_creados[ronda_actual]
        partidos_siguiente = partidos_creados[ronda_siguiente]

        for i, partido in enumerate(partidos_actual):
            siguiente = partidos_siguiente[i // 2]
            partido.partido_siguiente = siguiente
            partido.posicion_siguiente = 'LOCAL' if i % 2 == 0 else 'VISITANTE'
            partido.save()

    return partidos_creados


# ─── Competencia ──────────────────────────────────────────────────────────────

class CompetenciaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Competencias. (RF-34 a RF-37)
    Solo administradores pueden crear/modificar/eliminar.
    """
    queryset = Competencia.objects.filter(activa=True)
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return CompetenciaListSerializer
        return CompetenciaSerializer

    def perform_destroy(self, instance):
        """Baja lógica en lugar de delete real."""
        instance.activa = False
        instance.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAdministrador])
    def generar_fixture(self, request, pk=None):
        """
        Genera automáticamente el bracket de eliminación directa. (RF-42)
        Requiere exactamente 8 o 16 inscripciones ACEPTADAS.
        """
        competencia = self.get_object()

        # Validaciones previas
        if competencia.partidos.exists():
            return Response(
                {'detail': 'Esta competencia ya tiene un fixture generado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        inscripciones_aceptadas = competencia.inscripciones.filter(
            estado=Inscripcion.EstadoInscripcion.ACEPTADA
        ).select_related('equipo')

        total = inscripciones_aceptadas.count()
        if total not in (8, 16):
            return Response(
                {'detail': f'Se necesitan exactamente 8 o 16 equipos aceptados. Hay {total}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        equipos = [ins.equipo for ins in inscripciones_aceptadas]
        random.shuffle(equipos)  # sorteo aleatorio del bracket

        _generar_bracket(competencia, equipos)

        # Actualizar estado de la competencia
        competencia.estado = Competencia.EstadoCompetencia.EN_CURSO
        competencia.save()

        partidos = Partido.objects.filter(competencia=competencia).order_by('ronda', 'numero_partido')
        serializer = PartidoSerializer(partidos, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdministrador])
    def cambiar_estado(self, request, pk=None):
        """Permite al admin cambiar el estado de la competencia manualmente."""
        competencia = self.get_object()
        nuevo_estado = request.data.get('estado')
        estados_validos = [e[0] for e in Competencia.EstadoCompetencia.choices]
        if nuevo_estado not in estados_validos:
            return Response(
                {'detail': f"Estado inválido. Opciones: {estados_validos}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        competencia.estado = nuevo_estado
        competencia.save()
        return Response(CompetenciaSerializer(competencia).data)


# ─── Equipo ───────────────────────────────────────────────────────────────────

class EquipoViewSet(viewsets.ModelViewSet):
    """
    ABM de Equipos permanentes.
    Cualquier usuario autenticado puede crear un equipo.
    Solo el capitán puede modificarlo o darlo de baja.
    """
    queryset = Equipo.objects.filter(activo=True)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return EquipoListSerializer
        return EquipoSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsCapitanOrReadOnly()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """El usuario que crea el equipo queda como capitán y se agrega como miembro."""
        equipo = serializer.save(capitan=self.request.user)
        MiembroEquipo.objects.create(equipo=equipo, usuario=self.request.user)

    def perform_destroy(self, instance):
        """Baja lógica."""
        instance.activo = False
        instance.save()

    @action(detail=True, methods=['post'], url_path='miembros', permission_classes=[IsAuthenticated])
    def agregar_miembro(self, request, pk=None):
        """
        Agrega un jugador al equipo por username.
        Solo puede hacerlo el capitán.
        """
        equipo = self.get_object()
        if equipo.capitan != request.user:
            return Response(
                {'detail': 'Solo el capitán puede agregar miembros.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = MiembroEquipoSerializer(
            data=request.data,
            context={'request': request, 'equipo': equipo},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=['delete'],
        url_path=r'miembros/(?P<usuario_id>\d+)',
        permission_classes=[IsAuthenticated],
    )
    def quitar_miembro(self, request, pk=None, usuario_id=None):
        """
        Quita un jugador del equipo.
        Solo puede hacerlo el capitán. No puede quitarse a sí mismo.
        """
        equipo = self.get_object()
        if equipo.capitan != request.user:
            return Response(
                {'detail': 'Solo el capitán puede quitar miembros.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if str(equipo.capitan.id) == str(usuario_id):
            return Response(
                {'detail': 'El capitán no puede quitarse a sí mismo del equipo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        miembro = get_object_or_404(MiembroEquipo, equipo=equipo, usuario_id=usuario_id)
        miembro.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Inscripcion ──────────────────────────────────────────────────────────────

class InscripcionViewSet(viewsets.ModelViewSet):
    """
    Inscripción de equipos a una competencia. (RF-38 a RF-41)
    Capitán crea (POST), admin acepta/rechaza (PATCH).
    """
    serializer_class = InscripcionSerializer
    permission_classes = [IsAuthenticated]

    def get_competencia(self):
        return get_object_or_404(Competencia, pk=self.kwargs['competencia_pk'])

    def get_queryset(self):
        return Inscripcion.objects.filter(
            competencia=self.get_competencia()
        ).select_related('equipo', 'equipo__capitan')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['competencia'] = self.get_competencia()
        return ctx

    def get_permissions(self):
        if self.action in ('update', 'partial_update'):
            return [IsAdministrador()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()


# ─── Reglamento ───────────────────────────────────────────────────────────────

class ReglamentoView(views.APIView):
    """
    Reglamento de una competencia (1:1). (RF-50 a RF-53)
    GET/POST/PUT/DELETE anidado bajo /competencias/{id}/reglamento/
    """
    permission_classes = [IsAdminOrReadOnly]

    def _get_competencia(self, pk):
        return get_object_or_404(Competencia, pk=pk)

    def get(self, request, competencia_pk):
        competencia = self._get_competencia(competencia_pk)
        reglamento = get_object_or_404(Reglamento, competencia=competencia)
        return Response(ReglamentoSerializer(reglamento).data)

    def post(self, request, competencia_pk):
        competencia = self._get_competencia(competencia_pk)
        if hasattr(competencia, 'reglamento'):
            return Response(
                {'detail': 'Esta competencia ya tiene un reglamento. Use PUT para modificarlo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ReglamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(competencia=competencia)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, competencia_pk):
        competencia = self._get_competencia(competencia_pk)
        reglamento = get_object_or_404(Reglamento, competencia=competencia)
        serializer = ReglamentoSerializer(reglamento, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, competencia_pk):
        competencia = self._get_competencia(competencia_pk)
        reglamento = get_object_or_404(Reglamento, competencia=competencia)
        reglamento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Partido ──────────────────────────────────────────────────────────────────

class PartidoViewSet(viewsets.ModelViewSet):
    """
    Fixture: consulta y asignación de canchas/horarios. (RF-42 a RF-45, RF-54, RF-55)
    Lectura pública; escritura solo admin.
    """
    serializer_class = PartidoSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_competencia(self):
        return get_object_or_404(Competencia, pk=self.kwargs['competencia_pk'])

    def get_queryset(self):
        return Partido.objects.filter(
            competencia=self.get_competencia()
        ).select_related(
            'equipo_local', 'equipo_visitante', 'cancha', 'resultado'
        ).order_by('ronda', 'numero_partido')

    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Los partidos se generan automáticamente con /generar-fixture/. Use PATCH para asignar cancha y horario.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'No se puede eliminar un partido individualmente. Use la baja de competencia.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


# ─── Resultado ────────────────────────────────────────────────────────────────

class ResultadoView(views.APIView):
    """
    Registrar/consultar resultado de un partido. (RF-46 a RF-49)
    Al registrar, promueve automáticamente al ganador al siguiente partido del bracket.
    """
    permission_classes = [IsAuthenticated]

    def _get_partido(self, partido_pk):
        return get_object_or_404(
            Partido.objects.select_related(
                'equipo_local', 'equipo_visitante',
                'partido_siguiente', 'resultado',
            ),
            pk=partido_pk,
        )

    def get(self, request, partido_pk):
        partido = self._get_partido(partido_pk)
        resultado = get_object_or_404(Resultado, partido=partido)
        return Response(ResultadoSerializer(resultado).data)

    def post(self, request, partido_pk):
        if request.user.rol != 'ADMINISTRADOR':
            return Response(
                {'detail': 'Solo un administrador puede registrar resultados.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        partido = self._get_partido(partido_pk)
        serializer = ResultadoSerializer(
            data=request.data,
            context={'request': request, 'partido': partido},
        )
        serializer.is_valid(raise_exception=True)

        goles_local = serializer.validated_data['goles_local']
        goles_visitante = serializer.validated_data['goles_visitante']

        # Determinar ganador (no puede haber empate en eliminación directa)
        if goles_local == goles_visitante:
            return Response(
                {'detail': 'No puede haber empate en eliminación directa. Cargue el resultado correcto.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ganador = partido.equipo_local if goles_local > goles_visitante else partido.equipo_visitante

        resultado = serializer.save(partido=partido, equipo_ganador=ganador)

        # Marcar partido como finalizado
        partido.estado = Partido.EstadoPartido.FINALIZADO
        partido.save()

        # Promover ganador al siguiente partido del bracket (RF-42/fixture)
        if partido.partido_siguiente:
            siguiente = partido.partido_siguiente
            if partido.posicion_siguiente == 'LOCAL':
                siguiente.equipo_local = ganador
            else:
                siguiente.equipo_visitante = ganador
            siguiente.save()

        return Response(ResultadoSerializer(resultado).data, status=status.HTTP_201_CREATED)
