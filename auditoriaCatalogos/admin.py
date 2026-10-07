from django.contrib import admin
from django.shortcuts import redirect

from .models import (
    Puesto,
    Departamento,
    UnidadOperativa,
    Grupo,
    GoHome,
    TipoComite,
    CargoComite,
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