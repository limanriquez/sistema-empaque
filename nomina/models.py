
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from personas.models import Empleado
from operaciones.models import OperacionDiaria, ProductoEmpaque
from catalogos.models import ConceptoNomina

# Encabezado de nómina. Concentra los totales generales
# y registra quién la creó, cerró o canceló.
class Nomina(models.Model):

    total_percepciones = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    total_deducciones = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    total_neto = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="nominas_creadas"
    )

    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True
    )
    usuario_cierre = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="nominas_cerradas",
        null=True,
        blank=True
    )

    cancelada = models.BooleanField(default=False)

    class Meta:
        db_table = "nomina"
        verbose_name = "Nómina"
        verbose_name_plural = "Nóminas"

    def __str__(self):
        return f"Nómina {self.pk}"


# Relaciona las operaciones diarias incluidas en una nómina.
# Conserva las relaciones históricas cuando una nómina se cancela.
class NominaOperacionDiaria(models.Model):

    nomina = models.ForeignKey(
        Nomina,
        on_delete=models.PROTECT,
        related_name="operaciones_diarias"
    )

    operacion_diaria = models.ForeignKey(
        OperacionDiaria,
        on_delete=models.PROTECT,
        related_name="nominas"
    )

    class Meta:
        db_table = "nomina_operacion_diaria"
        verbose_name = "Operación diaria de nómina"
        verbose_name_plural = "Operaciones diarias de nómina"

        constraints = [
            models.UniqueConstraint(
                fields=["nomina", "operacion_diaria"],
                name="uq_nomina_operacion_diaria"
            )
        ]

    def clean(self):
        super().clean()

        if not self.nomina_id or not self.operacion_diaria_id:
            return

        # Una operación no puede pertenecer a dos nóminas vigentes.
        if not self.nomina.cancelada:
            existe = NominaOperacionDiaria.objects.filter(
                operacion_diaria_id=self.operacion_diaria_id,
                nomina__cancelada=False
            ).exclude(
                nomina_id=self.nomina_id
            ).exists()

            if existe:
                raise ValidationError({
                    "operacion_diaria": (
                        "Esta operación diaria ya pertenece a otra "
                        "nómina vigente."
                    )
                })

    def __str__(self):
        return f"Nómina {self.nomina_id} - Operación {self.operacion_diaria_id}"



# Concentrado de percepciones, extras y deducciones de cada empleado
# dentro de una nómina.
class NominaEmpleado(models.Model):

    nomina = models.ForeignKey(
        Nomina,
        on_delete=models.PROTECT,
        related_name="empleados"
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="nominas"
    )

    total_percepcion = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    # Importe habitual obtenido de EmpleadoExtra.
    total_extra_integrado = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    # Total de otros aumentos adicionales.
    total_extra = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    total_deduccion = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    total_neto = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = "nomina_empleado"
        verbose_name = "Empleado de nómina"
        verbose_name_plural = "Empleados de nómina"

        constraints = [
            models.UniqueConstraint(
                fields=["nomina", "empleado"],
                name="uq_nomina_empleado"
            )
        ]

    def __str__(self):
        return f"{self.empleado} - Nómina {self.nomina_id}"


# Detalle del destajo por producto de empaque.
# Almacena la cantidad trabajada, la tarifa aplicada y su importe total.
class NominaEmpleadoDestajo(models.Model):

    nomina_empleado = models.ForeignKey(
        NominaEmpleado,
        on_delete=models.PROTECT,
        related_name="destajos"
    )

    producto_empaque = models.ForeignKey(
        ProductoEmpaque,
        on_delete=models.PROTECT,
        related_name="detalles_destajo_nomina"
    )

    cantidad = models.PositiveIntegerField(default=0)

    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4
    )

    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = "nomina_empleado_destajo"
        verbose_name = "Destajo de empleado"
        verbose_name_plural = "Destajos de empleados"

        constraints = [
            models.UniqueConstraint(
                fields=["nomina_empleado", "producto_empaque"],
                name="uq_nomina_empleado_producto_destajo"
            )
        ]

    def __str__(self):
        return (
            f"{self.producto_empaque} - "
            f"{self.cantidad} cajas - ${self.total}"
        )


# ==========================================================
# MODELO: CONCEPTO DE EMPLEADO EN NÓMINA
#
# Registra los extras y deducciones aplicados a cada empleado
# dentro de una nómina.
#
# Cada registro relaciona un concepto del catálogo con el
# empleado y almacena el monto aplicado.
#
# Un empleado puede tener múltiples extras y deducciones
# dentro de una misma nómina.
# ==========================================================
class NominaEmpleadoConcepto(models.Model):

    nomina_empleado = models.ForeignKey(
        NominaEmpleado,
        on_delete=models.PROTECT,
        related_name="conceptos"
    )

    concepto = models.ForeignKey(
        ConceptoNomina,
        on_delete=models.PROTECT,
        related_name="aplicaciones"
    )

    monto = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    class Meta:
        db_table = "nomina_empleado_concepto"
        verbose_name = "Concepto de nómina aplicado"
        verbose_name_plural = "Conceptos de nómina aplicados"

    def __str__(self):
        return f"{self.concepto} - ${self.monto}"