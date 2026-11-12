from decimal import Decimal
from django.apps import apps

from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError, connection
from django.db.models import Q, F
from django.utils import timezone
from catalogos.models import Calidad, Tamano, EstacionTrabajo
from catalogoConfiguracion.models import CodigoTarima
from django.core.validators import MinValueValidator, MaxValueValidator

# Producto que se empaca, por ejemplo una caja de cierta presentación.
# Guarda el costo total de empacar una unidad y el precio que se cobra
# al cliente, que siempre debe ser mayor al costo. Cada producto tiene
# un BOM (ComponenteEmpaque) con los materiales que se descuentan por
# cada unidad empacada.
class ProductoEmpaque(models.Model):
    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )
    calidad = models.ForeignKey(
        "catalogos.Calidad",
        on_delete=models.PROTECT,
        related_name="productos_empaque",
        verbose_name="Calidad",
    )
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    costo_empaque = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=0,
        help_text="Costo que se paga al empacador por unidad.",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "operaciones_producto_empaque"
        verbose_name = "Producto de empaque"
        verbose_name_plural = "Productos de empaque"
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(costo_empaque__gte=0),
                name="ck_producto_costo_no_negativo",
            ),
        ]

    def __str__(self):
        return self.nombre



# BOM de un producto de empaque: cada fila es un material y la
# cantidad que se descuenta por cada unidad empacada. No mueve
# inventario: lo ejecuta el servicio de empaque.
class ComponenteEmpaque(models.Model):
    id = models.BigAutoField(primary_key=True)
    producto_empaque = models.ForeignKey(
        ProductoEmpaque,
        on_delete=models.CASCADE,
        related_name="componentes",
    )
    material = models.ForeignKey(
        "inventarios.Material",
        on_delete=models.PROTECT,
        related_name="usos_en_empaques",
    )
    cantidad_material = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        help_text="Cantidad de este material por cada unidad empacada.",
    )

    class Meta:
        db_table = "operaciones_componente_empaque"
        verbose_name = "Material del empaque"
        verbose_name_plural = "Materiales del empaque"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["producto_empaque", "material"],
                name="uq_componente_producto_material",
            ),
            models.CheckConstraint(
                condition=models.Q(cantidad_material__gt=0),
                name="ck_componente_cantidad_positiva",
            ),
        ]

    def __str__(self):
        return f"{self.material} x {self.cantidad_material}"

    # Si la unidad del material no admite decimales, la cantidad por
    # unidad empacada debe ser entera, así el total nunca sale
    # fraccionario.
    def clean(self):
        super().clean()

        if self.material_id and self.cantidad_material is not None:
            unidad = self.material.unidad_medida

            if (
                not unidad.permite_decimales
                and self.cantidad_material % 1 != Decimal("0")
            ):
                raise ValidationError(
                    {
                        "cantidad_material": (
                            f"La unidad «{unidad.nombre}» solo admite "
                            f"cantidades enteras."
                        )
                    }
                )



# ==========================================================
# MODELO: OPERACIÓN DIARIA
#
# Representa el expediente general de una jornada de trabajo
# dentro de la empacadora.
#
# RESPONSABILIDADES:
# - Registrar las jornadas de trabajo.
# - Controlar el inicio y cierre de cada jornada.
# - Identificar a los responsables del inicio y cierre.
# - Impedir que existan dos operaciones diarias vigentes.
# - Mantener la trazabilidad histórica de cada jornada.
# - Preparar las estaciones de trabajo al intentar iniciar.
# - Recuperar las asignaciones de la última operación cerrada.
#
# CICLO DE VIDA:
#
# 1. PENDIENTE:
#    La operación ya fue registrada, pero todavía no inicia.
#    abierta = False
#    iniciada = False
#
# 2. ACTIVA:
#    La operación inició correctamente y puede producir.
#    abierta = True
#    iniciada = True
#
# 3. CERRADA:
#    La operación terminó y no puede reabrirse.
#    abierta = False
#    iniciada = True
#
# REGLAS DE NEGOCIO:
# - Solo puede existir una operación pendiente o activa.
# - Las operaciones cerradas permanecen como historial.
# - Una operación pendiente puede configurarse antes de iniciar.
# - Para iniciar se requiere un LoteEmpaque abierto.
# - Para iniciar debe existir al menos un empleado activo
#   asignado a una estación de trabajo.
# - Todas las estaciones activas se preparan al iniciar.
# - Se recuperan los empleados activos de la última operación
#   cerrada que tenga asignaciones.
# - Si no existe historial, las estaciones quedan sin empleado.
# - Los empleados inactivos no se recuperan.
# - La preparación es idempotente: no duplica estaciones ni
#   sobrescribe asignaciones que ya existan.
# - Al iniciar se crea la relación OperacionLoteEmpaque.
# - La preparación, activación y relación con el lote
#   se ejecutan dentro de una transacción.
# - Una operación cerrada no puede reabrirse.
# - No se permite eliminar físicamente el registro.
#
# RELACIONES:
# - EmpleadosPuestoOperacion administra empleados y estaciones.
# - OperacionLoteEmpaque relaciona la jornada con el lote.
# ==========================================================

