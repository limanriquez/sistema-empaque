
from django import forms

from catalogos.models import UnidadMedida
from almacenes.models import SeccionAlmacen
from personas.models import Cliente, Proveedor

from .models import Material, MovimientoInventario


# ============================================================
# MATERIAL
# ============================================================

# Formulario para registrar y modificar materiales.
# Limpia espacios, normaliza el código a mayúsculas y evita duplicados
# sin distinguir mayúsculas. En el alta solo ofrece unidades activas.
class MaterialForm(forms.ModelForm):

    class Meta:
        model = Material
        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "unidad_medida",
            "activo",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "unidad_medida" in self.fields:
            self.fields["unidad_medida"].queryset = (
                UnidadMedida.objects.filter(activo=True)
            )

    def clean_codigo(self):
        codigo = (self.cleaned_data.get("codigo") or "").strip().upper()

        if not codigo:
            return None

        duplicados = Material.objects.filter(codigo__iexact=codigo)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe un material con este código."
            )

        return codigo

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())

        duplicados = Material.objects.filter(nombre__iexact=nombre)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe un material con este nombre."
            )

        return nombre


# ============================================================
# FORMULARIO BASE PARA MOVIMIENTOS
# ============================================================

# Comparte los catálogos y las validaciones comunes de los
# cuatro formularios de captura de inventario.
class MovimientoBaseForm(forms.ModelForm):

    class Meta:
        model = MovimientoInventario
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        secciones = SeccionAlmacen.objects.filter(
            activo=True,
            espacio__activo=True,
            espacio__almacen__activo=True,
        ).select_related("espacio__almacen")

        self.fields["material"].queryset = (
            Material.objects.filter(activo=True)
            .select_related("unidad_medida")
        )

        for campo in ("ubicacion_origen", "ubicacion_destino"):
            if campo in self.fields:
                self.fields[campo].queryset = secciones

        for campo in ("propietario_origen", "propietario_destino"):
            if campo in self.fields:
                self.fields[campo].queryset = (
                    Cliente.objects.filter(activo=True)
                    .select_related("persona")
                )

                self.fields[campo].help_text = (
                    "Seleccione el cliente propietario del material. "
                    "La empacadora también debe estar registrada como cliente."
                )

        if "proveedor" in self.fields:
            self.fields["proveedor"].queryset = (
                Proveedor.objects.filter(activo=True)
                .select_related("persona")
            )

    def clean_documento(self):
        return " ".join(
            (self.cleaned_data.get("documento") or "").split()
        )

    def clean_descripcion(self):
        return (self.cleaned_data.get("descripcion") or "").strip()

    def asignar_tipo(self, tipo):
        self.instance.tipo = tipo

    def save(self, commit=True):
        return super().save(commit=commit)


# ============================================================
# 1. ENTRADAS
# ============================================================

# Permite registrar compras y ajustes positivos.
# Todo material que ingresa debe tener un propietario destino.
class EntradaInventarioForm(MovimientoBaseForm):

    class Meta:
        model = MovimientoInventario
        fields = (
            "tipo",
            "material",
            "cantidad",
            "ubicacion_destino",
            "propietario_destino",
            "proveedor",
            "costo_unitario",
            "documento",
            "fecha",
            "descripcion",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tipo"].choices = (
            (
                MovimientoInventario.Tipo.COMPRA,
                "Compra",
            ),
            (
                MovimientoInventario.Tipo.AJUSTE_ENTRADA,
                "Ajuste positivo",
            ),
        )

        self.fields["ubicacion_destino"].label = "Sección de destino"

        self.fields["propietario_destino"].label = (
            "Propietario del material"
        )
        self.fields["propietario_destino"].required = True

        self.fields["costo_unitario"].required = False

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo")
        destino = cleaned_data.get("ubicacion_destino")
        propietario = cleaned_data.get("propietario_destino")
        proveedor = cleaned_data.get("proveedor")
        costo = cleaned_data.get("costo_unitario")

        if not destino:
            self.add_error(
                "ubicacion_destino",
                "Indique la sección donde ingresa el material.",
            )

        if not propietario:
            self.add_error(
                "propietario_destino",
                "Seleccione el propietario del material.",
            )

        if tipo == MovimientoInventario.Tipo.COMPRA:

            if costo is None:
                self.add_error(
                    "costo_unitario",
                    "Capture el costo unitario de la compra.",
                )

        elif tipo == MovimientoInventario.Tipo.AJUSTE_ENTRADA:

            if proveedor:
                self.add_error(
                    "proveedor",
                    "Un ajuste positivo no lleva proveedor.",
                )

            if costo is not None:
                self.add_error(
                    "costo_unitario",
                    "Un ajuste positivo no lleva costo de compra.",
                )

        return cleaned_data


# ============================================================
# 2. SALIDAS
# ============================================================

