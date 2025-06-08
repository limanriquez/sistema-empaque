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


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo", "rfc", "activo")
    search_fields = ("nombre", "rfc", "direccion")
    list_filter = ("activo", "tipo")
    list_display_links = ("id", "nombre")

    formfield_overrides = {
        models.DateField: {'widget': admin.widgets.AdminDateWidget(attrs={'class': 'vDateField'})},
    }

    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar empresas

    def save_model(self, request, obj, form, change):
        if obj.tipo == 1 and Empresa.objects.filter(tipo=1).exclude(pk=obj.pk).exists():
            messages.error(request, 'Ya existe una empresa matriz en el sistema. Solo puede haber una empresa matriz.')
            return
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        # Muestra todos los campos menos 'id'
        return [f.name for f in self.model._meta.fields if f.name != 'id']

@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nombre', 'apellido_paterno', 'apellido_materno', 'curp', 'rfc',
        'telefono', 'empresa', 'estatus'
    )
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'curp', 'rfc', 'usuario__username')
    list_filter = ('estatus', 'empresa', 'puesto')
    list_display_links = ('id', 'nombre')
    fields = (
        'nombre', 'apellido_paterno', 'apellido_materno', 'curp', 'rfc',
        'puesto', 'telefono', 'telefono_emergencia', 'contacto_emergencia',
        'direccion', 'fecha_ingreso', 'empresa', 'estatus', 'usuario'
    )

    # Deshabilitar la opción de eliminar
    def has_delete_permission(self, request, obj=None):
        return False

    # Permitir la creación
    def has_add_permission(self, request):
        return True

    # Permitir ver
    def has_view_permission(self, request, obj=None):
        return True

    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    # Mostrar los campos en la vista de lista
    list_display = (
        'id', 'nombre', 'apellido_paterno', 'apellido_materno', 'rfc', 
        'tipo_persona', 'telefono', 'correo_electronico', 'contacto_principal', 'estatus'
    )
    # Campos que se pueden buscar en el admin
    search_fields = ('nombre', 'apellido_paterno', 'apellido_materno', 'rfc', 'telefono')
    # Filtros por los cuales los usuarios pueden filtrar
    list_filter = ('estatus', 'tipo_persona')
    # Hacer que 'id' y 'nombre' sean enlaces que redirijan a la vista de detalle
    list_display_links = ('id', 'nombre')
    # Campos disponibles para visualizar y editar
    fields = (
        'nombre', 'apellido_paterno', 'apellido_materno', 'tipo_persona', 'rfc',
        'direccion', 'telefono', 'telefono_alternativo', 'correo_electronico', 
        'contacto_principal', 'estatus'
    )

    # Deshabilitar la opción de eliminar
    def has_delete_permission(self, request, obj=None):
        return False

    # Permitir la creación de proveedores
    def has_add_permission(self, request):
        return True

    # Permitir la visualización de proveedores
    def has_view_permission(self, request, obj=None):
        return True

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

@admin.register(Telefonos)
class TelefonosAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'empresa', 'status')
    search_fields = ('numero',)
    list_filter = ('status', 'empresa')
    list_display_links = ('id', 'numero')
    
    fields = ('numero', 'empresa', 'status')  # campos visibles en formulario

    def get_readonly_fields(self, request, obj=None):
        if obj:  # si es edición (obj existe)
            return ('numero', 'empresa')  # solo status editable
        else:
            return ()  # en creación todos editables
    
    # Permitir modificar solo 'status' en edición
    def has_change_permission(self, request, obj=None):
        return True
    
    # No permitir eliminar
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Permitir agregar
    def has_add_permission(self, request):
        return True
    
    # Permitir ver
    def has_view_permission(self, request, obj=None):
        return True

    class Meta:
        verbose_name = 'Teléfono'
        verbose_name_plural = 'Teléfonos'


@admin.register(ProductosAutorizados)
class ProductosAutorizadosAdmin(admin.ModelAdmin):
    list_display = ("id", "empresa_lider", "empresa_autorizada", "activo")
    search_fields = ("empresa_lider__nombre", "empresa_autorizada__nombre")
    list_filter = ("activo",)
    list_display_links = ("id", "empresa_lider", "empresa_autorizada")
    
    def has_delete_permission(self, request, obj=None):
        # Evita borrado desde el admin, igual puedes ajustar si quieres permitirlo
        return False

    def save_model(self, request, obj, form, change):
        if obj.empresa_lider == obj.empresa_autorizada:
            messages.error(request, "Una empresa no puede autorizarse a sí misma.")
            return
        # Validar unicidad manualmente para dar mensaje claro
        if ProductosAutorizados.objects.filter(
            empresa_lider=obj.empresa_lider,
            empresa_autorizada=obj.empresa_autorizada
        ).exclude(pk=obj.pk).exists():
            messages.error(request, "Esta relación ya existe.")
            return
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        # Mostrar todos menos 'id'
        return [f.name for f in self.model._meta.fields if f.name != 'id']



