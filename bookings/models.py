# pyrefly: ignore [missing-import]
from django.db import models


class Reserva(models.Model):
    """Reserva de una cancha por un usuario en un horario determinado."""

    class EstadoReserva(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        COMPLETADA = 'COMPLETADA', 'Completada'

    usuario = models.ForeignKey(
        'authentication.Usuario', on_delete=models.CASCADE,
        related_name='reservas', verbose_name='Usuario',
    )
    cancha = models.ForeignKey(
        'fields.Cancha', on_delete=models.CASCADE,
        related_name='reservas', verbose_name='Cancha',
    )
    fecha_reserva = models.DateTimeField(verbose_name='Fecha de Reserva')
    hora_inicio = models.DateTimeField(verbose_name='Hora de Inicio')
    hora_fin = models.DateTimeField(verbose_name='Hora de Fin')
    estado = models.CharField(
        max_length=20, choices=EstadoReserva.choices,
        default=EstadoReserva.PENDIENTE, verbose_name='Estado',
    )
    antelacion_cancelacion = models.PositiveIntegerField(
        default=24, help_text='Horas de antelación para cancelar',
        verbose_name='Antelación de Cancelación (hs)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_reserva']
        constraints = [
            models.UniqueConstraint(
                fields=['cancha', 'fecha_reserva', 'hora_inicio'],
                name='unique_cancha_fecha_hora',
            )
        ]

    def __str__(self):
        return f'Reserva #{self.pk} - {self.cancha} ({self.get_estado_display()})'


class ClaseEntrenamiento(models.Model):
    """Clase o entrenamiento dictado por un profesor en una cancha."""

    class TipoClase(models.TextChoices):
        FUNCIONAL = 'FUNCIONAL', 'Funcional'
        FUTBOL = 'FUTBOL', 'Fútbol'
        PADDLE = 'PADDLE', 'Paddle'
        PERSONALIZADO = 'PERSONALIZADO', 'Personalizado'

    profesor = models.ForeignKey(
        'authentication.Usuario', on_delete=models.CASCADE,
        limit_choices_to={'rol': 'PROFESOR'},
        related_name='clases_dictadas', verbose_name='Profesor',
    )
    cancha = models.ForeignKey(
        'fields.Cancha', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='clases', verbose_name='Cancha',
    )
    horario = models.DateTimeField(verbose_name='Horario')
    maximo_alumnos = models.PositiveIntegerField(verbose_name='Máximo de Alumnos')
    tipo_clase = models.CharField(
        max_length=20, choices=TipoClase.choices,
        verbose_name='Tipo de Clase',
    )
    alumnos = models.ManyToManyField(
        'authentication.Usuario', through='Asistencia',
        related_name='clases_inscriptas', blank=True,
        verbose_name='Alumnos Inscriptos',
    )

    class Meta:
        verbose_name = 'Clase de Entrenamiento'
        verbose_name_plural = 'Clases de Entrenamiento'
        ordering = ['-horario']

    def __str__(self):
        return f'{self.get_tipo_clase_display()} - {self.profesor.get_full_name()}'


class Asistencia(models.Model):
    """Tabla intermedia M:N entre ClaseEntrenamiento y Usuario (alumno)."""

    class EstadoAsistencia(models.TextChoices):
        PRESENTE = 'PRESENTE', 'Presente'
        AUSENTE = 'AUSENTE', 'Ausente'
        JUSTIFICADO = 'JUSTIFICADO', 'Justificado'

    clase = models.ForeignKey(
        ClaseEntrenamiento, on_delete=models.CASCADE,
        related_name='asistencias', verbose_name='Clase',
    )
    alumno = models.ForeignKey(
        'authentication.Usuario', on_delete=models.CASCADE,
        related_name='asistencias', verbose_name='Alumno',
    )
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    estado_asistencia = models.CharField(
        max_length=20, choices=EstadoAsistencia.choices,
        default=EstadoAsistencia.AUSENTE, verbose_name='Estado',
    )

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['clase', 'alumno']

    def __str__(self):
        return f'{self.alumno.get_full_name()} → {self.clase} ({self.get_estado_asistencia_display()})'
