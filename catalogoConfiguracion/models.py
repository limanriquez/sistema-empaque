
from django.db import models
from django.core.validators import (
    RegexValidator,
    MinValueValidator,
    MaxValueValidator,
)


# ==========================================================
# VALIDADORES
# ==========================================================

validar_codigo = RegexValidator(
    regex=r"^[A-Z0-9]{4,5}$",
    message=(
        "El código debe contener 4 o 5 caracteres "
        "alfanuméricos en mayúsculas."
    ),
)


# ==========================================================
# MODELO: CÓDIGO DE CAJA
# ==========================================================

class CodigoCaja(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    codigo = models.CharField(
        max_length=5,
        unique=True,
        validators=[validar_codigo],
        verbose_name="Código de caja",
    )

    usado = models.BooleanField(
        default=False,
        verbose_name="Usado",
    )

    class Meta:
        db_table = "catalogo_configuracion_codigo_caja"
        verbose_name = "Código de caja"
        verbose_name_plural = "Códigos de caja"
        ordering = ["id"]

    def __str__(self):
        return self.codigo


# ==========================================================
# MODELO: CÓDIGO DE TARIMA
# ==========================================================

class CodigoTarima(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    codigo_tarima = models.CharField(
        max_length=5,
        unique=True,
        validators=[validar_codigo],
        verbose_name="Código técnico",
    )

    consecutivo = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(99),
        ],
        verbose_name="Consecutivo visual",
    )

    usado = models.BooleanField(
        default=False,
        verbose_name="Usado",
    )

    class Meta:
        db_table = "catalogo_configuracion_codigo_tarima"
        verbose_name = "Código de tarima"
        verbose_name_plural = "Códigos de tarima"
        ordering = ["id"]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(consecutivo__gte=1)
                    & models.Q(consecutivo__lte=99)
                ),
                name="codigo_tarima_consecutivo_1_99",
            ),
        ]

    def __str__(self):
        return f"{self.consecutivo:02d} - {self.codigo_tarima}"
