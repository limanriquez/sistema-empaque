from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Desregistrar el modelo Group si está registrado
from django.contrib.auth.models import Group

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass  # Si no está registrado, no hacemos nada

class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "is_staff", "is_active")
    search_fields = ("email", "username")
    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('username',)}),
        ('Permisos', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:
            return fieldsets
        return fieldsets + (
            ('Password change', {'fields': ('password',)}),
        )

# Registro del modelo con la clase de administración personalizada
admin.site.register(User, CustomUserAdmin)
admin.site.site_header = "Panel de administración"
admin.site.index_title = "Usuarios"
admin.site.site_title = "Panel de Administración de Usuarios"
