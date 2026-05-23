# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Profesor

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'activo')
    list_editable = ('rol', 'activo')
    list_filter = ('rol', 'activo', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'telefono', 'direccion', 'certificacion_deportiva', 'alumnos', 'activo')}),
    )

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'certificacion_deportiva')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    filter_horizontal = ('alumnos',)
