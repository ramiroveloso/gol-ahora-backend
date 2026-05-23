from django.db import models


class Cancha(models.Model):
    """Representa una cancha o pista del complejo deportivo."""

    class TipoCancha(models.TextChoices):
        FUTBOL_5 = 'FUTBOL_5', 'Fútbol 5'
        FUTBOL_7 = 'FUTBOL_7', 'Fútbol 7'
        FUTBOL_11 = 'FUTBOL_11', 'Fútbol 11'
        PADDLE = 'PADDLE', 'Paddle'
        TENIS = 'TENIS', 'Tenis'

    class TipoSuperficie(models.TextChoices):
        CESPED_SINTETICO = 'CESPED_SINTETICO', 'Césped Sintético'
        CESPED_NATURAL = 'CESPED_NATURAL', 'Césped Natural'
        CEMENTO = 'CEMENTO', 'Cemento'
        POLVO_LADRILLO = 'POLVO_LADRILLO', 'Polvo de Ladrillo'

    numero = models.PositiveIntegerField(unique=True, verbose_name='Número de Cancha')
    tipo_cancha = models.CharField(
        max_length=20, choices=TipoCancha.choices,
        verbose_name='Tipo de Cancha',
    )
    superficie = models.CharField(
        max_length=20, choices=TipoSuperficie.choices,
        verbose_name='Tipo de Superficie',
    )
    capacidad = models.PositiveIntegerField(verbose_name='Capacidad')
    estado_disponibilidad = models.BooleanField(
        default=True, verbose_name='Disponible',
    )
    duracion_maxima_reserva = models.PositiveIntegerField(
        help_text='Duración máxima de reserva en minutos',
        verbose_name='Duración Máxima (min)',
    )
    precio_base_hora = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Precio Base por Hora ($)',
    )
    activa = models.BooleanField(default=True, verbose_name='Activa (baja lógica)')

    class Meta:
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'
        ordering = ['numero']

    def __str__(self):
        return f'Cancha #{self.numero} - {self.get_tipo_cancha_display()}'
