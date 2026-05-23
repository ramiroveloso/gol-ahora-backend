# pyrefly: ignore [missing-import]
from rest_framework import viewsets
from .models import Descuento, Cobro, ReciboPago
from .serializers import DescuentoSerializer, CobroSerializer, ReciboPagoSerializer


class DescuentoViewSet(viewsets.ModelViewSet):
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer


class CobroViewSet(viewsets.ModelViewSet):
    """
    CRUD de Cobros.
    Genera automáticamente un ReciboPago si el estado cambia a APROBADO.
    """
    queryset = Cobro.objects.all()
    serializer_class = CobroSerializer

    def perform_update(self, serializer):
        cobro = serializer.instance
        old_estado = cobro.estado_pago
        
        updated_cobro = serializer.save()

        # Generación automática de ReciboPago (RF-BACK-017)
        if old_estado != Cobro.EstadoPago.APROBADO and updated_cobro.estado_pago == Cobro.EstadoPago.APROBADO:
            if not hasattr(updated_cobro, 'recibo'):
                ReciboPago.objects.create(
                    cobro=updated_cobro,
                    detalle=f"Recibo por {updated_cobro.get_tipo_servicio_display()}"
                )


class ReciboPagoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vista de solo lectura para los recibos (RF-BACK-017).
    """
    queryset = ReciboPago.objects.all()
    serializer_class = ReciboPagoSerializer
