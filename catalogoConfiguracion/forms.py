from django import forms
from django.core.exceptions import ValidationError

from .models import CodigoCaja, CodigoTarima


class GenerarCodigosCajaForm(forms.Form):

    # ======================================================
    # LONGITUD DEL CÓDIGO
    # ======================================================

    longitud = forms.ChoiceField(
        label="Longitud del código",
        choices=[
            (4, "4 caracteres - 1,679,616 combinaciones"),
        ],
        initial=4,
        disabled=True,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    # ======================================================
    # CONFIRMACIÓN
    # ======================================================

    confirmar = forms.BooleanField(
        label=(
            "Confirmo que deseo generar los 1,679,616 "
            "códigos de caja."
        ),
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    # ======================================================
    # VALIDACIÓN DE LA TABLA
    # ======================================================

    def clean(self):

        cleaned_data = super().clean()

        if CodigoCaja.objects.exists():

            raise ValidationError(
                "No es posible generar el catálogo. "
                "La tabla de códigos de caja ya contiene "
                "registros y debe estar completamente vacía."
            )

        return cleaned_data

    # ======================================================
    # EJECUCIÓN DEL GENERADOR
    # ======================================================

    def generar(self):

        if not self.is_valid():
            raise ValidationError(
                "No se puede ejecutar la generación. "
                "Revisa los errores del formulario."
            )

        from .services import generar_codigos_caja

        return generar_codigos_caja(
            longitud=4
        )


class GenerarCodigosTarimaForm(forms.Form):

    # ======================================================
    # LONGITUD DEL CÓDIGO
    # ======================================================

    longitud = forms.ChoiceField(
        label="Longitud del código",
        choices=[
            (4, "4 caracteres - 1,679,616 combinaciones"),
        ],
        initial=4,
        disabled=True,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    # ======================================================
    # CONFIRMACIÓN
    # ======================================================

    confirmar = forms.BooleanField(
        label=(
            "Confirmo que deseo generar los 1,679,616 "
            "códigos de tarima."
        ),
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    # ======================================================
    # VALIDACIÓN DE LA TABLA
    # ======================================================

    def clean(self):

        cleaned_data = super().clean()

        if CodigoTarima.objects.exists():

            raise ValidationError(
                "No es posible generar el catálogo. "
                "La tabla de códigos de tarima ya contiene "
                "registros y debe estar completamente vacía."
            )

        return cleaned_data