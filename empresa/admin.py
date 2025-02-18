from django.contrib import admin
from django.contrib import messages  # Importar messages
from django.db import models  # Importar models
from .models import Empresa

# Personalización del panel de administración
admin.site.site_header = "Panel de control de Catálogos"
admin.site.site_title = "Panel de control de Catálogos"
admin.site.index_title = "Bienvenidos al panel de control de Catálogos"

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo", "rfc", "activo")
    search_fields = ("nombre", "rfc", "direccion")
    list_filter = ("activo", "tipo")
    list_display_links = ("id", "nombre")
    
    formfield_overrides = {
        models.DateField: {'widget': admin.widgets.AdminDateWidget(attrs={'class': 'vDateField'})},
    }

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar ninguna empresa
        return False

    def save_model(self, request, obj, form, change):
        # Verificar si ya existe una empresa matriz antes de guardar
        if obj.tipo == 1 and Empresa.objects.filter(tipo=1).exists():
            # Mostrar el mensaje de error
            messages.error(request, 'Ya existe una empresa matriz en el sistema. Solo puede haber una empresa matriz.')
            return  # Detener el guardado, no continuar con el proceso
        else:
            super().save_model(request, obj, form, change)

# Registrar el modelo y la configuración del admin
admin.site.register(Empresa, EmpresaAdmin)
