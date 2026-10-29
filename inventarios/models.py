from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

# Registra los materiales adquiridos para las operaciones de empaque,
# como cajas, bolsas, películas, etiquetas o cintas. Todos son
# consumibles: se descuentan al empacar y no regresan al inventario.
# Mantiene sus datos generales y la existencia total consolidada
# de sus ubicaciones.
class Material(models.Model):
    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    unidad_medida = models.ForeignKey(
        "catalogos.UnidadMedida",
        on_delete=models.PROTECT,
        related_name="materiales",
    )
    existencia = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
        editable=False,
        help_text=(
            "Suma de las existencias por ubicación. "
            "La actualizan los movimientos de inventario."
        ),
    )
    stock_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "inventarios_material"
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(stock_minimo__gte=0),
                name="ck_material_stock_minimo_no_negativo",
            ),
            models.CheckConstraint(
                condition=models.Q(existencia__gte=0),
                name="ck_material_existencia_no_negativa",
            ),
        ]

    def __str__(self):
        return self.nombre



# Registra cada cambio de existencia de un material: compras, consumos
# por empaque, mermas, ajustes y traslados entre secciones. Es un libro
# histórico: los movimientos no se editan ni se eliminan; un error se
# corrige con otro movimiento. La cantidad siempre es positiva; el
# efecto lo determinan el tipo y las ubicaciones de origen y destino.
class MovimientoInventario(models.Model):

    class Tipo(models.TextChoices):
        COMPRA = "COMPRA", "Entrada por compra"
        CONSUMO = "CONSUMO", "Salida por consumo"
        MERMA = "MERMA", "Merma"
        AJUSTE_ENTRADA = "AJUSTE_ENTRADA", "Ajuste positivo"
        AJUSTE_SALIDA = "AJUSTE_SALIDA", "Ajuste negativo"
        TRASLADO = "TRASLADO", "Traslado entre ubicaciones"

    # Tipos que suman, restan o mueven existencia. Los usarán los
    # servicios que actualicen el saldo por ubicación.
    TIPOS_ENTRADA = (Tipo.COMPRA, Tipo.AJUSTE_ENTRADA)
    TIPOS_SALIDA = (Tipo.CONSUMO, Tipo.MERMA, Tipo.AJUSTE_SALIDA)
    TIPOS_QUE_EXIGEN_DESCRIPCION = (
        Tipo.MERMA, Tipo.AJUSTE_ENTRADA, Tipo.AJUSTE_SALIDA,
    )

    id = models.BigAutoField(primary_key=True)

    material = models.ForeignKey(
        "Material",
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)

    ubicacion_origen = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="movimientos_origen",
        null=True,
        blank=True,
    )
    ubicacion_destino = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="movimientos_destino",
        null=True,
        blank=True,
    )

    # Solo en compras.
    proveedor = models.ForeignKey(
        "personas.Proveedor",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario",
        null=True,
        blank=True,
    )
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
    )
    documento = models.CharField(
        max_length=50,
        blank=True,
        help_text="Factura, remisión o folio que respalda el movimiento.",
    )

    descripcion = models.TextField(blank=True)

    # Fecha real del movimiento o de la adquisición (editable).
    fecha = models.DateField(default=timezone.localdate)
    # Cuándo y quién lo registró en el sistema (no editables).
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
    )

    class Meta:
        db_table = "inventarios_movimiento"
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["material", "fecha"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name="ck_movimiento_cantidad_positiva",
            ),
            # Ubicaciones coherentes con el tipo de movimiento.
            models.CheckConstraint(
                condition=(
                    Q(
                        tipo__in=["COMPRA", "AJUSTE_ENTRADA"],
                        ubicacion_origen__isnull=True,
                        ubicacion_destino__isnull=False,
                    )
                    | Q(
                        tipo__in=["CONSUMO", "MERMA", "AJUSTE_SALIDA"],
                        ubicacion_origen__isnull=False,
                        ubicacion_destino__isnull=True,
                    )
                    | (
                        Q(
                            tipo="TRASLADO",
                            ubicacion_origen__isnull=False,
                            ubicacion_destino__isnull=False,
                        )
                        & ~Q(ubicacion_origen=F("ubicacion_destino"))
                    )
                ),
                name="ck_movimiento_ubicaciones_segun_tipo",
            ),
            # Proveedor y costo solo existen en compras.
            models.CheckConstraint(
                condition=(
                    Q(tipo="COMPRA")
                    | Q(proveedor__isnull=True, costo_unitario__isnull=True)
                ),
                name="ck_movimiento_costo_solo_compra",
            ),
            models.CheckConstraint(
                condition=(
                    Q(costo_unitario__isnull=True)
                    | Q(costo_unitario__gte=0)
                ),
                name="ck_movimiento_costo_no_negativo",
            ),
            # Mermas y ajustes deben explicarse.
            models.CheckConstraint(
                condition=(
                    ~Q(tipo__in=["MERMA", "AJUSTE_ENTRADA", "AJUSTE_SALIDA"])
                    | ~Q(descripcion="")
                ),
                name="ck_movimiento_descripcion_en_ajustes",
            ),
        ]

    def __str__(self):
        return (
            f"{self.material.nombre} - "
            f"{self.get_tipo_display()} - {self.cantidad}"
        )

    # Costo total de la compra; None si el movimiento no tiene costo.
    @property
    def costo_total(self):
        if self.costo_unitario is None:
            return None

        return (self.cantidad * self.costo_unitario).quantize(
            Decimal("0.01")
        )

    # Mensajes claros antes de llegar a la base de datos.
    def clean(self):
        super().clean()

        if (
            self.tipo in self.TIPOS_QUE_EXIGEN_DESCRIPCION
            and not (self.descripcion or "").strip()
        ):
            raise ValidationError(
                {"descripcion": "Explique el motivo de este movimiento."}
            )

        # Si la unidad del material no admite decimales, la cantidad
        # debe ser entera.
        if self.material_id and self.cantidad is not None:
            unidad = self.material.unidad_medida

            if (
                not unidad.permite_decimales
                and self.cantidad % 1 != Decimal("0")
            ):
                raise ValidationError(
                    {
                        "cantidad": (
                            f"La unidad «{unidad.nombre}» solo admite "
                            f"cantidades enteras."
                        )
                    }
                )

    # El libro es inmutable: un movimiento ya guardado no se modifica
    # ni se elimina; se corrige con otro movimiento.
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                "Los movimientos de inventario no se pueden modificar."
            )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Los movimientos de inventario no se pueden eliminar."
        )


# Saldo actual de un material en una sección de almacén. Una fila por
# material y sección. No se captura a mano: lo actualizan los
# movimientos de inventario. El almacén y el espacio se obtienen
# desde la sección.
class ExistenciaMaterial(models.Model):
    id = models.BigAutoField(primary_key=True)
    material = models.ForeignKey(
        "Material",
        on_delete=models.PROTECT,
        related_name="existencias",
    )
    seccion = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="existencias_material",
    )
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
        editable=False,
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventarios_existencia"
        verbose_name = "Existencia de material"
        verbose_name_plural = "Existencias de materiales"
        ordering = ["material__nombre", "seccion"]
        constraints = [
            models.UniqueConstraint(
                fields=["material", "seccion"],
                name="uq_existencia_material_seccion",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad__gte=0),
                name="ck_existencia_cantidad_no_negativa",
            ),
        ]

    def __str__(self):
        return f"{self.material} en {self.seccion}: {self.cantidad}"