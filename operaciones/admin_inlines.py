from django.contrib import admin

from .models import ClienteProductoEmpaque


# Permite administrar las presentaciones autorizadas desde el cliente.
class ClienteProductoEmpaqueInline(admin.TabularInline):
    model = ClienteProductoEmpaque
    extra = 1
    can_delete = True
    autocomplete_fields = ("producto_empaque",)

    fields = (
        "producto_empaque",
        "activo",
        "creado_en",
    )

    readonly_fields = (
        "creado_en",
    )

    # Oculta los iconos de agregar, editar, consultar y eliminar
    # productos desde el selector de presentaciones.
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )

        if db_field.name == "producto_empaque" and field:
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_view_related = False
            field.widget.can_delete_related = False

        return field

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        widget = formset.form.base_fields["producto_empaque"].widget
        widget.can_add_related = False
        widget.can_change_related = False
        widget.can_view_related = False
        widget.can_delete_related = False

        return formset