from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from .forms import (
    ClienteForm,
    EmpleadoForm,
    PersonaAdminForm,
    PersonaFisicaAdminForm,
    PersonaMoralAdminForm,
    ProveedorForm,
    DestinatarioForm
)
from .models import Direccion, Empleado, EmpleadoExtra, Persona, Telefono, Cliente, Proveedor, Destinatario

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


# ==========================================================
# INLINE: EXTRAS DEL EMPLEADO
# ==========================================================

# Administra los conceptos extras asignados a cada empleado.
# El concepto muestra su monto y no requiere una columna de captura.
# El monto se asigna al guardar, en EmpleadoAdmin.save_formset.
class EmpleadoExtraInline(admin.TabularInline):
    model = EmpleadoExtra
    extra = 1
    autocomplete_fields = ("concepto_extra",)
    fields = ("concepto_extra",)
    verbose_name = "Extra asignado"
    verbose_name_plural = "Extras asignados"
    show_change_link = False

    # Los conceptos inactivos se ocultan del autocompletado en
    # ConceptoExtraAdmin.get_search_results (catalogos/admin.py).
    # No se filtra aquí para no impedir guardar empleados que ya
    # tienen asignado un concepto que después se desactivó.


# ==========================================================
# ADMIN: EMPLEADOS
# ==========================================================
# Configura el administrador de empleados.
# Permite administrar los datos laborales y sus extras asignados.
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
 
    form = EmpleadoForm
 
    list_display = (
        "id",
        "empleado",
        "puesto",
        "nss",
        "mostrar_sueldo_diario",
        "fecha_ingreso",
        "activo",
    )
 
    list_display_links = ("id", "empleado")
 
    # Evita una consulta adicional por fila para persona y puesto.
    list_select_related = ("persona", "puesto")
 
    search_fields = (
        "persona__nombres",
        "persona__apellido_paterno",
        "persona__apellido_materno",
        "persona__curp",
        "persona__rfc",
        "nss",
    )
 
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
 
    # Los puestos inactivos se ocultan del autocompletado en
    # PuestoAdmin.get_search_results (catalogos/admin.py) y se
    # validan en EmpleadoForm.clean_puesto.
    autocomplete_fields = ("persona", "puesto")
 
    # Impide cambiar la persona una vez asignada al empleado.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("persona",) + tuple(self.readonly_fields)
 
        return self.readonly_fields
 
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
 
        for field in form.base_fields.values():
            field.widget.attrs["autocomplete"] = "off"
 
        return form
 
    # Asigna el monto vigente del catálogo a los extras nuevos o
    # modificados. Las filas sin cambios conservan su monto.
    def save_formset(self, request, form, formset, change):
        if formset.model is not EmpleadoExtra:
            return super().save_formset(request, form, formset, change)
 
        instancias = formset.save(commit=False)
 
        for obj in formset.deleted_objects:
            obj.delete()
 
        for instancia in instancias:
            instancia.monto = instancia.concepto_extra.monto
            instancia.save()
 
        formset.save_m2m()
 
    # Impide eliminar empleados desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False
 
    # Elimina la acción de borrado masivo del listado.
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions
 
    # Muestra la persona asociada bajo la columna Empleado.
    @admin.display(description="Empleado")
    def empleado(self, obj):
        return obj.persona
 
    # Muestra el sueldo diario con separador de miles y dos decimales.
    @admin.display(description="Sueldo diario", ordering="sueldo_diario")
    def mostrar_sueldo_diario(self, obj):
        return f"${obj.sueldo_diario:,.2f}"

