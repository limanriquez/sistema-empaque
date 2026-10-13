from django.contrib import admin
from django.shortcuts import redirect
from django import forms

from .models import (
    Puesto,
    Departamento,
    UnidadOperativa,
    Grupo,
    GoHome,
    TipoComite,
    CargoComite,
    TipoDocumento,
     TipoDocumentoProceso,  # Nuevo catálogo
    Documento,
    Proceso,
)

@admin.register(GoHome)
class HomeLinkAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('/')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descripcion",
        "activo",
    )

    list_display_links = (
        "id",
        "descripcion",
    )

    search_fields = (
        "descripcion",
    )

    list_filter = (
        "activo",
    )

    ordering = (
        "descripcion",
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descripcion",
        "activo",
    )

    list_display_links = (
        "id",
        "descripcion",
    )

    search_fields = (
        "descripcion",
    )

    list_filter = (
        "activo",
    )

    ordering = (
        "descripcion",
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UnidadOperativa)
class UnidadOperativaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "tipo",
        "activo",
    )

    list_display_links = (
        "id",
        "nombre",
    )

    search_fields = (
        "nombre",
    )

    list_filter = (
        "tipo",
        "activo",
    )

    ordering = (
        "nombre",
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "descripcion",
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

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# CATÁLOGOS DEL MÓDULO DE COMITÉS
# ============================================================
# Catálogos utilizados para la configuración y operación
# de los comités.
#
# La baja de estos registros es lógica mediante el campo
# 'activo'. No se permite su eliminación física.
# ============================================================


@admin.register(TipoComite)
class TipoComiteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "descripcion",
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

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CargoComite)
class CargoComiteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "descripcion",
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

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# MÓDULO DE DOCUMENTOS Y PROCESOS
# ============================================================

class SinAutocompletadoAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs["autocomplete"] = "off"


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    form = SinAutocompletadoAdminForm

    list_display = ("id", "nombre", "activo")
    list_display_links = ("id", "nombre")
    search_fields = ("nombre",)
    list_filter = ("activo",)
    ordering = ("nombre",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    form = SinAutocompletadoAdminForm

    list_display = (
        "id",
        "nombre",
        "tipo_documento",
        "version",
        "fecha_publicacion",
        "activo",
    )
    list_display_links = ("id", "nombre")
    search_fields = ("nombre", "version")
    list_filter = ("tipo_documento", "activo", "fecha_publicacion")
    ordering = ("nombre", "version")
    readonly_fields = ("fecha_registro",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    form = SinAutocompletadoAdminForm

    list_display = (
        "id",
        "clave_control",
        "nombre",
        "documento",
        "activo",
    )
    list_display_links = ("id", "clave_control", "nombre")
    search_fields = ("clave_control", "nombre", "documento__nombre")
    list_filter = ("activo", "documento__tipo_documento")
    ordering = ("nombre",)
    readonly_fields = ("fecha_registro",)

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# TIPO DE DOCUMENTO DE PROCESO
# ============================================================
# Catálogo transversal para clasificar documentos operativos
# utilizados en los módulos del Sistema de Administración
# de Auditorías.
# ============================================================

@admin.register(TipoDocumentoProceso)
class TipoDocumentoProcesoAdmin(admin.ModelAdmin):

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

    def has_delete_permission(self, request, obj=None):
        return False