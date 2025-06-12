from django.contrib import admin
from inventarios.models import *
# Register your models here.
admin.site.site_header = "Inventario"
admin.site.site_title = "Panel de control para productos e inventario"
admin.site.index_title = "Bienvenidos al panel de control"

# Inline para manejar precios dentro del admin de Producto
class PrecioProductoInline(admin.TabularInline):
    model = PrecioProducto
    extra = 1  # cantidad de formularios vacíos por defecto
    fields = ('tipo_precio', 'precio', 'activo')
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return True  # puedes ajustar si quieres bloquearlo

from django.contrib import admin
from .models import Producto, PrecioProducto

class PrecioProductoInline(admin.TabularInline):
    model = PrecioProducto
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nombre', 'codigo', 'tipo_producto', 'empresa', 'orden',  # ← aquí
        'seccion', 'get_total_existencia', 'es_compuesto', 'vendible', 'activo'
    )

    fields = [
        'nombre', 'codigo', 'descripcion',
        'tipo_producto', 'empresa', 'orden',  # ← aquí
        'es_compuesto', 'vendible', 'activo'
    ]
  
    search_fields = ('nombre', 'codigo')
    list_filter = ('activo', 'tipo_producto', 'empresa', 'es_compuesto', 'vendible')
    list_display_links = ('id', 'nombre')
    inlines = [PrecioProductoInline]

    def get_total_existencia(self, obj):
        return sum(c.stock_item.existencia for c in obj.componentes.all())
    get_total_existencia.short_description = 'Total Existencia'

    def get_fields(self, request, obj=None):
        fields = [
            'nombre', 'codigo', 'descripcion',
            'tipo_producto', 'empresa', 'es_compuesto', 'vendible', 'activo'
        ]
        if obj:
            fields.insert(fields.index('empresa') + 1, 'seccion')
            fields.insert(fields.index('seccion') + 1, 'orden')  # inserta orden después de seccion
        else:
            fields.insert(fields.index('empresa') + 1, 'orden')  # si es nuevo objeto, también mostrar orden
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'seccion':
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    producto_id = request.resolver_match.kwargs.get('object_id')
                    from .models import Producto
                    producto = Producto.objects.get(id=producto_id)
                    empresa_id = producto.empresa_id
                    kwargs["queryset"] = Seccion.objects.filter(
                        id_estante__id_almacen__empresa_id=empresa_id
                    )
                except:
                    kwargs["queryset"] = Seccion.objects.none()
            else:
                kwargs["queryset"] = Seccion.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Limpia tipo_cristal si tipo_producto no es CRISTALES
        if obj.tipo_producto.tipo_producto.upper() != "CRISTALES":
            obj.tipo_cristal = None
        super().save_model(request, obj, form, change)

    def estante(self, obj):
        # Retorna nombre del estante relacionado
        if obj.seccion and obj.seccion.id_estante:
            return obj.seccion.id_estante.nombre
        return None
    estante.short_description = 'Estante'

    def almacen(self, obj):
        # Retorna nombre del almacen relacionado
        if obj.seccion and obj.seccion.id_estante and obj.seccion.id_estante.id_almacen:
            return obj.seccion.id_estante.id_almacen.nombre
        return None
    almacen.short_description = 'Almacén'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'existencia', 'listar_proveedores')
    list_display_links = ('nombre',)
    search_fields = ('nombre', 'proveedores__nombre')  # para buscar por proveedor
    filter_horizontal = ('proveedores',)  # para seleccionar varios proveedores fácilmente
    actions = None  # deshabilita acciones masivas como eliminar

    def has_delete_permission(self, request, obj=None):
        return False

    def listar_proveedores(self, obj):
        return ", ".join([p.nombre for p in obj.proveedores.all()])
    listar_proveedores.short_description = 'Proveedores'

@admin.register(BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto_nombre', 'stock_item_nombre', 'cantidad')
    list_display_links = ('producto_nombre', 'stock_item_nombre')
    search_fields = ('producto__nombre', 'stock_item__nombre')

    def producto_nombre(self, obj):
        return obj.producto.nombre
    producto_nombre.short_description = 'Producto'

    def stock_item_nombre(self, obj):
        return obj.stock_item.nombre
    stock_item_nombre.short_description = 'Stock Item'

@admin.register(ProductoZonaNotificacion)
class ProductoZonaNotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'zona', 'activo')
    list_filter = ('activo', 'zona')
    search_fields = ('producto__nombre', 'zona__nombre')
    list_display_links = ('id', 'producto')
    fields = ('producto', 'zona', 'activo')

    def has_delete_permission(self, request, obj=None):
        return False  # Evita eliminar desde admin

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True
