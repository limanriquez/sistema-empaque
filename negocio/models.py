
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

# ============================================================
# MODELO: OperacionComercial
# ============================================================
# Representa la operación comercial mediante la cual se
# negocia la venta o comercialización de producto terminado.
#
# La operación concentra:
# - El cliente con quien se realiza la negociación.
# - El usuario y fecha de apertura.
# - El estado de la operación.
# - Los importes totales de la negociación.
# - El usuario y fecha de cierre.
#
# Una operación puede integrar tarimas de diferentes lotes
# de empaque y propietarios.
#
# También puede contener conceptos comerciales sin necesidad
# de integrar tarimas.
#
# Las relaciones con tarimas y detalles comerciales se
# definirán mediante sus respectivos modelos.
#
# Una vez cerrada, la operación no debe modificarse mediante
# el flujo ordinario del sistema.
# ============================================================

class OperacionComercial(models.Model):

    # Estados posibles de la operación comercial.
    class Estatus(models.IntegerChoices):
        ABIERTA = 1, "Abierta"
        CERRADA = 2, "Cerrada"
        CANCELADA = 3, "Cancelada"

    # Identificador principal de la operación.
    id = models.BigAutoField(
        primary_key=True
    )

    # Cliente con quien se realiza la negociación.
    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="operaciones_comerciales",
        verbose_name="Cliente"
    )

    # Fecha y hora en que se inicia la operación comercial.
    fecha_apertura = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de apertura"
    )

    # Usuario responsable de abrir la operación.
    usuario_apertura = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="operaciones_comerciales_abiertas",
        verbose_name="Usuario de apertura"
    )

    # Estado actual de la operación comercial.
    estatus = models.IntegerField(
        choices=Estatus.choices,
        default=Estatus.ABIERTA,
        verbose_name="Estatus"
    )

    # Importe total de los conceptos antes de impuestos.
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal"
    )

    # Importe total de impuestos de la operación.
    iva = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="IVA"
    )

    # Importe total de la operación comercial, incluyendo IVA.
    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Total"
    )

    # Fecha y hora en que se cierra la operación.
    # Permanece nula mientras la operación esté abierta.
    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de cierre"
    )

    # Usuario responsable de cerrar la operación.
    # Permanece nulo mientras no exista un cierre.
    usuario_cierre = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="operaciones_comerciales_cerradas",
        verbose_name="Usuario de cierre"
    )

    # Observaciones generales de la negociación.
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    # Configuración administrativa del modelo.
    class Meta:
        verbose_name = "Operación comercial"
        verbose_name_plural = "Operaciones comerciales"
        ordering = ["-fecha_apertura"]

    # Representación del registro en Django Admin.
    def __str__(self):
        return f"Operación comercial {self.pk}"


# Catálogo de productos, servicios y otros conceptos que
# pueden integrarse en las operaciones comerciales.
# El precio sugerido es una referencia; el precio definitivo
# se establece en cada operación comercial.
class ConceptoComercial(models.Model):

    class Tipo(models.IntegerChoices):
        PRODUCTO = 1, "Producto"
        SERVICIO = 2, "Servicio"
        OTRO = 3, "Otro"

    # Identificador principal.
    id = models.BigAutoField(
        primary_key=True
    )

    # Nombre del concepto comercial.
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre"
    )

    # Tipo de concepto comercial.
    tipo = models.IntegerField(
        choices=Tipo.choices,
        default=Tipo.PRODUCTO,
        verbose_name="Tipo"
    )

    # Descripción adicional del concepto.
    descripcion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción"
    )

    # Precio sugerido como referencia comercial.
    precio_sugerido = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=0,
        verbose_name="Precio sugerido"
    )

    # Indica si el concepto está disponible.
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        verbose_name = "Concepto comercial"
        verbose_name_plural = "Conceptos comerciales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

# Relaciona clientes con conceptos comerciales para establecer
# precios particulares según las condiciones negociadas.
class PrecioCliente(models.Model):

    # Identificador principal.
    id = models.BigAutoField(
        primary_key=True
    )

    # Cliente al que corresponde el precio negociado.
    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="precios_comerciales",
        verbose_name="Cliente"
    )

    # Concepto comercial al que corresponde el precio.
    concepto = models.ForeignKey(
        "negocio.ConceptoComercial",
        on_delete=models.PROTECT,
        related_name="precios_clientes",
        verbose_name="Concepto comercial"
    )

    # Precio particular acordado con el cliente.
    precio = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )

    class Meta:
        verbose_name = "Precio por cliente"
        verbose_name_plural = "Precios por cliente"
        ordering = ["cliente", "concepto"]
        constraints = [
            models.UniqueConstraint(
                fields=["cliente", "concepto"],
                name="uq_precio_cliente_concepto"
            )
        ]

    def __str__(self):
        return f"{self.cliente} - {self.concepto}: {self.precio}"
