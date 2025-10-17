from django.contrib import admin
from .models import *
from django.shortcuts import redirect

# Personalización del panel de administración
admin.site.site_header = "Panel de control de Catálogos"
admin.site.site_title = "Panel de control de Catálogos"
admin.site.index_title = "Bienvenidos al panel de control de Catálogos"

@admin.register(GoHome)
class HomeLinkAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect('/')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Admin para el modelo Almacen
@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'empresa', 'status')
    search_fields = ('nombre', 'empresa__nombre')
    list_filter = ('status', 'empresa')
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'empresa', 'status')

    # Solo permitir agregar y ver
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True


# === ADMIN DE ESTANTE ===
@admin.register(Estante)
class EstanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'id_almacen', 'status')
    search_fields = ('nombre', 'id_almacen__nombre')
    list_filter = ('status', 'id_almacen__empresa')  # Filtro jerárquico por empresa
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'id_almacen', 'status')

    # Solo permitir agregar y ver
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

# === ADMIN DE SECCIÓN ===
@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'id_estante', 'status')
    search_fields = ('nombre', 'id_estante__nombre')
    list_filter = ('status', 'id_estante__id_almacen')  # Filtro por almacén
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'id_estante', 'status')

    # Solo permitir agregar y ver
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    class Meta:
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        
# Clase para personalizar la vista del modelo Puesto en el admin
@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    # Muestra las columnas en el panel de administración
    list_display = ("id", "nombre_puesto", "descripcion", "estatus")
    
    # Permite buscar por los siguientes campos en el admin
    search_fields = ("nombre_puesto", "descripcion")
    
    # Filtros en el panel de administración
    list_filter = ("estatus",)

     # Establecer que se puede hacer clic en 'nombre_puesto' para editar
    list_display_links = ("id","nombre_puesto")

     # Deshabilitar la opción de eliminar el objeto en el Admin
    def has_delete_permission(self, request, obj=None):
        return False  # No se podrá eliminar

    # Deshabilitar la opción de modificar el objeto en el Admin
    def has_change_permission(self, request, obj=None):
        return False  # No se podrá modificar

    # Permitir la creación de nuevos registros
    def has_add_permission(self, request):
        return True  # Se podrá agregar nuevas marcas

    # Permitir ver los registros en el Admin
    def has_view_permission(self, request, obj=None):
        return True  # Los usuarios podrán ver las marcas
    

@admin.register(TipoProducto)
class TipoProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_producto', 'status')
    search_fields = ('tipo_producto',)
    list_filter = ('tipo_producto', 'status')
    list_display_links = ('id', 'tipo_producto')
    fields = ('tipo_producto', 'status')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('tipo_producto',)
        return ()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True  # Se permite edición (solo para 'status')

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

@admin.register(TipoPrecio)
class TipoPrecioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'status')
    search_fields = ('nombre',)
    list_filter = ('nombre', 'status')
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'status')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('nombre',)
        return ()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True  # Se permite edición (solo para 'status')

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

@admin.register(ZonaNotificacion)
class ZonaNotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('activo',)
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'descripcion', 'activo')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

@admin.register(LugarEntrega)
class LugarEntregaAdmin(admin.ModelAdmin):
    # Columnas que se muestran en el listado del admin
    list_display = ("id", "nombre", "activo")

    # Campos por los que se puede buscar
    search_fields = ("nombre",)

    # Filtro lateral en el admin
    list_filter = ("activo",)

    # Establece los campos clicables
    list_display_links = ("id", "nombre")

    # No permitir eliminar el objeto desde el admin
    def has_delete_permission(self, request, obj=None):
        return False

    # Sí permitir modificar (por ejemplo, cambiar estado activo/inactivo)
    def has_change_permission(self, request, obj=None):
        return True

    # Permitir agregar nuevos registros
    def has_add_permission(self, request):
        return True

    # Permitir visualizar registros
    def has_view_permission(self, request, obj=None):
        return True

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    # Columnas que se muestran en el listado del admin
    list_display = ("id", "nombre", "activo")

    # Campos por los que se puede buscar
    search_fields = ("nombre",)

    # Filtro lateral en el admin
    list_filter = ("activo",)

    # Establece los campos clicables
    list_display_links = ("id", "nombre")

    # No permitir eliminar el objeto desde el admin
    def has_delete_permission(self, request, obj=None):
        return False

    # Sí permitir modificar (por ejemplo, cambiar estado activo/inactivo)
    def has_change_permission(self, request, obj=None):
        return True

    # Permitir agregar nuevos registros
    def has_add_permission(self, request):
        return True

    # Permitir visualizar registros
    def has_view_permission(self, request, obj=None):
        return True
# Con el decorador de la clase se sustituye esto

# Registrar el modelo y la configuración del admin
#admin.site.register(Puesto, PuestoAdmin)
# Registrar el modelo Marca y su configuración en el admin
#admin.site.register(Marca, MarcaAdmin)
# Registrar el modelo Modelo y su configuración en el admin
#admin.site.register(Modelo, ModeloAdmin)