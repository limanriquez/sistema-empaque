from django import forms

from .models import (
    RecepcionFruta,
    DetalleRecepcionFruta,
    MovimientoFruta,
    ExistenciaFruta,
)

from personas.models import Cliente, Empleado
from fruticultura.models import LoteHuerta, Variedad
from almacenes.models import SeccionAlmacen, Estiba


# ============================================================
# CONSULTAS BASE
# ============================================================

def clientes_activos():
    return Cliente.objects.filter(
        activo=True,
        persona__activo=True,
    ).select_related("persona")


def empleados_activos():
    return Empleado.objects.filter(
        activo=True,
        persona__activo=True,
    ).select_related("persona")


def lotes_activos():
    return LoteHuerta.objects.filter(
        activo=True,
        huerta__activo=True,
    ).select_related("huerta")


def variedades_activas():
    return Variedad.objects.filter(
        activo=True,
    ).order_by("nombre")


def secciones_activas():
    return SeccionAlmacen.objects.filter(
        activo=True,
        espacio__activo=True,
        espacio__almacen__activo=True,
    ).select_related(
        "espacio",
        "espacio__almacen",
    )


def estibas_activas():
    return Estiba.objects.filter(
        activo=True,
        seccion__isnull=False,
        seccion__activo=True,
    ).select_related("seccion")


def existencias_disponibles():
    return (
        ExistenciaFruta.objects
        .filter(cantidad_cajones__gt=0)
        .select_related(
            "cliente__persona",
            "lote_huerta__huerta",
            "seccion",
            "estiba",
        )
        .order_by(
            "cliente",
            "lote_huerta",
            "fecha_pizca",
            "seccion",
            "estiba",
        )
    )


# ============================================================
# VALIDACION CLIENTE - LOTE AGRICOLA
# ============================================================

def validar_cliente_lote(cliente, lote):

    if not cliente or not lote:
        return

    asignacion_valida = cliente.huertas_asignadas.filter(
        huerta_id=lote.huerta_id
    ).exists()

    if not asignacion_valida:
        raise forms.ValidationError(
            "El lote agrícola no pertenece a una huerta "
            "asignada al cliente."
        )


# ============================================================
# RECEPCION DE FRUTA
#
# Registra las entradas físicas de fruta a la empacadora,
# identificando cliente, lote agrícola, variedad, fecha de
# pizca y cantidad recibida.
#
# Permite distribuir la fruta entre diferentes secciones
# y estibas mediante DetalleRecepcionFruta.
#
# La variedad es obligatoria y solamente pueden seleccionarse
# variedades activas.
# ============================================================

