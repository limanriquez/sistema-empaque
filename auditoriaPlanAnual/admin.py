
from django.contrib import admin

from .models import (
    PlanAnual,
    ActividadPlan,
    NotaPlan,
)

from .forms import (
    PlanAnualForm,
    ActividadPlanForm,
    NotaPlanForm,
)


class ActividadPlanInline(admin.StackedInline):
    model = ActividadPlan
    form = ActividadPlanForm
    extra = 1
    show_change_link = False

    fields = (
        "tipo",
        "proceso",
        "nombre",
        "objetivo",
        "fecha_inicio",
        "fecha_termino",
        "responsable",
        "estado",
    )

    verbose_name = "Actividad o proceso"
    verbose_name_plural = "Programa de actividades"


class NotaPlanInline(admin.TabularInline):
    model = NotaPlan
    form = NotaPlanForm
    extra = 1

    fields = ("nota",)

    verbose_name = "Nota"
    verbose_name_plural = "Notas y observaciones"


@admin.register(PlanAnual)
class PlanAnualAdmin(admin.ModelAdmin):
    form = PlanAnualForm

    list_display = (
        "vigencia",
        "estado",
        "sesion_presentacion",
        "sesion_aprobacion",
        "fecha_aprobacion",
    )

    list_display_links = ("vigencia",)

    search_fields = (
        "objetivo",
        "alcance",
        "metodologia",
    )

    list_filter = (
        "estado",
        "vigencia",
        "fecha_aprobacion",
    )

    ordering = ("-vigencia",)

    fieldsets = (
        (
            "Plan Anual de Auditoría",
            {
                "fields": (
                    "vigencia",
                    "estado",
                    "objetivo",
                    "alcance",
                    "metodologia",
                    "criterios",
                ),
            },
        ),
        (
            "Sesiones del Comité",
            {
                "fields": (
                    "sesion_presentacion",
                    "sesion_aprobacion",
                    "fecha_aprobacion",
                ),
            },
        ),
        (
            "Firmas y participantes",
            {
                "fields": (
                    "realizo",
                    "presidente",
                    "secretario",
                    "integrante_1",
                    "integrante_2",
                ),
            },
        ),
    )

    inlines = (
        ActividadPlanInline,
        NotaPlanInline,
    )
