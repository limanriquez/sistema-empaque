from django.db import models
from django.db.models.functions import Lower

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



# Registra las unidades de medida utilizadas para expresar las
# cantidades de materiales en las operaciones de compra e inventario.
# Cada material usa una sola unidad, y todas sus cantidades (movimientos
# y recetas) se expresan en ella. Las unidades de conteo, como pieza o
# caja, pueden restringirse a cantidades enteras.
class UnidadMedida(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, unique=True)
    permite_decimales = models.BooleanField(
        default=True,
        help_text=(
            "Desmarque si la unidad solo admite cantidades enteras "
            "(piezas, cajas)."
        ),
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "inventario_unidad_medida"
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                Lower("nombre"),
                name="uq_unidad_nombre_ci",
            ),
            models.UniqueConstraint(
                Lower("abreviatura"),
                name="uq_unidad_abreviatura_ci",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"


# ==========================================================
# MODELO: ESTACIÓN DE TRABAJO
#
# Define las estaciones físicas de la empacadora donde se
# realizan las actividades operativas, como empaque,
# tarimado, almacén y administración.
#
# Este catálogo se utilizará para organizar y asignar al
# personal durante cada operación diaria.
# ==========================================================

class EstacionTrabajo(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la estación",
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
        db_table = "operacion_estacion_trabajo"
        verbose_name = "Estación de trabajo"
        verbose_name_plural = "Estaciones de trabajo"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==========================================================
# MODELO: CALIDAD
#
# Catálogo de calidades utilizadas en los productos de empaque.
# Permite clasificar los productos según su calidad comercial.
#
# Una calidad puede estar relacionada con múltiples productos
# de empaque.
#
# Las calidades utilizadas históricamente no deben eliminarse.
# Su disponibilidad se controla mediante el campo activo.
# ==========================================================

class Calidad(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

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

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        db_table = "catalogos_calidad"
        verbose_name = "Calidad"
        verbose_name_plural = "Calidades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==========================================================
# MODELO: TAMAÑO
#
# Catálogo de tamaños o calibres utilizados en los productos
# de empaque.
#
# Un tamaño puede estar relacionado con múltiples productos
# de empaque.
#
# Los tamaños utilizados históricamente no deben eliminarse.
# Su disponibilidad se controla mediante el campo activo.
# ==========================================================

class Tamano(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

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

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        db_table = "catalogos_tamano"
        verbose_name = "Tamaño"
        verbose_name_plural = "Tamaños"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==========================================================
# MODELO: CONCEPTO DE NÓMINA
#
# Catálogo de conceptos que pueden aplicarse en una nómina,
# clasificados como extras o deducciones.
#
# Cada concepto puede utilizarse en múltiples registros
# de nómina de diferentes empleados.
#
# Los conceptos utilizados históricamente no deben eliminarse.
# Su disponibilidad se controla mediante el campo activo.
# ==========================================================
class ConceptoNomina(models.Model):

    class Tipo(models.IntegerChoices):
        PERCEPCION = 1, "Percepción"
        DEDUCCION = 2, "Deducción"

    descripcion = models.CharField(
        max_length=150,
        unique=True
    )

    tipo = models.PositiveSmallIntegerField(
        choices=Tipo.choices
    )

    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "concepto_nomina"
        verbose_name = "Concepto de nómina"
        verbose_name_plural = "Conceptos de nómina"

    def __str__(self):
        return f"{self.descripcion} - {self.get_tipo_display()}"