class OperacionDiaria(models.Model):

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    fecha = models.DateField(
        default=timezone.localdate,
        verbose_name="Fecha operativa",
    )

    # ------------------------------------------------------
    # ESTADO DE LA OPERACIÓN
    # ------------------------------------------------------

    abierta = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="Abierta",
    )

    iniciada = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="Iniciada",
    )

    # ------------------------------------------------------
    # INFORMACIÓN DE INICIO Y CIERRE
    # ------------------------------------------------------

    hora_apertura = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Hora de inicio",
    )

    hora_cierre = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Hora de cierre",
    )

    abierto_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="operaciones_abiertas",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Iniciada por",
    )

    cerrado_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="operaciones_cerradas",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Cerrada por",
    )

    observaciones = models.TextField(
        blank=True,
        default="",
        verbose_name="Observaciones",
    )

    class Meta:

        db_table = "operacion_diaria"

        verbose_name = "Operación diaria"

        verbose_name_plural = "Operaciones diarias"

        ordering = ["-fecha", "-id"]

        constraints = [

            # Garantiza que no existan dos operaciones activas.
            models.UniqueConstraint(
                fields=["abierta"],
                condition=Q(abierta=True),
                name="una_sola_operacion_abierta",
            ),

            # Garantiza la coherencia de los tres estados.
            models.CheckConstraint(
                check=(
                    # Pendiente de iniciar.
                    Q(
                        abierta=False,
                        iniciada=False,
                        hora_apertura__isnull=True,
                        hora_cierre__isnull=True,
                        abierto_por__isnull=True,
                        cerrado_por__isnull=True,
                    )

                    |

                    # Operación activa.
                    Q(
                        abierta=True,
                        iniciada=True,
                        hora_apertura__isnull=False,
                        hora_cierre__isnull=True,
                        abierto_por__isnull=False,
                        cerrado_por__isnull=True,
                    )

                    |

                    # Operación cerrada.
                    Q(
                        abierta=False,
                        iniciada=True,
                        hora_apertura__isnull=False,
                        hora_cierre__isnull=False,
                        abierto_por__isnull=False,
                        cerrado_por__isnull=False,
                    )
                ),
                name="operacion_estado_horas_coherentes",
            ),

            # El cierre no puede ser anterior al inicio.
            models.CheckConstraint(
                check=(
                    Q(hora_cierre__isnull=True)
                    |
                    (
                        Q(hora_apertura__isnull=False)
                        & Q(hora_cierre__gte=F("hora_apertura"))
                    )
                ),
                name="cierre_posterior_a_apertura",
            ),
        ]

    def __str__(self):

        if self.abierta and self.iniciada:
            estado = "Activa"

        elif self.iniciada and not self.abierta:
            estado = "Cerrada"

        else:
            estado = "Pendiente"

        return f"Operación {self.fecha} - {estado} (#{self.id})"

    # ------------------------------------------------------
    # PROPIEDADES DE ESTADO
    # ------------------------------------------------------

    @property
    def pendiente(self):
        return not self.abierta and not self.iniciada

    @property
    def cerrada(self):
        return self.iniciada and not self.abierta

    @property
    def activa(self):
        return self.abierta and self.iniciada

    # ======================================================
    # PREPARACIÓN DE ESTACIONES DE TRABAJO
    # ======================================================

    def _preparar_estaciones(self, operacion):

        # Obtener el modelo del catálogo relacionado
        # directamente desde el campo estacion_trabajo.
        EstacionTrabajo = (
            EmpleadosPuestoOperacion
            ._meta
            .get_field("estacion_trabajo")
            .remote_field.model
        )

        # Consultar todas las estaciones activas.
        estaciones = list(
            EstacionTrabajo.objects
            .filter(activo=True)
            .order_by("nombre")
        )

        if not estaciones:
            raise ValidationError(
                "No existen estaciones de trabajo activas "
                "en el catálogo."
            )

        # Buscar la última operación diaria cerrada
        # que tenga al menos una asignación de personal.
        operacion_anterior = (
            OperacionDiaria.objects
            .filter(
                iniciada=True,
                abierta=False,
                pk__in=(
                    EmpleadosPuestoOperacion.objects
                    .filter(
                        estacion_trabajo__isnull=False,
                        empleado__isnull=False,
                    )
                    .values("operacion_diaria_id")
                ),
            )
            .exclude(pk=operacion.pk)
            .order_by("-fecha", "-id")
            .first()
        )

        # Diccionario:
        # ID de estación -> ID de empleado activo.
        empleados_por_estacion = {}

        if operacion_anterior:

            asignaciones_anteriores = (
                EmpleadosPuestoOperacion.objects
                .filter(
                    operacion_diaria=operacion_anterior,
                    estacion_trabajo__isnull=False,
                    empleado__isnull=False,
                    empleado__activo=True,
                    empleado__persona__activo=True,
                )
                .values_list(
                    "estacion_trabajo_id",
                    "empleado_id",
                )
            )

            empleados_por_estacion = dict(
                asignaciones_anteriores
            )

        # Consultar las estaciones que ya existen
        # en la operación actual.
        estaciones_existentes = set(
            EmpleadosPuestoOperacion.objects
            .filter(
                operacion_diaria=operacion,
                estacion_trabajo__isnull=False,
            )
            .values_list(
                "estacion_trabajo_id",
                flat=True,
            )
        )

        # Consultar los empleados ya utilizados
        # en la operación actual.
        empleados_existentes = set(
            EmpleadosPuestoOperacion.objects
            .filter(
                operacion_diaria=operacion,
                empleado__isnull=False,
            )
            .values_list(
                "empleado_id",
                flat=True,
            )
        )

        estaciones_creadas = 0

        # Preparar únicamente las estaciones faltantes.
        for estacion in estaciones:

            # No modificar estaciones ya registradas.
            if estacion.pk in estaciones_existentes:
                continue

            # Recuperar el empleado de la operación anterior.
            empleado_id = empleados_por_estacion.get(
                estacion.pk
            )

            # Evitar duplicar un empleado dentro
            # de la operación actual.
            if empleado_id in empleados_existentes:
                empleado_id = None

            # Crear el registro de la estación.
            # Si no hay empleado disponible, queda None.
            asignacion = EmpleadosPuestoOperacion(
                operacion_diaria=operacion,
                estacion_trabajo=estacion,
                empleado_id=empleado_id,
            )

            asignacion.full_clean()
            asignacion.save()

            estaciones_creadas += 1

            estaciones_existentes.add(estacion.pk)

            if empleado_id:
                empleados_existentes.add(empleado_id)

        return estaciones_creadas

    # ======================================================
    # INICIO DE OPERACIÓN
    # ======================================================

    @transaction.atomic
    def iniciar(self, persona, lote_empaque):

        # Recuperar y bloquear el registro para evitar
        # modificaciones concurrentes.
        operacion = (
            OperacionDiaria.objects
            .select_for_update()
            .get(pk=self.pk)
        )

        # La operación debe estar pendiente.
        if not operacion.pendiente:
            raise ValidationError(
                "La operación no está pendiente de iniciar "
                "o ya fue iniciada anteriormente."
            )

        # No permitir otra operación diaria vigente.
        # Se consideran pendientes y activas.
        otra_operacion_vigente = (
            OperacionDiaria.objects
            .filter(
                Q(iniciada=False) | Q(abierta=True)
            )
            .exclude(pk=operacion.pk)
            .exists()
        )

        if otra_operacion_vigente:
            raise ValidationError(
                "Ya existe otra operación diaria pendiente o activa. "
                "Solo puede existir una operación diaria vigente."
            )

        # Bloquear y recuperar el lote de empaque.
        try:

            lote = (
                LoteEmpaque.objects
                .select_for_update()
                .get(pk=lote_empaque.pk)
            )

        except LoteEmpaque.DoesNotExist:

            raise ValidationError(
                "El lote de empaque seleccionado no existe."
            )

        # El lote debe permanecer abierto.
        if not lote.abierto:
            raise ValidationError(
                "El lote de empaque seleccionado está cerrado."
            )

        # No debe existir previamente la relación.
        if OperacionLoteEmpaque.objects.filter(
            operacion_diaria=operacion
        ).exists():

            raise ValidationError(
                "La operación ya tiene una relación con un "
                "lote de empaque."
            )

        # --------------------------------------------------
        # PREPARAR LAS ESTACIONES
        # --------------------------------------------------

        self._preparar_estaciones(operacion)

        # --------------------------------------------------
        # VALIDAR PERSONAL ACTIVO
        # --------------------------------------------------

        tiene_personal = (
            EmpleadosPuestoOperacion.objects
            .filter(
                operacion_diaria=operacion,
                estacion_trabajo__isnull=False,
                empleado__activo=True,
                empleado__persona__activo=True,
            )
            .exists()
        )

        if not tiene_personal:

            # No lanzar excepción porque se deben conservar
            # los registros de estaciones recién preparados.
            # La operación permanece pendiente.
            self.refresh_from_db()

            return False

        # --------------------------------------------------
        # REGISTRAR EL INICIO
        # --------------------------------------------------

        operacion.abierta = True
        operacion.iniciada = True
        operacion.hora_apertura = timezone.now()
        operacion.abierto_por = persona

        # El savepoint permite capturar la restricción
        # de operación activa única.
        try:

            with transaction.atomic():

                operacion.save(
                    update_fields=[
                        "abierta",
                        "iniciada",
                        "hora_apertura",
                        "abierto_por",
                    ]
                )

        except IntegrityError:

            raise ValidationError(
                "No se puede iniciar la operación porque "
                "ya existe otra operación diaria activa."
            )

        # --------------------------------------------------
        # CREAR RELACIÓN CON EL LOTE DE EMPAQUE
        # --------------------------------------------------

        relacion = OperacionLoteEmpaque(
            operacion_diaria=operacion,
            lote_empaque=lote,
        )

        relacion.full_clean()
        relacion.save()

        # Actualizar la instancia original.
        self.refresh_from_db()

        return True

    # ======================================================
    # CIERRE DE OPERACIÓN
    # ======================================================

    @transaction.atomic
    def cerrar(self, persona):

        # Recuperar y bloquear el registro.
        operacion = (
            OperacionDiaria.objects
            .select_for_update()
            .get(pk=self.pk)
        )

        # Solo se puede cerrar una operación activa.
        if not operacion.abierta or not operacion.iniciada:
            raise ValidationError(
                "La operación no está activa."
            )

        if operacion.hora_apertura is None:
            raise ValidationError(
                "La operación no tiene registrada su hora de inicio."
            )

        # Cerrar la operación.
        operacion.abierta = False
        operacion.hora_cierre = timezone.now()
        operacion.cerrado_por = persona

        operacion.save(
            update_fields=[
                "abierta",
                "hora_cierre",
                "cerrado_por",
            ]
        )

        # Actualizar la instancia original.
        self.refresh_from_db()


