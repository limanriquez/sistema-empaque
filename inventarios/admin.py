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

