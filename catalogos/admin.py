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


# Con el decorador de la clase se sustituye esto

# Registrar el modelo y la configuración del admin
#admin.site.register(Puesto, PuestoAdmin)
# Registrar el modelo Marca y su configuración en el admin
#admin.site.register(Marca, MarcaAdmin)
# Registrar el modelo Modelo y su configuración en el admin
#admin.site.register(Modelo, ModeloAdmin)