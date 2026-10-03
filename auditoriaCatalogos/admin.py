from django.contrib import admin

from .models import (
    Puesto,
    Departamento,
    UnidadOperativa,
    Grupo,
)


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