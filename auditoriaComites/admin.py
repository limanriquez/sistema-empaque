from django.contrib import admin
from django.db.models import Prefetch


from .forms import (
    ComiteForm,
    ComiteIntegranteForm,
)

from .models import (
    Comite,
    ComiteIntegrante,
)


from .forms import (
    SesionComiteForm,
    AsistenciaSesionForm,
    AgendaSesionForm,
    DocumentoSesionForm,
    DocumentoSesionInlineFormSet,
)

from .models import (
    SesionComite,
    AsistenciaSesion,
    AgendaSesion,
    DocumentoSesion,
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



# ============================================================
# INLINE: ASISTENCIA
# ============================================================
# Permite agregar asistentes a la sesión.
# No permite eliminar físicamente registros de asistencia.
# ============================================================

class AsistenciaSesionInline(admin.TabularInline):
    model = AsistenciaSesion
    form = AsistenciaSesionForm

    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "persona",
        "tipo_asistencia",
        "observaciones",
    )

    autocomplete_fields = (
        "persona",
    )

    ordering = (
        "persona__apellido_paterno",
        "persona__nombre",
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# INLINE: AGENDA
# ============================================================
# Permite agregar y ordenar los puntos a tratar.
# ============================================================

class AgendaSesionInline(admin.TabularInline):
    model = AgendaSesion
    form = AgendaSesionForm

    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "numero_orden",
        "titulo",
        "descripcion",
        "nota",
    )

    ordering = (
        "numero_orden",
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# INLINE: DOCUMENTOS
# ============================================================
# Permite registrar documentos recibidos y generados.
# Los documentos pueden vincularse opcionalmente con un punto
# de agenda de la sesión actual.
# ============================================================

class DocumentoSesionInline(admin.TabularInline):
    model = DocumentoSesion
    form = DocumentoSesionForm
    formset = DocumentoSesionInlineFormSet

    extra = 0
    can_delete = False
    show_change_link = True

    fields = (
        "tipo_movimiento",
        "tipo_documento_proceso",
        "nombre",
        "fecha_documento",
        "agenda_sesion",
        "ubicacion",
        "observaciones",
    )

    ordering = (
        "tipo_movimiento",
        "nombre",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "tipo_documento_proceso",
                "agenda_sesion",
            )
        )

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# ADMIN: SESIONES DE COMITÉ
# ============================================================
# Permite crear la sesión inicialmente y completarla después.
#
# La asistencia, agenda y documentación se administran desde
# la misma pantalla mediante inlines.
#
# No se bloquea la edición automáticamente al cerrar la sesión.
# ============================================================

@admin.register(SesionComite)
class SesionComiteAdmin(admin.ModelAdmin):

    form = SesionComiteForm

    # --------------------------------------------------------
    # TABLA
    # --------------------------------------------------------

    list_display = (
        "id",
        "comite",
        "numero_sesion",
        "tipo_sesion",
        "fecha_inicio",
        "hora_inicio",
        "fecha_fin",
        "estado",
    )

    list_display_links = (
        "id",
        "numero_sesion",
    )

    # --------------------------------------------------------
    # BÚSQUEDA
    # --------------------------------------------------------

    search_fields = (
        "comite__nombre",
        "lugar",
        "observaciones",
    )

    search_help_text = (
        "Busca por nombre de comité, lugar u observaciones."
    )

    # --------------------------------------------------------
    # FILTROS
    # --------------------------------------------------------

    list_filter = (
        "comite",
        "tipo_sesion",
        "estado",
        "fecha_inicio",
    )

    # --------------------------------------------------------
    # ORDEN
    # --------------------------------------------------------

    ordering = (
        "-fecha_inicio",
        "-numero_sesion",
    )

    # --------------------------------------------------------
    # PAGINACIÓN
    # --------------------------------------------------------

    list_per_page = 50
    list_max_show_all = 200

    # --------------------------------------------------------
    # RENDIMIENTO
    # --------------------------------------------------------

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("comite")
            .prefetch_related(
                Prefetch(
                    "asistencias",
                    queryset=AsistenciaSesion.objects.select_related(
                        "persona"
                    ),
                ),
                Prefetch(
                    "agenda",
                    queryset=AgendaSesion.objects.order_by(
                        "numero_orden"
                    ),
                ),
                Prefetch(
                    "documentos",
                    queryset=DocumentoSesion.objects.select_related(
                        "tipo_documento_proceso",
                        "agenda_sesion",
                    ),
                ),
            )
        )

    # --------------------------------------------------------
    # FORMULARIO
    # --------------------------------------------------------

    fieldsets = (
        (
            "Información de la sesión",
            {
                "fields": (
                    "comite",
                    "numero_sesion",
                    "tipo_sesion",
                    "estado",
                )
            },
        ),
        (
            "Programación y horario",
            {
                "fields": (
                    "fecha_inicio",
                    "hora_inicio",
                    "fecha_fin",
                    "hora_fin",
                    "lugar",
                )
            },
        ),
        (
            "Observaciones",
            {
                "fields": (
                    "observaciones",
                )
            },
        ),
    )

    inlines = (
        AsistenciaSesionInline,
        AgendaSesionInline,
        DocumentoSesionInline,
    )

    # --------------------------------------------------------
    # OPCIONES DEL ADMIN
    # --------------------------------------------------------

    save_on_top = True
    save_as = False
    preserve_filters = True

    def has_delete_permission(self, request, obj=None):
        # Se conserva la trazabilidad histórica de las sesiones.
        return False