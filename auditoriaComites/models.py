from django.db import models
from django.core.exceptions import ValidationError

from auditoriaCatalogos.models import (
    TipoComite,
    CargoComite,
)

from auditoriaPersonas.models import (
    Persona,
)

# Importar el catálogo transversal de documentos de proceso.
from auditoriaCatalogos.models import TipoDocumentoProceso


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




# ============================================================
# MODELO: SESIÓN DE COMITÉ
# ============================================================
# Registra las sesiones ordinarias y extraordinarias de un
# comité, incluyendo su fecha, horario, estado y observaciones.
#
# Cada sesión pertenece a un registro de Comite. La numeración
# es única dentro de ese comité y puede reiniciarse cuando se
# crea un nuevo registro para otro periodo del comité.
# ============================================================
class SesionComite(models.Model):

    # Opciones para clasificar la sesión.
    TIPO_SESION_CHOICES = [
        ("ORDINARIA", "Ordinaria"),
        ("EXTRAORDINARIA", "Extraordinaria"),
    ]

    # Estado operativo de la sesión.
    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador"),
        ("ABIERTA", "Abierta"),
        ("CERRADA", "Cerrada"),
        ("CANCELADA", "Cancelada"),
    ]

    # Comité al que pertenece la sesión.
    # Se protege el registro para conservar la trazabilidad.
    comite = models.ForeignKey(
        "auditoriaComites.Comite",
        on_delete=models.PROTECT,
        related_name="sesiones"
    )

    # Número consecutivo de la sesión dentro del comité.
    numero_sesion = models.PositiveIntegerField()

    # Clasificación ordinaria o extraordinaria.
    tipo_sesion = models.CharField(
        max_length=15,
        choices=TIPO_SESION_CHOICES
    )

    # Fecha y hora programadas o registradas de inicio.
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField()

    # Fecha y hora de finalización.
    # Pueden permanecer vacías mientras la sesión no concluya.
    fecha_fin = models.DateField(
        blank=True,
        null=True
    )
    hora_fin = models.TimeField(
        blank=True,
        null=True
    )

    # Lugar físico o referencia de ubicación de la sesión.
    lugar = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    # Estado actual de la sesión.
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default="BORRADOR"
    )

    # Observaciones generales de la sesión.
    observaciones = models.TextField(
        blank=True,
        null=True
    )

    # Fecha y hora de creación del registro.
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "sesion_comite"
        ordering = ["-fecha_inicio", "-numero_sesion"]
        verbose_name = "Sesión de comité"
        verbose_name_plural = "Sesiones de comité"

        # No se permite repetir el número de sesión
        # dentro del mismo registro de comité.
        constraints = [
            models.UniqueConstraint(
                fields=["comite", "numero_sesion"],
                name="uq_sesion_comite_numero"
            )
        ]

    def clean(self):
        # La fecha de fin no puede ser anterior a la de inicio.
        if self.fecha_fin and self.fecha_inicio:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError({
                    "fecha_fin": (
                        "La fecha de finalización no puede "
                        "ser anterior a la fecha de inicio."
                    )
                })

        # Si ambas fechas son iguales, la hora de fin debe
        # ser posterior o igual a la hora de inicio.
        if (
            self.fecha_fin == self.fecha_inicio
            and self.hora_fin
            and self.hora_inicio
            and self.hora_fin < self.hora_inicio
        ):
            raise ValidationError({
                "hora_fin": (
                    "La hora de finalización no puede ser "
                    "anterior a la hora de inicio."
                )
            })

    def __str__(self):
        return f"Sesión {self.numero_sesion} - {self.comite}"


# ============================================================
# MODELO: ASISTENCIA A SESIÓN
# ============================================================
# Registra a las personas que efectivamente asistieron a una
# sesión y el tipo de asistencia que tuvieron.
#
# No representa personas convocadas ni personas ausentes.
# ============================================================
class AsistenciaSesion(models.Model):

    # Modalidad en que participó la persona.
    TIPO_ASISTENCIA_CHOICES = [
        ("PRESENCIAL", "Presencial"),
        ("VIRTUAL", "Virtual"),
    ]

    # Sesión a la que corresponde la asistencia.
    sesion = models.ForeignKey(
        SesionComite,
        on_delete=models.PROTECT,
        related_name="asistencias"
    )

    # Persona que asistió a la sesión.
    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="asistencias_sesion"
    )

    # Modalidad de participación.
    tipo_asistencia = models.CharField(
        max_length=12,
        choices=TIPO_ASISTENCIA_CHOICES
    )

    # Observaciones opcionales sobre la asistencia.
    observaciones = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = "asistencia_sesion"
        ordering = ["persona__apellido_paterno", "persona__nombre"]
        verbose_name = "Asistencia a sesión"
        verbose_name_plural = "Asistencias a sesión"

        # Una persona no puede registrarse dos veces
        # en la asistencia de una misma sesión.
        constraints = [
            models.UniqueConstraint(
                fields=["sesion", "persona"],
                name="uq_asistencia_sesion_persona"
            )
        ]

    def __str__(self):
        return f"{self.persona} - {self.sesion}"