class RecepcionFrutaForm(forms.ModelForm):

    class Meta:
        model = RecepcionFruta

        fields = (
            "cliente",
            "lote_huerta",
            "variedad",
            "fecha_pizca",
            "cantidad_cajones",
            "fecha_recepcion",
            "recibido_por",
            "observaciones",
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["cliente"].queryset = clientes_activos()
        self.fields["lote_huerta"].queryset = lotes_activos()
        self.fields["variedad"].queryset = variedades_activas()
        self.fields["variedad"].required = True
        self.fields["recibido_por"].queryset = empleados_activos()

    def clean(self):

        cleaned_data = super().clean()

        cliente = cleaned_data.get("cliente")
        lote = cleaned_data.get("lote_huerta")
        variedad = cleaned_data.get("variedad")

        if cliente and lote:

            try:
                validar_cliente_lote(cliente, lote)

            except forms.ValidationError as exc:
                self.add_error("lote_huerta", exc)

        if variedad and not variedad.activo:
            self.add_error(
                "variedad",
                "No se puede seleccionar una variedad inactiva.",
            )

        return cleaned_data


# ============================================================
# DETALLE DE RECEPCION
# ============================================================

class DetalleRecepcionFrutaForm(forms.ModelForm):

    class Meta:
        model = DetalleRecepcionFruta

        fields = (
            "seccion",
            "estiba",
            "cantidad_cajones",
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["seccion"].queryset = secciones_activas()
        self.fields["estiba"].queryset = estibas_activas()

    def clean(self):

        cleaned_data = super().clean()

        seccion = cleaned_data.get("seccion")
        estiba = cleaned_data.get("estiba")

        if estiba and seccion:

            if estiba.seccion_id != seccion.pk:

                self.add_error(
                    "estiba",
                    "La estiba no pertenece a la sección seleccionada.",
                )

        return cleaned_data


# ============================================================
# FORMULARIO BASE DE MOVIMIENTOS
# ============================================================

class MovimientoFrutaBaseForm(forms.ModelForm):

    tipo_movimiento = None

    class Meta:
        model = MovimientoFruta

        fields = (
            "cliente",
            "lote_huerta",
            "fecha_pizca",
            "cantidad_cajones",
            "seccion_origen",
            "estiba_origen",
            "seccion_destino",
            "estiba_destino",
            "descripcion",
            "fecha",
            "responsable",
        )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if self.tipo_movimiento:
            self.instance.tipo = self.tipo_movimiento

        if "cliente" in self.fields:
            self.fields["cliente"].queryset = clientes_activos()

        if "lote_huerta" in self.fields:
            self.fields["lote_huerta"].queryset = lotes_activos()

        if "responsable" in self.fields:
            self.fields["responsable"].queryset = empleados_activos()

        if "seccion_origen" in self.fields:
            self.fields["seccion_origen"].queryset = secciones_activas()

        if "seccion_destino" in self.fields:
            self.fields["seccion_destino"].queryset = secciones_activas()

        if "estiba_origen" in self.fields:
            self.fields["estiba_origen"].queryset = estibas_activas()

        if "estiba_destino" in self.fields:
            self.fields["estiba_destino"].queryset = estibas_activas()

    def clean(self):

        cleaned_data = super().clean()

        cliente = cleaned_data.get("cliente")
        lote = cleaned_data.get("lote_huerta")

        if cliente and lote:

            try:
                validar_cliente_lote(cliente, lote)

            except forms.ValidationError as exc:
                self.add_error("lote_huerta", exc)

        seccion_origen = cleaned_data.get("seccion_origen")
        estiba_origen = cleaned_data.get("estiba_origen")

        if estiba_origen and seccion_origen:

            if estiba_origen.seccion_id != seccion_origen.pk:

                self.add_error(
                    "estiba_origen",
                    "La estiba de origen no pertenece "
                    "a la sección indicada.",
                )

        seccion_destino = cleaned_data.get("seccion_destino")
        estiba_destino = cleaned_data.get("estiba_destino")

        if estiba_destino and seccion_destino:

            if estiba_destino.seccion_id != seccion_destino.pk:

                self.add_error(
                    "estiba_destino",
                    "La estiba de destino no pertenece "
                    "a la sección indicada.",
                )

        return cleaned_data


# ============================================================
# CAMPO AUXILIAR: EXISTENCIA SELECCIONADA
# ============================================================

def campo_existencia_origen():

    return forms.ModelChoiceField(
        queryset=ExistenciaFruta.objects.none(),
        label="Existencia de origen",
        required=True,
        help_text=(
            "Seleccione la existencia de fruta que utilizará "
            "el movimiento."
        ),
    )


# ============================================================
# MIXIN: OBTENER DATOS DESDE EXISTENCIA
# ============================================================

class ExistenciaOrigenFormMixin:

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["existencia_origen"].queryset = (
            existencias_disponibles()
        )

    def clean(self):

        cleaned_data = super().clean()

        existencia = cleaned_data.get("existencia_origen")
        cantidad = cleaned_data.get("cantidad_cajones")

        if not existencia:
            return cleaned_data

        # Datos comunes obtenidos de la existencia seleccionada.
        self.instance.cliente = existencia.cliente
        self.instance.lote_huerta = existencia.lote_huerta
        self.instance.fecha_pizca = existencia.fecha_pizca

        tipo = self.tipo_movimiento

        if tipo == MovimientoFruta.Tipo.AJUSTE_ENTRADA:

            # El ajuste positivo incrementa la ubicación seleccionada.
            self.instance.seccion_destino = existencia.seccion
            self.instance.estiba_destino = existencia.estiba

            self.instance.seccion_origen = None
            self.instance.estiba_origen = None

        else:

            # Las salidas y los traslados descuentan del origen.
            self.instance.seccion_origen = existencia.seccion
            self.instance.estiba_origen = existencia.estiba

        # Validación anticipada de disponibilidad.
        # MovimientoFruta.save() vuelve a validar el saldo
        # dentro de la transacción.
        if (
            tipo != MovimientoFruta.Tipo.AJUSTE_ENTRADA
            and cantidad is not None
            and cantidad > existencia.cantidad_cajones
        ):

            self.add_error(
                "cantidad_cajones",
                (
                    f"Existencia disponible: "
                    f"{existencia.cantidad_cajones} cajones. "
                    f"No puede solicitar {cantidad}."
                ),
            )

        return cleaned_data


# ============================================================
# SALIDA A PRODUCCION
# ============================================================

class SalidaProduccionForm(
    ExistenciaOrigenFormMixin,
    MovimientoFrutaBaseForm,
):

    existencia_origen = campo_existencia_origen()

    tipo_movimiento = MovimientoFruta.Tipo.SALIDA_PRODUCCION

    class Meta(MovimientoFrutaBaseForm.Meta):

        fields = (
            "existencia_origen",
            "cantidad_cajones",
            "descripcion",
            "fecha",
            "responsable",
        )


# ============================================================
# TRASLADO DE FRUTA
# ============================================================

class TrasladoFrutaForm(
    ExistenciaOrigenFormMixin,
    MovimientoFrutaBaseForm,
):

    existencia_origen = campo_existencia_origen()

    tipo_movimiento = MovimientoFruta.Tipo.TRASLADO

    class Meta(MovimientoFrutaBaseForm.Meta):

        fields = (
            "existencia_origen",
            "cantidad_cajones",
            "seccion_destino",
            "estiba_destino",
            "descripcion",
            "fecha",
            "responsable",
        )


# ============================================================
# MERMA DE FRUTA
# ============================================================

class MermaFrutaForm(
    ExistenciaOrigenFormMixin,
    MovimientoFrutaBaseForm,
):

    existencia_origen = campo_existencia_origen()

    tipo_movimiento = MovimientoFruta.Tipo.MERMA

    class Meta(MovimientoFrutaBaseForm.Meta):

        fields = (
            "existencia_origen",
            "cantidad_cajones",
            "descripcion",
            "fecha",
            "responsable",
        )


# ============================================================
# AJUSTE DE ENTRADA
# ============================================================

class AjusteEntradaFrutaForm(
    ExistenciaOrigenFormMixin,
    MovimientoFrutaBaseForm,
):

    existencia_origen = campo_existencia_origen()

    tipo_movimiento = MovimientoFruta.Tipo.AJUSTE_ENTRADA

    class Meta(MovimientoFrutaBaseForm.Meta):

        fields = (
            "existencia_origen",
            "cantidad_cajones",
            "descripcion",
            "fecha",
            "responsable",
        )


# ============================================================
# AJUSTE DE SALIDA
# ============================================================

class AjusteSalidaFrutaForm(
    ExistenciaOrigenFormMixin,
    MovimientoFrutaBaseForm,
):

    existencia_origen = campo_existencia_origen()

    tipo_movimiento = MovimientoFruta.Tipo.AJUSTE_SALIDA

    class Meta(MovimientoFrutaBaseForm.Meta):

        fields = (
            "existencia_origen",
            "cantidad_cajones",
            "descripcion",
            "fecha",
            "responsable",
        )