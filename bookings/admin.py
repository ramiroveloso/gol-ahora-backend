# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Reserva, ClaseEntrenamiento, Asistencia

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'cancha', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'estado')
    list_filter = ('estado', 'fecha_reserva', 'cancha')
    search_fields = ('usuario__username', 'usuario__email')
    list_editable = ('estado',)

class AsistenciaInline(admin.TabularInline):
    model = Asistencia
    extra = 1

@admin.register(ClaseEntrenamiento)
class ClaseEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_clase', 'profesor', 'cancha', 'horario', 'maximo_alumnos')
    list_filter = ('tipo_clase', 'horario')
    search_fields = ('profesor__username', 'profesor__email')
    inlines = [AsistenciaInline]

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'clase', 'alumno', 'estado_asistencia', 'fecha')
    list_filter = ('estado_asistencia', 'fecha')
    search_fields = ('alumno__username', 'alumno__email')
