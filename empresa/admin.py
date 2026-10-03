from django.contrib import admin
from django.contrib import messages  # Importar messages
from django.db import models  # Importar models
from django.contrib.auth.models import User  # Importa el modelo User
from .models import Empresa, Personal, Proveedor, Cliente, Telefonos, ProductosAutorizados
# Personalización del panel de administración
admin.site.site_header = "Panel de control de Catálogos"
admin.site.site_title = "Panel de control de Catálogos"
admin.site.index_title = "Bienvenidos al panel de control de Catálogos"

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Mostrar los campos en la vista de lista
    list_display = (
        'id', 'nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 
        'telefono_adicional', 'correo_electronico', 'rfc', 'tipo_persona', 'empresa','estatus', 'fecha_registro'
    )
    
    # Campos que se pueden buscar en el admin
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'correo_electronico', 'rfc')
    
    # Filtros por los cuales los usuarios pueden filtrar
    list_filter = ('estatus', 'tipo_persona')
    
    # Hacer que 'id' y 'nombre' sean enlaces que redirijan a la vista de detalle
    list_display_links = ('id', 'nombre')
    
    # Campos disponibles para visualizar y editar
    fields = (
        'nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'telefono_adicional', 
        'correo_electronico', 'direccion', 'rfc', 'tipo_persona','empresa','estatus'
    )
    
    # Deshabilitar la opción de eliminar
    def has_delete_permission(self, request, obj=None):
        return False

    # Permitir la creación de clientes
    def has_add_permission(self, request):
        return True

    # Permitir la visualización de clientes
    def has_view_permission(self, request, obj=None):
        return True

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


