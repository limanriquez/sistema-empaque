from django.db import models

from auditoriaCatalogos.models import (
    Puesto,
    Departamento,
    UnidadOperativa,
    Grupo,
)


class Persona(models.Model):
    nombre = models.CharField(max_length=150)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    curp = models.CharField(
        max_length=18,
        unique=True,
        blank=True,
        null=True
    )
    correo_institucional = models.EmailField(
        max_length=254,
        blank=True,
        null=True
    )
    telefono_institucional = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )
    extension = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "persona"
        ordering = [
            "apellido_paterno",
            "apellido_materno",
            "nombre",
        ]

    def __str__(self):
        return (
            f"{self.apellido_paterno} "
            f"{self.apellido_materno or ''} "
            f"{self.nombre}"
        ).strip()


class PersonaAdscripcion(models.Model):
    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="adscripciones"
    )
    puesto = models.ForeignKey(
        Puesto,
        on_delete=models.PROTECT,
        related_name="adscripciones"
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name="adscripciones"
    )
    unidad_operativa = models.ForeignKey(
        UnidadOperativa,
        on_delete=models.PROTECT,
        related_name="adscripciones"
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = "persona_adscripcion"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return (
            f"{self.persona} - "
            f"{self.puesto} - "
            f"{self.departamento} - "
            f"{self.unidad_operativa}"
        )


class PersonaGrupo(models.Model):
    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="grupos"
    )
    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.PROTECT,
        related_name="personas"
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = "persona_grupo"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "persona",
                    "grupo",
                    "fecha_inicio"
                ],
                name="uq_persona_grupo_inicio"
            )
        ]

    def __str__(self):
        return f"{self.persona} - {self.grupo}"