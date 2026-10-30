
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


# Registra los materiales adquiridos para las operaciones de empaque,
# como cajas, bolsas y etiquetas. Todos son consumibles: se descuentan
# al empacar y no regresan al inventario.
# Mantiene sus datos generales y la existencia total consolidada.
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
                condition=Q(stock_minimo__gte=0),
                name="ck_material_stock_minimo_no_negativo",
            ),
            models.CheckConstraint(
                condition=Q(existencia__gte=0),
                name="ck_material_existencia_no_negativa",
            ),
        ]

    def __str__(self):
        return self.nombre


# Excepción para proteger el historial de movimientos.
class MovimientoInmutable(PermissionDenied):
    """Se intentó modificar o eliminar un movimiento registrado."""


# Registra cada cambio de existencia de un material: compras, consumos,
# mermas, ajustes y traslados entre secciones o propietarios.
# Es un libro histórico: los movimientos no se editan ni se eliminan.
# La cantidad siempre es positiva; el efecto lo determinan el tipo,
# las ubicaciones y los propietarios.
class MovimientoInventario(models.Model):

    class Tipo(models.TextChoices):
        COMPRA = "COMPRA", "Entrada por compra"
        CONSUMO = "CONSUMO", "Salida por consumo"
        MERMA = "MERMA", "Merma"
        AJUSTE_ENTRADA = "AJUSTE_ENTRADA", "Ajuste positivo"
        AJUSTE_SALIDA = "AJUSTE_SALIDA", "Ajuste negativo"
        TRASLADO = "TRASLADO", "Traslado"

    # Tipos que suman, restan o mueven existencia.
    TIPOS_ENTRADA = (
        Tipo.COMPRA,
        Tipo.AJUSTE_ENTRADA,
    )

    TIPOS_SALIDA = (
        Tipo.CONSUMO,
        Tipo.MERMA,
        Tipo.AJUSTE_SALIDA,
    )

    TIPOS_QUE_EXIGEN_DESCRIPCION = (
        Tipo.MERMA,
        Tipo.AJUSTE_ENTRADA,
        Tipo.AJUSTE_SALIDA,
    )

    id = models.BigAutoField(primary_key=True)

    material = models.ForeignKey(
        "Material",
        on_delete=models.PROTECT,
        related_name="movimientos",
    )

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
    )

    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=3,
    )

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

    # Propietario del material que sale.
    # Es obligatorio para salidas y traslados.
    propietario_origen = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario_origen",
        null=True,
        blank=True,
    )

    # Propietario del material que ingresa.
    # Es obligatorio para entradas y traslados.
    propietario_destino = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="movimientos_inventario_destino",
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

    # Fecha real del movimiento o de la adquisición.
    fecha = models.DateField(default=timezone.localdate)

    # Cuándo y quién registró el movimiento.
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
            models.Index(fields=["propietario_origen", "fecha"]),
            models.Index(fields=["propietario_destino", "fecha"]),
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad__gt=0),
                name="ck_movimiento_cantidad_positiva",
            ),

            # Entradas: requieren propietario destino.
            models.CheckConstraint(
                condition=(
                    Q(
                        tipo__in=["COMPRA", "AJUSTE_ENTRADA"],
                        ubicacion_origen__isnull=True,
                        ubicacion_destino__isnull=False,
                        propietario_origen__isnull=True,
                        propietario_destino__isnull=False,
                    )

                    # Salidas: requieren propietario origen.
                    | Q(
                        tipo__in=[
                            "CONSUMO",
                            "MERMA",
                            "AJUSTE_SALIDA",
                        ],
                        ubicacion_origen__isnull=False,
                        ubicacion_destino__isnull=True,
                        propietario_origen__isnull=False,
                        propietario_destino__isnull=True,
                    )

                    # Traslados: requieren ambos propietarios.
                    # Deben cambiar ubicación o propietario.
                    | (
                        Q(
                            tipo="TRASLADO",
                            ubicacion_origen__isnull=False,
                            ubicacion_destino__isnull=False,
                            propietario_origen__isnull=False,
                            propietario_destino__isnull=False,
                        )
                        & (
                            ~Q(
                                ubicacion_origen=F("ubicacion_destino")
                            )
                            | ~Q(
                                propietario_origen=F(
                                    "propietario_destino"
                                )
                            )
                        )
                    )
                ),
                name="ck_movimiento_ubicaciones_propietarios",
            ),

            # Proveedor y costo solo existen en compras.
            models.CheckConstraint(
                condition=(
                    Q(tipo="COMPRA")
                    | Q(
                        proveedor__isnull=True,
                        costo_unitario__isnull=True,
                    )
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
                    ~Q(
                        tipo__in=[
                            "MERMA",
                            "AJUSTE_ENTRADA",
                            "AJUSTE_SALIDA",
                        ]
                    )
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

    # Costo total de la compra; None si no tiene costo.
    @property
    def costo_total(self):
        if self.costo_unitario is None or self.cantidad is None:
            return None

        return (self.cantidad * self.costo_unitario).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    # Mensajes claros antes de llegar a la base de datos.
    def clean(self):
        super().clean()

        errores = {}

        if (
            self.tipo in self.TIPOS_QUE_EXIGEN_DESCRIPCION
            and not (self.descripcion or "").strip()
        ):
            errores["descripcion"] = (
                "Explique el motivo de este movimiento."
            )

        # Entradas.
        if self.tipo in self.TIPOS_ENTRADA:

            if self.ubicacion_origen_id is not None:
                errores["ubicacion_origen"] = (
                    "Una entrada no lleva ubicación de origen."
                )

            if self.ubicacion_destino_id is None:
                errores["ubicacion_destino"] = (
                    "Indique dónde ingresa el material."
                )

            if self.propietario_origen_id is not None:
                errores["propietario_origen"] = (
                    "Una entrada no lleva propietario de origen."
                )

            if self.propietario_destino_id is None:
                errores["propietario_destino"] = (
                    "Seleccione el propietario del material."
                )

        # Salidas.
        elif self.tipo in self.TIPOS_SALIDA:

            if self.ubicacion_origen_id is None:
                errores["ubicacion_origen"] = (
                    "Indique de dónde sale el material."
                )

            if self.ubicacion_destino_id is not None:
                errores["ubicacion_destino"] = (
                    "Una salida no lleva ubicación de destino."
                )

            if self.propietario_origen_id is None:
                errores["propietario_origen"] = (
                    "Seleccione el propietario del material."
                )

            if self.propietario_destino_id is not None:
                errores["propietario_destino"] = (
                    "Una salida no lleva propietario de destino."
                )

        # Traslados.
        elif self.tipo == self.Tipo.TRASLADO:

            if self.ubicacion_origen_id is None:
                errores["ubicacion_origen"] = (
                    "Indique la ubicación de origen."
                )

            if self.ubicacion_destino_id is None:
                errores["ubicacion_destino"] = (
                    "Indique la ubicación de destino."
                )

            if self.propietario_origen_id is None:
                errores["propietario_origen"] = (
                    "Seleccione el propietario de origen."
                )

            if self.propietario_destino_id is None:
                errores["propietario_destino"] = (
                    "Seleccione el propietario de destino."
                )

            # El traslado debe cambiar ubicación o propietario.
            if (
                self.ubicacion_origen_id is not None
                and self.ubicacion_destino_id is not None
                and self.ubicacion_origen_id == self.ubicacion_destino_id
                and self.propietario_origen_id == self.propietario_destino_id
            ):
                errores["__all__"] = (
                    "El traslado debe cambiar la ubicación "
                    "o el propietario."
                )

        # Proveedor y costo solo en compras.
        if self.tipo != self.Tipo.COMPRA:

            if self.proveedor_id is not None:
                errores["proveedor"] = (
                    "Solo las compras llevan proveedor."
                )

            if self.costo_unitario is not None:
                errores["costo_unitario"] = (
                    "Solo las compras llevan costo unitario."
                )

        # Si la unidad no admite decimales, la cantidad debe ser entera.
        if self.material_id and self.cantidad is not None:

            unidad = self.material.unidad_medida

            if (
                not unidad.permite_decimales
                and self.cantidad % 1 != Decimal("0")
            ):
                errores["cantidad"] = (
                    f"La unidad «{unidad.nombre}» solo admite "
                    "cantidades enteras."
                )

        if errores:
            raise ValidationError(errores)

    # El libro es inmutable: se valida antes de guardar.
    def save(self, *args, **kwargs):

        if not self._state.adding:
            raise MovimientoInmutable(
                "Los movimientos de inventario no se pueden modificar."
            )

        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise MovimientoInmutable(
            "Los movimientos de inventario no se pueden eliminar."
        )


# Registra el saldo de un material en una sección de almacén,
# diferenciando al propietario del inventario.
# Todo registro de existencia debe tener un cliente propietario.
# Los saldos se actualizan mediante movimientos y pueden ser negativos.
class ExistenciaMaterial(models.Model):

    id = models.BigAutoField(primary_key=True)

    material = models.ForeignKey(
        "Material",
        on_delete=models.PROTECT,
        related_name="existencias",
    )

    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="existencias_material",
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

    stock_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=0,
    )

    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventarios_existencia"
        verbose_name = "Existencia de material"
        verbose_name_plural = "Existencias de materiales"
        ordering = ["material__nombre", "seccion"]

        constraints = [
            models.UniqueConstraint(
                fields=["material", "seccion", "cliente"],
                name="uq_existencia_material_seccion_cliente",
            ),
            models.CheckConstraint(
                condition=Q(stock_minimo__gte=0),
                name="ck_existencia_stock_minimo_no_negativo",
            ),
        ]

    def __str__(self):
        return (
            f"{self.material} - {self.cliente} "
            f"en {self.seccion}: {self.cantidad}"
        )
