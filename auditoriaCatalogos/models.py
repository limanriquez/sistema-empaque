from django.db import models

class GoHome(models.Model):
    class Meta:
        verbose_name = "A inicio"
        verbose_name_plural = "A inicio"
        managed = False  # No crea tabla
        
class Puesto(models.Model):
    descripcion = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "catalogo_puesto"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


class Departamento(models.Model):
    descripcion = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "catalogo_departamento"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion


class UnidadOperativa(models.Model):
    TIPO_CHOICES = [
        ("MATRIZ", "Matriz"),
        ("SUCURSAL", "Sucursal"),
        ("CORRESPONSALIA", "Corresponsalía"),
    ]

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "catalogo_unidad_operativa"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Grupo(models.Model):
    nombre = models.CharField(
        max_length=150,
        unique=True
    )
    descripcion = models.TextField(
        blank=True
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "catalogo_grupo"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre