
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    ExistenciaMaterial,
    Material,
    MovimientoInventario,
)


# Suma o resta cantidad al saldo de una sección y propietario.
# Todo registro de existencia debe tener un cliente propietario,
# incluida la empacadora.
# Se permiten saldos negativos.
def _ajustar_saldo(material_id, seccion_id, cliente_id, cambio):

    if not seccion_id:
        raise ValidationError(
            "No se indicó la sección del inventario."
        )

    if not cliente_id:
        raise ValidationError(
            "No se indicó el propietario del inventario."
        )

    existencia, _ = (
        ExistenciaMaterial.objects
        .select_for_update()
        .get_or_create(
            material_id=material_id,
            seccion_id=seccion_id,
            cliente_id=cliente_id,
        )
    )

    existencia.cantidad += cambio

    existencia.save(
        update_fields=[
            "cantidad",
            "actualizado_en",
        ]
    )


# Guarda el movimiento y actualiza, en una sola transacción,
# los saldos por material, sección y propietario.
# Todo lo que cree movimientos debe pasar por aquí.
@transaction.atomic
def registrar_movimiento(movimiento):

    Mov = MovimientoInventario

    # Evita registrar nuevamente un movimiento ya guardado.
    if movimiento.pk:
        raise ValidationError(
            "El movimiento ya fue registrado."
        )

    # Bloquea el material para serializar sus movimientos.
    try:
        Material.objects.select_for_update().get(
            pk=movimiento.material_id
        )
    except Material.DoesNotExist:
        raise ValidationError(
            "El material seleccionado no existe."
        )

    # Verifica que el tipo de movimiento sea válido.
    if movimiento.tipo not in (
        Mov.TIPOS_ENTRADA
        + Mov.TIPOS_SALIDA
        + (Mov.Tipo.TRASLADO,)
    ):
        raise ValidationError(
            "Tipo de movimiento no reconocido."
        )

    # Valida y guarda el movimiento.
    # El modelo ejecuta full_clean() en save().
    movimiento.save()

    cantidad = movimiento.cantidad

    origen = movimiento.ubicacion_origen_id
    destino = movimiento.ubicacion_destino_id

    propietario_origen = movimiento.propietario_origen_id
    propietario_destino = movimiento.propietario_destino_id

    # --------------------------------------------------------
    # TRASLADOS
    # --------------------------------------------------------

    # Descuenta del origen y suma al destino.
    # Puede cambiar la sección, el propietario o ambos.
    if movimiento.tipo == Mov.Tipo.TRASLADO:

        operaciones = [
            (
                origen,
                propietario_origen,
                -cantidad,
            ),
            (
                destino,
                propietario_destino,
                cantidad,
            ),
        ]

        # Bloquea y actualiza siempre en el mismo orden.
        operaciones.sort(
            key=lambda operacion: (
                operacion[0],
                operacion[1],
            )
        )

        for seccion_id, cliente_id, cambio in operaciones:

            _ajustar_saldo(
                movimiento.material_id,
                seccion_id,
                cliente_id,
                cambio,
            )

        return movimiento

    # --------------------------------------------------------
    # ENTRADAS
    # --------------------------------------------------------

    # Incrementan el saldo del propietario destino.
    if movimiento.tipo in Mov.TIPOS_ENTRADA:

        _ajustar_saldo(
            movimiento.material_id,
            destino,
            propietario_destino,
            cantidad,
        )

    # --------------------------------------------------------
    # SALIDAS
    # --------------------------------------------------------

    # Disminuyen el saldo del propietario de origen.
    elif movimiento.tipo in Mov.TIPOS_SALIDA:

        _ajustar_saldo(
            movimiento.material_id,
            origen,
            propietario_origen,
            -cantidad,
        )

    return movimiento