# ==========================================================
# MODELO: LOTE DE EMPAQUE
#
# Representa una corrida de producción de empaque vinculada
# a un lote de huerta y a una variedad específica de manzana.
#
# RESPONSABILIDADES:
# - Identificar el lote de huerta que se está procesando.
# - Identificar la variedad que se empacará.
# - Registrar el máximo de cajones disponibles al abrir
#   la corrida de producción.
# - Controlar la apertura y cierre de la corrida.
# - Registrar fechas y responsables de apertura y cierre.
# - Mantener la continuidad de una corrida entre diferentes
#   operaciones diarias.
#
# REGLAS DE NEGOCIO:
# - Cada lote de empaque pertenece a un solo LoteHuerta.
# - Cada lote de empaque corresponde a una sola variedad.
# - Un lote de huerta puede tener varios lotes de empaque,
#   incluso de variedades diferentes.
# - Un lote de empaque no puede cambiar su lote de huerta
#   ni su variedad una vez iniciado.
# - Solo puede existir un lote de empaque abierto globalmente.
# - Un lote cerrado no puede reabrirse.
# - No se permite cerrar un lote mientras existan tarimas
#   abiertas relacionadas con él.
# - El máximo de cajones se calcula al abrir la corrida,
#   utilizando las existencias de la variedad seleccionada.
# - El máximo queda como fotografía histórica y no cambia
#   automáticamente por movimientos posteriores del inventario.
# - Cerrar una operación diaria no implica cerrar el
#   lote de empaque.
#
# ==========================================================

