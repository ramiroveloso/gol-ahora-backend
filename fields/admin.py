# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Cancha, Complejo  # <-- 1. Importamos también el modelo Complejo

# 2. Registramos Complejo de forma simple para poder crearlos desde el Admin
@admin.register(Complejo)
class ComplejoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion')  # Ajustá los campos según los que tenga su modelo Complejo
    search_fields = ('nombre',)

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    # 3. Agregamos 'id' y 'complejo' al list_display para verlos en la tabla
    list_display = ('id', 'numero', 'tipo_cancha', 'superficie', 'estado_disponibilidad', 'precio_base_hora', 'complejo')
    list_filter = ('tipo_cancha', 'superficie', 'estado_disponibilidad', 'complejo')
    list_editable = ('estado_disponibilidad', 'precio_base_hora')
    search_fields = ('numero',)
