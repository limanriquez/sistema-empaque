from django import forms
from django.db.models import Q

from auditoriaCatalogos.models import Grupo, CargoComite
from auditoriaPersonas.models import Persona

from .models import Comite, ComiteIntegrante


class ComiteForm(forms.ModelForm):
    """
    Formulario para administrar la información general del comité.
    """

    class Meta:
        model = Comite
        fields = (
            "tipo_comite",
            "nombre",
            "fecha_constitucion",
            "fecha_inicio",
            "fecha_fin",
            "estatus",
            "observaciones",
        )


class ComiteIntegranteForm(forms.ModelForm):
    """
    Formulario para agregar una persona a un comité.

    Permite localizar personas:
        - directamente por persona;
        - mediante un Grupo.

    Una persona que ya tenga una participación ACTIVA dentro
    del comité actual no se muestra nuevamente como disponible.
    """

    BUSQUEDA_CHOICES = [
        ("PERSONA", "Buscar por persona"),
        ("GRUPO", "Buscar por grupo"),
    ]

    modo_busqueda = forms.ChoiceField(
        label="Buscar personas por",
        choices=BUSQUEDA_CHOICES,
        initial="PERSONA",
        required=False,
    )

    grupo = forms.ModelChoiceField(
        label="Grupo",
        queryset=Grupo.objects.all(),
        required=False,
    )

    class Meta:
        model = ComiteIntegrante
        fields = (
            "modo_busqueda",
            "grupo",
            "persona",
            "cargo_comite",
            "fecha_inicio",
            "observaciones",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["grupo"].label = "Grupo"

        self.fields["persona"].queryset = (
            Persona.objects
            .filter(activo=True)
            .order_by(
                "apellido_paterno",
                "apellido_materno",
                "nombre",
            )
        )

        self.fields["cargo_comite"].queryset = (
            CargoComite.objects
            .filter(activo=True)
            .order_by("nombre")
        )

        # Cuando estamos agregando una persona desde el inline,
        # instance.comite contiene el comité actual.
        if self.instance and self.instance.pk:
            comite = self.instance.comite
        else:
            comite = getattr(self.instance, "comite", None)

        if comite:
            personas_activas = ComiteIntegrante.objects.filter(
                comite=comite,
                estatus="ACTIVO",
            ).values_list(
                "persona_id",
                flat=True,
            )

            self.fields["persona"].queryset = (
                self.fields["persona"].queryset
                .exclude(id__in=personas_activas)
            )

        # Si el formulario recibió un grupo, filtramos las personas.
        grupo_id = self.data.get("grupo") or self.initial.get("grupo")

        if grupo_id:
            try:
                grupo_id = int(grupo_id)

                personas_grupo = Persona.objects.filter(
                    grupos__grupo_id=grupo_id,
                    activo=True,
                )

                if comite:
                    personas_grupo = personas_grupo.exclude(
                        id__in=personas_activas
                    )

                self.fields["persona"].queryset = (
                    personas_grupo
                    .distinct()
                    .order_by(
                        "apellido_paterno",
                        "apellido_materno",
                        "nombre",
                    )
                )

            except (TypeError, ValueError):
                pass

    def clean(self):
        cleaned_data = super().clean()

        persona = cleaned_data.get("persona")
        comite = getattr(self.instance, "comite", None)

        if persona and comite:
            existe = ComiteIntegrante.objects.filter(
                comite=comite,
                persona=persona,
                estatus="ACTIVO",
            ).exists()

            if existe:
                raise forms.ValidationError(
                    "La persona ya tiene una participación activa "
                    "en este comité."
                )

        return cleaned_data