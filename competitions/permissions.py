from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdministrador(BasePermission):
    """Solo usuarios con rol ADMINISTRADOR pueden acceder."""
    message = 'Se requiere rol de Administrador.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol == 'ADMINISTRADOR'
        )


class IsAdminOrReadOnly(BasePermission):
    """Administradores pueden escribir; usuarios autenticados solo leen."""
    message = 'Se requiere rol de Administrador para modificar.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.rol == 'ADMINISTRADOR'


class IsCapitanDelEquipo(BasePermission):
    """Solo el capitán del equipo puede modificarlo."""
    message = 'Solo el capitán del equipo puede realizar esta acción.'

    def has_object_permission(self, request, view, obj):
        # obj puede ser Equipo o MiembroEquipo
        equipo = obj if hasattr(obj, 'capitan') else obj.equipo
        return equipo.capitan == request.user


class IsCapitanOrReadOnly(BasePermission):
    """Capitán del equipo puede escribir; autenticados leen."""
    message = 'Solo el capitán del equipo puede realizar esta acción.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        equipo = obj if hasattr(obj, 'capitan') else obj.equipo
        return equipo.capitan == request.user