class LoteEmpaque(models.Model):

    # ------------------------------------------------------
    # IDENTIFICADOR
    # ------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    # ------------------------------------------------------
    # LOTE DE ORIGEN
    # ------------------------------------------------------

    lote_huerta = models.ForeignKey(
        "fruticultura.LoteHuerta",
        on_delete=models.PROTECT,
        related_name="lotes_empaque",
        verbose_name="Lote de huerta",
    )

    # ------------------------------------------------------
    # VARIEDAD QUE SE EMPACARÁ
    # ------------------------------------------------------

    variedad = models.ForeignKey(
        "fruticultura.Variedad",
        on_delete=models.PROTECT,
        related_name="lotes_empaque",
        verbose_name="Variedad",
    )

    # ------------------------------------------------------
    # EXISTENCIA MÁXIMA AUTORIZADA PARA LA CORRIDA
    # ------------------------------------------------------

    maximo_cajones = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Máximo de cajones disponibles",
    )

    # ------------------------------------------------------
    # ESTADO DE LA CORRIDA
    # ------------------------------------------------------

    abierto = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="Abierto",
    )

    # ------------------------------------------------------
    # CONTROL DE FECHAS
    # ------------------------------------------------------

    fecha_apertura = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Fecha y hora de apertura",
    )

    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Fecha y hora de cierre",
    )

    # ------------------------------------------------------
    # RESPONSABLES
    # ------------------------------------------------------

    abierto_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="lotes_empaque_abiertos",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Abierto por",
    )

    cerrado_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="lotes_empaque_cerrados",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Cerrado por",
    )

    # ------------------------------------------------------
    # OBSERVACIONES
    # ------------------------------------------------------

    observaciones = models.TextField(
        blank=True,
        default="",
        verbose_name="Observaciones",
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN DEL MODELO
    # ------------------------------------------------------

    class Meta:

        db_table = "operaciones_lote_empaque"

        verbose_name = "Lote de empaque"
        verbose_name_plural = "Lotes de empaque"

        ordering = ["-id"]

        constraints = [

            # Garantiza coherencia entre el estado y las fechas.
            models.CheckConstraint(
                condition=(
                    Q(
                        abierto=True,
                        fecha_apertura__isnull=False,
                        fecha_cierre__isnull=True,
                    )
                    |
                    Q(
                        abierto=False,
                        fecha_apertura__isnull=True,
                        fecha_cierre__isnull=True,
                    )
                    |
                    Q(
                        abierto=False,
                        fecha_apertura__isnull=False,
                        fecha_cierre__isnull=False,
                    )
                ),
                name="lote_empaque_estado_fechas",
            ),

            # El cierre nunca puede ser anterior a la apertura.
            models.CheckConstraint(
                condition=(
                    Q(fecha_cierre__isnull=True)
                    | Q(fecha_cierre__gte=F("fecha_apertura"))
                ),
                name="lote_empaque_cierre_posterior",
            ),
        ]

    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def __str__(self):

        return (
            f"Lote de empaque #{self.id} - "
            f"{self.lote_huerta} - "
            f"{self.variedad}"
        )

    # ======================================================
    # ESTADO
    # ======================================================

    @property
    def cerrado(self):

        return self.fecha_cierre is not None

    # ======================================================
    # VALIDACIÓN DE INMUTABILIDAD
    # ======================================================

    def clean(self):

        super().clean()

        if not self.pk:
            return

        original = (
            LoteEmpaque.objects
            .filter(pk=self.pk)
            .only(
                "lote_huerta_id",
                "variedad_id",
                "fecha_apertura",
                "maximo_cajones",
            )
            .first()
        )

        if original is None:
            return

        if original.fecha_apertura is not None:

            errores = {}

            if original.lote_huerta_id != self.lote_huerta_id:

                errores["lote_huerta"] = (
                    "No se puede cambiar el lote de huerta "
                    "una vez iniciado el lote de empaque."
                )

            if original.variedad_id != self.variedad_id:

                errores["variedad"] = (
                    "No se puede cambiar la variedad "
                    "una vez iniciado el lote de empaque."
                )

            if original.maximo_cajones != self.maximo_cajones:

                errores["maximo_cajones"] = (
                    "No se puede modificar el máximo de cajones "
                    "una vez iniciado el lote de empaque."
                )

            if errores:
                raise ValidationError(errores)

    # ======================================================
    # APERTURA DE LA CORRIDA
    # ======================================================

    @transaction.atomic
    def abrir(self, persona):

        if connection.vendor != "mysql":

            raise ValidationError(
                "La apertura requiere MySQL."
            )

        # --------------------------------------------------
        # 1. BLOQUEO GLOBAL PARA EVITAR APERTURAS SIMULTÁNEAS
        # --------------------------------------------------

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT GET_LOCK(%s, 10)",
                ["operaciones_lote_empaque_abierto"],
            )

            resultado_lock = cursor.fetchone()[0]

        if resultado_lock != 1:

            raise ValidationError(
                "No fue posible obtener el bloqueo para "
                "abrir el lote de empaque."
            )

        try:

            # --------------------------------------------------
            # 2. BLOQUEAR Y RECUPERAR EL LOTE DE EMPAQUE
            # --------------------------------------------------

            lote = (
                LoteEmpaque.objects
                .select_for_update()
                .get(pk=self.pk)
            )

            if lote.abierto:

                raise ValidationError(
                    "El lote de empaque ya está abierto."
                )

            if lote.fecha_apertura is not None:

                raise ValidationError(
                    "El lote de empaque ya fue cerrado "
                    "y no puede reabrirse."
                )

            if LoteEmpaque.objects.filter(abierto=True).exists():

                raise ValidationError(
                    "Ya existe otro lote de empaque abierto. "
                    "Debe cerrarse antes de abrir uno nuevo."
                )

            # --------------------------------------------------
            # 3. CONSULTAR EXISTENCIAS DEL LOTE AGRÍCOLA
            # --------------------------------------------------

            ExistenciaFruta = apps.get_model(
                "inventarioFruta",
                "ExistenciaFruta",
            )

            existencias = list(
                ExistenciaFruta.objects
                .select_for_update()
                .filter(
                    lote_huerta_id=lote.lote_huerta_id,
                    cantidad_cajones__gt=0,
                )
                .values_list(
                    "cliente_id",
                    "variedad_id",
                    "cantidad_cajones",
                )
            )

            if not existencias:

                raise ValidationError(
                    "El lote agrícola ya no tiene fruta "
                    "disponible en inventario."
                )

            # --------------------------------------------------
            # 4. VALIDAR PROPIETARIO ÚNICO DEL LOTE
            # --------------------------------------------------

            clientes = {
                cliente_id
                for cliente_id, variedad_id, cantidad
                in existencias
            }

            if len(clientes) != 1:

                raise ValidationError(
                    "El lote agrícola tiene existencias de varios "
                    "clientes. No es posible determinar un "
                    "propietario único."
                )

            # --------------------------------------------------
            # 5. CALCULAR EXISTENCIA DE LA VARIEDAD SELECCIONADA
            # --------------------------------------------------

            maximo_cajones = sum(
                cantidad
                for cliente_id, variedad_id, cantidad
                in existencias
                if variedad_id == lote.variedad_id
            )

            if maximo_cajones <= 0:

                raise ValidationError(
                    "La variedad seleccionada ya no tiene "
                    "cajones disponibles en inventario."
                )

            # --------------------------------------------------
            # 6. REGISTRAR APERTURA Y MÁXIMO AUTORIZADO
            # --------------------------------------------------

            lote.maximo_cajones = maximo_cajones
            lote.abierto = True
            lote.fecha_apertura = timezone.now()
            lote.abierto_por = persona

            lote.save(
                update_fields=[
                    "maximo_cajones",
                    "abierto",
                    "fecha_apertura",
                    "abierto_por",
                ]
            )

            self.refresh_from_db()

        finally:

            # Liberar bloqueo MySQL.
            with connection.cursor() as cursor:

                cursor.execute(
                    "SELECT RELEASE_LOCK(%s)",
                    ["operaciones_lote_empaque_abierto"],
                )

    # ======================================================
    # CIERRE DE LA CORRIDA
    # ======================================================

    @transaction.atomic
    def cerrar(self, persona):

        # --------------------------------------------------
        # 1. BLOQUEAR Y RECUPERAR EL LOTE
        # --------------------------------------------------

        lote = (
            LoteEmpaque.objects
            .select_for_update()
            .get(pk=self.pk)
        )

        if not lote.abierto:

            raise ValidationError(
                "El lote de empaque no está abierto."
            )

        if lote.fecha_apertura is None:

            raise ValidationError(
                "El lote de empaque no tiene registrada "
                "su fecha de apertura."
            )

        # --------------------------------------------------
        # 2. OBTENER MODELOS RELACIONADOS
        # --------------------------------------------------

        OperacionLoteEmpaque = apps.get_model(
            "operaciones",
            "OperacionLoteEmpaque",
        )

        Tarima = apps.get_model(
            "operaciones",
            "Tarima",
        )

        # --------------------------------------------------
        # 3. BLOQUEAR RELACIONES DEL LOTE
        #
        # Tarima.crear() también bloquea la relación
        # OperacionLoteEmpaque mediante select_for_update().
        # Esto evita que se cree una tarima concurrentemente
        # durante el cierre del lote.
        # --------------------------------------------------

        relaciones = (
            OperacionLoteEmpaque.objects
            .select_for_update()
            .filter(
                lote_empaque_id=lote.pk,
            )
            .order_by("pk")
        )

        # Ejecutar la consulta y adquirir los bloqueos.
        list(
            relaciones.values_list(
                "pk",
                flat=True,
            )
        )

        # --------------------------------------------------
        # 4. CONSULTAR Y BLOQUEAR TARIMAS ABIERTAS
        #
        # La relación es indirecta:
        # LoteEmpaque -> OperacionLoteEmpaque -> Tarima.
        # --------------------------------------------------

        tarimas_abiertas = list(
            Tarima.objects
            .select_for_update()
            .filter(
                operacion_lote_empaque__lote_empaque_id=lote.pk,
                abierta=True,
            )
            .order_by("pk")
            .values_list(
                "pk",
                flat=True,
            )
        )

        cantidad_tarimas_abiertas = len(tarimas_abiertas)

        # --------------------------------------------------
        # 5. IMPEDIR EL CIERRE SI EXISTEN TARIMAS ABIERTAS
        # --------------------------------------------------

        if cantidad_tarimas_abiertas > 0:

            raise ValidationError(
                (
                    "No se puede cerrar el LoteEmpaque. "
                    f"Existen {cantidad_tarimas_abiertas} "
                    "tarima(s) que todavía están abiertas. "
                    "Cierre primero todas las tarimas."
                )
            )

        # --------------------------------------------------
        # 6. REGISTRAR CIERRE
        # --------------------------------------------------

        lote.abierto = False
        lote.fecha_cierre = timezone.now()
        lote.cerrado_por = persona

        lote.save(
            update_fields=[
                "abierto",
                "fecha_cierre",
                "cerrado_por",
            ]
        )

        self.refresh_from_db()

        return self

