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


from django.db import models


class TipoDocumento(models.Model):
    """
    Catálogo de tipos de documentos institucionales.

    Clasifica los documentos utilizados en el Sistema de
    Administración de Auditorías.

    Tipos de documento:
        - Manuales
        - Políticas
        - Guías
        - Metodologías
        - Otros
    """

    nombre = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nombre de la clasificación del documento."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el tipo está disponible para nuevos registros."
    )

    class Meta:
        db_table = "tipo_documento"
        ordering = ["nombre"]
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"

    def __str__(self):
        return self.nombre

# ============================================================
#       MODELOS: DOCUMENTOS Y PROCESOS
# ============================================================


class Documento(models.Model):
    """
    Catálogo de documentos institucionales.

    Registra la identificación, versión, clasificación de la
    información y datos de publicación de los documentos
    utilizados como referencia en el sistema.

    Cada documento pertenece a un tipo de documento y tiene
    un nivel de clasificación de la información asignado.
    """

    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        related_name="documentos",
        help_text="Tipo de documento, por ejemplo: manual o política."
    )

    clasificacion = models.ForeignKey(
        "ClasificacionDocumento",
        on_delete=models.PROTECT,
        related_name="documentos",
        help_text="Nivel de clasificación de la información del documento."
    )

    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del documento."
    )

    version = models.CharField(
        max_length=20,
        help_text="Versión del documento."
    )

    fecha_publicacion = models.DateField(
        help_text="Fecha de publicación o actualización oficial."
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de registro automático."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el documento está disponible para nuevas operaciones."
    )

    fecha_baja = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora en que el documento fue desactivado."
    )

    class Meta:
        db_table = "catalogo_documento"
        ordering = ["nombre", "version"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self):
        return f"{self.nombre} ({self.version})"


class Proceso(models.Model):
    """
    Catálogo de procesos relacionados con documentos institucionales.

    Registra el nombre y la clave de control interno de cada proceso.
    Cada proceso se relaciona con un documento existente.
    """

    clave_control = models.CharField(
        max_length=30,
        unique=True,
        help_text="Clave única de control interno del proceso."
    )

    nombre = models.CharField(
        max_length=200,
        help_text="Nombre del proceso."
    )

    documento = models.ForeignKey(
        Documento,
        on_delete=models.PROTECT,
        related_name="procesos",
        help_text="Documento relacionado con el proceso."
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de registro automático."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el proceso está disponible para nuevas operaciones."
    )

    fecha_baja = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora en que el proceso fue desactivado."
    )

    class Meta:
        db_table = "catalogo_proceso"
        ordering = ["nombre"]
        verbose_name = "Proceso"
        verbose_name_plural = "Procesos"

    def __str__(self):
        return f"{self.clave_control} - {self.nombre}"



from django.db import models


# ============================================================
# CATÁLOGO: TIPO DE DOCUMENTO DE PROCESO
# ============================================================
# Propósito:
# Clasificar los documentos operativos que se registran durante
# los procesos de auditoría, por ejemplo: informes, oficios,
# solicitudes, cartas, presentaciones y evidencias.
#
# Este catálogo es transversal y puede ser utilizado por
# diferentes módulos del Sistema de Administración de Auditorías.
#
# Nota:
# No sustituye al catálogo TipoDocumento existente, destinado
# a clasificar documentos institucionales como manuales,
# políticas y guías.
# ============================================================
class TipoDocumentoProceso(models.Model):

    # Nombre de la clasificación documental.
    # Ejemplo: Informe, Oficio, Solicitud o Evidencia.
    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    # Descripción opcional para explicar el uso del tipo documental.
    descripcion = models.TextField(
        blank=True,
        null=True
    )

    # Indica si el tipo documental está disponible para utilizarse.
    # Si se desactiva, se conserva el registro histórico.
    activo = models.BooleanField(default=True)

    class Meta:
        # Nombre de la tabla en la base de datos.
        db_table = "tipo_documento_proceso"

        # Orden predeterminado al consultar el catálogo.
        ordering = ["nombre"]

        # Nombres descriptivos en Django Admin.
        verbose_name = "Tipo de documento de proceso"
        verbose_name_plural = "Tipos de documentos de proceso"

    def __str__(self):
        # Representación del registro en Django Admin y formularios.
        return self.nombre

# ============================================================
# MODELO: CLASIFICACIÓN DE LA INFORMACIÓN
# ============================================================

class ClasificacionDocumento(models.Model):
    """
    Catálogo de niveles de clasificación de la información.

    Determina el nivel de clasificación asignado a cada
    documento institucional, de acuerdo con la sensibilidad
    y las reglas de acceso aplicables a su contenido.

    Cada documento tendrá una clasificación seleccionada
    de este catálogo.
    """

    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre del nivel de clasificación de la información."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el nivel de clasificación está disponible."
    )

    class Meta:
        db_table = "catalogo_clasificacion_documento"
        ordering = ["nombre"]
        verbose_name = "Clasificación de la información"
        verbose_name_plural = "Clasificaciones de la información"

    def __str__(self):
        return self.nombre