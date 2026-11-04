
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone


# ============================================================
# MODELO: RECEPCIÓN DE FRUTA
#
# Registra las entradas físicas de fruta a la empacadora,
# identificando cliente, lote agrícola, variedad, fecha de
# pizca y cantidad recibida.
#
# Permite distribuir la fruta entre diferentes secciones
# y estibas mediante DetalleRecepcionFruta.
#
# Al confirmar la recepción se generan los movimientos
# de entrada correspondientes y se actualizan las existencias.
#
# Una recepción procesada no puede modificarse. Las
# correcciones deben realizarse mediante movimientos.
#
# ============================================================

class RecepcionFruta(models.Model):

    id = models.BigAutoField(primary_key=True)

    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="recepciones_fruta",
        verbose_name="Cliente",
    )

    lote_huerta = models.ForeignKey(
        "fruticultura.LoteHuerta",
        on_delete=models.PROTECT,
        related_name="recepciones_fruta",
        verbose_name="Lote agrícola",
    )

    variedad = models.ForeignKey(
        "fruticultura.Variedad",
        on_delete=models.PROTECT,
        related_name="recepciones_fruta",
        verbose_name="Variedad",
    )

    fecha_pizca = models.DateField(
        verbose_name="Fecha de pizca",
    )

    cantidad_cajones = models.PositiveIntegerField(
        verbose_name="Cantidad de cajones",
    )

    fecha_recepcion = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de recepción",
    )

    recibido_por = models.ForeignKey(
        "personas.Empleado",
        on_delete=models.PROTECT,
        related_name="recepciones_fruta",
        verbose_name="Recibido por",
    )

    observaciones = models.TextField(
        blank=True,
        default="",
        verbose_name="Observaciones",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creado en",
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recepciones_fruta_registradas",
        verbose_name="Registrado por",
    )

    class Meta:
        db_table = "inventario_fruta_recepcion"
        verbose_name = "Recepción de fruta"
        verbose_name_plural = "Recepciones de fruta"
        ordering = ["-fecha_recepcion", "-id"]

        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad_cajones__gt=0),
                name="ck_recepcion_fruta_cantidad_positiva",
            ),
        ]

        indexes = [
            models.Index(
                fields=["cliente", "fecha_recepcion"],
                name="ix_recepcion_fruta_cliente",
            ),
            models.Index(
                fields=["lote_huerta", "fecha_pizca"],
                name="ix_recepcion_fruta_lote_pizca",
            ),
            models.Index(
                fields=["variedad", "fecha_recepcion"],
                name="ix_recepcion_fruta_variedad",
            ),
        ]

    def __str__(self):
        return (
            f"Recepción {self.id} - {self.cliente} - "
            f"{self.variedad} - {self.cantidad_cajones} cajones"
        )

    def clean(self):
        super().clean()

        errores = {}

        if self.cliente_id and self.lote_huerta_id:

            asignacion_valida = (
                self.cliente.huertas_asignadas.filter(
                    huerta_id=self.lote_huerta.huerta_id
                ).exists()
            )

            if not asignacion_valida:
                errores["lote_huerta"] = (
                    "El lote agrícola no pertenece a una huerta "
                    "asignada al cliente."
                )

        if self.variedad_id and not self.variedad.activo:
            errores["variedad"] = (
                "No se puede registrar una recepción con "
                "una variedad inactiva."
            )

        if (
            self.cantidad_cajones is not None
            and self.cantidad_cajones <= 0
        ):
            errores["cantidad_cajones"] = (
                "La cantidad debe ser mayor que cero."
            )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):

        if not self._state.adding:

            procesada = MovimientoFruta.objects.filter(
                detalle_recepcion__recepcion_id=self.pk,
                tipo=MovimientoFruta.Tipo.RECEPCION,
            ).exists()

            if procesada:
                raise ValidationError(
                    "La recepción ya fue procesada y "
                    "no puede modificarse."
                )

        self.full_clean()
        super().save(*args, **kwargs)

    def confirmar(self):
        """
        Genera un movimiento de entrada por cada detalle
        de distribución. La operación es atómica.
        """

        with transaction.atomic():

            recepcion = (
                RecepcionFruta.objects
                .select_for_update()
                .get(pk=self.pk)
            )

            # Serializar también las operaciones del lote agrícola.
            from fruticultura.models import LoteHuerta

            LoteHuerta.objects.select_for_update().get(
                pk=recepcion.lote_huerta_id
            )

            detalles = list(
                recepcion.detalles.select_related(
                    "seccion",
                    "estiba",
                ).all()
            )

            if not detalles:
                raise ValidationError(
                    "La recepción debe tener al menos "
                    "una distribución."
                )

            total_distribuido = sum(
                detalle.cantidad_cajones
                for detalle in detalles
            )

            if total_distribuido != recepcion.cantidad_cajones:
                raise ValidationError(
                    "La suma de los cajones distribuidos "
                    "debe coincidir con la cantidad recibida."
                )

            if MovimientoFruta.objects.filter(
                detalle_recepcion__recepcion_id=recepcion.pk,
                tipo=MovimientoFruta.Tipo.RECEPCION,
            ).exists():

                raise ValidationError(
                    "Esta recepción ya fue procesada."
                )

            for detalle in detalles:

                MovimientoFruta.objects.create(
                    tipo=MovimientoFruta.Tipo.RECEPCION,
                    cliente=recepcion.cliente,
                    lote_huerta=recepcion.lote_huerta,
                    variedad=recepcion.variedad,
                    fecha_pizca=recepcion.fecha_pizca,
                    cantidad_cajones=detalle.cantidad_cajones,
                    seccion_destino=detalle.seccion,
                    estiba_destino=detalle.estiba,
                    detalle_recepcion=detalle,
                    fecha=recepcion.fecha_recepcion,
                    responsable=recepcion.recibido_por,
                    creado_por=recepcion.creado_por,
                    descripcion=(
                        f"Entrada correspondiente a la "
                        f"recepción {recepcion.pk}."
                    ),
                )

            return len(detalles)