# ==========================================================
# MODELO: OPERACIÓN - LOTE DE EMPAQUE
#
# Representa la participación de un lote de empaque dentro
# de una operación diaria de la empacadora.
#
# RESPONSABILIDADES:
# - Relacionar una jornada de trabajo con una corrida
#   específica de empaque.
# - Identificar en qué jornada se trabajó cada corrida.
# - Servir como referencia para las tarimas generadas
#   durante esa combinación de jornada y corrida.
#
# REGLAS DE NEGOCIO:
# - Cada registro relaciona una operación diaria y un
#   lote de empaque.
# - No se permiten combinaciones duplicadas.
# - La operación diaria debe estar abierta al crear
#   la relación.
# - El lote de empaque debe estar abierto al crear
#   la relación.
# - La relación no debe eliminarse si existen tarimas.
#
# RELACIONES:
# - OperacionDiaria: identifica la jornada.
# - LoteEmpaque: identifica la corrida de producción.
# - Tarima: utiliza esta relación para identificar
#   la jornada y corrida a las que pertenece.
#
# Este modelo no administra producción ni inventario.
# ==========================================================

class OperacionLoteEmpaque(models.Model):

    # ------------------------------------------------------
    # IDENTIFICADOR
    # ------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    # ------------------------------------------------------
    # JORNADA DE TRABAJO
    # ------------------------------------------------------

    operacion_diaria = models.ForeignKey(
        "operaciones.OperacionDiaria",
        on_delete=models.PROTECT,
        related_name="lotes_empaque",
        verbose_name="Operación diaria",
    )

    # ------------------------------------------------------
    # CORRIDA DE PRODUCCIÓN
    # ------------------------------------------------------

    lote_empaque = models.ForeignKey(
        "operaciones.LoteEmpaque",
        on_delete=models.PROTECT,
        related_name="operaciones_diarias",
        verbose_name="Lote de empaque",
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN DEL MODELO
    # ------------------------------------------------------

    class Meta:

        db_table = "operaciones_operacion_lote_empaque"

        verbose_name = "Operación y lote de empaque"
        verbose_name_plural = "Operaciones y lotes de empaque"

        ordering = ["-id"]

        constraints = [

            # Evita registrar dos veces la misma combinación.
            models.UniqueConstraint(
                fields=[
                    "operacion_diaria",
                    "lote_empaque",
                ],
                name="uq_operacion_lote_empaque",
            ),
        ]

    def __str__(self):

        return (
            f"Operación #{self.operacion_diaria_id} - "
            f"Lote de empaque #{self.lote_empaque_id}"
        )

    # ======================================================
    # VALIDACIONES
    # ======================================================

    def clean(self):

        super().clean()

        if not self.operacion_diaria_id or not self.lote_empaque_id:
            return

        if not self.operacion_diaria.abierta:
            raise ValidationError({
                "operacion_diaria": (
                    "La operación diaria debe estar abierta "
                    "para asociar un lote de empaque."
                )
            })

        if not self.lote_empaque.abierto:
            raise ValidationError({
                "lote_empaque": (
                    "El lote de empaque debe estar abierto "
                    "para asociarlo a una operación diaria."
                )
            })


# ==========================================================
# MODELO: TARIMA
#
# Representa una unidad física destinada a agrupar las cajas
# empacadas durante una jornada y una corrida de producción.
#
# RESPONSABILIDADES:
# - Identificar físicamente una tarima mediante CodigoTarima.
# - Asociar la tarima con una OperacionLoteEmpaque.
# - Controlar su apertura y cierre.
# - Registrar su capacidad máxima capturada al crearla.
# - Registrar quién abrió y quién cerró la tarima.
# - Registrar su ubicación física en el almacén.
#
# REGLAS DE NEGOCIO:
# - Cada tarima utiliza un código técnico único.
# - Cada tarima pertenece a una sola OperacionLoteEmpaque.
# - La capacidad máxima es obligatoria y debe ser mayor a cero.
# - No se permite superar la capacidad de la tarima.
# - El número de cajas se obtiene de DesgloseOperacion.
# - Una tarima cerrada no puede reabrirse.
# - Una tarima cerrada no admite nuevas cajas.
# - Una tarima puede cerrarse aunque no esté completa.
# - La ubicación de almacén puede modificarse incluso
#   después de cerrar la tarima.
# - El código técnico se marca como utilizado al crear
#   y asignar la tarima.
#
# ==========================================================

class Tarima(models.Model):

    # ------------------------------------------------------
    # IDENTIFICADOR
    # ------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    # ------------------------------------------------------
    # CÓDIGO ÚNICO DE TARIMA
    # ------------------------------------------------------

    codigo_tarima = models.OneToOneField(
        "catalogoConfiguracion.CodigoTarima",
        on_delete=models.PROTECT,
        related_name="tarima",
        verbose_name="Código de tarima",
    )

    # ------------------------------------------------------
    # RELACIÓN CON LA JORNADA Y CORRIDA
    # ------------------------------------------------------

    operacion_lote_empaque = models.ForeignKey(
        "operaciones.OperacionLoteEmpaque",
        on_delete=models.PROTECT,
        related_name="tarimas",
        verbose_name="Operación y lote de empaque",
    )

    # ------------------------------------------------------
    # RELACIÓN CON CATÁLOGO TAMAÑO
    # ------------------------------------------------------

    tamano = models.ForeignKey(
        "catalogos.Tamano",
        on_delete=models.PROTECT,
        related_name="tarimas",
        null=True,
        blank=True,
        verbose_name="Tamaño",
    )

    # ------------------------------------------------------
    # FECHA DE CREACIÓN
    # ------------------------------------------------------

    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Fecha y hora de creación",
    )

    # ------------------------------------------------------
    # CAPACIDAD
    # ------------------------------------------------------

    capacidad_maxima = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="Capacidad máxima de cajas",
    )

    # ------------------------------------------------------
    # ESTADO
    # ------------------------------------------------------

    abierta = models.BooleanField(
        default=True,
        editable=False,
        verbose_name="Abierta",
    )

    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Fecha y hora de cierre",
    )

    # ------------------------------------------------------
    # RESPONSABLES
    # ------------------------------------------------------

    abierta_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="tarimas_abiertas",
        verbose_name="Abierta por",
    )

    cerrada_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="tarimas_cerradas",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Cerrada por",
    )

    # ------------------------------------------------------
    # UBICACIÓN EN ALMACÉN
    # ------------------------------------------------------

    seccion_almacen = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="tarimas",
        null=True,
        blank=True,
        verbose_name="Sección de almacén",
    )
    # Operación comercial a la que fue asignada la tarima.
    # Si se libera o cancela la asignación, queda sin relación.
    operacion_comercial = models.ForeignKey(
        "negocio.OperacionComercial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tarimas",
        verbose_name="Operación comercial"
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN DEL MODELO
    # ------------------------------------------------------

    class Meta:

        db_table = "operaciones_tarima"

        verbose_name = "Tarima"
        verbose_name_plural = "Tarimas"

        ordering = ["-fecha_creacion", "-id"]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        abierta=True,
                        fecha_cierre__isnull=True,
                        cerrada_por__isnull=True,
                    )
                    |
                    models.Q(
                        abierta=False,
                        fecha_cierre__isnull=False,
                        cerrada_por__isnull=False,
                    )
                ),
                name="ck_tarima_estado_cierre",
            ),
        ]

    def __str__(self):

        return (
            f"Tarima {self.codigo_tarima.consecutivo:02d} - "
            f"{self.codigo_tarima.codigo_tarima}"
        )

    # ======================================================
    # CONTROL DE CAJAS
    # ======================================================

    @property
    def total_cajas(self):

        return self.cajas.count()

    @property
    def espacios_disponibles(self):

        return max(
            self.capacidad_maxima - self.total_cajas,
            0,
        )

    # ======================================================
    # VALIDACIONES
    # ======================================================

    def clean(self):

        super().clean()

        if not self.pk:
            return

        original = Tarima.objects.filter(
            pk=self.pk
        ).first()

        if original is None:
            return

        # Una tarima cerrada nunca puede volver a abrirse.
        if not original.abierta and self.abierta:

            raise ValidationError({
                "abierta": (
                    "Una tarima cerrada no puede reabrirse."
                )
            })

        # No se permite cambiar el código ni la operación
        # a la que pertenece una tarima existente.
        if original.codigo_tarima_id != self.codigo_tarima_id:

            raise ValidationError({
                "codigo_tarima": (
                    "No se puede cambiar el código de una tarima existente."
                )
            })

        if (
            original.operacion_lote_empaque_id
            != self.operacion_lote_empaque_id
        ):

            raise ValidationError({
                "operacion_lote_empaque": (
                    "No se puede cambiar la operación y lote "
                    "de una tarima existente."
                )
            })

    # ======================================================
    # CREACIÓN Y ASIGNACIÓN DEL CÓDIGO
    # ======================================================

    @classmethod
    @transaction.atomic
    def crear(
        cls,
        codigo_tarima,
        operacion_lote_empaque,
        persona,
        capacidad_maxima,
    ):

        # --------------------------------------------------
        # BLOQUEAR CÓDIGO
        # --------------------------------------------------

        codigo = (
            CodigoTarima.objects
            .select_for_update()
            .get(pk=codigo_tarima.pk)
        )

        if codigo.usado:

            raise ValidationError(
                "El código de tarima ya fue utilizado."
            )

        # --------------------------------------------------
        # VALIDAR OPERACIÓN Y LOTE
        # --------------------------------------------------

        relacion = (
            OperacionLoteEmpaque.objects
            .select_for_update()
            .get(pk=operacion_lote_empaque.pk)
        )

        if not relacion.operacion_diaria.abierta:

            raise ValidationError(
                "La operación diaria está cerrada."
            )

        if not relacion.lote_empaque.abierto:

            raise ValidationError(
                "El lote de empaque está cerrado."
            )

        # --------------------------------------------------
        # VALIDAR CAPACIDAD
        # --------------------------------------------------

        if capacidad_maxima is None or capacidad_maxima < 1:

            raise ValidationError({
                "capacidad_maxima": (
                    "La capacidad máxima debe ser mayor a cero."
                )
            })

        # --------------------------------------------------
        # MARCAR CÓDIGO COMO UTILIZADO
        # --------------------------------------------------

        codigo.usado = True

        codigo.save(
            update_fields=["usado"]
        )

        # --------------------------------------------------
        # CREAR TARIMA
        # --------------------------------------------------

        tarima = cls(
            codigo_tarima=codigo,
            operacion_lote_empaque=relacion,
            abierta_por=persona,
            capacidad_maxima=capacidad_maxima,
            abierta=True,
        )

        tarima.full_clean()
        tarima.save()

        return tarima

    # ======================================================
    # CIERRE DE TARIMA
    # ======================================================

    @transaction.atomic
    def cerrar(self, persona):

        tarima = (
            Tarima.objects
            .select_for_update()
            .get(pk=self.pk)
        )

        if not tarima.abierta:

            raise ValidationError(
                "La tarima ya está cerrada."
            )

        tarima.abierta = False
        tarima.fecha_cierre = timezone.now()
        tarima.cerrada_por = persona

        tarima.save(
            update_fields=[
                "abierta",
                "fecha_cierre",
                "cerrada_por",
            ]
        )

        self.refresh_from_db()

        return self

