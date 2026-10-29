from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from .models import ExistenciaMaterial, Material, MovimientoInventario


# Suma o resta cantidad al saldo de una sección. Bloquea la fila para
# que dos movimientos simultáneos no se pisen y rechaza saldos negativos.
def _ajustar_saldo(material_id, seccion_id, cambio):
    existencia, _ = ExistenciaMaterial.objects.select_for_update().get_or_create(
        material_id=material_id,
        seccion_id=seccion_id,
    )

    nueva = existencia.cantidad + cambio

    if nueva < Decimal("0"):
        raise ValidationError(
            f"Existencia insuficiente en la sección: hay "
            f"{existencia.cantidad:,.3f}."
        )

    existencia.cantidad = nueva
    existencia.save(update_fields=["cantidad", "actualizado_en"])


# Guarda el movimiento y actualiza, en una sola transacción, el saldo
# de las secciones involucradas y la existencia total del material.
# Todo lo que cree movimientos (admin, órdenes de empaque, scripts)
# debe pasar por aquí.
@transaction.atomic
def registrar_movimiento(movimiento):
    Mov = MovimientoInventario

    # Bloquea el material para serializar movimientos del mismo material.
    Material.objects.select_for_update().get(pk=movimiento.material_id)

    movimiento.save()

    cantidad = movimiento.cantidad
    origen = movimiento.ubicacion_origen_id
    destino = movimiento.ubicacion_destino_id

    # Un traslado mueve saldo entre secciones; el total no cambia.
    # Se bloquea siempre en el mismo orden para evitar interbloqueos.
    if movimiento.tipo == Mov.Tipo.TRASLADO:
        for seccion_id, cambio in sorted(
            [(origen, -cantidad), (destino, cantidad)]
        ):
            _ajustar_saldo(movimiento.material_id, seccion_id, cambio)
        return movimiento

    if movimiento.tipo in Mov.TIPOS_ENTRADA:
        _ajustar_saldo(movimiento.material_id, destino, cantidad)
        total = cantidad
    else:
        _ajustar_saldo(movimiento.material_id, origen, -cantidad)
        total = -cantidad

    Material.objects.filter(pk=movimiento.material_id).update(
        existencia=F("existencia") + total
    )

    return movimiento