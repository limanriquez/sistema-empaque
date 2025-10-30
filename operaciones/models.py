from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from empresa.models import Personal, Empresa, Cliente
from inventarios.models import Producto, ProductoZonaNotificacion, BOM
from catalogos.models import ZonaNotificacion, LugarEntrega, MetodoPago

from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from django.dispatch import receiver
from django.db.models import Sum

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
    otros_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    cambio = models.DecimalField(max_digits=12, decimal_places=2)
    lugar_entrega = models.ForeignKey(LugarEntrega, on_delete=models.PROTECT, related_name='ventas',null=True,blank=True)
    atencion = models.ForeignKey(Personal, on_delete=models.PROTECT, related_name='ventas_atendidas') #Mesero que levanta la comanda
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)  # Para manejo lógico de borrado
    pagada = models.BooleanField(default=False)  
    abonada = models.BooleanField(default=False) 

    def __str__(self):
        return f"Venta #{self.id} - Cliente: {self.cliente.nombre} - Total: {self.total}"

class DesgloseVenta(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name='desglose')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='ventas_detalle')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)  # Se guarda explícitamente
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='desglose_venta')
    observaciones = models.TextField(blank=True, null=True)


    class Meta:
        verbose_name = 'Desglose de Venta'
        verbose_name_plural = 'Desgloses de Ventas'

    def __str__(self):
        return f"{self.producto.nombre} - ${self.total:.2f} (Venta #{self.venta_id})"

"""
Registra las notificaciones generadas para cada producto vendido en las diferentes zonas de preparación.
Permite rastrear el estado de cada notificación (pendiente, entregada, cancelada) para una gestión eficiente
del proceso de cocción y despacho dentro de la orden.
"""
class NotificacionZona(models.Model):
    ESTADO_PENDIENTE = 1
    ESTADO_PROCESO = 2
    ESTADO_ENTREGADA = 3
    ESTADO_CANCELADA = 4

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_PROCESO, 'Proceso'),
        (ESTADO_ENTREGADA, 'Entregada'),
        (ESTADO_CANCELADA, 'Cancelada'),
    ]

    desglose_venta = models.OneToOneField(
        DesgloseVenta, 
        on_delete=models.CASCADE, 
        related_name='notificacion_zona'
    )
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

class PagoVenta(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.PROTECT, related_name='pagos')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    referencia = models.CharField(max_length=100, blank=True, null=True)  # Opcional, útil para tarjeta o transferencia
    fecha_pago = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)  # Lógica de anulación o activación
    
    class Meta:
        verbose_name = "Pago de Venta"
        verbose_name_plural = "Pagos de Venta"
        ordering = ['fecha_pago']

    def __str__(self):
        return f"{self.metodo_pago.nombre} - ${self.monto} (Venta #{self.venta_id})"


@receiver(post_save, sender=PagoVenta)
def actualizar_venta_post_pago(sender, instance, created, **kwargs):
    if created and instance.activo:
        venta = instance.venta

        # Recalcular total real de la venta a partir de los desgloses
        total_desglose = venta.desglose.aggregate(total=Sum('total'))['total'] or 0
        venta.total = total_desglose

        # Marcar abonada si se creó cualquier pago activo
        venta.abonada = True

        # Marcar pagada si la suma de pagos activos >= total de la venta
        total_pagos = venta.pagos.filter(activo=True).aggregate(total=Sum('monto'))['total'] or 0
        venta.pagada = total_pagos >= venta.total

        venta.save(update_fields=['total', 'abonada', 'pagada'])
    
@receiver(post_delete, sender=PagoVenta)
def actualizar_venta_post_eliminar_pago(sender, instance, **kwargs):
    venta = instance.venta

    # Total real de la venta a partir de sus desgloses
    total_venta = venta.desglose.aggregate(total=Sum('total'))['total'] or 0

    # Suma de pagos activos restantes
    total_pagos = venta.pagos.filter(activo=True).aggregate(total=Sum('monto'))['total'] or 0

    # Si ya no hay pagos activos, abonada = False
    venta.abonada = total_pagos > 0

    # Si la suma de pagos < total de la venta, pagada = False
    venta.pagada = total_pagos >= total_venta

    venta.save(update_fields=['abonada', 'pagada'])


@receiver(post_save, sender=DesgloseVenta)
def crear_notificacion_zona(sender, instance, created, **kwargs):
    if not created:
        return  # Solo al crear un desglose

    producto = instance.producto

    # Obtenemos la zona activa del producto (asumimos 1 sola)
    try:
        zona_config = ProductoZonaNotificacion.objects.get(producto=producto, activo=True)
    except ProductoZonaNotificacion.DoesNotExist:
        # Si no hay zona configurada, no hacemos nada
        return

    # Opcional: generar notificaciones para cada componente del BOM
   # bom_items = BOM.objects.filter(producto=producto)
   # for item in bom_items:
    NotificacionZona.objects.create(
        desglose_venta=instance,
        zona=zona_config.zona,
        producto=producto,
        cantidad=1,  # Escalar según BOM
        estado=NotificacionZona.ESTADO_PENDIENTE
    )


class Egreso(models.Model):
    corte_caja = models.ForeignKey(
        'CorteCaja',
        on_delete=models.CASCADE,
        related_name='detalle_egresos'
    )
    personal = models.ForeignKey(Personal, on_delete=models.PROTECT, related_name='egresos')
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Egreso #{self.id} - ${self.monto:.2f}"

class Ingreso(models.Model):
    corte_caja = models.ForeignKey(
        'CorteCaja',
        on_delete=models.CASCADE,
        related_name='detalle_ingresos'
    )
    personal = models.ForeignKey(Personal, on_delete=models.PROTECT, related_name='ingresos')
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Ingreso #{self.id} - ${self.monto:.2f}"