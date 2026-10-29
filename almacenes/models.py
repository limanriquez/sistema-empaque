from django.db import models


# Registra las bodegas o instalaciones físicas de la empacadora.
# Una bodega puede contener múltiples espacios independientes, como
# cámaras de refrigeración, áreas de almacenamiento u otras zonas.
# No administra existencias ni determina qué productos se almacenan.
class Almacen(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "almacen_almacen"
        verbose_name = "Almacén"
        verbose_name_plural = "Almacenes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# Registra los espacios físicos independientes que pertenecen a una
# bodega, como cámaras de frío, zonas de almacenamiento o áreas de
# maniobras. Cada espacio pertenece a un solo almacén y puede contener
# múltiples secciones. Su existencia no depende de la mercancía almacenada.
class EspacioAlmacen(models.Model):
    id = models.BigAutoField(primary_key=True)
    almacen = models.ForeignKey(
        Almacen,
        on_delete=models.PROTECT,
        related_name="espacios",
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "almacen_espacio"
        verbose_name = "Espacio de almacén"
        verbose_name_plural = "Espacios de almacén"
        ordering = ["almacen", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["almacen", "nombre"],
                name="uq_espacio_almacen_nombre",
            ),
        ]

    def __str__(self):
        return f"{self.almacen} - {self.nombre}"


# Registra las secciones físicas en las que se divide un espacio de
# almacén. Cada sección pertenece a un solo espacio y puede almacenar
# directamente pallets, embalajes, insumos u otros elementos. También
# puede contener múltiples estibas, sin que estas sean obligatorias.
class SeccionAlmacen(models.Model):
    id = models.BigAutoField(primary_key=True)
    espacio = models.ForeignKey(
        EspacioAlmacen,
        on_delete=models.PROTECT,
        related_name="secciones",
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "almacen_seccion"
        verbose_name = "Sección de almacén"
        verbose_name_plural = "Secciones de almacén"
        ordering = ["espacio", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["espacio", "nombre"],
                name="uq_seccion_espacio_nombre",
            ),
        ]

    def __str__(self):
        return f"{self.espacio} - {self.nombre}"


# Identifica las estibas disponibles para las operaciones de almacenamiento.
# Una estiba puede registrarse sin ubicación asignada y posteriormente
# asociarse a una sección cuando se utilice. Una sección puede tener
# múltiples estibas. Las posiciones verticales y la mercancía que ocupa
# cada posición se administrarán desde el módulo de inventario.
class Estiba(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    seccion = models.ForeignKey(
        SeccionAlmacen,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="estibas",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "almacen_estiba"
        verbose_name = "Estiba"
        verbose_name_plural = "Estibas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
