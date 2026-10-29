from django.contrib import admin
from django.db.models import F

from .forms import MaterialForm, MovimientoInventarioForm
from .models import ExistenciaMaterial, Material, MovimientoInventario
from .services import registrar_movimiento

# Filtro del listado por nivel de existencia respecto al stock mínimo.
class NivelStockFilter(admin.SimpleListFilter):
    title = "nivel de stock"
    parameter_name = "nivel_stock"

    def lookups(self, request, model_admin):
        return (
            ("bajo", "En o bajo el mínimo"),
            ("agotado", "Agotado"),
        )

    def queryset(self, request, queryset):
        if self.value() == "bajo":
            return queryset.filter(
                stock_minimo__gt=0,
                existencia__lte=F("stock_minimo"),
            )

        if self.value() == "agotado":
            return queryset.filter(existencia__lte=0)

        return queryset


# Administra los materiales de empaque y su existencia consolidada.
# La existencia es de solo lectura: la modifican los movimientos de
# inventario. La unidad no cambia una vez creado el material. No
# habilita la eliminación.
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):

    form = MaterialForm

    list_display = (
        "id",
        "codigo",
        "nombre",
        "mostrar_existencia",
        "mostrar_stock_minimo",
        "stock_suficiente",
        "activo",
    )

    list_display_links = ("id", "nombre")

    # Evita una consulta adicional por fila para la unidad de medida.
    list_select_related = ("unidad_medida",)

    list_filter = (
        "activo",
        NivelStockFilter,
        "unidad_medida",
    )

    # Requerido por autocomplete_fields en movimientos y BOM.
    search_fields = (
        "codigo",
        "nombre",
        "descripcion",
    )

    fields = (
        "codigo",
        "nombre",
        "descripcion",
        "unidad_medida",
        "existencia",
        "stock_minimo",
        "activo",
    )

    # La existencia solo cambia por movimientos de inventario.
    # La unidad no cambia una vez creado el material, para no alterar
    # el significado de las cantidades ya registradas.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("existencia", "unidad_medida")

        return ("existencia",)

    # Muestra la existencia con la abreviatura de su unidad.
    @admin.display(description="Existencia", ordering="existencia")
    def mostrar_existencia(self, obj):
        return f"{obj.existencia:,.3f} {obj.unidad_medida.abreviatura}"

    # Muestra el stock mínimo con la abreviatura de su unidad.
    @admin.display(description="Stock mínimo", ordering="stock_minimo")
    def mostrar_stock_minimo(self, obj):
        return f"{obj.stock_minimo:,.3f} {obj.unidad_medida.abreviatura}"

    # Indica si la existencia supera el stock mínimo.
    @admin.display(description="Stock suficiente", boolean=True)
    def stock_suficiente(self, obj):
        if obj.stock_minimo > 0:
            return obj.existencia > obj.stock_minimo

        return obj.existencia > 0

    # Impide eliminar materiales desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


# Administra el libro de movimientos de inventario. Solo permite
# registrar movimientos nuevos: no se editan ni se eliminan, y los
# errores se corrigen con otro movimiento. Al registrar, actualiza los
# saldos por sección y la existencia consolidada del material.
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):

    form = MovimientoInventarioForm

    list_display = (
        "id",
        "fecha",
        "tipo",
        "material",
        "mostrar_cantidad",
        "ubicacion_origen",
        "ubicacion_destino",
        "proveedor",
        "documento",
    )

    list_display_links = ("id", "material")
    date_hierarchy = "fecha"

    # Evita consultas adicionales por fila.
    list_select_related = (
        "material__unidad_medida",
        "ubicacion_origen__espacio__almacen",
        "ubicacion_destino__espacio__almacen",
        "proveedor__persona",
    )

    list_filter = ("tipo", "fecha", "material__unidad_medida")

    search_fields = (
        "material__nombre",
        "material__codigo",
        "documento",
        "descripcion",
        "proveedor__persona__razon_social",
        "proveedor__persona__nombre_comercial",
        "proveedor__persona__nombres",
        "proveedor__persona__apellido_paterno",
    )

    autocomplete_fields = (
        "material",
        "ubicacion_origen",
        "ubicacion_destino",
        "proveedor",
    )

    campos_captura = (
        "tipo",
        "material",
        "cantidad",
        "ubicacion_origen",
        "ubicacion_destino",
        "proveedor",
        "costo_unitario",
        "documento",
        "fecha",
        "descripcion",
    )

    # Al consultar un movimiento se agregan quién y cuándo lo registró.
    def get_fields(self, request, obj=None):
        if obj:
            return self.campos_captura + ("creado_por", "creado_en")

        return self.campos_captura

    # Un movimiento registrado es de solo lectura.
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.get_fields(request, obj)

        return ()

    # Registra al usuario responsable y delega en el servicio, que
    # guarda el movimiento y actualiza los saldos en una transacción.
    def save_model(self, request, obj, form, change):
        obj.creado_por = request.user
        registrar_movimiento(obj)

    # Muestra la cantidad con la abreviatura de la unidad del material.
    @admin.display(description="Cantidad", ordering="cantidad")
    def mostrar_cantidad(self, obj):
        return f"{obj.cantidad:,.3f} {obj.material.unidad_medida.abreviatura}"

    # Solo se registran movimientos nuevos.
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Consulta de existencias por material y sección. Es de solo lectura:
# los saldos solo cambian por movimientos de inventario. Con el filtro
# por almacén se ve el stock de cada uno.
@admin.register(ExistenciaMaterial)
class ExistenciaMaterialAdmin(admin.ModelAdmin):

    list_display = ("material", "almacen", "espacio", "seccion", "cantidad")
    list_select_related = ("material", "seccion__espacio__almacen")
    list_filter = ("seccion__espacio__almacen", "seccion__espacio")
    search_fields = ("material__nombre", "material__codigo", "seccion__nombre")

    @admin.display(
        description="Almacén", ordering="seccion__espacio__almacen__nombre"
    )
    def almacen(self, obj):
        return obj.seccion.espacio.almacen

    @admin.display(description="Espacio", ordering="seccion__espacio__nombre")
    def espacio(self, obj):
        return obj.seccion.espacio

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False