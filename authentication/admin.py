# pyrefly: ignore [missing-import]
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Profesor


@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del panel de administración para el modelo Usuario general.
    """
    # Cambiamos 'activo' por 'is_active' que es el campo nativo real de Django
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active')
    list_filter = ('rol', 'is_active', 'is_staff', 'is_superuser')
    list_editable = ('rol', 'is_active')
    
    # Mapeamos los campos customizados en los formularios del Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Canchas', {'fields': ('rol', 'telefono', 'dni')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Canchas', {'fields': ('rol', 'telefono', 'dni', 'first_name', 'last_name', 'email')}),
    )


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el Proxy de Profesores.
    """
    # Removemos 'certificacion_deportiva' y dejamos los campos reales del modelo Usuario
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'telefono', 'dni')
    search_fields = ('username', 'first_name', 'last_name', 'dni')
    
    # Quitamos 'filter_horizontal' de alumnos ya que las inscripciones se manejan en las Clases
    fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'dni', 'rol', 'is_active')

    def save_model(self, request, obj, form, change):
        # Forzamos que cualquier usuario guardado desde este panel nazca con el rol de PROFESOR
        obj.rol = Usuario.Roles.PROFESOR
        super().save_model(request, obj, form, change)
