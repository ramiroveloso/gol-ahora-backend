# pyrefly: ignore [missing-import]
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class ProfesorManager(UserManager):
    """
    Manager personalizado para el rol o proxy de Profesores.
    Hereda de UserManager para garantizar que Django Admin tenga acceso
    a métodos críticos de autenticación como 'normalize_email'.
    """
    def get_queryset(self):
        # Mantiene el filtro para que este mánager solo traiga usuarios que sean profesores
        return super().get_queryset().filter(rol='PROFESOR')


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema Gol Ahora.
    Contempla los roles del ecosistema (Socio, Profesor, Administrador).
    """
    class Roles(models.TextChoices):
        SOCIO = 'SOCIO', 'Socio'
        PROFESOR = 'PROFESOR', 'Profesor'
        ADMIN = 'ADMIN', 'Administrador'

    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.SOCIO,
        verbose_name='Rol del Usuario'
    )
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    dni = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name='DNI')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_rol_display()})'


class Profesor(Usuario):
    """
    Modelo Proxy para segmentar la lógica y administración 
    de los profesores en el Django Admin sin duplicar tablas.
    """
    objects = ProfesorManager()

    class Meta:
        proxy = True
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
