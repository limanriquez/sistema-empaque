from decimal import Decimal

from django import forms

from catalogos.models import UnidadMedida

from .models import ExistenciaMaterial, Material, MovimientoInventario

from almacenes.models import SeccionAlmacen
from personas.models import Proveedor


# Formulario para registrar y modificar materiales.
# Limpia espacios, normaliza el código a mayúsculas y evita duplicados
# sin distinguir mayúsculas. En el alta solo ofrece unidades activas.
# Si la unidad no admite decimales, el stock mínimo debe ser entero.
# La existencia no se captura aquí: la actualizan los movimientos.
class MaterialForm(forms.ModelForm):

    class Meta:
        model = Material
        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "unidad_medida",
            "stock_minimo",
            "activo",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Al editar, el admin muestra la unidad de solo lectura y
        # el campo no existe en el formulario.
        if "unidad_medida" in self.fields:
            self.fields["unidad_medida"].queryset = (
                UnidadMedida.objects.filter(activo=True)
            )

    def clean_codigo(self):
        # El código es opcional; vacío se guarda como NULL para que
        # varios materiales sin código no choquen con el unique.
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

    def clean(self):
        cleaned_data = super().clean()

        stock_minimo = cleaned_data.get("stock_minimo")

        # Al editar, la unidad no está en el formulario: se toma de la
        # instancia. En un alta sin unidad elegida, getattr devuelve None.
        unidad = cleaned_data.get("unidad_medida") or getattr(
            self.instance, "unidad_medida", None
        )

        if stock_minimo is not None:
            if stock_minimo < 0:
                self.add_error(
                    "stock_minimo",
                    "El stock mínimo no puede ser negativo.",
                )
            elif (
                unidad
                and not unidad.permite_decimales
                and stock_minimo % 1 != Decimal("0")
            ):
                self.add_error(
                    "stock_minimo",
                    f"La unidad «{unidad.nombre}» solo admite "
                    f"cantidades enteras.",
                )

        return cleaned_data


# Formulario para registrar movimientos de inventario.
# Exige las ubicaciones, el proveedor y el costo que corresponden a cada
# tipo de movimiento, y evita sacar más material del que hay en la
# sección de origen. Solo ofrece materiales, secciones y proveedores
# activos. La descripción obligatoria en mermas y ajustes, y las
# cantidades enteras según la unidad, las valida
# MovimientoInventario.clean.
class MovimientoInventarioForm(forms.ModelForm):

    class Meta:
        model = MovimientoInventario
        fields = (
            "tipo",
            "material",
            "cantidad",
            "ubicacion_origen",
            "ubicacion_destino",
            "proveedor",
            "costo_unitario",
            "documento",
            "fecha",
            "descripcion",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        secciones = SeccionAlmacen.objects.filter(
            activo=True,
            espacio__activo=True,
            espacio__almacen__activo=True,
        ).select_related("espacio__almacen")

        self.fields["material"].queryset = Material.objects.filter(
            activo=True
        ).select_related("unidad_medida")
        self.fields["ubicacion_origen"].queryset = secciones
        self.fields["ubicacion_destino"].queryset = secciones
        self.fields["proveedor"].queryset = Proveedor.objects.filter(
            activo=True
        ).select_related("persona")

    def clean_documento(self):
        return " ".join(self.cleaned_data["documento"].split())

    def clean_descripcion(self):
        return self.cleaned_data["descripcion"].strip()

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo")
        material = cleaned_data.get("material")
        cantidad = cleaned_data.get("cantidad")
        origen = cleaned_data.get("ubicacion_origen")
        destino = cleaned_data.get("ubicacion_destino")
        proveedor = cleaned_data.get("proveedor")
        costo = cleaned_data.get("costo_unitario")

        if not tipo:
            return cleaned_data

        es_entrada = tipo in MovimientoInventario.TIPOS_ENTRADA
        es_salida = tipo in MovimientoInventario.TIPOS_SALIDA
        es_traslado = tipo == MovimientoInventario.Tipo.TRASLADO
        es_compra = tipo == MovimientoInventario.Tipo.COMPRA

        # Ubicaciones según el tipo de movimiento.
        if es_entrada:
            if not destino:
                self.add_error(
                    "ubicacion_destino",
                    "Indique la sección donde ingresa el material.",
                )
            if origen:
                self.add_error(
                    "ubicacion_origen",
                    "Una entrada no lleva sección de origen.",
                )

        if es_salida:
            if not origen:
                self.add_error(
                    "ubicacion_origen",
                    "Indique la sección de donde sale el material.",
                )
            if destino:
                self.add_error(
                    "ubicacion_destino",
                    "Una salida no lleva sección de destino.",
                )

        if es_traslado:
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
                    "El destino debe ser distinto del origen.",
                )

        # Proveedor y costo: solo en compras.
        if es_compra:
            if costo is None:
                self.add_error(
                    "costo_unitario",
                    "Capture el costo unitario de la compra.",
                )
        else:
            if proveedor:
                self.add_error(
                    "proveedor",
                    "Solo las compras llevan proveedor.",
                )
            if costo is not None:
                self.add_error(
                    "costo_unitario",
                    "Solo las compras llevan costo.",
                )

        # No se puede sacar ni trasladar más de lo que hay en la
        # sección de origen.
        if (es_salida or es_traslado) and material and cantidad and origen:
            disponible = (
                ExistenciaMaterial.objects.filter(
                    material=material, seccion=origen
                )
                .values_list("cantidad", flat=True)
                .first()
            ) or Decimal("0")

            if disponible < cantidad:
                self.add_error(
                    "cantidad",
                    f"Existencia insuficiente en esa sección: hay "
                    f"{disponible:,.3f} "
                    f"{material.unidad_medida.abreviatura}.",
                )

        return cleaned_data