from django.contrib import admin

from .models import (
    Persona,
    PersonaAdscripcion,
    PersonaGrupo,
)


class PersonaAdscripcionInline(admin.StackedInline):
    model = PersonaAdscripcion
    extra = 0
    max_num = 1
    can_delete = False

    fields = (
        "puesto",
        "departamento",
        "unidad_operativa",
        "fecha_inicio",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(fecha_fin__isnull=True)
            .select_related(
                "puesto",
                "departamento",
                "unidad_operativa",
            )
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "puesto":
            kwargs["queryset"] = (
                db_field.related_model.objects
                .filter(activo=True)
                .order_by("descripcion")
            )

        elif db_field.name == "departamento":
            kwargs["queryset"] = (
                db_field.related_model.objects
                .filter(activo=True)
                .order_by("descripcion")
            )

        elif db_field.name == "unidad_operativa":
            kwargs["queryset"] = (
                db_field.related_model.objects
                .filter(activo=True)
                .order_by("nombre")
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )


class PersonaGrupoInline(admin.TabularInline):
    model = PersonaGrupo
    extra = 1

    fields = (
        "grupo",
        "fecha_inicio",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(fecha_fin__isnull=True)
            .select_related("grupo")
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "grupo":
            kwargs["queryset"] = (
                db_field.related_model.objects
                .filter(activo=True)
                .order_by("nombre")
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre_completo",
        "curp",
        "correo_institucional",
        "telefono_institucional",
        "extension",
        "activo",
    )

    list_display_links = (
        "id",
        "nombre_completo",
    )

    search_fields = (
        "nombre",
        "apellido_paterno",
        "apellido_materno",
        "curp",
        "correo_institucional",
        "telefono_institucional",
    )

    list_filter = (
        "activo",
    )

    ordering = (
        "apellido_paterno",
        "apellido_materno",
        "nombre",
    )

    fieldsets = (
        (
            "Datos personales",
            {
                "fields": (
                    "nombre",
                    "apellido_paterno",
                    "apellido_materno",
                    "curp",
                )
            },
        ),
        (
            "Contacto institucional",
            {
                "fields": (
                    "correo_institucional",
                    "telefono_institucional",
                    "extension",
                )
            },
        ),
        (
            "Estado",
            {
                "fields": (
                    "activo",
                )
            },
        ),
    )

    inlines = (
        PersonaAdscripcionInline,
        PersonaGrupoInline,
    )

    def nombre_completo(self, obj):
        return str(obj)

    nombre_completo.short_description = "Nombre"

    def has_delete_permission(self, request, obj=None):
        return False