# Permite registrar consumos, mermas y ajustes negativos.
# Todo material que sale debe tener un propietario de origen.
class SalidaInventarioForm(MovimientoBaseForm):

    class Meta:
        model = MovimientoInventario
        fields = (
            "tipo",
            "material",
            "cantidad",
            "ubicacion_origen",
            "propietario_origen",
            "documento",
            "fecha",
            "descripcion",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tipo"].choices = (
            (
                MovimientoInventario.Tipo.CONSUMO,
                "Consumo",
            ),
            (
                MovimientoInventario.Tipo.MERMA,
                "Merma",
            ),
            (
                MovimientoInventario.Tipo.AJUSTE_SALIDA,
                "Ajuste negativo",
            ),
        )

        self.fields["ubicacion_origen"].label = "Sección de origen"

        self.fields["propietario_origen"].label = (
            "Propietario del material"
        )
        self.fields["propietario_origen"].required = True

    def clean(self):
        cleaned_data = super().clean()

        origen = cleaned_data.get("ubicacion_origen")
        propietario = cleaned_data.get("propietario_origen")

        if not origen:
            self.add_error(
                "ubicacion_origen",
                "Indique la sección de donde sale el material.",
            )

        if not propietario:
            self.add_error(
                "propietario_origen",
                "Seleccione el propietario del material.",
            )

        return cleaned_data


# ============================================================
# 3. TRASPASO ENTRE ALMACENES
# ============================================================

# Cambia la ubicación física del material.
# Conserva el mismo propietario en origen y destino.
class TraspasoAlmacenForm(MovimientoBaseForm):

    propietario = forms.ModelChoiceField(
        queryset=Cliente.objects.none(),
        required=True,
        label="Propietario del material",
        help_text=(
            "Seleccione el propietario del material, "
            "incluida la empacadora si corresponde."
        ),
    )

    class Meta:
        model = MovimientoInventario
        fields = (
            "material",
            "cantidad",
            "ubicacion_origen",
            "ubicacion_destino",
            "fecha",
            "documento",
            "descripcion",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["propietario"].queryset = (
            Cliente.objects.filter(activo=True)
            .select_related("persona")
        )

        self.fields["ubicacion_origen"].label = (
            "Almacén / sección origen"
        )
        self.fields["ubicacion_destino"].label = (
            "Almacén / sección destino"
        )

    def clean(self):
        cleaned_data = super().clean()

        origen = cleaned_data.get("ubicacion_origen")
        destino = cleaned_data.get("ubicacion_destino")
        propietario = cleaned_data.get("propietario")

        if not origen:
            self.add_error(
                "ubicacion_origen",
                "Indique la sección de origen.",
            )

        if not destino:
            self.add_error(
                "ubicacion_destino",
                "Indique la sección de destino.",
            )

        if origen and destino and origen == destino:
            self.add_error(
                "ubicacion_destino",
                "La sección de origen y destino deben ser diferentes.",
            )

        if not propietario:
            self.add_error(
                "propietario",
                "Seleccione el propietario del material.",
            )

        # El propietario se conserva en ambos extremos.
        self.instance.propietario_origen = propietario
        self.instance.propietario_destino = propietario
        self.instance.tipo = MovimientoInventario.Tipo.TRASLADO

        return cleaned_data

    def save(self, commit=True):
        propietario = self.cleaned_data["propietario"]

        self.instance.propietario_origen = propietario
        self.instance.propietario_destino = propietario
        self.instance.tipo = MovimientoInventario.Tipo.TRASLADO

        return super().save(commit=commit)


# ============================================================
# 4. TRASPASO ENTRE CLIENTES
# ============================================================

# Cambia la propiedad del material.
# Conserva la misma ubicación física.
class TraspasoClienteForm(MovimientoBaseForm):

    seccion = forms.ModelChoiceField(
        queryset=SeccionAlmacen.objects.none(),
        required=True,
        label="Sección donde se encuentra el material",
    )

    class Meta:
        model = MovimientoInventario
        fields = (
            "material",
            "cantidad",
            "seccion",
            "propietario_origen",
            "propietario_destino",
            "fecha",
            "documento",
            "descripcion",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["seccion"].queryset = (
            SeccionAlmacen.objects.filter(
                activo=True,
                espacio__activo=True,
                espacio__almacen__activo=True,
            ).select_related("espacio__almacen")
        )

        self.fields["propietario_origen"].label = (
            "Propietario actual"
        )
        self.fields["propietario_origen"].required = True

        self.fields["propietario_destino"].label = (
            "Nuevo propietario"
        )
        self.fields["propietario_destino"].required = True

    def clean(self):
        cleaned_data = super().clean()

        seccion = cleaned_data.get("seccion")
        propietario_origen = cleaned_data.get("propietario_origen")
        propietario_destino = cleaned_data.get("propietario_destino")

        if not seccion:
            self.add_error(
                "seccion",
                "Seleccione la sección donde se encuentra el material.",
            )

        if (
            propietario_origen is not None
            and propietario_destino is not None
            and propietario_origen == propietario_destino
        ):
            self.add_error(
                "propietario_destino",
                "El propietario de origen y destino deben ser diferentes.",
            )

        # La ubicación física permanece igual.
        self.instance.ubicacion_origen = seccion
        self.instance.ubicacion_destino = seccion

        self.instance.propietario_origen = propietario_origen
        self.instance.propietario_destino = propietario_destino

        self.instance.tipo = MovimientoInventario.Tipo.TRASLADO

        return cleaned_data

    def save(self, commit=True):
        seccion = self.cleaned_data["seccion"]

        self.instance.ubicacion_origen = seccion
        self.instance.ubicacion_destino = seccion

        self.instance.propietario_origen = (
            self.cleaned_data["propietario_origen"]
        )

        self.instance.propietario_destino = (
            self.cleaned_data["propietario_destino"]
        )

        self.instance.tipo = MovimientoInventario.Tipo.TRASLADO

        return super().save(commit=commit)