# ============================================================
# MODELO: AGENDA DE SESIÓN
# ============================================================
# Contiene los puntos del orden del día de cada sesión.
# El número de orden identifica la posición del punto dentro
# de una sesión específica.
# ============================================================
class AgendaSesion(models.Model):

    # Sesión a la que pertenece el punto de agenda.
    sesion = models.ForeignKey(
        SesionComite,
        on_delete=models.PROTECT,
        related_name="agenda"
    )

    # Posición consecutiva del punto dentro de la agenda.
    numero_orden = models.PositiveIntegerField()

    # Título breve del punto.
    titulo = models.CharField(max_length=200)

    # Descripción o detalle del asunto a tratar.
    descripcion = models.TextField()

    # Nota adicional opcional.
    nota = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        db_table = "agenda_sesion"
        ordering = ["numero_orden"]
        verbose_name = "Punto de agenda"
        verbose_name_plural = "Puntos de agenda"

        # El número de orden no se puede repetir
        # dentro de la misma sesión.
        constraints = [
            models.UniqueConstraint(
                fields=["sesion", "numero_orden"],
                name="uq_agenda_sesion_orden"
            )
        ]

    def __str__(self):
        return f"{self.numero_orden}. {self.titulo}"


# ============================================================
# MODELO: DOCUMENTO DE SESIÓN
# ============================================================
# Registra documentos recibidos o generados durante una sesión.
#
# tipo_movimiento:
#   1 = Entrada
#   2 = Salida
#
# El documento puede asociarse a un punto de agenda cuando
# corresponda. La ubicación almacena una referencia al archivo
# o a su repositorio autorizado, no el archivo binario.
# ============================================================
class DocumentoSesion(models.Model):

    # Clasificación del movimiento documental.
    TIPO_MOVIMIENTO_CHOICES = [
        (1, "Entrada"),
        (2, "Salida"),
    ]

    # Sesión a la que corresponde el documento.
    sesion = models.ForeignKey(
        SesionComite,
        on_delete=models.PROTECT,
        related_name="documentos"
    )

    # Punto de agenda relacionado, si aplica.
    agenda_sesion = models.ForeignKey(
        AgendaSesion,
        on_delete=models.PROTECT,
        related_name="documentos",
        blank=True,
        null=True
    )

    # Indica si el documento se recibe o se genera.
    tipo_movimiento = models.PositiveSmallIntegerField(
        choices=TIPO_MOVIMIENTO_CHOICES
    )

    # Clasificación documental del catálogo transversal.
    tipo_documento_proceso = models.ForeignKey(
        TipoDocumentoProceso,
        on_delete=models.PROTECT,
        related_name="documentos_sesion"
    )

    # Nombre o título con el que se identifica el documento.
    nombre = models.CharField(max_length=200)

    # Fecha que aparece en el documento, si está disponible.
    fecha_documento = models.DateField(
        blank=True,
        null=True
    )

    # Ruta, URL o identificador del documento en el repositorio.
    ubicacion = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    # Observaciones adicionales.
    observaciones = models.TextField(
        blank=True,
        null=True
    )

    # Fecha y hora en que el sistema registra el documento.
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "documento_sesion"
        ordering = ["tipo_movimiento", "nombre"]
        verbose_name = "Documento de sesión"
        verbose_name_plural = "Documentos de sesión"

    def clean(self):
        # Si se vincula un punto de agenda, debe pertenecer
        # a la misma sesión indicada en este documento.
        if (
            self.agenda_sesion_id
            and self.sesion_id
            and not AgendaSesion.objects.filter(
                pk=self.agenda_sesion_id,
                sesion_id=self.sesion_id
            ).exists()
        ):
            raise ValidationError({
                "agenda_sesion": (
                    "El punto de agenda debe pertenecer "
                    "a la misma sesión del documento."
                )
            })

    def __str__(self):
        return f"{self.nombre} - {self.sesion}"