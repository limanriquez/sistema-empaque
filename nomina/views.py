
# --------------------------------------------------
# BIBLIOTECA ESTÁNDAR
# --------------------------------------------------

import json

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


# --------------------------------------------------
# FRAMEWORK DJANGO
# --------------------------------------------------

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


# --------------------------------------------------
# MODELOS
# --------------------------------------------------

from personas.models import Empleado, EmpleadoExtra

from operaciones.models import (
    OperacionDiaria,
    EmpleadosPuestoOperacion,
    DesgloseOperacion,
    ProductoEmpaque,
)

from nomina.models import (
    Nomina,
    NominaOperacionDiaria,
    NominaEmpleado,
    NominaEmpleadoDestajo,
)


# ==================================================
# VISTA: PANTALLA DE GENERACIÓN DE NÓMINA
# ==================================================

@login_required()
def nomina(request):

    return render(
        request,
        'nomina/nomina.html',
        {
            'title': 'Generación de nómina',
        }
    )


# ==================================================
# VISTA: GENERAR NÓMINA
#
# Recibe un rango de fechas y genera:
#
# 1. Encabezado de nómina.
# 2. Relaciones con operaciones diarias.
# 3. Concentrado por empleado.
# 4. Percepciones por sueldo fijo.
# 5. Detalles de destajo.
# 6. Extras integrados.
# 7. Totales generales.
#
# Toda la operación se ejecuta dentro de una
# transacción atómica.
# ==================================================

