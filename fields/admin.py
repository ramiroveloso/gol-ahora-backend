# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Cancha

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo_cancha', 'superficie', 'estado_disponibilidad', 'precio_base_hora')
    list_filter = ('tipo_cancha', 'superficie', 'estado_disponibilidad')
    list_editable = ('estado_disponibilidad', 'precio_base_hora')
    search_fields = ('numero',)