# ==========================================================
# MODELO: DESGLOSE DE OPERACIÓN
#
# Representa una caja física individual producida durante
# una operación de empaque.
#
# RESPONSABILIDADES:
# - Identificar cada caja mediante un CodigoCaja único.
# - Registrar el producto de empaque utilizado.
# - Conservar la calidad seleccionada por el operador.
# - Conservar el tamaño correspondiente al producto.
# - Registrar la variedad del lote de empaque.
# - Identificar la tarima a la que pertenece la caja.
# - Registrar la estación y el empleado responsables.
# - Registrar automáticamente la fecha y hora de captura.
# - Conservar el precio individual de la caja cuando exista.
# - Mantener el historial de cajas canceladas.
#
# REGLAS DE NEGOCIO:
# - Cada registro representa una sola caja física.
# - Cada CodigoCaja puede utilizarse una sola vez.
# - El código no se libera aunque la caja sea cancelada.
# - La tarima determina la operación diaria y el lote
#   de empaque al que pertenece la caja.
# - La variedad se obtiene del LoteEmpaque y se conserva
#   directamente en este registro.
# - El tamaño se obtiene del ProductoEmpaque y se conserva
#   directamente en este registro.
# - La calidad se selecciona independientemente por el operador.
# - El empleado y la estación quedan registrados como
#   información histórica de la caja.
# - Una tarima no puede superar su capacidad de 50 cajas.
# - No se permite eliminar físicamente una caja.
# - Una caja cancelada conserva todos sus datos originales.
#
# RELACIONES:
# - CodigoCaja: código técnico de uso único.
# - ProductoEmpaque: presentación empacada.
# - Calidad: calidad seleccionada por el operador.
# - Tamano: tamaño histórico de la caja.
# - Variedad: variedad del lote de empaque.
# - Tarima: unidad física que contiene la caja.
# - EstacionTrabajo: estación donde se empacó.
# - Empleado: responsable del empaque.
# - Persona: responsable de una eventual cancelación.
#
# El modelo no administra directamente el inventario.
# El consumo de materiales corresponde al flujo de registro
# de producción, utilizando el BOM de ProductoEmpaque.
# ==========================================================

