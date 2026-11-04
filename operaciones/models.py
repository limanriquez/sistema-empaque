from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from django.db.models import Q, F
from django.utils import timezone

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


# ==========================================================
# MODELO: OPERACIÓN DIARIA
#
# Representa el expediente general de una jornada de trabajo
# dentro de la empacadora.
#
# Controla la apertura y cierre de la operación. La
# información específica de personal, estaciones, lotes
# y producción se administra mediante modelos relacionados.
# ==========================================================

class OperacionDiaria(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    fecha = models.DateField(
        default=timezone.localdate,
        verbose_name="Fecha operativa",
    )

    abierta = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="Abierta",
    )

    hora_apertura = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Hora de apertura",
    )

    hora_cierre = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Hora de cierre",
    )

    abierto_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="operaciones_abiertas",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Abierto por",
    )

    cerrado_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="operaciones_cerradas",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Cerrado por",
    )

    observaciones = models.TextField(
        blank=True,
        default="",
        verbose_name="Observaciones",
    )

    class Meta:
        db_table = "operacion_diaria"
        verbose_name = "Operación diaria"
        verbose_name_plural = "Operaciones diarias"
        ordering = ["-fecha", "-id"]

        constraints = [

            # Solo puede existir una operación abierta a la vez.
            models.UniqueConstraint(
                fields=["abierta"],
                condition=Q(abierta=True),
                name="una_sola_operacion_abierta",
            ),

            # Una operación abierta debe tener hora de apertura
            # y no debe tener hora de cierre.
            models.CheckConstraint(
                check=(
                    Q(
                        abierta=True,
                        hora_apertura__isnull=False,
                        hora_cierre__isnull=True,
                    )
                    |
                    Q(
                        abierta=False,
                        hora_apertura__isnull=True,
                        hora_cierre__isnull=True,
                    )
                    |
                    Q(
                        abierta=False,
                        hora_apertura__isnull=False,
                        hora_cierre__isnull=False,
                    )
                ),
                name="operacion_estado_horas_coherentes",
            ),

            # El cierre no puede ser anterior a la apertura.
            models.CheckConstraint(
                check=(
                    Q(hora_cierre__isnull=True)
                    | Q(hora_cierre__gte=F("hora_apertura"))
                ),
                name="cierre_posterior_a_apertura",
            ),
        ]

    def __str__(self):
        return f"Operación {self.fecha} (#{self.id})"

    # ------------------------------------------------------
    # Estado
    # ------------------------------------------------------

    @property
    def cerrada(self):
        return self.hora_cierre is not None

    # ------------------------------------------------------
    # Apertura de operación
    # ------------------------------------------------------

    @transaction.atomic
    def abrir(self, persona):

        # Recuperar el estado actual y bloquear el registro.
        operacion = (
            OperacionDiaria.objects
            .select_for_update()
            .get(pk=self.pk)
        )

        if operacion.abierta:
            raise ValidationError("La operación ya está abierta.")

        if operacion.hora_cierre is not None:
            raise ValidationError(
                "La operación ya fue cerrada y no puede reabrirse."
            )

        operacion.abierta = True
        operacion.hora_apertura = timezone.now()
        operacion.abierto_por = persona

        try:
            with transaction.atomic():
                operacion.save(
                    update_fields=[
                        "abierta",
                        "hora_apertura",
                        "abierto_por",
                    ]
                )
        except IntegrityError:
            raise ValidationError(
                "Ya existe otra operación abierta."
            )

        # Actualizar la instancia original.
        self.refresh_from_db()

    # ------------------------------------------------------
    # Cierre de operación
    # ------------------------------------------------------

    @transaction.atomic
    def cerrar(self, persona):

        # Recuperar el estado actual y bloquear el registro.
        operacion = (
            OperacionDiaria.objects
            .select_for_update()
            .get(pk=self.pk)
        )

        if not operacion.abierta:
            raise ValidationError("La operación no está abierta.")

        if operacion.hora_apertura is None:
            raise ValidationError(
                "La operación no tiene registrada su apertura."
            )

        operacion.abierta = False
        operacion.hora_cierre = timezone.now()
        operacion.cerrado_por = persona

        operacion.save(
            update_fields=[
                "abierta",
                "hora_cierre",
                "cerrado_por",
            ]
        )

        # Actualizar la instancia original.
        self.refresh_from_db()