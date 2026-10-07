from django.contrib import admin

from .forms import (
    ComiteForm,
    ComiteIntegranteForm,
)

from .models import (
    Comite,
    ComiteIntegrante,
)


class ComiteIntegranteInline(admin.TabularInline):
    """
    Administración de los integrantes del comité.

    Permite:
        - agregar integrantes;
        - consultar integrantes;
        - conservar el historial;
        - finalizar participaciones.

    Las participaciones históricas no deben eliminarse físicamente.
    """

    model = ComiteIntegrante
    form = ComiteIntegranteForm

    extra = 0

    fields = (
        "persona",
        "cargo_comite",
        "fecha_inicio",
        "fecha_fin",
        "estatus",
        "motivo_fin",
        "observaciones",
    )

    autocomplete_fields = (
        "persona",
        "cargo_comite",
    )

    readonly_fields = (
        "fecha_fin",
        "estatus",
        "motivo_fin",
    )

    ordering = (
        "-fecha_inicio",
    )

    def has_delete_permission(self, request, obj=None):
        """
        No se permite eliminar físicamente una participación.

        El historial debe conservarse.
        """
        return False


@admin.register(Comite)
class ComiteAdmin(admin.ModelAdmin):
    """
    Administración principal de los Comités.

    Desde aquí se administra:

        - Tipo de comité.
        - Nombre o identificación.
        - Fecha de constitución.
        - Periodo.
        - Estatus.
        - Observaciones.
        - Integrantes del comité.

    Los integrantes se administran mediante ComiteIntegranteInline.
    """

    form = ComiteForm

    list_display = (
        "id",
        "nombre",
        "tipo_comite",
        "fecha_constitucion",
        "fecha_inicio",
        "fecha_fin",
        "estatus",
    )

    list_display_links = (
        "id",
        "nombre",
    )

    search_fields = (
        "nombre",
        "observaciones",
    )

    list_filter = (
        "tipo_comite",
        "estatus",
    )

    ordering = (
        "-fecha_inicio",
        "nombre",
    )

    autocomplete_fields = (
        "tipo_comite",
    )

    fieldsets = (
        (
            "Información del comité",
            {
                "fields": (
                    "tipo_comite",
                    "nombre",
                    "fecha_constitucion",
                    "fecha_inicio",
                    "fecha_fin",
                    "estatus",
                    "observaciones",
                )
            },
        ),
    )

    inlines = (
        ComiteIntegranteInline,
    )

    def has_delete_permission(self, request, obj=None):
        """
        No se permite eliminar físicamente un comité,
        debido a la necesidad de conservar su historial.
        """
        return False