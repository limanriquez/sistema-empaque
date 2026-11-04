from django.contrib import admin
from .models import Huerta, LoteHuerta, Variedad
from .forms import HuertaForm, LoteHuertaForm
 

# Register your models here.
@admin.register(Huerta)
class HuertaAdmin(admin.ModelAdmin):
    form = HuertaForm

    list_display = (
        "id",
        "nombre",
        "descripcion",
        "activo",
    )

    list_display_links = (
        "nombre",
    )

    search_fields = (
        "nombre",
        "descripcion",
    )

    list_filter = (
        "activo",
    )

    list_per_page = 25
    ordering = ("nombre",)

    readonly_fields = ("id",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LoteHuerta)
class LoteHuertaAdmin(admin.ModelAdmin):
    form = LoteHuertaForm

    list_display = (
        "id",
        "nombre",
        "huerta",
        "descripcion",
        "activo",
    )

    list_display_links = (
        "nombre",
    )

    search_fields = (
        "nombre",
        "huerta__nombre",
        "descripcion",
    )

    list_filter = (
        "huerta",
        "activo",
    )

    list_select_related = (
        "huerta",
    )

    list_per_page = 25
    ordering = ("huerta__nombre", "nombre")

    readonly_fields = ("id",)

    def has_delete_permission(self, request, obj=None):
        return False
    

# ==========================================================
# ADMIN: VARIEDAD
#
# Administración del catálogo de variedades de fruta.
#
# Permite registrar, consultar, buscar y activar o desactivar
# variedades utilizadas en los procesos de la empacadora.
#
# No se permite la eliminación física de registros para
# conservar la trazabilidad histórica.
#
# La baja de una variedad se realiza mediante el campo
# activo.
#
# ==========================================================

@admin.register(Variedad)
class VariedadAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre",
        "activo",
    )

    list_display_links = ("nombre",)
    list_filter = ("activo",)
    search_fields = ("nombre",)
    #list_editable = ("activo",)
    ordering = ("nombre",)

    fields = (
        "nombre",
        "activo",
        "observaciones",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions