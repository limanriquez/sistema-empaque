
from django.db import models
from django.core.exceptions import ValidationError

from auditoriaPersonas.models import Persona
from auditoriaCatalogos.models import Proceso
from auditoriaComites.models import SesionComite


# ============================================================
# MODELO: PLAN ANUAL DE AUDITORÍA
# ============================================================
class PlanAnual(models.Model):

    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador"),
        ("EN_ESPERA", "En espera de aprobación"),
        ("ACEPTADO", "Aceptado"),
        ("CANCELADO", "Cancelado"),
    ]

    vigencia = models.PositiveIntegerField(
        unique=True,
        help_text="Ejercicio anual al que corresponde el plan."
    )

    objetivo = models.TextField(
        help_text="Objetivo general del plan anual."
    )

    alcance = models.TextField(
        help_text="Alcance general del plan anual."
    )

    metodologia = models.TextField(
        help_text="Metodología general para ejecutar las auditorías."
    )

    criterios = models.TextField(
        help_text="Criterios normativos y documentales aplicables."
    )

    sesion_presentacion = models.ForeignKey(
        SesionComite,
        on_delete=models.PROTECT,
        related_name="planes_presentados",
        blank=True,
        null=True,
        help_text="Sesión del Comité en la que se presentó el plan."
    )

    sesion_aprobacion = models.ForeignKey(
        SesionComite,
        on_delete=models.PROTECT,
        related_name="planes_aprobados",
        blank=True,
        null=True,
        help_text="Sesión del Comité en la que se aprobó el plan."
    )

    realizo = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="planes_realizados",
        blank=True,
        null=True,
        help_text="Persona que elaboró el plan."
    )

    presidente = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="planes_como_presidente",
        blank=True,
        null=True,
        help_text="Presidente que participa en la aprobación."
    )

    secretario = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="planes_como_secretario",
        blank=True,
        null=True,
        help_text="Secretario que participa en la aprobación."
    )

    integrante_1 = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="planes_como_integrante_1",
        blank=True,
        null=True,
        help_text="Primer integrante que participa en la aprobación."
    )

    integrante_2 = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="planes_como_integrante_2",
        blank=True,
        null=True,
        help_text="Segundo integrante que participa en la aprobación."
    )

    fecha_aprobacion = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha en que el Comité aprobó el plan."
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default="BORRADOR"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "auditoria_plan_anual"
        ordering = ["-vigencia"]
        verbose_name = "Plan anual de auditoría"
        verbose_name_plural = "Planes anuales de auditoría"

    def clean(self):
        if self.estado == "ACEPTADO":
            if not self.sesion_aprobacion:
                raise ValidationError({
                    "sesion_aprobacion":
                        "Debe indicar la sesión en la que se aprobó el plan."
                })

            if not self.fecha_aprobacion:
                raise ValidationError({
                    "fecha_aprobacion":
                        "Debe indicar la fecha de aprobación."
                })

    def __str__(self):
        return f"Plan Anual de Auditoría {self.vigencia}"


# ============================================================
# MODELO: ACTIVIDAD DEL PLAN ANUAL
# ============================================================
class ActividadPlan(models.Model):
    plan = models.ForeignKey(
        PlanAnual,
        on_delete=models.CASCADE,
        related_name="actividades"
    )

    proceso = models.ForeignKey(
        Proceso,
        on_delete=models.PROTECT,
        related_name="actividades_plan",
        blank=True,
        null=True
    )
    
    nombre = models.CharField(
        max_length=200,
        blank=True,
        help_text=(
            "Nombre de la actividad que se realizará cuando no "
            "corresponda a un proceso del catálogo."
        ),
    )

    objetivo = models.TextField(
        blank=True,
        null=True
    )

    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()

    responsable = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        default="Pendiente"
    )

    class Meta:
        ordering = ["fecha_inicio"]
        verbose_name = "Actividad del plan"
        verbose_name_plural = "Actividades del plan"

    def __str__(self):
        return self.nombre


# ============================================================
# MODELO: NOTA DEL PLAN ANUAL
# ============================================================
class NotaPlan(models.Model):

    plan = models.ForeignKey(
        PlanAnual,
        on_delete=models.PROTECT,
        related_name="notas"
    )

    nota = models.TextField(
        help_text="Contenido de la nota u observación del plan."
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "auditoria_plan_nota"
        ordering = ["fecha_registro"]
        verbose_name = "Nota del plan"
        verbose_name_plural = "Notas del plan"

    def __str__(self):
        return f"Nota del plan {self.plan.vigencia}"