# Administra los clientes registrados en el sistema.
# Permite consultar, buscar y filtrar clientes sin habilitar su eliminación.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteForm

    list_display = (
        "id",
        "cliente",
        "mostrar_limite_credito",
        "fecha_registro",
        "activo",
    )

    list_display_links = ("id", "cliente")
    list_select_related = ("persona",)

    search_fields = (
        "persona__nombres",
        "persona__apellido_paterno",
        "persona__apellido_materno",
        "persona__razon_social",
        "persona__nombre_comercial",
        "persona__rfc",
        "persona__curp",
    )

    list_filter = ("activo", "persona__tipo_persona")
    ordering = ("persona__id",)

    autocomplete_fields = ("persona",)

    fields = (
        "persona",
        "limite_credito",
        "fecha_registro",
        "activo",
    )

    readonly_fields = ("fecha_registro",)

    # Muestra la persona asociada bajo la columna Cliente.
    @admin.display(description="Cliente")
    def cliente(self, obj):
        return obj.persona

    # Al editar, la persona no se puede cambiar.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("persona",) + tuple(self.readonly_fields)

        return self.readonly_fields

    # Impide eliminar clientes desde el administrador.
    def has_delete_permission(self, request, obj=None):
        return False

    # Oculta la acción de eliminación masiva.
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

   # Muestra el límite de crédito con separador de miles y dos decimales.
    @admin.display(description="Límite de crédito", ordering="limite_credito")
    def mostrar_limite_credito(self, obj):
        return f"${obj.limite_credito:,.2f}"



# Administra los proveedores registrados en el sistema.
# Permite consultar y modificar sus datos comerciales sin habilitar su eliminación.
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
 
    form = ProveedorForm
 
    list_display = (
        "id",
        "proveedor",
        "mostrar_limite_credito",
        "fecha_registro",
        "activo",
    )
 
    list_display_links = ("id", "proveedor")
    list_select_related = ("persona",)
 
    search_fields = (
        "persona__nombres",
        "persona__apellido_paterno",
        "persona__apellido_materno",
        "persona__razon_social",
        "persona__nombre_comercial",
        "persona__rfc",
        "persona__curp",
    )
 
    list_filter = ("activo", "persona__tipo_persona")
 
    autocomplete_fields = ("persona",)
 
    fields = (
        "persona",
        "limite_credito",
        "fecha_registro",
        "activo",
    )
 
    readonly_fields = ("fecha_registro",)
 
    # Impide cambiar la persona una vez asignada al proveedor.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("persona",) + tuple(self.readonly_fields)
 
        return self.readonly_fields
 
    # Muestra la persona asociada bajo la columna Proveedor.
    @admin.display(description="Proveedor")
    def proveedor(self, obj):
        return obj.persona
 
    # Muestra el límite de crédito con separador de miles y dos decimales.
    @admin.display(
        description="Límite de crédito",
        ordering="limite_credito",
    )
    def mostrar_limite_credito(self, obj):
        return f"${obj.limite_credito:,.2f}"
 
    # Impide eliminar proveedores desde Django Admin.
    # Sin este permiso, Django también oculta la acción de borrado masivo.
    def has_delete_permission(self, request, obj=None):
        return False


# Administra los destinatarios registrados en el sistema.
# Permite consultar y modificar su estado sin habilitar su eliminación.
@admin.register(Destinatario)
class DestinatarioAdmin(admin.ModelAdmin):

    form = DestinatarioForm

    list_display = (
        "id",
        "destinatario",
        "fecha_registro",
        "activo",
    )

    list_display_links = ("id", "destinatario")
    list_select_related = ("persona",)

    search_fields = (
        "persona__nombres",
        "persona__apellido_paterno",
        "persona__apellido_materno",
        "persona__razon_social",
        "persona__nombre_comercial",
        "persona__rfc",
        "persona__curp",
    )

    list_filter = ("activo", "persona__tipo_persona")

    autocomplete_fields = ("persona",)

    fields = (
        "persona",
        "fecha_registro",
        "activo",
    )

    readonly_fields = ("fecha_registro",)

    # Al editar, impide cambiar la persona asignada.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("persona",) + tuple(self.readonly_fields)

        return self.readonly_fields

    # Muestra la persona asociada bajo la columna Destinatario.
    # Se ordena por razón social, apellidos y nombres para cubrir
    # personas físicas y morales.
    @admin.display(
        description="Destinatario",
        ordering=(
            "persona__razon_social",
            "persona__apellido_paterno",
            "persona__apellido_materno",
            "persona__nombres",
        ),
    )
    def destinatario(self, obj):
        return obj.persona

    # Impide eliminar destinatarios desde Django Admin.
    # Sin este permiso, Django también oculta la acción de borrado masivo.
    def has_delete_permission(self, request, obj=None):
        return False