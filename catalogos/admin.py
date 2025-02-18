from django.contrib import admin
from .models import Puesto

# Personalización del panel de administración
admin.site.site_header = "Panel de control de Catálogos"
admin.site.site_title = "Panel de control de Catálogos"
admin.site.index_title = "Bienvenidos al panel de control de Catálogos"

# Clase para personalizar la vista del modelo Puesto en el admin
class PuestoAdmin(admin.ModelAdmin):
    # Muestra las columnas en el panel de administración
    list_display = ("id", "nombre_puesto", "descripcion", "estatus")
    
    # Permite buscar por los siguientes campos en el admin
    search_fields = ("nombre_puesto", "descripcion")
    
    # Filtros en el panel de administración
    list_filter = ("estatus",)

     # Establecer que se puede hacer clic en 'nombre_puesto' para editar
    list_display_links = ("id","nombre_puesto")
    
    # Hierarchy para ordenar por fecha de creación o algún otro campo si lo tuvieras
    # date_hierarchy = "fecha_creacion"  # Si tuvieses un campo de fecha

# Registrar el modelo y la configuración del admin
admin.site.register(Puesto, PuestoAdmin)
