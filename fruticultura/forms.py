from django import forms
from .models import Huerta, LoteHuerta

class HuertaForm(forms.ModelForm):
    class Meta:
        model = Huerta
        fields = [
            "nombre",
            "descripcion",
            "activo",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "autocomplete": "off",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()

        queryset = Huerta.objects.filter(nombre__iexact=nombre)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Ya existe una huerta con ese nombre."
            )

        return nombre


class LoteHuertaForm(forms.ModelForm):
    class Meta:
        model = LoteHuerta
        fields = [
            "huerta",
            "nombre",
            "descripcion",
            "activo",
        ]

        widgets = {
            "huerta": forms.Select(attrs={
                "class": "form-select",
            }),
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "autocomplete": "off",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        huerta = self.cleaned_data.get("huerta")

        queryset = LoteHuerta.objects.filter(
            huerta=huerta,
            nombre__iexact=nombre,
        )

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Ya existe un lote con ese nombre en esta huerta."
            )

        return nombre
    

