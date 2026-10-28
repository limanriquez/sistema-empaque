from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from .forms import (
    PersonaAdminForm,
    PersonaFisicaAdminForm,
    PersonaMoralAdminForm,
    
)
from .models import Persona, Direccion, Telefono
from .models import Empleado, EmpleadoExtra
from .forms import EmpleadoExtraForm
# ==========================================================
# INLINE: DIRECCIONES
# ==========================================================

class DireccionInline(admin.StackedInline):
    model = Direccion
    verbose_name = "Dirección"
    verbose_name_plural = "Direcciones"
    extra = 1

    fields = (
        "tipo_direccion",
        "calle",
        "numero_exterior",
        "numero_interior",
        "colonia",
        "codigo_postal",
        "localidad",
        "municipio",
        "estado",
        "pais",
        "es_principal",
        "activa",
        "referencias",
    )


# ==========================================================
# INLINE: TELÉFONOS
# ==========================================================

class TelefonoInline(admin.StackedInline):
    model = Telefono
    verbose_name = "Teléfono"
    verbose_name_plural = "Teléfonos"
    extra = 1

    fields = (
        "tipo_telefono",
        "numero",
        "activo",
    )


# ==========================================================
# ADMIN: PERSONAS
# ==========================================================

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):

    form = PersonaAdminForm

    list_display = (
        "id",
        "tipo_persona",
        "identificacion",
        "curp",
        "rfc",
    )

    list_filter = (
        "tipo_persona",
    )

    search_fields = (
        "curp",
        "rfc",
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "razon_social",
        "nombre_comercial",
    )

    readonly_fields = (
        "id",
        "creado_en",
    )

    # No se muestran activo ni las fechas de control.
    fieldsets = (
        (
            "Datos de persona",
            {
                "fields": (
                    "id",
                    "tipo_persona",
                    "curp",
                    "rfc",
                    "nombres",
                    "apellido_paterno",
                    "apellido_materno",
                    "razon_social",
                    "nombre_comercial",
                ),
            },
        ),
    )

    inlines = (
        DireccionInline,
        TelefonoInline,
    )

    class Media:
        js = ("personas/admin/persona_admin.js",)
        css = {
            "all": ("personas/admin/persona_admin.css",),
        }

    # ------------------------------------------------------
    # FILTRAR EL LISTADO POR TIPO DE PERSONA
    # ------------------------------------------------------

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        tipo_persona = request.GET.get("tipo_persona")

        if tipo_persona == "1":
            queryset = queryset.filter(
                tipo_persona=Persona.TipoPersona.FISICA
            )

        elif tipo_persona == "2":
            queryset = queryset.filter(
                tipo_persona=Persona.TipoPersona.MORAL
            )

        return queryset
    
       # Filtra los resultados del autocompletado cuando se selecciona
    # una persona para el formulario de empleado.
    # En los demás formularios conserva el comportamiento existente.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        # Identifica el autocompletado del campo persona de Empleado.
        if (
            request.GET.get("app_label") == "personas"
            and request.GET.get("model_name") == "empleado"
            and request.GET.get("field_name") == "persona"
        ):
            queryset = queryset.filter(
                tipo_persona=Persona.TipoPersona.FISICA
            )

        return queryset, use_distinct

       # ------------------------------------------------------
    # IMPEDIR ELIMINACIÓN DE PERSONAS
    # ------------------------------------------------------

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    # ------------------------------------------------------
    # URL PERSONALIZADA PARA ALTA DE PERSONA FÍSICA Y MORAL
    # ------------------------------------------------------

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "add/fisica/",
                self.admin_site.admin_view(self.add_fisica_view),
                name="personas_persona_add_fisica",
            ),
            path(
                "add/moral/",
                self.admin_site.admin_view(self.add_moral_view),
                name="personas_persona_add_moral",
            ),
        ]

        return custom_urls + urls

    def add_fisica_view(self, request):
        request._persona_tipo_alta = "fisica"
        return self.add_view(request)

    def add_moral_view(self, request):
        request._persona_tipo_alta = "moral"
        return self.add_view(request)

    def add_view(self, request, form_url="", extra_context=None):
        if not getattr(request, "_persona_tipo_alta", None):
            return redirect(
                reverse("admin:personas_persona_add_fisica")
            )

        return super().add_view(
            request,
            form_url,
            extra_context,
        )

    # ------------------------------------------------------
    # FORMULARIO Y AUTOCOMPLETADO
    # ------------------------------------------------------

    def get_form(self, request, obj=None, **kwargs):
        tipo_alta = getattr(request, "_persona_tipo_alta", None)

        if obj is None:
            if tipo_alta == "fisica":
                kwargs["form"] = PersonaFisicaAdminForm
            elif tipo_alta == "moral":
                kwargs["form"] = PersonaMoralAdminForm

        form_class = super().get_form(
            request,
            obj,
            **kwargs,
        )

        for campo in form_class.base_fields.values():
            campo.widget.attrs["autocomplete"] = "off"

        campos_personales = (
            "curp",
            "rfc",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "razon_social",
            "nombre_comercial",
        )

        for nombre in campos_personales:
            if nombre in form_class.base_fields:
                widget = form_class.base_fields[nombre].widget
                widget.attrs["autocomplete"] = "off"
                widget.attrs["autocorrect"] = "off"
                widget.attrs["autocapitalize"] = "off"
                widget.attrs["spellcheck"] = "false"

        return form_class

    # ------------------------------------------------------
    # CAMPOS PARA ALTA DE PERSONA FÍSICA O MORAL
    # ------------------------------------------------------

   
    def get_fieldsets(self, request, obj=None):
        tipo_alta = getattr(request, "_persona_tipo_alta", None)

        # Al editar, usar el tipo que ya tiene guardado la persona.
        if obj is not None:
            if obj.tipo_persona == Persona.TipoPersona.FISICA:
                return (
                    (
                        "Datos de persona física",
                        {
                            "fields": (
                                "id",
                                "curp",
                                "rfc",
                                "nombres",
                                "apellido_paterno",
                                "apellido_materno",
                            ),
                        },
                    ),
                )

            return (
                (
                    "Datos de persona moral",
                    {
                        "fields": (
                            "id",
                            "rfc",
                            "razon_social",
                            "nombre_comercial",
                        ),
                    },
                ),
            )

        # Al dar de alta, usar el tipo indicado por la ruta.
        if tipo_alta == "fisica":
            return (
                (
                    "Datos de persona física",
                    {
                        "fields": (
                            "curp",
                            "rfc",
                            "nombres",
                            "apellido_paterno",
                            "apellido_materno",
                        ),
                    },
                ),
            )

        if tipo_alta == "moral":
            return (
                (
                    "Datos de persona moral",
                    {
                        "fields": (
                            "rfc",
                            "razon_social",
                            "nombre_comercial",
                        ),
                    },
                ),
            )

        return super().get_fieldsets(request, obj)

    # ------------------------------------------------------
    # GUARDADO
    # ------------------------------------------------------

    def save_model(self, request, obj, form, change):
        if not change:
            tipo_alta = getattr(request, "_persona_tipo_alta", None)

            if tipo_alta == "fisica":
                obj.tipo_persona = Persona.TipoPersona.FISICA
                obj.razon_social = ""
                obj.nombre_comercial = ""

            elif tipo_alta == "moral":
                obj.tipo_persona = Persona.TipoPersona.MORAL
                obj.curp = None
                obj.nombres = ""
                obj.apellido_paterno = ""
                obj.apellido_materno = ""

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    
    # ------------------------------------------------------
    # IDENTIFICACIÓN EN EL LISTADO
    # Muestra el nombre o razón social como enlace al
    # formulario de edición de la persona correspondiente.
    # ------------------------------------------------------

    @admin.display(description="Nombre o razón social")
    def identificacion(self, obj):
        if obj.tipo_persona == Persona.TipoPersona.FISICA:
            nombre = " ".join(
                filter(
                    None,
                    (
                        obj.nombres,
                        obj.apellido_paterno,
                        obj.apellido_materno,
                    ),
                )
            )
        else:
            nombre = obj.nombre_comercial or obj.razon_social

        url = reverse(
            "admin:personas_persona_change",
            args=[obj.pk],
        )

        return format_html(
            '<a href="{}">{}</a>',
            url,
            nombre,
        )


    
    # ------------------------------------------------------
    # PREPARAR LOS BOTONES DE ALTA DEL LISTADO
    # Proporciona a la plantilla las rutas específicas para
    # agregar personas físicas y personas morales.
    # ------------------------------------------------------

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context["alta_persona_fisica_url"] = reverse(
            "admin:personas_persona_add_fisica"
        )

        extra_context["alta_persona_moral_url"] = reverse(
            "admin:personas_persona_add_moral"
        )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    
