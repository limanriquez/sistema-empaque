from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


# Producto que se empaca, por ejemplo una caja de cierta presentación.
# Guarda el costo total de empacar una unidad y el precio que se cobra
# al cliente, que siempre debe ser mayor al costo. Cada producto tiene
# un BOM (ComponenteEmpaque) con los materiales que se descuentan por
# cada unidad empacada.
class ProductoEmpaque(models.Model):
    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    costo_empaque = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=0,
        help_text="Costo total de empacar una unidad.",
    )
    precio_cobro = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Precio que se cobra al cliente por cada unidad empacada.",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "operaciones_producto_empaque"
        verbose_name = "Producto de empaque"
        verbose_name_plural = "Productos de empaque"
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(costo_empaque__gte=0),
                name="ck_producto_costo_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(precio_cobro__gte=0),
                name="ck_producto_precio_no_negativo",
            ),
            # El precio de cobro debe superar el costo de empacar.
            models.CheckConstraint(
                condition=models.Q(precio_cobro__gt=models.F("costo_empaque")),
                name="ck_producto_precio_mayor_costo",
                violation_error_message=(
                    "El precio de cobro debe ser mayor al costo de empaque."
                ),
            ),
        ]

    def __str__(self):
        return self.nombre

    # Ganancia por unidad empacada: lo que se cobra menos lo que cuesta.
    @property
    def margen_unitario(self):
        return self.precio_cobro - self.costo_empaque


# BOM de un producto de empaque: cada fila es un material y la
# cantidad que se descuenta por cada unidad empacada. No mueve
# inventario: lo ejecuta el servicio de empaque.
class ComponenteEmpaque(models.Model):
    id = models.BigAutoField(primary_key=True)
    producto_empaque = models.ForeignKey(
        ProductoEmpaque,
        on_delete=models.CASCADE,
        related_name="componentes",
    )
    material = models.ForeignKey(
        "inventarios.Material",
        on_delete=models.PROTECT,
        related_name="usos_en_empaques",
    )
    cantidad_material = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        help_text="Cantidad de este material por cada unidad empacada.",
    )

    class Meta:
        db_table = "operaciones_componente_empaque"
        verbose_name = "Material del empaque"
        verbose_name_plural = "Materiales del empaque"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["producto_empaque", "material"],
                name="uq_componente_producto_material",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad_material__gt=0),
                name="ck_componente_cantidad_positiva",
            ),
        ]

    def __str__(self):
        return f"{self.material} x {self.cantidad_material}"

    # Si la unidad del material no admite decimales, la cantidad por
    # unidad empacada debe ser entera, así el total nunca sale
    # fraccionario.
    def clean(self):
        super().clean()

        if self.material_id and self.cantidad_material is not None:
            unidad = self.material.unidad_medida

            if (
                not unidad.permite_decimales
                and self.cantidad_material % 1 != Decimal("0")
            ):
                raise ValidationError(
                    {
                        "cantidad_material": (
                            f"La unidad «{unidad.nombre}» solo admite "
                            f"cantidades enteras."
                        )
                    }
                )


# Relaciona los clientes con los productos de empaque que tienen
# autorizados. Permite determinar qué presentaciones puede seleccionar
# cada cliente al iniciar un lote de empaque.
class ClienteProductoEmpaque(models.Model):
    id = models.BigAutoField(primary_key=True)

    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="productos_empaque",
    )
    producto_empaque = models.ForeignKey(
        "ProductoEmpaque",
        on_delete=models.PROTECT,
        related_name="autorizaciones_cliente",
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "operaciones_cliente_producto_empaque"
        verbose_name = "Producto de empaque por cliente"
        verbose_name_plural = "Productos de empaque por cliente"
        ordering = ["cliente", "producto_empaque"]
        constraints = [
            models.UniqueConstraint(
                fields=["cliente", "producto_empaque"],
                name="uq_cliente_producto_empaque",
            ),
        ]

    def __str__(self):
        return f"{self.cliente} - {self.producto_empaque}"