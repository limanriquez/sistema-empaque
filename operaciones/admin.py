from django.contrib import admin
from django.db.models import Count

from .forms import (
    ComponenteEmpaqueForm,
    ComponenteEmpaqueFormSet,
    ProductoEmpaqueForm,
)
from .models import ComponenteEmpaque, ProductoEmpaque

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


# Administra los productos que se empacan, con su costo, su precio de
# cobro y su BOM. La lista muestra solo los productos; al abrir uno se
# ven y editan los materiales que descuenta por cada unidad empacada.
# No habilita la eliminación: un producto fuera de uso se desactiva.
@admin.register(ProductoEmpaque)
class ProductoEmpaqueAdmin(admin.ModelAdmin):

    form = ProductoEmpaqueForm

    list_display = (
        "id",
        "codigo",
        "nombre",
        "mostrar_costo",
        "mostrar_precio",
        "mostrar_margen",
        "num_materiales",
        "activo",
    )

    list_display_links = ("id", "nombre")
    list_filter = ("activo",)
    search_fields = ("codigo", "nombre", "descripcion")
    inlines = [ComponenteEmpaqueInline]

    fields = (
        "codigo",
        "nombre",
        "descripcion",
        "costo_empaque",
        "precio_cobro",
        "margen",
        "activo",
    )

    readonly_fields = ("margen",)

    # Cuenta los materiales del BOM sin una consulta por fila.
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
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


