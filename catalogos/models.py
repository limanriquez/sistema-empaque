from django.db import models


class GoHome(models.Model):
    class Meta:
        managed = False
        app_label = "catalogos"
        verbose_name = "A inicio"
        verbose_name_plural = "A inicio"


# ==========================================================
# CATÁLOGO: PUESTOS
# Define los puestos laborales que pueden asignarse
# a los empleados de la empresa.
# ==========================================================

class Puesto(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del puesto",
    )

    descripcion = models.TextField(
        blank=True,
        default="",
        verbose_name="Descripción",
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        db_table = "personas_puesto"
        verbose_name = "Puesto"
        verbose_name_plural = "Puestos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre



# Catálogo de conceptos de pago adicionales para empleados.
# Permite definir el nombre, descripción, monto predeterminado
# y estado de cada concepto, como bonos, destajos o compensaciones.
class ConceptoExtra(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre",
    )
    descripcion = models.TextField(
        blank=True,
        default="",
        verbose_name="Descripción",
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Monto",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        db_table = "catalogos_concepto_extra"
        verbose_name = "Concepto extra"
        verbose_name_plural = "Conceptos extras"
        ordering = ["nombre"]

     # Muestra el nombre y el monto del concepto en los selectores.
    def __str__(self):
        return f"{self.nombre} - ${self.monto:,.2f}"

