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

