from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from operaciones.models import CorteCaja, CorteCajaEmpresa
from empresa.models import ProductosAutorizados

@receiver(post_save, sender=CorteCaja)
def crear_empresas_autorizadas(sender, instance, created, **kwargs):
    if created:
        autorizadas_ids = ProductosAutorizados.objects.filter(
            empresa_lider=instance.empresa,
            activo=True
        ).values_list('empresa_autorizada_id', flat=True)

        cortes_empresa_objs = [
            CorteCajaEmpresa(corte_caja=instance, empresa_id=empresa_id)
            for empresa_id in autorizadas_ids
        ]
        CorteCajaEmpresa.objects.bulk_create(cortes_empresa_objs)

    # Si quieres que al cambiar estatus a CERRADO, se calcule fecha_cierre y saldo_final:
    if not created and instance.estatus == CorteCaja.CERRADO and not instance.fecha_cierre:
        instance.fecha_cierre = timezone.now()

        # Aquí calcula saldo_final si quieres:
        instance.saldo_final = (
            instance.saldo_inicial +
            instance.ingresos_efectivo +
            instance.ingresos_tarjeta +
            instance.ingresos_transferencia -
            instance.egresos
        )
        instance.save(update_fields=['fecha_cierre', 'saldo_final'])