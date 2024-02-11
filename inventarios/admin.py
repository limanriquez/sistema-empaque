from django.contrib import admin

from inventarios.models import *
# Register your models here.
admin.site.site_header = "Inventario Horizont Re"
admin.site.site_title = "Panel de control para inventarios de Horizon Re."
admin.site.index_title = "Bienvenidos al panel de control"

class InventarioAdmin(admin.ModelAdmin):
    #Muestra en el panel de administracion los registros con cada una de las columnas para el caso siguiente mostrara 3 columas
    list_display = ("Id","NoInventario","Descripcion","Observaciones","Ubicacion","FechaAdquisicion","Categoria",)
    search_fields = ("NoInventario","Descripcion","Categoria")
    # Muestra una tabla con contenido para filtar en el panel de administrador
    list_filter = ("NoInventario","Descripcion","Categoria")
    date_hierarchy = "FechaAdquisicion"

class CategoriaAdmin(admin.ModelAdmin):
    #Muestra en el panel de administracion los registros con cada una de las columnas para el caso siguiente mostrara 3 columas
    list_display = ("Categoria",)
    search_fields = ("Categoria",)
    # Muestra una tabla con contenido para filtar en el panel de administrador
    list_filter = ("Categoria",)

class CatalogoElementoInventarioAdmin(admin.ModelAdmin):
    #Muestra en el panel de administracion los registros con cada una de las columnas para el caso siguiente mostrara 3 columas
    list_display = ("Descripcion",)
    search_fields = ("Descripcion",)
    # Muestra una tabla con contenido para filtar en el panel de administrador
    list_filter = ("Descripcion",)

class DepartamentoAdmin(admin.ModelAdmin):
    #Muestra en el panel de administracion los registros con cada una de las columnas para el caso siguiente mostrara 3 columas
    list_display = ("Descripcion",)
    search_fields = ("Descripcion",)
    # Muestra una tabla con contenido para filtar en el panel de administrador
    list_filter = ("Descripcion",)

class ElementoInventarioAdmin(admin.ModelAdmin):
    #Muestra en el panel de administracion los registros con cada una de las columnas para el caso siguiente mostrara 3 columas
    list_display = ("Descripcion",)
    search_fields = ("Descripcion",)
    # Muestra una tabla con contenido para filtar en el panel de administrador
    list_filter = ("Descripcion",)


admin.site.register(Inventario,InventarioAdmin)
admin.site.register(Categoria,CategoriaAdmin)
admin.site.register(CatalogoElementoInventario,CatalogoElementoInventarioAdmin)
admin.site.register(Departamento,DepartamentoAdmin)
admin.site.register(ElementoInventario,ElementoInventarioAdmin)
