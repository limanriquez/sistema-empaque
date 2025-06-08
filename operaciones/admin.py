from django.contrib import admin
from operaciones.models import CorteCaja, CorteCajaEmpresa
from django import forms
from django.contrib import admin
from django.utils.timezone import now
from django.contrib import admin
from empresa.models import ProductosAutorizados, Personal, Empresa
from .models import CorteCaja, CorteCajaEmpresa
from django.db import transaction

from django.utils.timezone import now

from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db import transaction

@admin.register(CorteCaja)
class CorteCajaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'empresa', 'personal', 'fecha_apertura', 'fecha_cierre',
        'estatus_display', 'saldo_inicial', 'saldo_final', 'get_total_ingresos', 'egresos'
    )
    list_filter = ('estatus', 'empresa', 'personal', 'fecha_apertura')
    search_fields = ('empresa__nombre', 'personal__nombre')
    list_display_links = ('id', 'fecha_apertura')

    base_readonly_fields = (
        'fecha_apertura',
        'fecha_cierre',
        'saldo_final',
        'ingresos_efectivo',
        'ingresos_tarjeta',
        'ingresos_transferencia',
        'egresos',
    )

    def get_total_ingresos(self, obj):
        return obj.ingresos_efectivo + obj.ingresos_tarjeta + obj.ingresos_transferencia
    get_total_ingresos.short_description = 'Total Ingresos'

    def estatus_display(self, obj):
        return obj.get_estatus_display()
    estatus_display.short_description = 'Estado actual del corte de caja'

    def get_fields(self, request, obj=None):
        if obj is None:
            return [
                'empresa', 'personal',
                'saldo_inicial',
                'ingresos_efectivo', 'ingresos_tarjeta', 'ingresos_transferencia',
                'egresos', 'fecha_apertura', 'estatus',
                'observaciones',
            ]
        return [
            'empresa', 'personal',
            'saldo_inicial', 'saldo_final',
            'ingresos_efectivo', 'ingresos_tarjeta', 'ingresos_transferencia',
            'egresos', 'fecha_apertura', 'fecha_cierre', 'estatus',
            'observaciones',
        ]

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.base_readonly_fields + ('empresa', 'personal', 'saldo_inicial')
        return self.base_readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "personal":
            try:
                personal = request.user.personal
                kwargs["queryset"] = Personal.objects.filter(pk=personal.pk)
                kwargs["initial"] = personal.pk
            except Personal.DoesNotExist:
                kwargs["queryset"] = Personal.objects.none()

        if db_field.name == "empresa":
            try:
                empresa = request.user.personal.empresa
                kwargs["queryset"] = Empresa.objects.filter(pk=empresa.pk)
                kwargs["initial"] = empresa.pk
            except (Personal.DoesNotExist, AttributeError):
                kwargs["queryset"] = Empresa.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "estatus":
            if request.resolver_match.view_name.endswith("add"):
                kwargs['choices'] = [(CorteCaja.ABIERTO, "Abierto")]
            else:
                kwargs['choices'] = [
                    (val, label) for val, label in CorteCaja.ESTATUS_CHOICES
                    if val != CorteCaja.ABIERTO
                ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.personal = request.user.personal
            obj.empresa = request.user.personal.empresa
        else:
            if obj.estatus == CorteCaja.CERRADO and not obj.fecha_cierre:
                obj.fecha_cierre = now()
        super().save_model(request, obj, form, change)