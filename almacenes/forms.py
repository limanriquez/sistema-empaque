from django import forms
from django.db.models import Q

from .models import Almacen, EspacioAlmacen, Estiba, SeccionAlmacen


# Formulario para registrar y modificar almacenes.
# Limpia espacios y evita nombres duplicados sin distinguir mayúsculas.
class AlmacenForm(forms.ModelForm):

    class Meta:
        model = Almacen
        fields = ("nombre", "descripcion", "activo")

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())

        duplicados = Almacen.objects.filter(nombre__iexact=nombre)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe un almacén con este nombre."
            )

        return nombre


# Formulario para registrar y modificar espacios de almacén.
# Limpia espacios y evita nombres duplicados dentro del mismo almacén,
# sin distinguir mayúsculas. En el alta solo ofrece almacenes activos.
class EspacioAlmacenForm(forms.ModelForm):

    class Meta:
        model = EspacioAlmacen
        fields = ("almacen", "nombre", "descripcion", "activo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Al editar, el admin muestra el almacén de solo lectura y
        # el campo no existe en el formulario.
        if "almacen" in self.fields:
            self.fields["almacen"].queryset = Almacen.objects.filter(
                activo=True
            )

    def clean_nombre(self):
        return " ".join(self.cleaned_data["nombre"].split())

    def clean(self):
        cleaned_data = super().clean()

        # Al editar, el almacén no está en el formulario: se toma de la instancia.
        almacen = cleaned_data.get("almacen") or getattr(
            self.instance, "almacen", None
        )
        nombre = cleaned_data.get("nombre")

        if almacen and nombre:
            duplicados = EspacioAlmacen.objects.filter(
                almacen=almacen,
                nombre__iexact=nombre,
            )

            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)

            if duplicados.exists():
                self.add_error(
                    "nombre",
                    "Ya existe un espacio con este nombre en el almacén.",
                )

        return cleaned_data


# Formulario para registrar y modificar secciones de almacén.
# Limpia espacios y evita nombres duplicados dentro del mismo espacio,
# sin distinguir mayúsculas. En el alta solo ofrece espacios activos
# que pertenezcan a almacenes activos.
class SeccionAlmacenForm(forms.ModelForm):

    class Meta:
        model = SeccionAlmacen
        fields = ("espacio", "nombre", "descripcion", "activo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Al editar, el admin muestra el espacio de solo lectura y
        # el campo no existe en el formulario.
        if "espacio" in self.fields:
            self.fields["espacio"].queryset = (
                EspacioAlmacen.objects.filter(
                    activo=True,
                    almacen__activo=True,
                ).select_related("almacen")
            )

    def clean_nombre(self):
        return " ".join(self.cleaned_data["nombre"].split())

    def clean(self):
        cleaned_data = super().clean()

        # Al editar, el espacio no está en el formulario: se toma de la instancia.
        espacio = cleaned_data.get("espacio") or getattr(
            self.instance, "espacio", None
        )
        nombre = cleaned_data.get("nombre")

        if espacio and nombre:
            duplicados = SeccionAlmacen.objects.filter(
                espacio=espacio,
                nombre__iexact=nombre,
            )

            if self.instance.pk:
                duplicados = duplicados.exclude(pk=self.instance.pk)

            if duplicados.exists():
                self.add_error(
                    "nombre",
                    "Ya existe una sección con este nombre en el espacio.",
                )

        return cleaned_data


# Formulario para registrar y modificar estibas.
# Limpia espacios y evita nombres duplicados sin distinguir mayúsculas.
# La sección es opcional y puede cambiarse o quitarse en cualquier momento.
# Solo ofrece secciones activas (de espacios y almacenes activos), pero
# conserva la sección actual aunque se haya desactivado, para no impedir
# guardar la estiba.
class EstibaForm(forms.ModelForm):

    class Meta:
        model = Estiba
        fields = ("nombre", "seccion", "activo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        filtro = Q(
            activo=True,
            espacio__activo=True,
            espacio__almacen__activo=True,
        )

        # Mantiene como válida la sección actual aunque ya esté inactiva.
        if self.instance.pk and self.instance.seccion_id:
            filtro |= Q(pk=self.instance.seccion_id)

        self.fields["seccion"].queryset = (
            SeccionAlmacen.objects.filter(filtro).select_related(
                "espacio__almacen"
            )
        )
        self.fields["seccion"].help_text = (
            "Opcional. Déjela vacía si la estiba no está ubicada."
        )

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())

        duplicados = Estiba.objects.filter(nombre__iexact=nombre)

        if self.instance.pk:
            duplicados = duplicados.exclude(pk=self.instance.pk)

        if duplicados.exists():
            raise forms.ValidationError(
                "Ya existe una estiba con este nombre."
            )

        return nombre