from django import forms
from django.db.models import Q

from auditoriaCatalogos.models import Grupo, CargoComite
from auditoriaPersonas.models import Persona

from .models import Comite, ComiteIntegrante



from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from auditoriaCatalogos.models import TipoDocumentoProceso

from .models import (
    SesionComite,
    AsistenciaSesion,
    AgendaSesion,
    DocumentoSesion,
)


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






# ============================================================
# FORMULARIO: SESIÓN DE COMITÉ
# ============================================================
# Permite crear una sesión y completar sus datos posteriormente.
# La sesión puede guardarse sin fecha de finalización.
# ============================================================

class SesionComiteForm(forms.ModelForm):

    class Meta:
        model = SesionComite
        fields = (
            "comite",
            "numero_sesion",
            "tipo_sesion",
            "fecha_inicio",
            "hora_inicio",
            "fecha_fin",
            "hora_fin",
            "lugar",
            "estado",
            "observaciones",
        )

        widgets = {
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date"}
            ),
            "hora_inicio": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "hora_fin": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "observaciones": forms.Textarea(
                attrs={"rows": 3}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        fecha_inicio = cleaned_data.get("fecha_inicio")
        hora_inicio = cleaned_data.get("hora_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")
        hora_fin = cleaned_data.get("hora_fin")

        # La fecha y hora de finalización deben capturarse juntas.
        if bool(fecha_fin) != bool(hora_fin):
            raise ValidationError(
                "Para registrar la finalización, captura "
                "tanto la fecha como la hora."
            )

        # La finalización no puede ser anterior al inicio.
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                self.add_error(
                    "fecha_fin",
                    "La fecha de finalización no puede ser "
                    "anterior a la fecha de inicio."
                )

            elif (
                fecha_fin == fecha_inicio
                and hora_inicio
                and hora_fin
                and hora_fin < hora_inicio
            ):
                self.add_error(
                    "hora_fin",
                    "La hora de finalización no puede ser "
                    "anterior a la hora de inicio."
                )

        return cleaned_data


# ============================================================
# FORMULARIO: ASISTENCIA A SESIÓN
# ============================================================
# Muestra personas activas.
# Conserva disponible la persona seleccionada si posteriormente
# se desactiva, para no perder la referencia histórica.
# ============================================================

class AsistenciaSesionForm(forms.ModelForm):

    class Meta:
        model = AsistenciaSesion
        fields = (
            "persona",
            "tipo_asistencia",
            "observaciones",
        )

        widgets = {
            "observaciones": forms.Textarea(
                attrs={"rows": 2}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        personas = Persona.objects.filter(
            activo=True
        )

        # Permite conservar la persona de un registro histórico.
        if self.instance and self.instance.pk:
            personas = (
                Persona.objects.filter(
                    activo=True
                )
                | Persona.objects.filter(
                    pk=self.instance.persona_id
                )
            )

        self.fields["persona"].queryset = (
            personas.distinct().order_by(
                "apellido_paterno",
                "apellido_materno",
                "nombre",
            )
        )


# ============================================================
# FORMULARIO: PUNTO DE AGENDA
# ============================================================
# Captura el orden, título y descripción de cada asunto.
# ============================================================

class AgendaSesionForm(forms.ModelForm):

    class Meta:
        model = AgendaSesion
        fields = (
            "numero_orden",
            "titulo",
            "descripcion",
            "nota",
        )

        widgets = {
            "descripcion": forms.Textarea(
                attrs={"rows": 3}
            ),
            "nota": forms.Textarea(
                attrs={"rows": 2}
            ),
        }


# ============================================================
# FORMULARIO: DOCUMENTO DE SESIÓN
# ============================================================
# Registra documentos de entrada y salida.
# Los tipos inactivos no se ofrecen para nuevos registros,
# pero se conserva el tipo seleccionado en registros existentes.
# ============================================================

class DocumentoSesionForm(forms.ModelForm):

    class Meta:
        model = DocumentoSesion
        fields = (
            "agenda_sesion",
            "tipo_movimiento",
            "tipo_documento_proceso",
            "nombre",
            "fecha_documento",
            "ubicacion",
            "observaciones",
        )

        widgets = {
            "fecha_documento": forms.DateInput(
                attrs={"type": "date"}
            ),
            "observaciones": forms.Textarea(
                attrs={"rows": 2}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tipos = TipoDocumentoProceso.objects.filter(
            activo=True
        )

        if self.instance and self.instance.pk:
            tipos = (
                TipoDocumentoProceso.objects.filter(
                    activo=True
                )
                | TipoDocumentoProceso.objects.filter(
                    pk=self.instance.tipo_documento_proceso_id
                )
            )

        self.fields["tipo_documento_proceso"].queryset = (
            tipos.distinct().order_by("nombre")
        )


# ============================================================
# FORMSET: DOCUMENTOS DE SESIÓN
# ============================================================
# Limita los puntos de agenda disponibles a los que pertenecen
# a la sesión actual.
#
# La validación se realiza también en el formset para impedir
# referencias a puntos de agenda de otra sesión.
# ============================================================

class DocumentoSesionInlineFormSet(BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)

        if "agenda_sesion" in form.fields:
            queryset = AgendaSesion.objects.none()

            if self.instance and self.instance.pk:
                queryset = AgendaSesion.objects.filter(
                    sesion=self.instance
                )

            form.fields["agenda_sesion"].queryset = (
                queryset.order_by("numero_orden")
            )

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            agenda = form.cleaned_data.get("agenda_sesion")

            if (
                agenda
                and self.instance.pk
                and agenda.sesion_id != self.instance.pk
            ):
                raise ValidationError(
                    "Todos los puntos de agenda seleccionados "
                    "deben pertenecer a la sesión actual."
                )
