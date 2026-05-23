# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Competencia

@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_competencia', 'activa', 'created_at')
    list_filter = ('tipo_competencia', 'activa')
    search_fields = ('nombre',)
    filter_horizontal = ('participantes',)
