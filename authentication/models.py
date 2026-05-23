from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo unificado de usuario del sistema.
    Extiende AbstractUser para aprovechar el hashing de contraseñas,
    permisos y sesiones built-in de Django.
    """

    class Rol(models.TextChoices):
        SOCIO = 'SOCIO', 'Socio'
        EMPLEADO = 'EMPLEADO', 'Empleado'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        PROFESOR = 'PROFESOR', 'Profesor/Entrenador'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.SOCIO,
        verbose_name='Rol',
    )
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
    certificacion_deportiva = models.CharField(
        max_length=255, blank=True,
        verbose_name='Certificación Deportiva',
        help_text='Solo aplica a profesores/entrenadores',
    )
    # M2M self-referential: un profesor tiene muchos alumnos asignados
    alumnos = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='entrenadores',
        limit_choices_to={'rol': Rol.SOCIO},
        verbose_name='Alumnos Asignados',
    )
    activo = models.BooleanField(default=True, verbose_name='Activo (baja lógica)')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_rol_display()})'


class ProfesorManager(models.Manager):
    """Manager que filtra automáticamente solo usuarios con rol PROFESOR."""

    def get_queryset(self):
        return super().get_queryset().filter(rol=Usuario.Rol.PROFESOR)


class Profesor(Usuario):
    """
    Proxy Model: hereda de Usuario sin crear tabla extra.
    Polimorfismo — Profesor ES UN Usuario, diferenciado por rol.
    """
    objects = ProfesorManager()

    class Meta:
        proxy = True
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'

    def verificar_certificacion(self):
        """Verifica si el profesor tiene certificación deportiva cargada."""
        return bool(self.certificacion_deportiva)