@login_required
@require_POST
def iniciar_nomina(request):

    # ==================================================
    # 1. VALIDAR DATOS RECIBIDOS
    # ==================================================

    try:

        datos = json.loads(request.body)

        if not isinstance(datos, dict):
            raise ValueError()

        fecha_inicio = datetime.strptime(
            datos.get('fecha_inicio', ''),
            '%Y-%m-%d'
        ).date()

        fecha_fin = datetime.strptime(
            datos.get('fecha_fin', ''),
            '%Y-%m-%d'
        ).date()

    except (ValueError, TypeError, json.JSONDecodeError):

        return JsonResponse({
            'mensaje': 'Las fechas recibidas no son válidas.'
        }, status=400)

    if fecha_inicio > fecha_fin:

        return JsonResponse({
            'mensaje': (
                'La fecha inicial no puede ser posterior '
                'a la fecha final.'
            )
        }, status=400)

    try:

        # ==============================================
        # 2. INICIAR TRANSACCIÓN
        # ==============================================

        with transaction.atomic():

            # ------------------------------------------
            # 2.1 CONSULTAR OPERACIONES DEL PERIODO
            # ------------------------------------------

            operaciones = list(
                OperacionDiaria.objects
                .select_for_update()
                .filter(
                    fecha__range=(
                        fecha_inicio,
                        fecha_fin
                    )
                )
                .order_by('id')
            )

            if not operaciones:

                raise ValidationError(
                    'No existen operaciones diarias '
                    'en el rango de fechas seleccionado.'
                )

            operaciones_ids = [
                operacion.id
                for operacion in operaciones
            ]

            # ------------------------------------------
            # 2.2 VALIDAR OPERACIONES CERRADAS
            #
            # Una operación pendiente o abierta impide
            # generar la nómina completa del periodo.
            # ------------------------------------------

            operaciones_pendientes = [
                operacion.id
                for operacion in operaciones
                if (
                    not operacion.iniciada
                    or operacion.abierta
                )
            ]

            if operaciones_pendientes:

                raise ValidationError(
                    'No se puede generar la nómina. '
                    'Existen operaciones pendientes '
                    'o todavía abiertas. '
                    f'Operaciones: {operaciones_pendientes}'
                )

            # ------------------------------------------
            # 2.3 VALIDAR QUE NO ESTÉN EN OTRA NÓMINA
            # VIGENTE
            # ------------------------------------------

            operaciones_existentes = list(
                NominaOperacionDiaria.objects
                .filter(
                    operacion_diaria_id__in=operaciones_ids,
                    nomina__cancelada=False
                )
                .values_list(
                    'operacion_diaria_id',
                    flat=True
                )
            )

            if operaciones_existentes:

                raise ValidationError(
                    'No se puede generar la nómina. '
                    'Las siguientes operaciones ya pertenecen '
                    'a otra nómina vigente: '
                    f'{operaciones_existentes}'
                )

            # ==============================================
            # 3. OBTENER EMPLEADOS ASIGNADOS
            # ==============================================

            asignaciones = list(
                EmpleadosPuestoOperacion.objects
                .filter(
                    operacion_diaria_id__in=operaciones_ids,
                    empleado__isnull=False
                )
                .values_list(
                    'empleado_id',
                    'operacion_diaria_id'
                )
                .distinct()
            )

            # Los empleados se consolidan por su ID.
            # No se filtra por empleado.activo.
            # La asignación a la operación determina
            # su participación en el periodo.

            empleados_ids = {
                empleado_id
                for empleado_id, operacion_id in asignaciones
            }

            if not empleados_ids:

                raise ValidationError(
                    'No existen empleados asignados '
                    'a las operaciones del periodo.'
                )

            # ==============================================
            # 4. CONTAR DÍAS DE OPERACIÓN POR EMPLEADO
            # ==============================================

            dias_empleado = (
                EmpleadosPuestoOperacion.objects
                .filter(
                    operacion_diaria_id__in=operaciones_ids,
                    empleado_id__in=empleados_ids
                )
                .values('empleado_id')
                .annotate(
                    dias=Count(
                        'operacion_diaria_id',
                        distinct=True
                    )
                )
            )

            dias_por_empleado = {
                registro['empleado_id']: registro['dias']
                for registro in dias_empleado
            }

            # ==============================================
            # 5. OBTENER EMPLEADOS
            # ==============================================

            empleados = list(
                Empleado.objects
                .filter(
                    pk__in=empleados_ids
                )
                .order_by('id')
            )

            # ==============================================
            # 6. OBTENER EXTRAS INTEGRADOS
            #
            # Origen:
            # Empleado -> extras -> EmpleadoExtra
            #
            # Se conserva el total como fotografía
            # histórica en NominaEmpleado.
            # ==============================================

            extras = (
                EmpleadoExtra.objects
                .filter(
                    empleado_id__in=empleados_ids
                )
                .values('empleado_id')
                .annotate(
                    total=Sum('monto')
                )
            )

            extras_por_empleado = {
                registro['empleado_id']: (
                    registro['total'] or Decimal('0.00')
                )
                for registro in extras
            }

            # ==============================================
            # 7. OBTENER CAJAS DE DESTAJO
            #
            # Se consideran exclusivamente:
            # - Operaciones del periodo.
            # - Cajas no canceladas.
            # - Empleados asignados al periodo.
            #
            # La operación se obtiene mediante:
            # DesgloseOperacion -> Tarima ->
            # OperacionLoteEmpaque -> OperacionDiaria
            # ==============================================

            destajos = list(
                DesgloseOperacion.objects
                .filter(
                    tarima__operacion_lote_empaque__operacion_diaria_id__in=operaciones_ids,
                    empleado_id__in=empleados_ids,
                    cancelada=False
                )
                .values(
                    'empleado_id',
                    'producto_empaque_id'
                )
                .annotate(
                    cantidad=Count('id')
                )
                .order_by(
                    'empleado_id',
                    'producto_empaque_id'
                )
            )

            # ------------------------------------------
            # 7.1 RECUPERAR PRODUCTOS DE EMPAQUE
            # ------------------------------------------

            productos_ids = {
                detalle['producto_empaque_id']
                for detalle in destajos
            }

            productos = ProductoEmpaque.objects.in_bulk(
                productos_ids
            )

            # ------------------------------------------
            # 7.2 AGRUPAR DESTAJO POR EMPLEADO
            # ------------------------------------------

            destajos_por_empleado = {}

            for detalle in destajos:

                empleado_id = detalle['empleado_id']

                destajos_por_empleado.setdefault(
                    empleado_id,
                    []
                ).append(detalle)

            # ==============================================
            # 8. CREAR ENCABEZADO DE NÓMINA
            # ==============================================

            nomina_obj = Nomina.objects.create(
                usuario_creacion=request.user
            )

            # ==============================================
            # 9. RELACIONAR OPERACIONES CON LA NÓMINA
            # ==============================================

            for operacion in operaciones:

                relacion = NominaOperacionDiaria(
                    nomina=nomina_obj,
                    operacion_diaria=operacion
                )

                relacion.full_clean()
                relacion.save()

            # ==============================================
            # 10. INICIALIZAR TOTALES GENERALES
            # ==============================================

            total_percepciones = Decimal('0.00')
            total_deducciones = Decimal('0.00')
            total_neto = Decimal('0.00')

            # ==============================================
            # 11. GENERAR NÓMINA POR EMPLEADO
            # ==============================================

            for empleado in empleados:

                # ------------------------------------------
                # 11.1 EXTRA INTEGRADO
                # ------------------------------------------

                total_extra_integrado = (
                    extras_por_empleado.get(
                        empleado.pk,
                        Decimal('0.00')
                    )
                )

                # ------------------------------------------
                # 11.2 CALCULAR PERCEPCIÓN BASE
                # ------------------------------------------

                total_percepcion = Decimal('0.00')

                detalles_preparados = []

                # ------------------------------------------
                # EMPLEADO DE SUELDO FIJO
                # ------------------------------------------

                if empleado.tipo_remuneracion == (
                    Empleado.TipoRemuneracion.FIJO
                ):

                    dias = dias_por_empleado.get(
                        empleado.pk,
                        0
                    )

                    total_percepcion = (
                        empleado.sueldo_diario * dias
                    )

                # ------------------------------------------
                # EMPLEADO DE DESTAJO
                # ------------------------------------------

                elif empleado.tipo_remuneracion == (
                    Empleado.TipoRemuneracion.DESTAJO
                ):

                    detalles = (
                        destajos_por_empleado.get(
                            empleado.pk,
                            []
                        )
                    )

                    for detalle in detalles:

                        producto = productos.get(
                            detalle['producto_empaque_id']
                        )

                        if producto is None:

                            raise ValidationError(
                                'No se encontró un producto '
                                'de empaque relacionado '
                                'con un destajo.'
                            )

                        cantidad = detalle['cantidad']

                        # La tarifa salarial está en:
                        # ProductoEmpaque.costo_empaque

                        precio_unitario = (
                            producto.costo_empaque
                        )

                        # El precio unitario conserva
                        # cuatro decimales.
                        #
                        # El importe monetario del detalle
                        # se redondea a dos decimales.

                        total_detalle = (
                            precio_unitario * cantidad
                        ).quantize(
                            Decimal('0.01'),
                            rounding=ROUND_HALF_UP
                        )

                        detalles_preparados.append({
                            'producto': producto,
                            'cantidad': cantidad,
                            'precio_unitario': precio_unitario,
                            'total': total_detalle
                        })

                        total_percepcion += total_detalle

                else:

                    raise ValidationError(
                        f'El empleado {empleado.pk} tiene '
                        'un tipo de remuneración no válido.'
                    )

                # ------------------------------------------
                # 11.3 CALCULAR NETO DEL EMPLEADO
                # ------------------------------------------

                total_extra = Decimal('0.00')
                total_deduccion = Decimal('0.00')

                total_neto_empleado = (
                    total_percepcion
                    + total_extra_integrado
                    + total_extra
                    - total_deduccion
                )

                # ------------------------------------------
                # 11.4 CREAR CONCENTRADO DEL EMPLEADO
                # ------------------------------------------

                empleado_nomina = NominaEmpleado.objects.create(
                    nomina=nomina_obj,
                    empleado=empleado,
                    total_percepcion=total_percepcion,
                    total_extra_integrado=total_extra_integrado,
                    total_extra=total_extra,
                    total_deduccion=total_deduccion,
                    total_neto=total_neto_empleado
                )

                # ------------------------------------------
                # 11.5 REGISTRAR DETALLES DE DESTAJO
                # ------------------------------------------

                for detalle in detalles_preparados:

                    NominaEmpleadoDestajo.objects.create(
                        nomina_empleado=empleado_nomina,
                        producto_empaque=detalle['producto'],
                        cantidad=detalle['cantidad'],
                        precio_unitario=detalle['precio_unitario'],
                        total=detalle['total']
                    )

                # ------------------------------------------
                # 11.6 ACUMULAR TOTALES GENERALES
                # ------------------------------------------

                total_percepciones += (
                    total_percepcion
                    + total_extra_integrado
                    + total_extra
                )

                total_deducciones += total_deduccion

                total_neto += total_neto_empleado

            # ==============================================
            # 12. ACTUALIZAR TOTALES DEL ENCABEZADO
            # ==============================================

            nomina_obj.total_percepciones = (
                total_percepciones
            )

            nomina_obj.total_deducciones = (
                total_deducciones
            )

            nomina_obj.total_neto = total_neto

            nomina_obj.save(
                update_fields=[
                    'total_percepciones',
                    'total_deducciones',
                    'total_neto'
                ]
            )

        # ==============================================
        # 13. RESPUESTA EXITOSA
        # ==============================================

        return JsonResponse({
            'mensaje': 'La nómina se generó correctamente.',
            'nomina_id': nomina_obj.pk,
            'total_operaciones': len(operaciones),
            'total_empleados': len(empleados),
            'total_percepciones': str(total_percepciones),
            'total_deducciones': str(total_deducciones),
            'total_neto': str(total_neto)
        }, status=200)

    except ValidationError as error:

        return JsonResponse({
            'mensaje': ' '.join(error.messages)
        }, status=400)

    except IntegrityError:

        return JsonResponse({
            'mensaje': (
                'No fue posible generar la nómina debido a '
                'un conflicto de integridad. Es posible que '
                'alguna operación haya sido incluida en otra '
                'nómina simultáneamente.'
            )
        }, status=409)
