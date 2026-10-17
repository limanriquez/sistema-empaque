from django.db import models



class RegistroAuditoria(models.Model):

    id_revision = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="ID de revisión",
    )

    id_criterio = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="ID de criterio",
    )

    tipo = models.CharField(
        max_length=20,
        choices=[
            ("HALLAZGO", "Hallazgo"),
            ("EVIDENCIA", "Evidencia"),
            ("OBSERVACION", "Observación"),
            ("RECOMENDACION", "Recomendación"),
            ("NOTA", "Nota"),
            ("OTRO", "Otro"),
        ],
        verbose_name="Tipo",
    )

    observacion = models.TextField(
        blank=True,
        default="",
        verbose_name="Observación",
    )

    recomendacion = models.TextField(
        blank=True,
        default="",
        verbose_name="Recomendación",
    )

    notas = models.TextField(
        blank=True,
        default="",
        verbose_name="Notas",
    )

    status = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    archivo = models.FileField(
        upload_to="auditoria/registros/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Archivo adjunto",
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
    )

    @property
    def id_compuesto(self):
        return f"{self.id_revision}-{self.id_criterio}"

    def __str__(self):
        return f"{self.id_compuesto} - {self.get_tipo_display()}"

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        ordering = ["-fecha_creacion"]
