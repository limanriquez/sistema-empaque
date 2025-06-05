from django.contrib import admin
from operaciones.models import CorteCaja

@admin.register(CorteCaja)
class CorteCajaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'empresa', 'personal', 'fecha_apertura', 'fecha_cierre',
        'estatus_display', 'saldo_inicial', 'saldo_final', 'get_total_ingresos', 'egresos'
    )
    list_filter = ('estatus', 'empresa', 'personal', 'fecha_apertura')
    search_fields = ('empresa__nombre', 'personal__nombre')
    list_display_links = ('id', 'fecha_apertura')

    readonly_fields = (
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
    estatus_display.short_description = 'Estado'

    def get_fields(self, request, obj=None):
        fields = [
            'empresa', 'personal',
            'saldo_inicial', 'saldo_final',
            'ingresos_efectivo', 'ingresos_tarjeta', 'ingresos_transferencia',
            'egresos', 'fecha_apertura', 'fecha_cierre', 'estatus',
            'observaciones'
        ]
        if obj is None:
            fields.remove('estatus')
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields + ('estatus',)
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

