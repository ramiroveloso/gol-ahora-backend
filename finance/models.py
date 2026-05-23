from django.db import models


class Descuento(models.Model):
    """Descuento aplicable a un cobro."""

    class TipoDescuento(models.TextChoices):
        PORCENTAJE = 'PORCENTAJE', 'Porcentaje'
        MONTO_FIJO = 'MONTO_FIJO', 'Monto Fijo'

    tipo_descuento = models.CharField(
        max_length=20, choices=TipoDescuento.choices,
        verbose_name='Tipo de Descuento',
    )
    porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Valor (% o $)',
    )
    descripcion = models.CharField(
        max_length=255, blank=True,
        verbose_name='Descripción',
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Descuento'
        verbose_name_plural = 'Descuentos'

    def __str__(self):
        if self.tipo_descuento == self.TipoDescuento.PORCENTAJE:
            return f'{self.porcentaje}% - {self.descripcion}'
        return f'${self.porcentaje} - {self.descripcion}'


class Cobro(models.Model):
    """
    Cobro genérico: puede originarse de una reserva, clase, competencia, etc.
    Se vincula al servicio correspondiente mediante FKs nullables.
    """

    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        TARJETA_DEBITO = 'TARJETA_DEBITO', 'Tarjeta de Débito'
        TARJETA_CREDITO = 'TARJETA_CREDITO', 'Tarjeta de Crédito'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
        MERCADO_PAGO = 'MERCADO_PAGO', 'Mercado Pago'

    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADO = 'APROBADO', 'Aprobado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'

    class TipoServicio(models.TextChoices):
        RESERVA = 'RESERVA', 'Reserva de Cancha'
        CLASE = 'CLASE', 'Clase/Entrenamiento'
        COMPETENCIA = 'COMPETENCIA', 'Inscripción a Competencia'
        OTRO = 'OTRO', 'Otro'

    usuario = models.ForeignKey(
        'authentication.Usuario', on_delete=models.CASCADE,
        related_name='cobros', verbose_name='Usuario',
    )
    tipo_servicio = models.CharField(
        max_length=20, choices=TipoServicio.choices,
        verbose_name='Tipo de Servicio',
    )
    # FKs nullables — solo una se usa según tipo_servicio
    reserva = models.ForeignKey(
        'bookings.Reserva', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cobros',
        verbose_name='Reserva',
    )
    clase = models.ForeignKey(
        'bookings.ClaseEntrenamiento', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cobros',
        verbose_name='Clase',
    )
    competencia = models.ForeignKey(
        'competitions.Competencia', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cobros',
        verbose_name='Competencia',
    )
    descuento = models.ForeignKey(
        Descuento, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='cobros',
        verbose_name='Descuento',
    )
    monto = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Monto ($)',
    )
    fecha_cobro = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de Cobro',
    )
    metodo_pago = models.CharField(
        max_length=20, choices=MetodoPago.choices,
        verbose_name='Método de Pago',
    )
    estado_pago = models.CharField(
        max_length=20, choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE, verbose_name='Estado del Pago',
    )

    class Meta:
        verbose_name = 'Cobro'
        verbose_name_plural = 'Cobros'
        ordering = ['-fecha_cobro']

    def __str__(self):
        return f'Cobro #{self.pk} - {self.usuario} - ${self.monto} ({self.get_estado_pago_display()})'


class ReciboPago(models.Model):
    """Recibo generado automáticamente al aprobar un cobro."""

    cobro = models.OneToOneField(
        Cobro, on_delete=models.CASCADE,
        related_name='recibo', verbose_name='Cobro',
    )
    detalle = models.TextField(verbose_name='Detalle')
    fecha_emision = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de Emisión',
    )

    class Meta:
        verbose_name = 'Recibo de Pago'
        verbose_name_plural = 'Recibos de Pago'

    def __str__(self):
        return f'Recibo #{self.pk} - Cobro #{self.cobro_id}'