# ============================================================
# MODELO: DETALLE DE RECEPCIÓN DE FRUTA
#
# Distribuye la cantidad recibida entre secciones y estibas.
#
# No permite duplicar ubicaciones dentro de una recepción
# ni modificar o eliminar distribuciones procesadas.
#
# ============================================================

class DetalleRecepcionFruta(models.Model):

    id = models.BigAutoField(primary_key=True)

    recepcion = models.ForeignKey(
        RecepcionFruta,
        on_delete=models.PROTECT,
        related_name="detalles",
        verbose_name="Recepción",
    )

    seccion = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="detalles_recepcion_fruta",
        verbose_name="Sección",
    )

    estiba = models.ForeignKey(
        "almacenes.Estiba",
        on_delete=models.PROTECT,
        related_name="detalles_recepcion_fruta",
        null=True,
        blank=True,
        verbose_name="Estiba",
    )

    cantidad_cajones = models.PositiveIntegerField(
        verbose_name="Cantidad de cajones",
    )

    class Meta:
        db_table = "inventario_fruta_detalle_recepcion"
        verbose_name = "Distribución de recepción"
        verbose_name_plural = "Distribuciones de recepción"
        ordering = ["id"]

        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad_cajones__gt=0),
                name="ck_detalle_fruta_cantidad_positiva",
            ),
        ]

    def __str__(self):
        return (
            f"Recepción {self.recepcion_id} - "
            f"{self.seccion} - {self.cantidad_cajones} cajones"
        )

    def clean(self):
        super().clean()

        errores = {}

        if self.estiba_id and self.seccion_id:

            if self.estiba.seccion_id != self.seccion_id:
                errores["estiba"] = (
                    "La estiba no pertenece a la sección indicada."
                )

        if (
            self.cantidad_cajones is not None
            and self.cantidad_cajones <= 0
        ):
            errores["cantidad_cajones"] = (
                "La cantidad debe ser mayor que cero."
            )

        if self.recepcion_id and self.seccion_id:

            duplicado = (
                DetalleRecepcionFruta.objects.filter(
                    recepcion_id=self.recepcion_id,
                    seccion_id=self.seccion_id,
                    estiba_id=self.estiba_id,
                )
                .exclude(pk=self.pk)
                .exists()
            )

            if duplicado:
                errores["__all__"] = (
                    "Ya existe una distribución para esta "
                    "sección y estiba dentro de la recepción."
                )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):

        with transaction.atomic():

            RecepcionFruta.objects.select_for_update().get(
                pk=self.recepcion_id
            )

            if self.pk and MovimientoFruta.objects.filter(
                detalle_recepcion_id=self.pk
            ).exists():

                raise ValidationError(
                    "Una distribución que ya generó un movimiento "
                    "no puede modificarse."
                )

            self.full_clean()
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        if self.pk and MovimientoFruta.objects.filter(
            detalle_recepcion_id=self.pk
        ).exists():

            raise ValidationError(
                "No se puede eliminar una distribución "
                "que ya generó un movimiento."
            )

        return super().delete(*args, **kwargs)


