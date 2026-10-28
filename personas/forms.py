from django import forms

from .models import Empleado, EmpleadoExtra, Persona

class PersonaAdminForm(forms.ModelForm):
    """
    Formulario general para consultar o editar personas.
    """

    class Meta:
        model = Persona
        fields = (
            "tipo_persona",
            "curp",
            "rfc",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "razon_social",
            "nombre_comercial",
        )

    def clean(self):
        cleaned_data = super().clean()

        curp = (cleaned_data.get("curp") or "").strip().upper()
        rfc = (cleaned_data.get("rfc") or "").strip().upper()

        if "curp" in cleaned_data:
            cleaned_data["curp"] = curp or None

        if "rfc" in cleaned_data:
            cleaned_data["rfc"] = rfc or None

        otras_personas = Persona.objects.all()

        if self.instance.pk:
            otras_personas = otras_personas.exclude(pk=self.instance.pk)

        if curp and otras_personas.filter(curp=curp).exists():
            self.add_error(
                "curp",
                "Ya existe una persona registrada con esta CURP.",
            )

        if rfc and otras_personas.filter(rfc=rfc).exists():
            self.add_error(
                "rfc",
                "Ya existe una persona registrada con este RFC.",
            )

        return cleaned_data


class PersonaFisicaAdminForm(forms.ModelForm):
    """
    Formulario exclusivo para registrar personas físicas.
    """

    class Meta:
        model = Persona
        fields = (
            "curp",
            "rfc",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
        )

    def clean(self):
        cleaned_data = super().clean()

        curp = (cleaned_data.get("curp") or "").strip().upper()
        rfc = (cleaned_data.get("rfc") or "").strip().upper()

        cleaned_data["curp"] = curp or None
        cleaned_data["rfc"] = rfc or None

        otras_personas = Persona.objects.all()

        if self.instance.pk:
            otras_personas = otras_personas.exclude(pk=self.instance.pk)

        # CURP obligatoria y única.
        if not curp:
            self.add_error(
                "curp",
                "La CURP es obligatoria para una persona física.",
            )
        elif len(curp) != 18:
            self.add_error(
                "curp",
                "La CURP debe tener 18 caracteres.",
            )
        elif otras_personas.filter(curp=curp).exists():
            self.add_error(
                "curp",
                "Ya existe una persona registrada con esta CURP.",
            )

        # RFC opcional y único.
        if rfc:
            if len(rfc) != 13:
                self.add_error(
                    "rfc",
                    "El RFC de una persona física debe tener 13 caracteres.",
                )
            elif otras_personas.filter(rfc=rfc).exists():
                self.add_error(
                    "rfc",
                    "Ya existe una persona registrada con este RFC.",
                )

        # Nombre y apellido paterno obligatorios.
        if not (cleaned_data.get("nombres") or "").strip():
            self.add_error("nombres", "Capture el nombre.")

        if not (cleaned_data.get("apellido_paterno") or "").strip():
            self.add_error(
                "apellido_paterno",
                "Capture el apellido paterno.",
            )

        # Limpiar campos exclusivos de persona moral.
        cleaned_data["razon_social"] = ""
        cleaned_data["nombre_comercial"] = ""
        cleaned_data["tipo_persona"] = Persona.TipoPersona.FISICA

        return cleaned_data


class PersonaMoralAdminForm(forms.ModelForm):
    """
    Formulario exclusivo para registrar personas morales.
    """

    class Meta:
        model = Persona
        fields = (
            "rfc",
            "razon_social",
            "nombre_comercial",
        )

    def clean(self):
        cleaned_data = super().clean()

        rfc = (cleaned_data.get("rfc") or "").strip().upper()
        razon_social = (
            cleaned_data.get("razon_social") or ""
        ).strip()
        nombre_comercial = (
            cleaned_data.get("nombre_comercial") or ""
        ).strip()

        cleaned_data["rfc"] = rfc or None
        cleaned_data["razon_social"] = razon_social
        cleaned_data["nombre_comercial"] = nombre_comercial

        otras_personas = Persona.objects.all()

        if self.instance.pk:
            otras_personas = otras_personas.exclude(pk=self.instance.pk)

        # RFC obligatorio y único.
        if not rfc:
            self.add_error(
                "rfc",
                "El RFC es obligatorio para una persona moral.",
            )
        elif len(rfc) != 12:
            self.add_error(
                "rfc",
                "El RFC de una persona moral debe tener 12 caracteres.",
            )
        elif otras_personas.filter(rfc=rfc).exists():
            self.add_error(
                "rfc",
                "Ya existe una persona registrada con este RFC.",
            )

        # Razón social obligatoria.
        if not razon_social:
            self.add_error(
                "razon_social",
                "Capture la razón social.",
            )

        # Limpiar campos exclusivos de persona física.
        cleaned_data["curp"] = None
        cleaned_data["nombres"] = ""
        cleaned_data["apellido_paterno"] = ""
        cleaned_data["apellido_materno"] = ""

        # El tipo se determina en el servidor.
        cleaned_data["tipo_persona"] = Persona.TipoPersona.MORAL

        return cleaned_data



# Formulario para registrar y modificar empleados.
# Limita la selección a personas físicas y valida los datos laborales.
class EmpleadoForm(forms.ModelForm):

    class Meta:
        model = Empleado
        fields = (
            "persona",
            "nss",
            "puesto",
            "sueldo_diario",
            "fecha_ingreso",
            "activo",
        )

        widgets = {
            "nss": forms.TextInput(attrs={
                "autocomplete": "off",
                "maxlength": "11",
                "placeholder": "11 dígitos (opcional)",
            }),
            "sueldo_diario": forms.NumberInput(attrs={
                "min": "0",
                "step": "0.01",
                "autocomplete": "off",
            }),
            "fecha_ingreso": forms.DateInput(attrs={
                "type": "date",
                "autocomplete": "off",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # El selector del formulario solo debe incluir personas físicas.
        self.fields["persona"].queryset = Persona.objects.filter(
            tipo_persona=1
        )

    def clean_persona(self):
        # Impide asignar una persona moral, incluso si se envía manualmente.
        persona = self.cleaned_data["persona"]

        if persona.tipo_persona != 1:
            raise forms.ValidationError(
                "Solo se pueden registrar personas físicas como empleados."
            )

        return persona

    def clean_nss(self):
        # El NSS es opcional; si se captura, debe contener 11 dígitos.
        nss = self.cleaned_data.get("nss", "").strip()

        if nss and (not nss.isdigit() or len(nss) != 11):
            raise forms.ValidationError(
                "El NSS debe contener exactamente 11 dígitos."
            )

        return nss

    def clean_sueldo_diario(self):
        # El sueldo diario no puede ser negativo.
        sueldo = self.cleaned_data["sueldo_diario"]

        if sueldo < 0:
            raise forms.ValidationError(
                "El sueldo diario no puede ser negativo."
            )

        return sueldo


# Formulario para asignar conceptos extras a un empleado.
# El monto se obtiene del catálogo y no puede editarse manualmente.
class EmpleadoExtraForm(forms.ModelForm):

    class Meta:
        model = EmpleadoExtra
        fields = ("concepto_extra", "monto")
        widgets = {
            "monto": forms.NumberInput(attrs={
                "readonly": "readonly",
                "step": "0.01",
            }),
        }