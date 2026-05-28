# pyrefly: ignore [missing-import]
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class ProfesorManager(BaseUserManager):
    """
    Manager personalizado para el proxy de Profesores.
    Hereda de BaseUserManager para garantizar métodos de limpieza (normalize_email)
    y compatibilidad absoluta con el Django Admin.
    """
    def get_queryset(self):
        return super().get_queryset().filter(rol='PROFESOR')


class UsuarioManager(BaseUserManager):
    """
    Manager base para el modelo Usuario personalizado.
    Garantiza la creación correcta de usuarios y superusuarios con soporte de roles.
    """
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


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

    # Asignamos el mánager robusto de autenticación customizada
    objects = UsuarioManager()

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
