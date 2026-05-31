from django.db import models


class Competencia(models.Model):
    """
    Entidad que abarca Ligas y Torneos.
    Las competencias son de 8 o 16 equipos para garantizar brackets coherentes.
    """

    class TipoCompetencia(models.TextChoices):
        LIGA = 'LIGA', 'Liga'
        TORNEO = 'TORNEO', 'Torneo'
        COPA = 'COPA', 'Copa'

    class EstadoCompetencia(models.TextChoices):
        INSCRIPCION_ABIERTA = 'INSCRIPCION_ABIERTA', 'Inscripción Abierta'
        INSCRIPCION_CERRADA = 'INSCRIPCION_CERRADA', 'Inscripción Cerrada'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        FINALIZADA = 'FINALIZADA', 'Finalizada'

    class MaxEquipos(models.IntegerChoices):
        OCHO = 8, '8 equipos'
        DIECISEIS = 16, '16 equipos'

    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    tipo_competencia = models.CharField(
        max_length=20, choices=TipoCompetencia.choices,
        verbose_name='Tipo de Competencia',
    )
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    max_equipos = models.PositiveIntegerField(
        choices=MaxEquipos.choices,
        default=MaxEquipos.OCHO,
        verbose_name='Máximo de Equipos',
    )
    estado = models.CharField(
        max_length=25,
        choices=EstadoCompetencia.choices,
        default=EstadoCompetencia.INSCRIPCION_ABIERTA,
        verbose_name='Estado',
    )
    fecha_inicio = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha de Inicio',
    )
    fecha_fin = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha de Fin',
    )
    activa = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Competencia'
        verbose_name_plural = 'Competencias'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nombre} ({self.get_tipo_competencia_display()})'


class Equipo(models.Model):
    """
    Equipo permanente. El capitán es el usuario que lo crea y lo administra.
    Un equipo puede inscribirse a distintas competencias.
    """
    nombre = models.CharField(max_length=255, unique=True, verbose_name='Nombre del Equipo')
    capitan = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.CASCADE,
        related_name='equipos_como_capitan',
        verbose_name='Capitán',
    )
    jugadores = models.ManyToManyField(
        'authentication.Usuario',
        through='MiembroEquipo',
        related_name='equipos',
        blank=True,
        verbose_name='Jugadores',
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} (Capitán: {self.capitan.get_full_name()})'


class MiembroEquipo(models.Model):
    """
    Tabla intermedia M:N entre Equipo y Usuario.
    Representa la pertenencia de un jugador a un equipo.
    """
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='miembros',
        verbose_name='Equipo',
    )
    usuario = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.CASCADE,
        related_name='membresias',
        verbose_name='Usuario',
    )
    fecha_ingreso = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Ingreso')

    class Meta:
        verbose_name = 'Miembro de Equipo'
        verbose_name_plural = 'Miembros de Equipo'
        unique_together = ['equipo', 'usuario']

    def __str__(self):
        return f'{self.usuario.get_full_name()} → {self.equipo.nombre}'


class Reglamento(models.Model):
    """
    Reglamento específico de una competencia (1:1).
    """
    competencia = models.OneToOneField(
        Competencia,
        on_delete=models.CASCADE,
        related_name='reglamento',
        verbose_name='Competencia',
    )
    titulo = models.CharField(max_length=255, verbose_name='Título')
    contenido = models.TextField(verbose_name='Contenido')
    duracion_partido_min = models.PositiveIntegerField(
        default=60,
        verbose_name='Duración del Partido (min)',
    )
    jugadores_por_equipo = models.PositiveIntegerField(
        default=5,
        verbose_name='Jugadores por Equipo',
    )

    class Meta:
        verbose_name = 'Reglamento'
        verbose_name_plural = 'Reglamentos'

    def __str__(self):
        return f'Reglamento — {self.competencia.nombre}'


