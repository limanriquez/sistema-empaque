from django.contrib import admin

from .forms import (
    AlmacenForm,
    EspacioAlmacenForm,
    EstibaForm,
    SeccionAlmacenForm,
)
from .models import Almacen, EspacioAlmacen, Estiba, SeccionAlmacen


# Administra las bodegas o instalaciones físicas de la empacadora.
# Permite consultar, buscar y modificar almacenes sin habilitar su eliminación.
@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):

    form = AlmacenForm

    list_display = (
        "id",
        "nombre",
        "activo",
    )

    list_display_links = ("id", "nombre")
    list_filter = ("activo",)
    search_fields = ("nombre", "descripcion")

    fields = (
        "nombre",
        "descripcion",
        "activo",
    )

    # Oculta almacenes inactivos en el autocompletado del campo
    # almacen de Espacio.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if (
            request.GET.get("app_label") == "almacen"
            and request.GET.get("model_name") == "espacioalmacen"
            and request.GET.get("field_name") == "almacen"
        ):
            queryset = queryset.filter(activo=True)

        return queryset, use_distinct

    # Impide eliminar almacenes desde Django Admin.
    # Sin este permiso, Django también oculta la acción de borrado masivo.
    def has_delete_permission(self, request, obj=None):
        return False


# Administra los espacios físicos de cada almacén, como cámaras de frío
# o zonas de almacenamiento. Impide cambiar el almacén una vez asignado
# y no habilita la eliminación.
@admin.register(EspacioAlmacen)
class EspacioAlmacenAdmin(admin.ModelAdmin):

    form = EspacioAlmacenForm

    list_display = (
        "id",
        "nombre",
        "almacen",
        "activo",
    )

    list_display_links = ("id", "nombre")
    list_select_related = ("almacen",)
    list_filter = ("activo", "almacen")

    search_fields = (
        "nombre",
        "descripcion",
        "almacen__nombre",
    )

    autocomplete_fields = ("almacen",)

    fields = (
        "almacen",
        "nombre",
        "descripcion",
        "activo",
    )

    # Evita una consulta por resultado: el __str__ del espacio
    # muestra también el almacén.
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("almacen")

    # Oculta espacios inactivos (o de almacenes inactivos) en el
    # autocompletado del campo espacio de Sección.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if (
            request.GET.get("app_label") == "almacen"
            and request.GET.get("model_name") == "seccionalmacen"
            and request.GET.get("field_name") == "espacio"
        ):
            queryset = queryset.filter(
                activo=True,
                almacen__activo=True,
            )

        return queryset, use_distinct

    # Al editar, el almacén no se puede cambiar.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("almacen",) + tuple(self.readonly_fields)

        return self.readonly_fields

    # Impide eliminar espacios desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


# Administra las secciones físicas de cada espacio de almacén.
# Impide cambiar el espacio una vez asignado y no habilita la eliminación.
@admin.register(SeccionAlmacen)
class SeccionAlmacenAdmin(admin.ModelAdmin):

    form = SeccionAlmacenForm

    list_display = (
        "id",
        "nombre",
        "espacio",
        "activo",
    )

    list_display_links = ("id", "nombre")

    # Evita consultas adicionales por fila: el __str__ del espacio
    # también consulta el almacén.
    list_select_related = ("espacio__almacen",)

    list_filter = ("activo", "espacio__almacen", "espacio")

    search_fields = (
        "nombre",
        "descripcion",
        "espacio__nombre",
        "espacio__almacen__nombre",
    )

    autocomplete_fields = ("espacio",)

    fields = (
        "espacio",
        "nombre",
        "descripcion",
        "activo",
    )

    # Evita una consulta por resultado: el __str__ de la sección
    # muestra también el espacio y el almacén.
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "espacio__almacen"
        )

    # Oculta secciones inactivas (o de espacios y almacenes inactivos)
    # en el autocompletado del campo seccion de Estiba.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if (
            request.GET.get("app_label") == "almacen"
            and request.GET.get("model_name") == "estiba"
            and request.GET.get("field_name") == "seccion"
        ):
            queryset = queryset.filter(
                activo=True,
                espacio__activo=True,
                espacio__almacen__activo=True,
            )

        return queryset, use_distinct

    # Al editar, el espacio no se puede cambiar.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("espacio",) + tuple(self.readonly_fields)

        return self.readonly_fields

    # Impide eliminar secciones desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


# Administra las estibas disponibles para el almacenamiento.
# La sección es opcional: la estiba puede anclarse a cualquier sección,
# cambiarse de lugar o quedar sin ubicación en cualquier momento.
# No habilita la eliminación.
@admin.register(Estiba)
class EstibaAdmin(admin.ModelAdmin):

    form = EstibaForm

    list_display = (
        "id",
        "nombre",
        "ubicacion",
        "activo",
    )

    list_display_links = ("id", "nombre")

    # Evita consultas adicionales por fila: el __str__ de la sección
    # consulta el espacio y este, a su vez, el almacén.
    list_select_related = ("seccion__espacio__almacen",)

    list_filter = (
        "activo",
        ("seccion", admin.EmptyFieldListFilter),
        "seccion__espacio__almacen",
    )

    search_fields = (
        "nombre",
        "seccion__nombre",
        "seccion__espacio__nombre",
        "seccion__espacio__almacen__nombre",
    )

    autocomplete_fields = ("seccion",)

    fields = (
        "nombre",
        "seccion",
        "activo",
    )

    # Muestra la ubicación actual de la estiba.
    @admin.display(
        description="Ubicación",
        ordering="seccion__espacio__almacen__nombre",
    )
    def ubicacion(self, obj):
        return obj.seccion or "Sin ubicación"

    # Impide eliminar estibas desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False