class DesgloseOperacion(models.Model):

    # ------------------------------------------------------
    # IDENTIFICADOR
    # ------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    # ------------------------------------------------------
    # CÓDIGO ÚNICO DE CAJA
    # ------------------------------------------------------

    codigo_caja = models.OneToOneField(
        "catalogoConfiguracion.CodigoCaja",
        on_delete=models.PROTECT,
        related_name="desglose_operacion",
        verbose_name="Código de caja",
    )

    # ------------------------------------------------------
    # PRODUCTO DE EMPAQUE
    # ------------------------------------------------------

    producto_empaque = models.ForeignKey(
        "operaciones.ProductoEmpaque",
        on_delete=models.PROTECT,
        related_name="cajas_empacadas",
        verbose_name="Producto de empaque",
    )

    # ------------------------------------------------------
    # CLASIFICACIÓN DE LA CAJA
    # ------------------------------------------------------

    calidad = models.ForeignKey(
        "catalogos.Calidad",
        on_delete=models.PROTECT,
        related_name="cajas_empacadas",
        verbose_name="Calidad",
    )

    tamano = models.ForeignKey(
        "catalogos.Tamano",
        on_delete=models.PROTECT,
        related_name="cajas_empacadas",
        verbose_name="Tamaño",
    )

    variedad = models.ForeignKey(
        "fruticultura.Variedad",
        on_delete=models.PROTECT,
        related_name="cajas_empacadas",
        verbose_name="Variedad",
    )

    # ------------------------------------------------------
    # TARIMA
    # ------------------------------------------------------

    tarima = models.ForeignKey(
        "operaciones.Tarima",
        on_delete=models.PROTECT,
        related_name="cajas",
        verbose_name="Tarima",
    )

    # ------------------------------------------------------
    # RESPONSABLES DE PRODUCCIÓN
    # ------------------------------------------------------

    estacion_trabajo = models.ForeignKey(
        "catalogos.EstacionTrabajo",
        on_delete=models.PROTECT,
        related_name="cajas_empacadas",
        verbose_name="Estación de trabajo",
    )

    empleado = models.ForeignKey(
        "personas.Empleado",
        on_delete=models.PROTECT,
        related_name="cajas_empacadas",
        verbose_name="Empleado responsable",
    )

    # ------------------------------------------------------
    # FECHA DE REGISTRO
    # ------------------------------------------------------

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Fecha y hora de registro",
    )

    # ------------------------------------------------------
    # PRECIO INDIVIDUAL
    # ------------------------------------------------------

    precio_caja = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=None,
        verbose_name="Precio por caja",
    )

    # ------------------------------------------------------
    # CANCELACIÓN
    # ------------------------------------------------------

    cancelada = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="Cancelada",
    )

    fecha_cancelacion = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Fecha y hora de cancelación",
    )

    cancelada_por = models.ForeignKey(
        "personas.Persona",
        on_delete=models.PROTECT,
        related_name="cajas_canceladas",
        null=True,
        blank=True,
        editable=False,
        verbose_name="Cancelada por",
    )

    motivo_cancelacion = models.TextField(
        blank=True,
        default="",
        verbose_name="Motivo de cancelación",
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN
    # ------------------------------------------------------

    class Meta:

        db_table = "operaciones_desglose_operacion"

        verbose_name = "Caja empacada"
        verbose_name_plural = "Cajas empacadas"

        ordering = ["-fecha_registro", "-id"]

        indexes = [
            models.Index(
                fields=["tarima", "cancelada"],
                name="idx_desg_tarima_cancel",
            ),
            models.Index(
                fields=["fecha_registro"],
                name="idx_desg_fecha",
            ),
            models.Index(
                fields=["variedad", "tamano", "calidad"],
                name="idx_desg_clasificacion",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(precio_caja__isnull=True)
                    | models.Q(precio_caja__gte=0)
                ),
                name="ck_desg_precio_no_negativo",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        cancelada=False,
                        fecha_cancelacion__isnull=True,
                        cancelada_por__isnull=True,
                    )
                    |
                    models.Q(
                        cancelada=True,
                        fecha_cancelacion__isnull=False,
                        cancelada_por__isnull=False,
                    )
                ),
                name="ck_desg_estado_cancelacion",
            ),
        ]

    def __str__(self):

        return (
            f"Caja {self.codigo_caja.codigo} - "
            f"{self.producto_empaque.nombre}"
        )

    # ======================================================
    # VALIDACIONES
    # ======================================================

    def clean(self):

        super().clean()

        errores = {}

        # El tamaño debe corresponder al producto seleccionado.
        if (
            self.producto_empaque_id
            and self.tamano_id
            and self.producto_empaque.tamano_id != self.tamano_id
        ):
            errores["tamano"] = (
                "El tamaño debe corresponder al producto de empaque."
            )

        # La variedad debe corresponder al lote de empaque
        # asociado a la operación de la tarima.
        if self.tarima_id and self.variedad_id:

            variedad_lote = (
                self.tarima.operacion_lote_empaque
                .lote_empaque.variedad_id
            )

            if variedad_lote != self.variedad_id:
                errores["variedad"] = (
                    "La variedad no corresponde al lote de empaque "
                    "de la tarima seleccionada."
                )

        if self.precio_caja is not None and self.precio_caja < 0:
            errores["precio_caja"] = (
                "El precio de la caja no puede ser negativo."
            )

        if errores:
            raise ValidationError(errores)



