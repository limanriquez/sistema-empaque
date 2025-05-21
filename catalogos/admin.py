from django.contrib import admin
from .models import *

# Personalización del panel de administración
admin.site.site_header = "Panel de control de Catálogos"
admin.site.site_title = "Panel de control de Catálogos"
admin.site.index_title = "Bienvenidos al panel de control de Catálogos"

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

    class Meta:
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'


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

    class Meta:
        verbose_name = 'Estante'
        verbose_name_plural = 'Estantes'


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
    
    # Hierarchy para ordenar por fecha de creación o algún otro campo si lo tuvieras
    # date_hierarchy = "fecha_creacion"  # Si tuvieses un campo de fecha
# Personalización de la vista de Marca
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)
    search_fields = ('nombre',)
    list_filter = ('nombre',)
    list_display_links = ('id', 'nombre')
    fields = ('nombre',)

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

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'


@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'marca')
    search_fields = ('nombre', 'marca__nombre')
    list_filter = ('marca',)
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'marca')

    # Deshabilitar la opción de eliminar el objeto en el Admin
    def has_delete_permission(self, request, obj=None):
        return False  # No se podrá eliminar

    # Deshabilitar la opción de modificar el objeto en el Admin
    def has_change_permission(self, request, obj=None):
        return False  # No se podrá modificar

    # Permitir la creación de nuevos registros
    def has_add_permission(self, request):
        return True  # Se podrá agregar nuevos modelos

    # Permitir ver los registros en el Admin
    def has_view_permission(self, request, obj=None):
        return True  # Los usuarios podrán ver los modelos

    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'

@admin.register(Servicios)
class ServiciosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'estatus')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('estatus',)
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'descripcion', 'estatus')

    # Deshabilitar la opción de eliminar el objeto en el Admin
    def has_delete_permission(self, request, obj=None):
        return False  # No se podrá eliminar

    # Deshabilitar la opción de modificar el objeto en el Admin
    def has_change_permission(self, request, obj=None):
        return False  # No se podrá modificar

    # Permitir la creación de nuevos registros
    def has_add_permission(self, request):
        return True  # Se podrá agregar nuevos servicios

    # Permitir ver los registros en el Admin
    def has_view_permission(self, request, obj=None):
        return True  # Los usuarios podrán ver los servicios

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

@admin.register(Seguros)
class SegurosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'rfc', 'telefono', 'correo_electronico', 'estatus')
    search_fields = ('nombre', 'rfc', 'telefono', 'correo_electronico')
    list_filter = ('estatus',)  # Filtro para mostrar activos/inactivos
    list_display_links = ('id', 'nombre')
    fields = ('nombre', 'rfc', 'direccion', 'telefono', 'telefono_adicional', 'correo_electronico', 'contacto', 'estatus')

    # Deshabilitar la opción de eliminar el objeto en el Admin
    def has_delete_permission(self, request, obj=None):
        return False  # No se podrá eliminar

    # Deshabilitar la opción de modificar el objeto en el Admin
    def has_change_permission(self, request, obj=None):
        return False  # No se podrá modificar

    # Permitir la creación de nuevos registros
    def has_add_permission(self, request):
        return True  # Se podrá agregar nuevos seguros

    # Permitir ver los registros en el Admin
    def has_view_permission(self, request, obj=None):
        return True  # Los usuarios podrán ver los seguros

    class Meta:
        verbose_name = 'Seguro'
        verbose_name_plural = 'Seguros'    


@admin.register(TipoContacto)
class TipoContactoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'status')
    search_fields = ('tipo',)
    list_filter = ('status',)
    list_display_links = ('id', 'tipo')
    fields = ('tipo', 'status')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('tipo',)  # Solo se puede modificar status en edición
        return ()  # En creación, todos los campos editables

    def has_change_permission(self, request, obj=None):
        return True  # Permitimos edición (solo status editable)

    def has_delete_permission(self, request, obj=None):
        return False  # No se puede eliminar

    def has_add_permission(self, request):
        return True  # Se permite agregar nuevos registros

    def has_view_permission(self, request, obj=None):
        return True  # Se permite visualizar


@admin.register(TipoCristal)
class TipoCristalAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_cristal', 'status')
    search_fields = ('tipo_cristal',)
    list_filter = ('tipo_cristal', 'status')
    list_display_links = ('id', 'tipo_cristal')
    fields = ('tipo_cristal', 'status')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si es edición, bloquear tipo_cristal
            return ('tipo_cristal',)
        return ()

    # Deshabilitar eliminación
    def has_delete_permission(self, request, obj=None):
        return False

    # Permitir modificación
    def has_change_permission(self, request, obj=None):
        return True  # Necesario para permitir editar status

    # Permitir creación
    def has_add_permission(self, request):
        return True

    # Permitir visualización
    def has_view_permission(self, request, obj=None):
        return True

    class Meta:
        verbose_name = 'Tipo de Cristal'
        verbose_name_plural = 'Tipos de Cristal'

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

    class Meta:
        verbose_name = 'Tipo de producto'
        verbose_name_plural = 'Tipos de productos'

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

    class Meta:
        verbose_name = 'Tipo de precio'
        verbose_name_plural = 'Tipos de precios'
# Con el decorador de la clase se sustituye esto

# Registrar el modelo y la configuración del admin
#admin.site.register(Puesto, PuestoAdmin)
# Registrar el modelo Marca y su configuración en el admin
#admin.site.register(Marca, MarcaAdmin)
# Registrar el modelo Modelo y su configuración en el admin
#admin.site.register(Modelo, ModeloAdmin)