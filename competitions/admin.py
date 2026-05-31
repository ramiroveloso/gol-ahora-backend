from django.contrib import admin
from .models import (
    Competencia, Equipo, MiembroEquipo,
    Reglamento, Inscripcion, Partido, Resultado,
)


# ─── Inlines ──────────────────────────────────────────────────────────────────

class MiembroEquipoInline(admin.TabularInline):
    model = MiembroEquipo
    extra = 1
    autocomplete_fields = ['usuario']


class InscripcionInline(admin.TabularInline):
    model = Inscripcion
    extra = 0
    readonly_fields = ['fecha_inscripcion']


class ReglamentoInline(admin.StackedInline):
    model = Reglamento
    extra = 0
    can_delete = True


class ResultadoInline(admin.StackedInline):
    model = Resultado
    extra = 0
    readonly_fields = ['equipo_ganador']


class PartidoInline(admin.TabularInline):
    model = Partido
    extra = 0
    readonly_fields = ['ronda', 'numero_partido', 'equipo_local', 'equipo_visitante', 'estado']
    fields = ['ronda', 'numero_partido', 'equipo_local', 'equipo_visitante', 'cancha', 'fecha_hora', 'estado']


# ─── ModelAdmins ──────────────────────────────────────────────────────────────

@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_competencia', 'estado', 'max_equipos', 'activa', 'created_at')
    list_filter = ('tipo_competencia', 'estado', 'activa', 'max_equipos')
    search_fields = ('nombre',)
    readonly_fields = ('created_at',)
    inlines = [ReglamentoInline, InscripcionInline, PartidoInline]


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capitan', 'activo', 'created_at')
    list_filter = ('activo',)
    search_fields = ('nombre', 'capitan__username', 'capitan__first_name', 'capitan__last_name')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['capitan']
    inlines = [MiembroEquipoInline]


@admin.register(MiembroEquipo)
class MiembroEquipoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'equipo', 'fecha_ingreso')
    list_filter = ('equipo',)
    search_fields = ('usuario__username', 'equipo__nombre')
    readonly_fields = ('fecha_ingreso',)
    autocomplete_fields = ['usuario', 'equipo']


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'competencia', 'estado', 'fecha_inscripcion')
    list_filter = ('estado', 'competencia')
    search_fields = ('equipo__nombre', 'competencia__nombre')
    readonly_fields = ('fecha_inscripcion',)
    autocomplete_fields = ['equipo', 'competencia']


@admin.register(Reglamento)
class ReglamentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'competencia', 'duracion_partido_min', 'jugadores_por_equipo')
    search_fields = ('titulo', 'competencia__nombre')
    autocomplete_fields = ['competencia']


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'competencia', 'ronda', 'numero_partido', 'cancha', 'fecha_hora', 'estado')
    list_filter = ('competencia', 'ronda', 'estado')
    search_fields = ('competencia__nombre', 'equipo_local__nombre', 'equipo_visitante__nombre')
    autocomplete_fields = ['competencia', 'equipo_local', 'equipo_visitante', 'cancha']
    inlines = [ResultadoInline]


@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ('partido', 'goles_local', 'goles_visitante', 'equipo_ganador')
    search_fields = ('partido__competencia__nombre',)
    readonly_fields = ('equipo_ganador',)