# Administra los conceptos extras asignados a cada empleado.
# El concepto muestra su monto y no requiere una columna de captura.
class EmpleadoExtraInline(admin.TabularInline):
    model = EmpleadoExtra
    extra = 1
    autocomplete_fields = ("concepto_extra",)
    fields = ("concepto_extra",)
    verbose_name = "Extra asignado"
    verbose_name_plural = "Extras asignados"
    show_change_link = False

    # Solo permite seleccionar conceptos extras activos.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "concepto_extra":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                activo=True
            )

        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    # Asigna automáticamente el monto vigente del catálogo al guardar.
    def save_new(self, form, commit=True):
        instancia = form.save(commit=False)
        instancia.monto = instancia.concepto_extra.monto

        if commit:
            instancia.save()
            form.save_m2m()

        return instancia

    # Actualiza el monto cuando se modifica una asignación existente.
    def save_existing(self, form, instancia, commit=True):
        instancia = form.save(commit=False)
        instancia.monto = instancia.concepto_extra.monto

        if commit:
            instancia.save()
            form.save_m2m()

        return instancia



# Configura el administrador de empleados.
# Permite administrar los datos laborales y sus extras asignados.
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "persona",
        "puesto",
        "nss",
        "sueldo_diario",
        "fecha_ingreso",
        "activo",
    )

    list_display_links = ("id", "persona")
    search_fields = ("persona__curp", "persona__rfc", "nss")
    list_filter = ("activo", "puesto")
    ordering = ("persona__id",)
    inlines = (EmpleadoExtraInline,)

    fields = (
        "persona",
        "nss",
        "puesto",
        "sueldo_diario",
        "fecha_ingreso",
        "activo",
    )

    autocomplete_fields = ("persona", "puesto")

    # Solo permite seleccionar puestos activos en el formulario.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "puesto":
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                activo=True
            )

        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        for field in form.base_fields.values():
            field.widget.attrs["autocomplete"] = "off"

        return form

        # Impide eliminar empleados desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False

    # Elimina la acción de borrado masivo del listado.
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

