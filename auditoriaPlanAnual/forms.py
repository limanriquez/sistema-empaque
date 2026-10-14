
from django import forms

from .models import (
    PlanAnual,
    ActividadPlan,
    NotaPlan,
)


class PlanAnualForm(forms.ModelForm):
    class Meta:
        model = PlanAnual
        fields = "__all__"


class ActividadPlanForm(forms.ModelForm):
    TIPO_CHOICES = [
        ("PROCESO", "Proceso existente"),
        ("ACTIVIDAD", "Actividad nueva"),
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.RadioSelect,
        label="Tipo de registro",
        initial="ACTIVIDAD",
        required=True,
    )

    class Meta:
        model = ActividadPlan
        fields = [
            "proceso",
            "nombre",
            "objetivo",
            "fecha_inicio",
            "fecha_termino",
            "responsable",
            "estado",
        ]
        labels = {
            "proceso": "Proceso",
            "nombre": "Nombre de la actividad",
            "objetivo": "Objetivo particular",
            "fecha_inicio": "Fecha de inicio",
            "fecha_termino": "Fecha de término",
            "responsable": "Responsable",
            "estado": "Estado",
        }
        help_texts = {
            "proceso": (
                "Selecciona un proceso del catálogo cuando "
                "corresponda a un proceso existente."
            ),
            "nombre": (
                "Captura el nombre cuando sea una actividad nueva "
                "que no corresponda a un proceso del catálogo."
            ),
        }
        widgets = {
            "objetivo": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["proceso"].required = False
        self.fields["nombre"].required = False

        if self.instance and self.instance.pk:
            self.initial["tipo"] = (
                "PROCESO"
                if self.instance.proceso_id
                else "ACTIVIDAD"
            )

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo")
        proceso = cleaned_data.get("proceso")
        nombre = (cleaned_data.get("nombre") or "").strip()

        if tipo == "PROCESO":
            if not proceso:
                self.add_error(
                    "proceso",
                    "Selecciona un proceso del catálogo.",
                )
            else:
                cleaned_data["nombre"] = proceso.nombre

        elif tipo == "ACTIVIDAD":
            if not nombre:
                self.add_error(
                    "nombre",
                    "Captura el nombre de la actividad nueva.",
                )

            cleaned_data["proceso"] = None
            cleaned_data["nombre"] = nombre

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        tipo = self.cleaned_data.get("tipo")

        if tipo == "PROCESO" and instance.proceso_id:
            instance.nombre = instance.proceso.nombre

        elif tipo == "ACTIVIDAD":
            instance.proceso = None
            instance.nombre = (
                self.cleaned_data.get("nombre") or ""
            ).strip()

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class NotaPlanForm(forms.ModelForm):
    class Meta:
        model = NotaPlan
        fields = "__all__"
