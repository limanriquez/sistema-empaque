from decimal import Decimal
from django import forms
from .models import UnidadMedida, EstacionTrabajo

# Formulario para registrar y modificar unidades de medida.
# Limpia espacios y evita nombres y abreviaturas duplicados sin
# distinguir mayúsculas. Impide restringir a enteros una unidad que ya
# tiene materiales con cantidades fraccionarias.
class UnidadMedidaForm(forms.ModelForm):

    class Meta:
        model = UnidadMedida
        fields = ("nombre", "abreviatura", "permite_decimales", "activo")

    def _duplicados(self, **filtro):
        duplicados = UnidadMedida.objects.filter(**filtro)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        return duplicados.exists()

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())

        if self._duplicados(nombre__iexact=nombre):
            raise forms.ValidationError(
                "Ya existe una unidad con este nombre."
            )

        return nombre

    def clean_abreviatura(self):
        # La abreviatura conserva su capitalización (por ejemplo "L"
        # para litro), pero no admite espacios internos.
        abreviatura = "".join(self.cleaned_data["abreviatura"].split())

        if not abreviatura:
            raise forms.ValidationError("Capture la abreviatura.")

        if self._duplicados(abreviatura__iexact=abreviatura):
            raise forms.ValidationError(
                "Ya existe una unidad con esta abreviatura."
            )

        return abreviatura

    def clean(self):
        cleaned_data = super().clean()

        # Al pasar de decimales a enteros, verifica que ningún material
        # que use la unidad tenga cantidades fraccionarias.
        if (
            self.instance.pk
            and self.instance.permite_decimales
            and cleaned_data.get("permite_decimales") is False
        ):
            for material in self.instance.materiales.all():
                if (
                    material.existencia % 1 != Decimal("0")
                    or material.stock_minimo % 1 != Decimal("0")
                ):
                    self.add_error(
                        "permite_decimales",
                        f"No se puede restringir a enteros: el material "
                        f"«{material.nombre}» tiene cantidades con "
                        f"decimales.",
                    )
                    break

        return cleaned_data

    
# ==========================================================
# FORMULARIO: ESTACIÓN DE TRABAJO
#
# Permite registrar y modificar las estaciones de trabajo
# de la empacadora, controlando sus datos generales y estado.
#
# Se desactiva el autocompletado para evitar que el navegador
# muestre sugerencias de registros capturados anteriormente.
# ==========================================================

class EstacionTrabajoForm(forms.ModelForm):

    class Meta:
        model = EstacionTrabajo

        fields = [
            "nombre",
            "descripcion",
            "activo",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la estación",
                "autocomplete": "new-password",
            }),

            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción de la estación",
                "autocomplete": "off",
            }),

            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