# ==========================================================
# MODELO: EMPLEADOS PUESTO OPERACIÓN
#
# Registra qué empleado participa en una operación diaria
# y en qué estación de trabajo desempeña sus actividades.
#
# RESPONSABILIDADES:
# - Asociar un empleado con una operación diaria.
# - Asignar una estación de trabajo al empleado.
# - Permitir liberar una estación sin eliminar la asignación.
# - Permitir cambiar la estación actualizando el mismo registro.
#
# REGLAS DE NEGOCIO:
# - Cada empleado puede tener una sola asignación por
#   operación diaria.
# - Cada estación puede estar asignada a un solo empleado
#   dentro de una operación diaria.
# - La estación puede ser NULL cuando el empleado no tiene
#   una estación asignada temporalmente.
# - Una estación liberada puede asignarse a otro empleado.
# - Cambiar de estación actualiza el registro existente.
# - No se conserva historial de cambios de estación.
# - No se permiten nuevas asignaciones en operaciones
#   diarias cerradas.
# - La asignación pertenece a una sola operación diaria.
#
# RELACIONES:
# - OperacionDiaria: jornada de trabajo.
# - Empleado: trabajador participante.
# - EstacionTrabajo: lugar físico donde desempeña
#   sus actividades.
#
# Este modelo no administra asistencia, horarios laborales
# ni incidencias del empleado.
# ==========================================================

class EmpleadosPuestoOperacion(models.Model):

    # ------------------------------------------------------
    # IDENTIFICADOR
    # ------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
    )

    # ------------------------------------------------------
    # OPERACIÓN DIARIA
    # ------------------------------------------------------

    operacion_diaria = models.ForeignKey(
        "operaciones.OperacionDiaria",
        on_delete=models.PROTECT,
        related_name="empleados_puestos",
        verbose_name="Operación diaria",
    )

    # ------------------------------------------------------
    # EMPLEADO
    # ------------------------------------------------------

    empleado = models.ForeignKey(
        "personas.Empleado",
        on_delete=models.PROTECT,
        related_name="asignaciones_operacion",
        null=True,
        blank=True,
        verbose_name="Empleado",
    )

    # ------------------------------------------------------
    # ESTACIÓN DE TRABAJO
    # ------------------------------------------------------

    estacion_trabajo = models.ForeignKey(
        "catalogos.EstacionTrabajo",
        on_delete=models.PROTECT,
        related_name="asignaciones_operacion",
        null=True,
        blank=True,
        verbose_name="Estación de trabajo",
    )

    # ------------------------------------------------------
    # FECHA DE ASIGNACIÓN
    # ------------------------------------------------------

    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Fecha y hora de asignación",
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN DEL MODELO
    # ------------------------------------------------------

    class Meta:

        db_table = "operaciones_empleados_puesto_operacion"

        verbose_name = "Asignación de empleado a operación"
        verbose_name_plural = "Asignaciones de empleados a operaciones"

        ordering = [
            "operacion_diaria",
            "estacion_trabajo",
            "empleado",
        ]

        constraints = [

            # Un empleado solamente puede tener un registro
            # dentro de la misma operación diaria.
            models.UniqueConstraint(
                fields=[
                    "operacion_diaria",
                    "empleado",
                ],
                name="uq_empleado_operacion_diaria",
            ),

            # Una estación solamente puede pertenecer a un
            # empleado dentro de la misma operación diaria.
            # Las asignaciones sin estación no participan
            # en esta restricción.
            models.UniqueConstraint(
                fields=[
                    "operacion_diaria",
                    "estacion_trabajo",
                ],
                condition=Q(estacion_trabajo__isnull=False),
                name="uq_estacion_operacion_diaria",
            ),
        ]

        indexes = [
            models.Index(
                fields=["operacion_diaria", "estacion_trabajo"],
                name="idx_emp_puesto_operacion",
            ),
        ]

    def __str__(self):

        estacion = (
            str(self.estacion_trabajo)
            if self.estacion_trabajo_id
            else "Sin estación asignada"
        )

        return (
            f"{self.empleado} - {estacion} - "
            f"{self.operacion_diaria}"
        )

    # ======================================================
    # VALIDACIONES
    # ======================================================

    def clean(self):

        super().clean()

        if self.operacion_diaria_id:

            operacion = self.operacion_diaria

            if operacion.cerrada:
                raise ValidationError({
                    "operacion_diaria": (
                        "No se pueden modificar asignaciones "
                        "de una operación diaria cerrada."
                    )
                })
