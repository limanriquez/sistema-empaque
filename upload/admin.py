import csv

from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponse
from django.utils.html import format_html

from .models import RegistroAuditoria


class TieneArchivoFilter(admin.SimpleListFilter):
    title = "Evidencia adjunta"
    parameter_name = "tiene_archivo"

    def lookups(self, request, model_admin):
        return (
            ("si", "Con archivo"),
            ("no", "Sin archivo"),
        )

    def queryset(self, request, queryset):
        if self.value() == "si":
            return queryset.exclude(
                Q(archivo="") | Q(archivo__isnull=True)
            )

        if self.value() == "no":
            return queryset.filter(
                Q(archivo="") | Q(archivo__isnull=True)
            )

        return queryset


def proteger_csv(valor):
    """
    Evita que el contenido de texto se interprete como fórmula
    al abrir el CSV en Excel.
    """
    texto = "" if valor is None else str(valor)

    if texto.lstrip().startswith(
        ("=", "+", "-", "@", "\t", "\r")
    ):
        return "'" + texto

    return texto


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):

    # Columnas del listado
    list_display = (
        "id",
        "id_revision",
        "id_criterio",
        "tipo",
        "indicador_archivo",
        "status",
        "fecha_creacion",
        "fecha_actualizacion",
    )

    list_display_links = (
        "id",
        "id_revision",
    )

    # Filtros laterales
    list_filter = (
        "tipo",
        "status",
        TieneArchivoFilter,
    )

    # Buscar exclusivamente por ID de revisión exacto
    search_fields = (
        "=id_revision",
    )

    search_help_text = (
        "Escribe el ID de revisión y pulsa Buscar. "
        "La búsqueda es exacta."
    )

    # Orden predeterminado por ID de revisión ascendente
    ordering = (
        "id_revision",
    )

    list_per_page = 50
    list_max_show_all = 200

    # Permite cambiar el estado directamente en el listado
    list_editable = (
        "status",
    )

    # Campos de solo lectura
    readonly_fields = (
        "id_compuesto",
        "fecha_creacion",
        "fecha_actualizacion",
    )

    # Organización del formulario
    fieldsets = (
        ("Identificación", {
            "fields": (
                "id_revision",
                "id_criterio",
                "id_compuesto",
                "tipo",
                "status",
            )
        }),
        ("Información de auditoría", {
            "fields": (
                "observacion",
                "recomendacion",
                "notas",
            )
        }),
        ("Evidencia documental", {
            "fields": (
                "archivo",
            )
        }),
        ("Control del registro", {
            "fields": (
                "fecha_creacion",
                "fecha_actualizacion",
            ),
            "classes": (
                "collapse",
            ),
        }),
    )

    # Acciones masivas
    actions = (
        "activar_registros",
        "desactivar_registros",
        "exportar_csv",
    )

    @admin.display(
        description="Evidencia",
        ordering="archivo",
    )
    def indicador_archivo(self, obj):
        if obj.archivo:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">'
                'Ver archivo</a>',
                obj.archivo.url,
            )

        return "Sin archivo"

    @admin.action(
        description="Activar registros seleccionados"
    )
    def activar_registros(self, request, queryset):
        cantidad = queryset.filter(
            status=False
        ).update(status=True)

        self.message_user(
            request,
            f"{cantidad} registro(s) activado(s).",
            messages.SUCCESS,
        )

    @admin.action(
        description="Desactivar registros seleccionados"
    )
    def desactivar_registros(self, request, queryset):
        cantidad = queryset.filter(
            status=True
        ).update(status=False)

        self.message_user(
            request,
            f"{cantidad} registro(s) desactivado(s).",
            messages.SUCCESS,
        )

    @admin.action(
        description="Exportar seleccionados a CSV (Excel)"
    )
    def exportar_csv(self, request, queryset):
        respuesta = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )

        respuesta["Content-Disposition"] = (
            'attachment; filename="registros_auditoria.csv"'
        )

        # BOM UTF-8 para conservar acentos en Excel
        respuesta.write("\ufeff")

        writer = csv.writer(respuesta)

        writer.writerow([
            "ID",
            "ID revisión",
            "ID criterio",
            "Tipo",
            "Observación",
            "Recomendación",
            "Notas",
            "Activo",
            "Archivo",
            "Fecha creación",
            "Fecha actualización",
        ])

        for registro in queryset.iterator(chunk_size=1000):
            writer.writerow([
                registro.pk,
                proteger_csv(registro.id_revision),
                proteger_csv(registro.id_criterio),
                registro.get_tipo_display(),
                proteger_csv(registro.observacion),
                proteger_csv(registro.recomendacion),
                proteger_csv(registro.notas),
                "Sí" if registro.status else "No",
                (
                    registro.archivo.name
                    if registro.archivo
                    else ""
                ),
                registro.fecha_creacion,
                registro.fecha_actualizacion,
            ])

        return respuesta
