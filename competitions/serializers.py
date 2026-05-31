# pyrefly: ignore [missing-import]
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Competencia, Equipo, MiembroEquipo,
    Reglamento, Inscripcion, Partido, Resultado,
)
from gol_ahora_back.utils import EpochMillisecondsField

Usuario = get_user_model()


# ─── Auxiliares ───────────────────────────────────────────────────────────────

class UsuarioResumenSerializer(serializers.ModelSerializer):
    """Mini-serializer de usuario para anidar en equipos/inscripciones."""
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name']


# ─── Equipo ───────────────────────────────────────────────────────────────────

class MiembroEquipoSerializer(serializers.ModelSerializer):
    usuario = UsuarioResumenSerializer(read_only=True)
    username = serializers.CharField(write_only=True)

    class Meta:
        model = MiembroEquipo
        fields = ['id', 'usuario', 'username', 'fecha_ingreso']
        read_only_fields = ['fecha_ingreso']

    def validate_username(self, value):
        try:
            return Usuario.objects.get(username=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError(f"No existe un usuario con username '{value}'.")

    def create(self, validated_data):
        usuario = validated_data.pop('username')  # ya es el objeto Usuario tras validate
        equipo = self.context['equipo']
        if MiembroEquipo.objects.filter(equipo=equipo, usuario=usuario).exists():
            raise serializers.ValidationError({'username': 'El usuario ya es miembro de este equipo.'})
        return MiembroEquipo.objects.create(equipo=equipo, usuario=usuario)


class EquipoSerializer(serializers.ModelSerializer):
    capitan = UsuarioResumenSerializer(read_only=True)
    miembros = MiembroEquipoSerializer(many=True, read_only=True)
    cantidad_miembros = serializers.SerializerMethodField()

    class Meta:
        model = Equipo
        fields = ['id', 'nombre', 'capitan', 'miembros', 'cantidad_miembros', 'activo', 'created_at']
        read_only_fields = ['capitan', 'activo', 'created_at']

    def get_cantidad_miembros(self, obj):
        return obj.miembros.count()


class EquipoListSerializer(serializers.ModelSerializer):
    """Versión liviana para listados."""
    capitan = UsuarioResumenSerializer(read_only=True)
    cantidad_miembros = serializers.SerializerMethodField()

    class Meta:
        model = Equipo
        fields = ['id', 'nombre', 'capitan', 'cantidad_miembros', 'activo']

    def get_cantidad_miembros(self, obj):
        return obj.miembros.count()


# ─── Reglamento ───────────────────────────────────────────────────────────────

class ReglamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reglamento
        fields = ['id', 'titulo', 'contenido', 'duracion_partido_min', 'jugadores_por_equipo']


# ─── Inscripcion ──────────────────────────────────────────────────────────────

class InscripcionSerializer(serializers.ModelSerializer):
    equipo_detail = EquipoListSerializer(source='equipo', read_only=True)
    fecha_inscripcion = EpochMillisecondsField(read_only=True)

    class Meta:
        model = Inscripcion
        fields = ['id', 'equipo', 'equipo_detail', 'estado', 'fecha_inscripcion']
        read_only_fields = ['estado', 'fecha_inscripcion']

    def validate_equipo(self, equipo):
        request = self.context['request']
        # Solo el capitán puede inscribir su equipo
        if equipo.capitan != request.user and request.user.rol != 'ADMINISTRADOR':
            raise serializers.ValidationError('Solo el capitán del equipo puede inscribirlo.')
        return equipo

    def validate(self, attrs):
        competencia = self.context['competencia']
        equipo = attrs['equipo']

        # Verificar que la competencia acepte inscripciones
        if competencia.estado != Competencia.EstadoCompetencia.INSCRIPCION_ABIERTA:
            raise serializers.ValidationError('La competencia no está aceptando inscripciones.')

        # Verificar cupo disponible
        inscriptos = competencia.inscripciones.filter(
            estado=Inscripcion.EstadoInscripcion.ACEPTADA
        ).count()
        if inscriptos >= competencia.max_equipos:
            raise serializers.ValidationError('La competencia ya alcanzó el cupo máximo de equipos.')

        # Verificar que el equipo no esté ya inscripto
        if Inscripcion.objects.filter(competencia=competencia, equipo=equipo).exists():
            raise serializers.ValidationError('Este equipo ya está inscripto en la competencia.')

        return attrs

    def create(self, validated_data):
        competencia = self.context['competencia']
        return Inscripcion.objects.create(competencia=competencia, **validated_data)


# ─── Resultado ────────────────────────────────────────────────────────────────

class ResultadoSerializer(serializers.ModelSerializer):
    equipo_ganador = EquipoListSerializer(read_only=True)

    class Meta:
        model = Resultado
        fields = ['id', 'goles_local', 'goles_visitante', 'equipo_ganador', 'observaciones']
        read_only_fields = ['equipo_ganador']

    def validate(self, attrs):
        partido = self.context['partido']
        if not partido.equipo_local or not partido.equipo_visitante:
            raise serializers.ValidationError(
                'No se puede cargar resultado: el partido no tiene ambos equipos asignados.'
            )
        if partido.estado == Partido.EstadoPartido.FINALIZADO:
            raise serializers.ValidationError('Este partido ya tiene resultado cargado.')
        return attrs


# ─── Partido ──────────────────────────────────────────────────────────────────

class PartidoSerializer(serializers.ModelSerializer):
    equipo_local = EquipoListSerializer(read_only=True)
    equipo_visitante = EquipoListSerializer(read_only=True)
    resultado = ResultadoSerializer(read_only=True)
    fecha_hora = EpochMillisecondsField(required=False, allow_null=True)

    class Meta:
        model = Partido
        fields = [
            'id', 'ronda', 'numero_partido',
            'equipo_local', 'equipo_visitante',
            'cancha', 'fecha_hora', 'estado',
            'resultado',
        ]
        read_only_fields = ['ronda', 'numero_partido', 'equipo_local', 'equipo_visitante', 'estado']


# ─── Competencia ──────────────────────────────────────────────────────────────

class CompetenciaSerializer(serializers.ModelSerializer):
    reglamento = ReglamentoSerializer(read_only=True)
    fecha_inicio = EpochMillisecondsField(required=False, allow_null=True)
    fecha_fin = EpochMillisecondsField(required=False, allow_null=True)
    equipos_inscriptos = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id', 'nombre', 'tipo_competencia', 'descripcion',
            'max_equipos', 'estado', 'fecha_inicio', 'fecha_fin',
            'activa', 'created_at', 'reglamento', 'equipos_inscriptos',
        ]
        read_only_fields = ['estado', 'created_at']

    def get_equipos_inscriptos(self, obj):
        return obj.inscripciones.filter(
            estado=Inscripcion.EstadoInscripcion.ACEPTADA
        ).count()


class CompetenciaListSerializer(serializers.ModelSerializer):
    """Versión liviana para listados."""
    fecha_inicio = EpochMillisecondsField(required=False, allow_null=True)
    fecha_fin = EpochMillisecondsField(required=False, allow_null=True)
    equipos_inscriptos = serializers.SerializerMethodField()

    class Meta:
        model = Competencia
        fields = [
            'id', 'nombre', 'tipo_competencia', 'max_equipos',
            'estado', 'fecha_inicio', 'fecha_fin', 'activa', 'equipos_inscriptos',
        ]

    def get_equipos_inscriptos(self, obj):
        return obj.inscripciones.filter(
            estado=Inscripcion.EstadoInscripcion.ACEPTADA
        ).count()
