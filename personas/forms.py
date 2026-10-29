from django import forms

from .models import Empleado, EmpleadoExtra, Persona, Cliente, Proveedor, Destinatario


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
    El tipo de persona y la limpieza de campos de persona moral
    se resuelven en PersonaAdmin.save_model.
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

        return cleaned_data


class PersonaMoralAdminForm(forms.ModelForm):
    """
    Formulario exclusivo para registrar personas morales.
    El tipo de persona y la limpieza de campos de persona física
    se resuelven en PersonaAdmin.save_model.
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
        # No se definen widgets: el admin usa los suyos por defecto
        # (calendario de Django en la fecha, estilos del admin, etc.).
        # El autocomplete="off" lo aplica EmpleadoAdmin.get_form.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Al editar, el admin muestra la persona de solo lectura y
        # el campo no existe en el formulario.
        if "persona" in self.fields:
            # El selector solo debe incluir personas físicas.
            self.fields["persona"].queryset = Persona.objects.filter(
                tipo_persona=Persona.TipoPersona.FISICA
            )

        self.fields["nss"].widget.attrs["placeholder"] = (
            "11 dígitos (opcional)"
        )

    def clean_persona(self):
        # Impide asignar una persona moral, incluso si se envía manualmente.
        persona = self.cleaned_data["persona"]

        if persona.tipo_persona != Persona.TipoPersona.FISICA:
            raise forms.ValidationError(
                "Solo se pueden registrar personas físicas como empleados."
            )

        return persona

    def clean_puesto(self):
        # No permite elegir un puesto inactivo, pero sí conservar el que
        # el empleado ya tiene aunque se haya desactivado después.
        puesto = self.cleaned_data["puesto"]
        puesto_actual_id = self.instance.puesto_id if self.instance.pk else None

        if not puesto.activo and puesto.pk != puesto_actual_id:
            raise forms.ValidationError(
                "El puesto seleccionado no está activo."
            )

        return puesto

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
# Actualmente no se usa en el admin; se conserva por si se requiere
# fuera de él.
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


# Formulario para registrar y modificar clientes.
# En el alta solo ofrece personas activas que aún no son clientes.
class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = (
            "persona",
            "limite_credito",
            "activo",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Al editar, el admin muestra la persona de solo lectura y
        # el campo no existe en el formulario.
        if "persona" in self.fields:
            self.fields["persona"].queryset = Persona.objects.filter(
                activo=True,
                cliente__isnull=True,
            )

    def clean_limite_credito(self):
        # El límite de crédito no puede ser negativo.
        limite = self.cleaned_data["limite_credito"]

        if limite < 0:
            raise forms.ValidationError(
                "El límite de crédito no puede ser negativo."
            )

        return limite


# Formulario para registrar y modificar proveedores.
# En el alta solo ofrece personas activas que aún no son proveedores.
# El límite de crédito se valida mediante las reglas del modelo.
class ProveedorForm(forms.ModelForm):

    class Meta:
        model = Proveedor
        fields = (
            "persona",
            "limite_credito",
            "activo",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Al editar, el admin muestra la persona de solo lectura y
        # el campo no existe en el formulario.
        if "persona" in self.fields:
            self.fields["persona"].queryset = Persona.objects.filter(
                activo=True,
                proveedor__isnull=True,
            )


# Formulario para registrar y modificar destinatarios.
# En el alta solo ofrece personas activas que aún no son destinatarios.
# Al editar, la persona queda bloqueada y no puede cambiarse.
# Reutiliza los datos generales almacenados en Persona.
class DestinatarioForm(forms.ModelForm):

    class Meta:
        model = Destinatario
        fields = (
            "persona",
            "activo",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si el campo no está (por ejemplo, el admin lo muestra de solo
        # lectura al editar), no hay nada que configurar.
        if "persona" not in self.fields:
            return

        if self.instance.pk:
            # Edición: la persona no se puede cambiar. Con disabled,
            # Django ignora lo enviado y conserva el valor de la instancia.
            self.fields["persona"].disabled = True
        else:
            # Alta: solo personas activas que aún no son destinatarios.
            self.fields["persona"].queryset = Persona.objects.filter(
                activo=True,
                destinatario__isnull=True,
            ).order_by(
                "apellido_paterno",
                "apellido_materno",
                "nombres",
            )