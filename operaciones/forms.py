from django import forms
from django.db.models import Q

from inventarios.models import Material

from .models import ComponenteEmpaque, ProductoEmpaque, ClienteProductoEmpaque

from django.core.exceptions import ValidationError


# Formulario para registrar y modificar productos de empaque.
# Limpia espacios, normaliza el código a mayúsculas y evita duplicados
# sin distinguir mayúsculas. El costo y el precio no pueden ser
# negativos. Que el precio sea mayor al costo lo exige el modelo.
class ProductoEmpaqueForm(forms.ModelForm):

    class Meta:
        model = ProductoEmpaque
        fields = (
            "codigo",
            "nombre",
            "descripcion",
            "costo_empaque",
            "precio_cobro",
            "activo",
        )

    def clean_codigo(self):
        # El código es opcional; vacío se guarda como NULL para que
        # varios productos sin código no choquen con el unique.
        codigo = (self.cleaned_data.get("codigo") or "").strip().upper()

        if not codigo:
            return None

        duplicados = ProductoEmpaque.objects.filter(codigo__iexact=codigo)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe un producto de empaque con este código."
            )

        return codigo

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())

        duplicados = ProductoEmpaque.objects.filter(nombre__iexact=nombre)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe un producto de empaque con este nombre."
            )

        return nombre

    def clean_costo_empaque(self):
        costo = self.cleaned_data["costo_empaque"]

        if costo < 0:
            raise forms.ValidationError("El costo no puede ser negativo.")

        return costo

    def clean_precio_cobro(self):
        precio = self.cleaned_data["precio_cobro"]

        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")

        return precio


# Formulario de cada material del BOM, usado en la tabla dentro del
# producto. Solo ofrece materiales activos; al editar conserva el que
# ya tenía la fila aunque se haya desactivado después. Las cantidades
# enteras según la unidad las valida ComponenteEmpaque.clean.
class ComponenteEmpaqueForm(forms.ModelForm):

    class Meta:
        model = ComponenteEmpaque
        fields = ("material", "cantidad_material")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        filtro = Q(activo=True)

        if self.instance.material_id:
            filtro |= Q(pk=self.instance.material_id)

        self.fields["material"].queryset = Material.objects.filter(
            filtro
        ).select_related("unidad_medida")

    def clean_cantidad_material(self):
        cantidad = self.cleaned_data["cantidad_material"]

        if cantidad <= 0:
            raise forms.ValidationError(
                "La cantidad debe ser mayor a cero."
            )

        return cantidad


# Conjunto de materiales del BOM dentro del producto. Exige al menos
# un material, también al borrar filas de un producto ya existente.
class ComponenteEmpaqueFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super().clean()

        # Si hay errores en las filas, se muestran primero esos.
        if any(self.errors):
            return

        con_material = [
            form
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get("DELETE", False)
            and form.cleaned_data.get("material")
        ]

        if not con_material:
            raise forms.ValidationError(
                "El producto debe tener al menos un material en su BOM."
            )


# Formulario para administrar las presentaciones autorizadas de cada cliente.
class ClienteProductoEmpaqueForm(forms.ModelForm):

    class Meta:
        model = ClienteProductoEmpaque
        fields = ["cliente", "producto_empaque", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        productos = ProductoEmpaque.objects.filter(activo=True)

        # Permite conservar la presentación actual si posteriormente
        # se desactiva, sin ofrecerla para nuevas relaciones.
        if self.instance.pk and self.instance.producto_empaque_id:
            productos = ProductoEmpaque.objects.filter(
                activo=True
            ) | ProductoEmpaque.objects.filter(
                pk=self.instance.producto_empaque_id
            )

        self.fields["producto_empaque"].queryset = productos.distinct()

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        producto = cleaned_data.get("producto_empaque")

        if cliente and producto:
            duplicado = ClienteProductoEmpaque.objects.filter(
                cliente=cliente,
                producto_empaque=producto,
            )

            if self.instance.pk:
                duplicado = duplicado.exclude(pk=self.instance.pk)

            if duplicado.exists():
                raise ValidationError(
                    "Este producto de empaque ya está relacionado "
                    "con el cliente seleccionado."
                )

        return cleaned_data