from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
# Catálogo de huertas de donde procede la fruta.
# Es independiente de los clientes, ya que una misma huerta
# puede estar asignada a uno o varios clientes.
class Huerta(models.Model):
    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    nombre = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nombre de la huerta",
    )

    descripcion = models.TextField(
        blank=True,
        default="",
        verbose_name="Descripción",
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activa",
    )

    class Meta:
        db_table = "catalogos_fruta_huerta"
        verbose_name = "Huerta"
        verbose_name_plural = "Huertas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# Establece la relación entre los clientes y las huertas.
# Permite asignar varias huertas a un cliente y compartir
# una misma huerta entre diferentes clientes.
class ClienteHuerta(models.Model):
    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="huertas_asignadas",
        verbose_name="Cliente",
    )

    huerta = models.ForeignKey(
        "fruticultura.Huerta",
        on_delete=models.PROTECT,
        related_name="clientes_asignados",
        verbose_name="Huerta",
    )

    class Meta:
        db_table = "catalogos_fruta_cliente_huerta"
        verbose_name = "Asignación de huerta"
        verbose_name_plural = "Asignaciones de huertas"
        ordering = ["cliente", "huerta"]

        constraints = [
            models.UniqueConstraint(
                fields=["cliente", "huerta"],
                name="uq_cliente_huerta",
            ),
        ]

    def __str__(self):
        return f"{self.cliente} - {self.huerta}"


# Catálogo de lotes que pertenecen a una huerta.
# Identifica los lotes de origen de la fruta sin administrar
# cantidades recibidas ni existencias de inventario.
class LoteHuerta(models.Model):
    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    huerta = models.ForeignKey(
        "fruticultura.Huerta",
        on_delete=models.PROTECT,
        related_name="lotes",
        verbose_name="Huerta",
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del lote",
    )

    descripcion = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción",
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        db_table = "catalogos_fruta_lote_huerta"
        verbose_name = "Lote de huerta"
        verbose_name_plural = "Lotes de huerta"
        ordering = ["huerta", "nombre"]

        constraints = [
            models.UniqueConstraint(
                fields=["huerta", "nombre"],
                name="uq_lote_huerta_nombre",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.huerta}"

    
    # ==========================================================
# MODELO: VARIEDAD
#
# Catálogo de variedades de fruta utilizadas en la empacadora.
#
# Permite identificar y clasificar la variedad de manzana
# que ingresa al inventario y posteriormente se utiliza
# durante los procesos de producción.
#
# Cada variedad se registra una sola vez y puede asociarse
# a múltiples recepciones, existencias, movimientos de fruta
# y lotes de producción.
#
# El catálogo permite activar o desactivar variedades.
# Las variedades utilizadas en operaciones históricas no
# deben eliminarse físicamente, para conservar la trazabilidad.
#
# Ejemplos:
# - Golden
# - Golden Blush
# - Granny Smith
# - Red Delicious
# - Cameo
# - Rome Beauty
#
# ==========================================================

class Variedad(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre",
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    observaciones = models.TextField(
        blank=True,
        default="",
        verbose_name="Observaciones",
    )

    class Meta:
        db_table = "fruticultura_variedad"

        verbose_name = "Variedad"
        verbose_name_plural = "Variedades"

        ordering = ["nombre"]

        constraints = [
            models.UniqueConstraint(
                fields=["nombre"],
                name="uq_fruticultura_variedad_nombre",
            ),
        ]

    def __str__(self):
        return self.nombre

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Las variedades no pueden eliminarse físicamente. "
            "Utilice el campo activo para deshabilitarlas."
        )