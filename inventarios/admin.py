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

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nombre', 'codigo', 'tipo_producto', 'tipo_cristal', 
        'empresa', 'seccion', 'estante', 'almacen', 'total_existencia', 'activo'
    )
    search_fields = ('nombre', 'codigo')
    list_filter = ('activo', 'tipo_producto', 'tipo_cristal', 'empresa')
    list_display_links = ('id', 'nombre')
    inlines = [PrecioProductoInline]

    def get_fields(self, request, obj=None):
        fields = [
            'nombre', 'codigo', 'descripcion',
            'tipo_producto', 'tipo_cristal', 'empresa',
            'total_existencia', 'activo'
        ]
        if obj:
            fields.insert(6, 'seccion')  # después de empresa
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly = []
        if obj:
            # Si el tipo_producto NO es CRISTALES, tipo_cristal es readonly
            if obj.tipo_producto.tipo_producto.upper() != "CRISTALES":
                readonly.append('tipo_cristal')
        return readonly

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