class Inscripcion(models.Model):
    """
    Inscripción de un Equipo a una Competencia.
    El capitán la crea (PENDIENTE), el admin la acepta o rechaza.
    """

    class EstadoInscripcion(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ACEPTADA = 'ACEPTADA', 'Aceptada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'

    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        verbose_name='Competencia',
    )
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='inscripciones',
        verbose_name='Equipo',
    )
    estado = models.CharField(
        max_length=10,
        choices=EstadoInscripcion.choices,
        default=EstadoInscripcion.PENDIENTE,
        verbose_name='Estado',
    )
    fecha_inscripcion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Inscripción')

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        unique_together = ['competencia', 'equipo']
        ordering = ['-fecha_inscripcion']

    def __str__(self):
        return f'{self.equipo.nombre} → {self.competencia.nombre} ({self.get_estado_display()})'


class Partido(models.Model):
    """
    Enfrentamiento entre dos equipos dentro de una competencia.
    Los partidos de rondas futuras se crean con equipos nulos (se definen
    al avanzar el ganador de la ronda anterior).
    """

    class Ronda(models.TextChoices):
        OCTAVOS = 'OCTAVOS', 'Octavos de Final'
        CUARTOS = 'CUARTOS', 'Cuartos de Final'
        SEMIFINAL = 'SEMIFINAL', 'Semifinal'
        FINAL = 'FINAL', 'Final'

    class EstadoPartido(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        FINALIZADO = 'FINALIZADO', 'Finalizado'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'

    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.CASCADE,
        related_name='partidos',
        verbose_name='Competencia',
    )
    equipo_local = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='partidos_como_local',
        verbose_name='Equipo Local',
    )
    equipo_visitante = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='partidos_como_visitante',
        verbose_name='Equipo Visitante',
    )
    cancha = models.ForeignKey(
        'fields.Cancha',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='partidos',
        verbose_name='Cancha',
    )
    fecha_hora = models.DateTimeField(
        null=True, blank=True, verbose_name='Fecha y Hora',
    )
    ronda = models.CharField(
        max_length=15, choices=Ronda.choices, verbose_name='Ronda',
    )
    numero_partido = models.PositiveIntegerField(verbose_name='Número de Partido')
    # Referencia al partido de la siguiente ronda (árbol del fixture)
    partido_siguiente = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='partidos_previos',
        verbose_name='Partido Siguiente (bracket)',
    )
    # Si el ganador va como local o visitante en el siguiente partido
    posicion_siguiente = models.CharField(
        max_length=10,
        choices=[('LOCAL', 'Local'), ('VISITANTE', 'Visitante')],
        null=True, blank=True,
        verbose_name='Posición en Partido Siguiente',
    )
    estado = models.CharField(
        max_length=10,
        choices=EstadoPartido.choices,
        default=EstadoPartido.PENDIENTE,
        verbose_name='Estado',
    )

    class Meta:
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'
        unique_together = ['competencia', 'ronda', 'numero_partido']
        ordering = ['ronda', 'numero_partido']

    def __str__(self):
        local = self.equipo_local.nombre if self.equipo_local else 'TBD'
        visitante = self.equipo_visitante.nombre if self.equipo_visitante else 'TBD'
        return f'[{self.get_ronda_display()}] {local} vs {visitante}'


class Resultado(models.Model):
    """
    Marcador final de un partido (1:1 con Partido).
    Al registrar, el sistema promueve automáticamente al ganador al siguiente partido del bracket.
    """
    partido = models.OneToOneField(
        Partido,
        on_delete=models.CASCADE,
        related_name='resultado',
        verbose_name='Partido',
    )
    goles_local = models.PositiveIntegerField(default=0, verbose_name='Goles Local')
    goles_visitante = models.PositiveIntegerField(default=0, verbose_name='Goles Visitante')
    equipo_ganador = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='partidos_ganados',
        verbose_name='Equipo Ganador',
    )
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')

    class Meta:
        verbose_name = 'Resultado'
        verbose_name_plural = 'Resultados'

    def __str__(self):
        return f'Resultado Partido #{self.partido_id}: {self.goles_local} - {self.goles_visitante}'