# ============================================================
# MODELO: EXISTENCIA DE FRUTA
#
# Mantiene los saldos físicos de fruta por cliente, lote
# agrícola, variedad, fecha de pizca y ubicación.
#
# La variedad forma parte de la identidad de la existencia,
# evitando mezclar diferentes variedades en una ubicación.
#
# Las existencias solamente se actualizan mediante
# movimientos de inventario.
#
# ============================================================

class ExistenciaFruta(models.Model):

    id = models.BigAutoField(primary_key=True)

    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="existencias_fruta",
        verbose_name="Cliente",
    )

    lote_huerta = models.ForeignKey(
        "fruticultura.LoteHuerta",
        on_delete=models.PROTECT,
        related_name="existencias_fruta",
        verbose_name="Lote agrícola",
    )

    variedad = models.ForeignKey(
        "fruticultura.Variedad",
        on_delete=models.PROTECT,
        related_name="existencias_fruta",
        verbose_name="Variedad",
    )

    fecha_pizca = models.DateField(
        verbose_name="Fecha de pizca",
    )

    seccion = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="existencias_fruta",
        verbose_name="Sección",
    )

    estiba = models.ForeignKey(
        "almacenes.Estiba",
        on_delete=models.PROTECT,
        related_name="existencias_fruta",
        null=True,
        blank=True,
        verbose_name="Estiba",
    )

    cantidad_cajones = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Cantidad de cajones",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        db_table = "inventario_fruta_existencia"
        verbose_name = "Existencia de fruta"
        verbose_name_plural = "Existencias de fruta"

        ordering = [
            "cliente",
            "lote_huerta",
            "variedad",
            "fecha_pizca",
            "seccion",
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad_cajones__gte=0),
                name="ck_existencia_fruta_no_negativa",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "cliente",
                    "lote_huerta",
                    "variedad",
                    "fecha_pizca",
                ],
                name="ix_existencia_fruta_origen",
            ),
            models.Index(
                fields=["seccion", "estiba"],
                name="ix_existencia_fruta_ubicacion",
            ),
        ]

    def __str__(self):
        return (
            f"{self.cliente} - {self.lote_huerta} - "
            f"{self.variedad} - {self.fecha_pizca} - "
            f"{self.cantidad_cajones} cajones"
        )

    def clean(self):
        super().clean()

        if (
            self.estiba_id
            and self.seccion_id
            and self.estiba.seccion_id != self.seccion_id
        ):
            raise ValidationError({
                "estiba": (
                    "La estiba no pertenece a la sección indicada."
                )
            })

        if self.cliente_id and self.lote_huerta_id:

            asignacion_valida = (
                self.cliente.huertas_asignadas.filter(
                    huerta_id=self.lote_huerta.huerta_id
                ).exists()
            )

            if not asignacion_valida:
                raise ValidationError({
                    "lote_huerta": (
                        "El lote no pertenece a una huerta "
                        "asignada al cliente."
                    )
                })

    def save(self, *args, **kwargs):
        raise ValidationError(
            "Las existencias de fruta solamente se actualizan "
            "mediante movimientos de inventario."
        )

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "No se pueden eliminar existencias de fruta."
        )


