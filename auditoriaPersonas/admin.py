from django.contrib import admin
from django.db.models import Prefetch

from .models import (
    Persona,
    PersonaAdscripcion,
    PersonaGrupo,
)


# ============================================================
# ADSCRIPCIÓN
# ============================================================

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
        "fecha_fin",
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


# ============================================================
# GRUPOS
# ============================================================

class PersonaGrupoInline(admin.TabularInline):
    model = PersonaGrupo
    extra = 1

    fields = (
        "grupo",
        "fecha_inicio",
        "fecha_fin",
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


# ============================================================
# PERSONA
# ============================================================

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):

    # --------------------------------------------------------
    # TABLA
    # --------------------------------------------------------

    list_display = (
        "id",
        "nombre_completo",
        "curp",
        "correo_institucional",
        "telefono_institucional",
        "puesto_actual",
        "departamento_actual",
        "unidad_actual",
        "activo",
    )

    list_display_links = (
        "id",
        "nombre_completo",
    )

    # --------------------------------------------------------
    # BÚSQUEDA
    # --------------------------------------------------------

    search_fields = (
        "nombre",
        "apellido_paterno",
        "apellido_materno",
        "=curp",
        "=correo_institucional",
        "telefono_institucional",
        "extension",

        "adscripciones__puesto__descripcion",
        "adscripciones__departamento__descripcion",
        "adscripciones__unidad_operativa__nombre",

        "grupos__grupo__nombre",
    )

    search_help_text = (
        "Busca por nombre, CURP, correo, teléfono, "
        "puesto, departamento, unidad operativa o grupo."
    )

    # --------------------------------------------------------
    # FILTROS
    # --------------------------------------------------------

    list_filter = (
        "activo",
        "adscripciones__puesto",
        "adscripciones__departamento",
        "adscripciones__unidad_operativa",
        "grupos__grupo",
    )

    # --------------------------------------------------------
    # ORDEN
    # --------------------------------------------------------

    ordering = (
        "apellido_paterno",
        "apellido_materno",
        "nombre",
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

        adscripcion_actual = (
            PersonaAdscripcion.objects
            .filter(fecha_fin__isnull=True)
            .select_related(
                "puesto",
                "departamento",
                "unidad_operativa",
            )
        )

        grupos_actuales = (
            PersonaGrupo.objects
            .filter(fecha_fin__isnull=True)
            .select_related("grupo")
        )

        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch(
                    "adscripciones",
                    queryset=adscripcion_actual,
                    to_attr="adscripcion_actual",
                ),
                Prefetch(
                    "grupos",
                    queryset=grupos_actuales,
                    to_attr="grupos_actuales",
                ),
            )
        )

    # --------------------------------------------------------
    # COLUMNAS CALCULADAS
    # --------------------------------------------------------

    @admin.display(
        description="Nombre",
        ordering=(
            "apellido_paterno",
            "apellido_materno",
            "nombre",
        ),
    )
    def nombre_completo(self, obj):
        return str(obj)

    @admin.display(
        description="Puesto",
        ordering="adscripciones__puesto__descripcion",
    )
    def puesto_actual(self, obj):

        if not obj.adscripcion_actual:
            return "-"

        return obj.adscripcion_actual[0].puesto.descripcion

    @admin.display(
        description="Departamento",
        ordering="adscripciones__departamento__descripcion",
    )
    def departamento_actual(self, obj):

        if not obj.adscripcion_actual:
            return "-"

        return obj.adscripcion_actual[0].departamento.descripcion

    @admin.display(
        description="Unidad",
        ordering="adscripciones__unidad_operativa__nombre",
    )
    def unidad_actual(self, obj):

        if not obj.adscripcion_actual:
            return "-"

        return obj.adscripcion_actual[0].unidad_operativa.nombre

    # --------------------------------------------------------
    # FORMULARIO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # OPCIONES DEL ADMIN
    # --------------------------------------------------------

    save_on_top = True
    save_as = False
    preserve_filters = True

    def has_delete_permission(self, request, obj=None):
        return False