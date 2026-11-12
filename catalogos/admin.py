from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .forms import UnidadMedidaForm, EstacionTrabajoForm, ConceptoNominaForm
from .models import ConceptoExtra, GoHome, Puesto, UnidadMedida, EstacionTrabajo, Tamano, Calidad, ConceptoNomina


@admin.register(GoHome)
class GoHomeAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_model_perms(self, request):
        return {
            "add": False,
            "change": True,
            "delete": False,
            "view": False,
        }

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("home"))


# Administrador del catálogo de puestos.
# Permite consultar, registrar, buscar y filtrar puestos,
# así como activar o desactivar los registros desde su formulario.
@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):

    # Columnas que se mostrarán en el listado.
    list_display = ("id", "nombre", "descripcion", "activo")

    # Columnas que permiten abrir el formulario de edición.
    list_display_links = ("id", "nombre")

    # Campos utilizados para realizar búsquedas.
    search_fields = ("nombre", "descripcion")

    # Filtro para mostrar puestos activos o inactivos.
    list_filter = ("activo",)

    # Orden alfabético por nombre.
    ordering = ("nombre",)

    def get_form(self, request, obj=None, **kwargs):
        # Obtiene el formulario de alta o edición del puesto.
        form = super().get_form(request, obj, **kwargs)

        # Desactiva las sugerencias de autocompletado del navegador.
        for field in form.base_fields.values():
            field.widget.attrs["autocomplete"] = "off"

        return form

    # En el autocompletado de empleados, muestra únicamente
    # los puestos activos, sin alterar el listado del catálogo.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if (
            request.GET.get("app_label") == "personas"
            and request.GET.get("model_name") == "empleado"
            and request.GET.get("field_name") == "puesto"
        ):
            queryset = queryset.filter(activo=True)

        return queryset, use_distinct

    # Impide eliminar puestos desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


# Administrador del catálogo de conceptos extras para empleados.
# Permite registrar, consultar, buscar y activar o desactivar conceptos,
# así como administrar su descripción y monto desde Django Admin.
@admin.register(ConceptoExtra)
class ConceptoExtraAdmin(admin.ModelAdmin):

    # Columnas que se mostrarán en el listado del catálogo.
    list_display = ("id", "nombre", "descripcion", "monto", "activo")

    # Columnas que permiten abrir el formulario al hacer clic.
    list_display_links = ("id", "nombre")

    # Campos en los que se buscará el texto ingresado.
    search_fields = ("nombre", "descripcion")

    # Filtro lateral para mostrar conceptos activos o inactivos.
    list_filter = ("activo",)

    # Ordena los conceptos alfabéticamente por nombre.
    ordering = ("nombre",)

    def get_form(self, request, obj=None, **kwargs):
        # Obtiene el formulario de alta o edición del concepto extra.
        form = super().get_form(request, obj, **kwargs)

        # Evita que el navegador sugiera valores guardados anteriormente.
        for field in form.base_fields.values():
            field.widget.attrs["autocomplete"] = "off"

        return form

    # En el autocompletado de extras del empleado, muestra
    # únicamente los conceptos activos.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if (
            request.GET.get("app_label") == "personas"
            and request.GET.get("model_name") == "empleadoextra"
            and request.GET.get("field_name") == "concepto_extra"
        ):
            queryset = queryset.filter(activo=True)

        return queryset, use_distinct

    # Impide eliminar conceptos extras desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


# Administra las unidades de medida de los materiales.
# No habilita la eliminación: una unidad en uso está protegida y las
# demás se retiran desactivándolas.
@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):

    form = UnidadMedidaForm

    list_display = (
        "id",
        "nombre",
        "abreviatura",
        "permite_decimales",
        "activo",
    )

    list_display_links = ("id", "nombre")
    list_filter = ("activo", "permite_decimales")
    search_fields = ("nombre", "abreviatura")

    fields = (
        "nombre",
        "abreviatura",
        "permite_decimales",
        "activo",
    )

    # Impide eliminar unidades desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False

# ==========================================================
# ADMIN: ESTACIÓN DE TRABAJO
#
# Administra el catálogo de estaciones de la empacadora.
# Los registros no pueden eliminarse; únicamente pueden
# modificarse o desactivarse.
# ==========================================================

@admin.register(EstacionTrabajo)
class EstacionTrabajoAdmin(admin.ModelAdmin):

    form = EstacionTrabajoForm

    list_display = (
        "id",
        "nombre",
        "activo",
    )

    search_fields = (
        "nombre",
        "descripcion",
    )

    list_filter = (
        "activo",
    )

    ordering = (
        "nombre",
    )

    readonly_fields = (
        "id",
    )

    fields = (
        "id",
        "nombre",
        "descripcion",
        "activo",
    )

    # Impide eliminar registros desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


# ==========================================================
# ADMINISTRACIÓN: CALIDAD
#
# Permite administrar las calidades comerciales utilizadas
# en los productos de empaque.
#
# Los registros no pueden eliminarse físicamente para
# conservar la integridad histórica.
# ==========================================================

@admin.register(Calidad)
class CalidadAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre",
        "activo",
    )

    list_display_links = (
        "id",
        "nombre",
    )

    search_fields = (
        "nombre",
        "descripcion",
    )

    list_filter = (
        "activo",
    )

    ordering = (
        "nombre",
    )

    list_per_page = 25

    fields = (
        "nombre",
        "descripcion",
        "activo",
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ==========================================================
# ADMINISTRACIÓN: TAMAÑO
#
# Permite administrar los tamaños o calibres utilizados
# en los productos de empaque.
#
# Los registros no pueden eliminarse físicamente para
# conservar la integridad histórica.
# ==========================================================

@admin.register(Tamano)
class TamanoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre",
        "activo",
    )

    list_display_links = (
        "id",
        "nombre",
    )

    search_fields = (
        "nombre",
        "descripcion",
    )

    list_filter = (
        "activo",
    )

    ordering = (
        "nombre",
    )

    list_per_page = 25

    fields = (
        "nombre",
        "descripcion",
        "activo",
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ==========================================================
# ADMIN: CONCEPTO DE NÓMINA
#
# Administración del catálogo de conceptos de nómina.
# No permite eliminar registros para conservar su historial.
# ==========================================================
@admin.register(ConceptoNomina)
class ConceptoNominaAdmin(admin.ModelAdmin):

    form = ConceptoNominaForm

    list_display = (
        "id",
        "descripcion",
        "tipo",
        "activo",
    )

    list_filter = (
        "tipo",
        "activo",
    )

    search_fields = (
        "descripcion",
    )

    ordering = (
        "descripcion",
    )

    def has_delete_permission(self, request, obj=None):
        return False