# ============================================================
# MODELO: MOVIMIENTO DE FRUTA
#
# Registra todas las entradas, salidas, traslados, mermas
# y ajustes del inventario de fruta.
#
# Cada movimiento identifica cliente, lote agrícola,
# variedad, fecha de pizca y ubicación.
#
# Los movimientos son inmutables y actualizan las existencias
# automáticamente dentro de una transacción.
#
# ============================================================

class MovimientoInmutable(Exception):
    """Protege el historial de movimientos de fruta."""


class MovimientoFruta(models.Model):

    class Tipo(models.TextChoices):

        RECEPCION = "RECEPCION", "Entrada por recepción"

        SALIDA_PRODUCCION = (
            "SALIDA_PRODUCCION",
            "Salida hacia producción",
        )

        TRASLADO = "TRASLADO", "Traslado"

        MERMA = "MERMA", "Merma"

        AJUSTE_ENTRADA = (
            "AJUSTE_ENTRADA",
            "Ajuste positivo",
        )

        AJUSTE_SALIDA = (
            "AJUSTE_SALIDA",
            "Ajuste negativo",
        )

    TIPOS_ENTRADA = (
        Tipo.RECEPCION,
        Tipo.AJUSTE_ENTRADA,
    )

    TIPOS_SALIDA = (
        Tipo.SALIDA_PRODUCCION,
        Tipo.MERMA,
        Tipo.AJUSTE_SALIDA,
    )

    id = models.BigAutoField(primary_key=True)

    tipo = models.CharField(
        max_length=25,
        choices=Tipo.choices,
        verbose_name="Tipo de movimiento",
    )

    cliente = models.ForeignKey(
        "personas.Cliente",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta",
        verbose_name="Cliente",
    )

    lote_huerta = models.ForeignKey(
        "fruticultura.LoteHuerta",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta",
        verbose_name="Lote agrícola",
    )

    variedad = models.ForeignKey(
        "fruticultura.Variedad",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta",
        verbose_name="Variedad",
    )

    fecha_pizca = models.DateField(
        verbose_name="Fecha de pizca",
    )

    cantidad_cajones = models.PositiveIntegerField(
        verbose_name="Cantidad de cajones",
    )

    seccion_origen = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta_origen",
        null=True,
        blank=True,
        verbose_name="Sección de origen",
    )

    estiba_origen = models.ForeignKey(
        "almacenes.Estiba",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta_origen",
        null=True,
        blank=True,
        verbose_name="Estiba de origen",
    )

    seccion_destino = models.ForeignKey(
        "almacenes.SeccionAlmacen",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta_destino",
        null=True,
        blank=True,
        verbose_name="Sección de destino",
    )

    estiba_destino = models.ForeignKey(
        "almacenes.Estiba",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta_destino",
        null=True,
        blank=True,
        verbose_name="Estiba de destino",
    )

    detalle_recepcion = models.OneToOneField(
        DetalleRecepcionFruta,
        on_delete=models.PROTECT,
        related_name="movimiento",
        null=True,
        blank=True,
        verbose_name="Detalle de recepción",
    )

    descripcion = models.TextField(
        blank=True,
        default="",
        verbose_name="Descripción",
    )

    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha del movimiento",
    )

    responsable = models.ForeignKey(
        "personas.Empleado",
        on_delete=models.PROTECT,
        related_name="movimientos_fruta",
        verbose_name="Responsable del movimiento",
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimientos_fruta_registrados",
        verbose_name="Registrado por",
    )

    class Meta:
        db_table = "inventario_fruta_movimiento"
        verbose_name = "Movimiento de fruta"
        verbose_name_plural = "Movimientos de fruta"
        ordering = ["-fecha", "-id"]

        constraints = [
            models.CheckConstraint(
                condition=Q(cantidad_cajones__gt=0),
                name="ck_mov_fruta_cantidad_positiva",
            ),
        ]

        indexes = [
            models.Index(
                fields=["cliente", "fecha"],
                name="ix_mov_fruta_cliente_fecha",
            ),
            models.Index(
                fields=["lote_huerta", "variedad", "fecha_pizca"],
                name="ix_mov_fruta_lote_pizca",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.cliente} - {self.variedad} - "
            f"{self.cantidad_cajones} cajones"
        )

    def clean(self):
        super().clean()

        errores = {}

        if (
            self.cantidad_cajones is not None
            and self.cantidad_cajones <= 0
        ):
            errores["cantidad_cajones"] = (
                "La cantidad debe ser mayor que cero."
            )

        if self.cliente_id and self.lote_huerta_id:

            asignacion_valida = (
                self.cliente.huertas_asignadas.filter(
                    huerta_id=self.lote_huerta.huerta_id
                ).exists()
            )

            if not asignacion_valida:
                errores["lote_huerta"] = (
                    "El lote no pertenece a una huerta "
                    "asignada al cliente."
                )

        # Validar sección y estiba de origen.
        if self.estiba_origen_id:

            if (
                self.seccion_origen_id
                and self.estiba_origen.seccion_id
                != self.seccion_origen_id
            ):
                errores["estiba_origen"] = (
                    "La estiba de origen no pertenece "
                    "a la sección indicada."
                )

        # Validar sección y estiba de destino.
        if self.estiba_destino_id:

            if (
                self.seccion_destino_id
                and self.estiba_destino.seccion_id
                != self.seccion_destino_id
            ):
                errores["estiba_destino"] = (
                    "La estiba de destino no pertenece "
                    "a la sección indicada."
                )

        # Validaciones según el tipo de movimiento.
        if self.tipo in self.TIPOS_ENTRADA:

            if self.seccion_origen_id or self.estiba_origen_id:
                errores["seccion_origen"] = (
                    "Una entrada no requiere ubicación de origen."
                )

            if not self.seccion_destino_id:
                errores["seccion_destino"] = (
                    "Indique la sección de destino."
                )

        elif self.tipo in self.TIPOS_SALIDA:

            if not self.seccion_origen_id:
                errores["seccion_origen"] = (
                    "Indique la sección de origen."
                )

            if self.seccion_destino_id or self.estiba_destino_id:
                errores["seccion_destino"] = (
                    "Una salida no requiere ubicación de destino."
                )

        elif self.tipo == self.Tipo.TRASLADO:

            if not self.seccion_origen_id:
                errores["seccion_origen"] = (
                    "Indique la sección de origen."
                )

            if not self.seccion_destino_id:
                errores["seccion_destino"] = (
                    "Indique la sección de destino."
                )

            misma_ubicacion = (
                self.seccion_origen_id == self.seccion_destino_id
                and self.estiba_origen_id == self.estiba_destino_id
            )

            if (
                self.seccion_origen_id
                and self.seccion_destino_id
                and misma_ubicacion
            ):
                errores["__all__"] = (
                    "El traslado debe cambiar de ubicación."
                )

        # Validar relación con el detalle de recepción.
        if self.tipo == self.Tipo.RECEPCION:

            if not self.detalle_recepcion_id:
                errores["detalle_recepcion"] = (
                    "Una recepción debe relacionarse "
                    "con su detalle de distribución."
                )

            elif self.detalle_recepcion:

                detalle = self.detalle_recepcion
                recepcion = detalle.recepcion

                if (
                    detalle.cantidad_cajones
                    != self.cantidad_cajones
                ):
                    errores["cantidad_cajones"] = (
                        "La cantidad debe coincidir con "
                        "el detalle de recepción."
                    )

                if (
                    recepcion.cliente_id != self.cliente_id
                    or recepcion.lote_huerta_id != self.lote_huerta_id
                    or recepcion.variedad_id != self.variedad_id
                    or recepcion.fecha_pizca != self.fecha_pizca
                    or detalle.seccion_id != self.seccion_destino_id
                    or detalle.estiba_id != self.estiba_destino_id
                ):
                    errores["detalle_recepcion"] = (
                        "Los datos del movimiento no coinciden "
                        "con el detalle de recepción."
                    )

        elif self.detalle_recepcion_id:

            errores["detalle_recepcion"] = (
                "Solo las entradas por recepción pueden "
                "relacionarse con un detalle."
            )

        # Mermas y ajustes deben justificarse.
        if self.tipo in (
            self.Tipo.MERMA,
            self.Tipo.AJUSTE_ENTRADA,
            self.Tipo.AJUSTE_SALIDA,
        ):

            if not self.descripcion.strip():
                errores["descripcion"] = (
                    "Explique el motivo del movimiento."
                )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):

        if not self._state.adding:
            raise MovimientoInmutable(
                "Los movimientos de fruta no se pueden modificar."
            )

        with transaction.atomic():

            from fruticultura.models import LoteHuerta

            # Mutex transaccional para serializar movimientos
            # y creación de existencias del mismo lote agrícola.
            LoteHuerta.objects.select_for_update().get(
                pk=self.lote_huerta_id
            )

            self.full_clean()

            cambios = []

            if self.tipo in self.TIPOS_ENTRADA:

                cambios.append((
                    self.seccion_destino,
                    self.estiba_destino,
                    self.cantidad_cajones,
                ))

            elif self.tipo in self.TIPOS_SALIDA:

                cambios.append((
                    self.seccion_origen,
                    self.estiba_origen,
                    -self.cantidad_cajones,
                ))

            elif self.tipo == self.Tipo.TRASLADO:

                cambios.append((
                    self.seccion_origen,
                    self.estiba_origen,
                    -self.cantidad_cajones,
                ))

                cambios.append((
                    self.seccion_destino,
                    self.estiba_destino,
                    self.cantidad_cajones,
                ))

            # Consolidar variaciones por ubicación.
            saldos = {}

            for seccion, estiba, variacion in cambios:

                clave = (
                    seccion.pk,
                    estiba.pk if estiba else None,
                )

                saldos[clave] = (
                    saldos.get(clave, 0) + variacion
                )

            existencias = {}

            for (seccion_id, estiba_id), variacion in saldos.items():

                existencia = (
                    ExistenciaFruta.objects
                    .filter(
                        cliente_id=self.cliente_id,
                        lote_huerta_id=self.lote_huerta_id,
                        variedad_id=self.variedad_id,
                        fecha_pizca=self.fecha_pizca,
                        seccion_id=seccion_id,
                        estiba_id=estiba_id,
                    )
                    .first()
                )

                cantidad_actual = (
                    existencia.cantidad_cajones
                    if existencia else 0
                )

                nueva_cantidad = cantidad_actual + variacion

                if nueva_cantidad < 0:
                    raise ValidationError(
                        "No hay suficientes cajones disponibles "
                        f"en la sección {seccion_id}. "
                        f"Existencia: {cantidad_actual}; "
                        f"salida solicitada: {abs(variacion)}."
                    )

                existencias[(seccion_id, estiba_id)] = (
                    existencia,
                    nueva_cantidad,
                )

            # Registrar el movimiento histórico.
            super().save(*args, **kwargs)

            # Actualizar las existencias.
            for (seccion_id, estiba_id), (
                existencia,
                nueva_cantidad,
            ) in existencias.items():

                if existencia:

                    ExistenciaFruta.objects.filter(
                        pk=existencia.pk
                    ).update(
                        cantidad_cajones=nueva_cantidad,
                        actualizado_en=timezone.now(),
                    )

                else:

                    ubicacion = next(
                        (
                            (seccion, estiba)
                            for seccion, estiba, _ in cambios
                            if seccion.pk == seccion_id
                            and (
                                estiba.pk if estiba else None
                            ) == estiba_id
                        ),
                        None,
                    )

                    seccion, estiba = ubicacion

                    nueva_existencia = ExistenciaFruta(
                        cliente_id=self.cliente_id,
                        lote_huerta_id=self.lote_huerta_id,
                        variedad_id=self.variedad_id,
                        fecha_pizca=self.fecha_pizca,
                        seccion=seccion,
                        estiba=estiba,
                        cantidad_cajones=nueva_cantidad,
                    )

                    # Guardado interno: evita el bloqueo del save()
                    # público de ExistenciaFruta.
                    models.Model.save(nueva_existencia)

    def delete(self, *args, **kwargs):
        raise MovimientoInmutable(
            "Los movimientos de fruta no se pueden eliminar."
        )
