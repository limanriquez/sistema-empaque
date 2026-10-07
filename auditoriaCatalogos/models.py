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


#Modelos de catalogos de comítes

from django.db import models


class TipoComite(models.Model):
    """
    Catálogo de tipos de comité.

    Define la clasificación o naturaleza del comité que se constituye
    dentro de la organización.

    Ejemplos:
        - Comité de Auditoría
        - Comité de Riesgos
        - Comité de Crédito

    El catálogo permite agregar, modificar y desactivar tipos de comité.
    La desactivación es lógica mediante el campo 'activo'; no se elimina
    físicamente el registro.
    """

    nombre = models.CharField(
        max_length=150,
        unique=True,
        help_text="Nombre del tipo de comité."
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción y propósito del tipo de comité."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el tipo de comité está disponible para nuevas operaciones."
    )

    class Meta:
        db_table = "tipo_comite"
        ordering = ["nombre"]
        verbose_name = "Tipo de comité"
        verbose_name_plural = "Tipos de comité"

    def __str__(self):
        return self.nombre


class CargoComite(models.Model):
    """
    Catálogo de cargos dentro de un comité.

    Define la función que una persona desempeña como integrante
    de un comité.

    Ejemplos:
        - Presidente
        - Secretario
        - Vocal
        - Vocal Suplente
        - Consejero
        - Coordinador
        - Representante
        - Asesor

    Este catálogo representa el cargo dentro del comité y no debe
    confundirse con el 'Puesto' de la persona dentro de la organización.

    Tampoco representa un rol de seguridad o permisos del sistema.
    """

    nombre = models.CharField(
        max_length=150,
        unique=True,
        help_text="Nombre del cargo dentro del comité."
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de la función del cargo dentro del comité."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el cargo está disponible para nuevas operaciones."
    )

    class Meta:
        db_table = "cargo_comite"
        ordering = ["nombre"]
        verbose_name = "Cargo de comité"
        verbose_name_plural = "Cargos de comité"

    def __str__(self):
        return self.nombre