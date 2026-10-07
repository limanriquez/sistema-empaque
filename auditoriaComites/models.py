from django.db import models

from auditoriaCatalogos.models import (
    TipoComite,
    CargoComite,
)

from auditoriaPersonas.models import (
    Persona,
)


class Comite(models.Model):
    """
    Representa un comité formalmente constituido para un periodo
    determinado.

    El comité se relaciona con un TipoComite para identificar su
    naturaleza o clasificación.

    Cada nuevo periodo del comité genera un nuevo registro de Comite.

    Los cambios de integrantes durante el mismo periodo NO generan
    un nuevo comité. Esos cambios se registran mediante
    ComiteIntegrante, conservando el historial de participación.

    Ejemplo:

        Comité de Auditoría 2026

        Tipo:
            Comité de Auditoría

        Periodo:
            01/01/2026 - 31/12/2026
    """

    ESTATUS_CHOICES = [
        ("ACTIVO", "Activo"),
        ("FINALIZADO", "Finalizado"),
        ("CANCELADO", "Cancelado"),
    ]

    tipo_comite = models.ForeignKey(
        TipoComite,
        on_delete=models.PROTECT,
        related_name="comites",
        help_text=(
            "Tipo al que pertenece el comité."
        ),
    )

    nombre = models.CharField(
        max_length=150,
        help_text=(
            "Nombre o identificación del comité."
        ),
    )

    fecha_constitucion = models.DateField(
        help_text=(
            "Fecha de constitución formal del comité."
        ),
    )

    fecha_inicio = models.DateField(
        help_text=(
            "Fecha de inicio del periodo del comité."
        ),
    )

    fecha_fin = models.DateField(
        blank=True,
        null=True,
        help_text=(
            "Fecha de terminación del periodo del comité."
        ),
    )

    estatus = models.CharField(
        max_length=20,
        choices=ESTATUS_CHOICES,
        default="ACTIVO",
        help_text=(
            "Estado actual del comité."
        ),
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "Observaciones generales relacionadas con el comité."
        ),
    )

    class Meta:
        db_table = "comite"
        ordering = [
            "-fecha_inicio",
            "nombre",
        ]
        verbose_name = "Comité"
        verbose_name_plural = "Comités"

    def __str__(self):
        return self.nombre


class ComiteIntegrante(models.Model):
    """
    Representa la participación histórica de una Persona dentro
    de un Comité y el CargoComite que desempeña.

    Este modelo es el encargado de conservar el historial de
    integrantes del comité.

    Una persona puede dejar de participar en un comité sin que
    se elimine físicamente su registro histórico.

    Cuando una persona deja el comité:

        1. Se registra la fecha de finalización.
        2. Se cambia el estatus a FINALIZADO.
        3. Se registra el motivo de finalización.

    Cuando una persona es reemplazada durante el mismo periodo:

        - Se finaliza la participación anterior.
        - Se crea una nueva participación para la persona que
          ocupa su lugar.

    Cuando una persona cambia de cargo dentro del mismo comité:

        - Se finaliza la participación anterior con motivo
          CAMBIO_CARGO.
        - Se crea una nueva participación con el nuevo cargo.

    De esta manera se conserva el historial de participación
    de las personas dentro de los comités.
    """

    ESTATUS_CHOICES = [
        ("ACTIVO", "Activo"),
        ("FINALIZADO", "Finalizado"),
    ]

    MOTIVO_FIN_CHOICES = [
        (
            "CAMBIO_INTEGRANTE",
            "Cambio de integrante",
        ),
        (
            "FIN_PERIODO",
            "Fin de periodo",
        ),
        (
            "RENUNCIA",
            "Renuncia",
        ),
        (
            "REMOCION",
            "Remoción",
        ),
        (
            "CAMBIO_CARGO",
            "Cambio de cargo",
        ),
        (
            "OTRO",
            "Otro",
        ),
    ]

    comite = models.ForeignKey(
        Comite,
        on_delete=models.PROTECT,
        related_name="integrantes",
        help_text=(
            "Comité al que pertenece la participación."
        ),
    )

    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="participaciones_comite",
        help_text=(
            "Persona que participa en el comité."
        ),
    )

    cargo_comite = models.ForeignKey(
        CargoComite,
        on_delete=models.PROTECT,
        related_name="integrantes",
        help_text=(
            "Cargo desempeñado por la persona dentro del comité."
        ),
    )

    fecha_inicio = models.DateField(
        help_text=(
            "Fecha de inicio de la participación de la persona "
            "en el comité."
        ),
    )

    fecha_fin = models.DateField(
        blank=True,
        null=True,
        help_text=(
            "Fecha en que termina la participación de la persona "
            "en el comité."
        ),
    )

    estatus = models.CharField(
        max_length=20,
        choices=ESTATUS_CHOICES,
        default="ACTIVO",
        help_text=(
            "Estado actual de la participación."
        ),
    )

    motivo_fin = models.CharField(
        max_length=30,
        choices=MOTIVO_FIN_CHOICES,
        blank=True,
        null=True,
        help_text=(
            "Motivo por el que terminó la participación."
        ),
    )

    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "Observaciones específicas de la participación."
        ),
    )

    class Meta:
        db_table = "comite_integrante"
        ordering = [
            "-fecha_inicio",
        ]
        verbose_name = "Integrante de comité"
        verbose_name_plural = "Integrantes de comité"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "comite",
                    "persona",
                    "cargo_comite",
                    "fecha_inicio",
                ],
                name="uq_comite_persona_cargo_inicio",
            ),
        ]

    def __str__(self):
        return (
            f"{self.persona} - "
            f"{self.comite} - "
            f"{self.cargo_comite}"
        )