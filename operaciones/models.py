from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from empresa.models import Personal, Empresa, Cliente
from inventarios.models import Producto
from catalogos.models import ZonaNotificacion

class CorteCaja(models.Model):
    ABIERTO = 1
    CERRADO = 2
    CANCELADO = 3

    ESTATUS_CHOICES = [
        (ABIERTO, 'Abierto'),
        (CERRADO, 'Cerrado'),
        (CANCELADO, 'Cancelado'),
    ]
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='cortes')
    personal = models.ForeignKey(Personal, on_delete=models.PROTECT, related_name='cortes')
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingresos_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_transferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_apertura = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    egresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    estatus = models.IntegerField(
        choices=ESTATUS_CHOICES,
        default=ABIERTO,
        help_text="Estado actual del corte de caja"
    )
    empresas_autorizadas = models.ManyToManyField(
        Empresa,
        through='CorteCajaEmpresa',
        related_name='cortes_autorizados'
    )

    class Meta:
        verbose_name = "Corte de Caja"
        verbose_name_plural = "Cortes de Caja"
        ordering = ['-fecha_apertura']

    def clean(self):
        if self.estatus == self.ABIERTO:
            qs = CorteCaja.objects.filter(estatus=self.ABIERTO, empresa=self.empresa)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Ya existe un corte de caja abierto para esta empresa.")

class CorteCajaEmpresa(models.Model):
    corte_caja = models.ForeignKey(CorteCaja, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('corte_caja', 'empresa')

class Ventas(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    corte_caja = models.ForeignKey(CorteCaja, on_delete=models.PROTECT, related_name='ventas')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)  # Para manejo lógico de borrado

    def __str__(self):
        return f"Venta #{self.id} - Cliente: {self.cliente.nombre} - Total: {self.total}"

"""
Registra las notificaciones generadas para cada producto vendido en las diferentes zonas de preparación.
Permite rastrear el estado de cada notificación (pendiente, entregada, cancelada) para una gestión eficiente
del proceso de cocción y despacho dentro de la orden.
"""
class NotificacionZona(models.Model):
    ESTADO_PENDIENTE = 1
    ESTADO_ENTREGADA = 2
    ESTADO_CANCELADA = 3

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_ENTREGADA, 'Entregada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE) 
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    zona = models.ForeignKey(ZonaNotificacion, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    creada_en = models.DateTimeField(auto_now_add=True)
    estado = models.IntegerField(choices=ESTADOS, default=ESTADO_PENDIENTE)

    class Meta:
        verbose_name = "Notificación en Zona"
        verbose_name_plural = "Notificaciones en Zonas"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en {self.zona.nombre} para orden {self.orden.id} - Estado: {self.get_estado_display()}"

