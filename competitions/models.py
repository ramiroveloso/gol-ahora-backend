from django.db import models


class Competencia(models.Model):
    """
    Entidad genérica que abarca Ligas y Torneos.
    Sin API por ahora — modelos listos para cuando se necesite.
    """

    class TipoCompetencia(models.TextChoices):
        LIGA = 'LIGA', 'Liga'
        TORNEO = 'TORNEO', 'Torneo'
        COPA = 'COPA', 'Copa'

    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    tipo_competencia = models.CharField(
        max_length=20, choices=TipoCompetencia.choices,
        verbose_name='Tipo de Competencia',
    )
    fixture = models.JSONField(
        default=dict, blank=True,
        verbose_name='Fixture',
        help_text='Objeto JSON flexible con la estructura del fixture',
    )
    participantes = models.ManyToManyField(
        'authentication.Usuario', related_name='competencias',
        blank=True, verbose_name='Participantes',
    )
    activa = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Competencia'
        verbose_name_plural = 'Competencias'

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_competencia_display()})'
