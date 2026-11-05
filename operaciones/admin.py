from django.contrib import admin, messages
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import OperacionDiaria
from .forms import OperacionDiariaForm

from .forms import (
    ComponenteEmpaqueForm,
    ComponenteEmpaqueFormSet,
    ProductoEmpaqueForm,
    OperacionDiariaForm,
)
from .models import ComponenteEmpaque, ProductoEmpaque, OperacionDiaria

# Tabla de materiales dentro del producto: se elige el material, se
# captura la cantidad por unidad empacada y se ve su unidad. El
# producto debe tener al menos un material.
class ComponenteEmpaqueInline(admin.TabularInline):
    model = ComponenteEmpaque
    form = ComponenteEmpaqueForm
    formset = ComponenteEmpaqueFormSet
    extra = 1
    autocomplete_fields = ("material",)
    fields = ("material", "cantidad_material", "unidad")
    readonly_fields = ("unidad",)

    # Evita una consulta adicional por fila para la unidad.
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "material__unidad_medida"
        )

    # Muestra la unidad del material elegido.
    @admin.display(description="Unidad")
    def unidad(self, obj):
        if obj.pk:
            return obj.material.unidad_medida.abreviatura

        return "-"


# Administra los productos que se empacan, con su costo, precio de
# cobro, tamaño y su BOM. La lista muestra solo los productos;
# al abrir uno se ven y editan los materiales que descuenta por cada
# unidad empacada.
# La calidad se captura directamente en el registro de cada caja,
# no pertenece al catálogo de productos.
# No habilita la eliminación: un producto fuera de uso se desactiva.

@admin.register(ProductoEmpaque)
class ProductoEmpaqueAdmin(admin.ModelAdmin):

    form = ProductoEmpaqueForm

    list_display = (
        "id",
        "codigo",
        "nombre",
        "tamano",
        "mostrar_costo",
        "mostrar_precio",
        "mostrar_margen",
        "num_materiales",
        "activo",
    )

    list_display_links = ("id", "nombre")

    list_filter = (
        "activo",
        "tamano",
    )

    search_fields = (
        "codigo",
        "nombre",
        "descripcion",
        "tamano__nombre",
    )

    inlines = [ComponenteEmpaqueInline]

    fields = (
        "codigo",
        "nombre",
        "descripcion",
        "tamano",
        "costo_empaque",
        "precio_cobro",
        "margen",
        "activo",
    )

    readonly_fields = ("margen",)

    # Cuenta los materiales del BOM sin una consulta por fila.
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "tamano",
        ).annotate(
            _num_materiales=Count("componentes")
        )

    @admin.display(description="Costo", ordering="costo_empaque")
    def mostrar_costo(self, obj):
        return f"$ {obj.costo_empaque:,.2f}"

    @admin.display(description="Precio de cobro", ordering="precio_cobro")
    def mostrar_precio(self, obj):
        return f"$ {obj.precio_cobro:,.2f}"

    @admin.display(description="Margen")
    def mostrar_margen(self, obj):
        return f"$ {obj.margen_unitario:,.2f}"

    # Cantidad de materiales del BOM; 0 indica un producto sin configurar.
    @admin.display(description="Materiales en el BOM", ordering="_num_materiales")
    def num_materiales(self, obj):
        return obj._num_materiales

    # Ganancia por unidad, solo para consulta dentro del formulario.
    @admin.display(description="Margen por unidad")
    def margen(self, obj):
        if obj.pk:
            return f"$ {obj.margen_unitario:,.2f}"

        return "-"

    # Impide eliminar productos desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


        
# ==========================================================
# ADMIN: OPERACIÓN DIARIA
#
# Si no existe una operación abierta, permite crear una
# nueva y la abre automáticamente.
#
# Si existe una operación abierta, permite editarla y
# al guardar registra su cierre.
#
# Las operaciones cerradas permanecen como historial.
# ==========================================================

@admin.register(OperacionDiaria)
class OperacionDiariaAdmin(admin.ModelAdmin):

    form = OperacionDiariaForm

    list_display = (
        "id",
        "fecha",
        "estado",
        "hora_apertura",
        "hora_cierre",
    )

    list_filter = (
        "abierta",
        "fecha",
    )

    ordering = (
        "-fecha",
        "-id",
    )

    readonly_fields = (
        "fecha",
        "abierta",
        "hora_apertura",
        "hora_cierre",
        "abierto_por",
        "cerrado_por",
    )

    fields = (
        "fecha",
        "observaciones",
        "abierta",
        "hora_apertura",
        "abierto_por",
        "hora_cierre",
        "cerrado_por",
    )

    # ------------------------------------------------------
    # Estado
    # ------------------------------------------------------

    @admin.display(description="Estado")
    def estado(self, obj):
        return "ABIERTA" if obj.abierta else "CERRADA"

    # ------------------------------------------------------
    # Integración con el usuario autenticado
    # ------------------------------------------------------

    def get_form(self, request, obj=None, **kwargs):

        FormClass = super().get_form(request, obj, **kwargs)

        class FormConRequest(FormClass):

            def __init__(self, *args, **form_kwargs):
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

        return FormConRequest

    # ------------------------------------------------------
    # Control de creación
    # ------------------------------------------------------

    def has_add_permission(self, request):

        return (
            super().has_add_permission(request)
            and not OperacionDiaria.objects.filter(
                abierta=True
            ).exists()
        )

    # ------------------------------------------------------
    # Control de modificación
    # ------------------------------------------------------

    def get_readonly_fields(self, request, obj=None):

        if obj is not None and not obj.abierta:
            return self.fields

        return self.readonly_fields

    # ------------------------------------------------------
    # Guardar operación
    # ------------------------------------------------------

    @transaction.atomic
    def save_model(self, request, obj, form, change):

        # El formulario ya validó que el empleado exista
        # y que se encuentre activo.
        empleado = request.user.perfil_empleado
        persona = empleado.persona

        if not change:

            # Crear y abrir una operación nueva.
            super().save_model(request, obj, form, change)

            obj.abrir(persona)

            self.message_user(
                request,
                "Operación creada y abierta correctamente.",
                messages.SUCCESS,
            )

        else:

            # Recuperar y bloquear el registro actual.
            operacion = (
                OperacionDiaria.objects
                .select_for_update()
                .get(pk=obj.pk)
            )

            if not operacion.abierta:
                raise ValidationError(
                    "La operación ya está cerrada."
                )

            # Guardar observaciones.
            super().save_model(request, obj, form, change)

            # Cerrar la operación.
            obj.cerrar(persona)

            self.message_user(
                request,
                "Operación cerrada correctamente.",
                messages.SUCCESS,
            )

    # ------------------------------------------------------
    # No permitir eliminar
    # ------------------------------------------------------

    def has_delete_permission(self, request, obj=None):
        return False
