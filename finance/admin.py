# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import Descuento, Cobro, ReciboPago

@admin.register(Descuento)
class DescuentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_descuento', 'porcentaje', 'descripcion', 'activo')
    list_filter = ('tipo_descuento', 'activo')

class ReciboPagoInline(admin.StackedInline):
    model = ReciboPago
    readonly_fields = ('detalle', 'fecha_emision')
    extra = 0

@admin.register(Cobro)
class CobroAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo_servicio', 'monto', 'estado_pago', 'fecha_cobro')
    list_filter = ('tipo_servicio', 'estado_pago', 'metodo_pago', 'fecha_cobro')
    search_fields = ('usuario__username', 'usuario__email')
    list_editable = ('estado_pago',)
    inlines = [ReciboPagoInline]

@admin.register(ReciboPago)
class ReciboPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cobro', 'fecha_emision')
    search_fields = ('cobro__id', 'cobro__usuario__username')
    readonly_fields = ('cobro', 'detalle', 'fecha_emision')
    
    def has_add_permission(self, request):
        return False
