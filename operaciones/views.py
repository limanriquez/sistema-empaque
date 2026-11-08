# Librerías estándar de Python
from decimal import Decimal, InvalidOperation
from weasyprint import HTML

# Librerías de Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime
from pytz import timezone as pytz_timezone  # opcional si quieres zona específica
from django.template.loader import render_to_string

from .models import OperacionDiaria, ProductoEmpaque, EmpleadosPuestoOperacion
# Django REST Framework
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.views.decorators.http import require_GET

from authentication.decoradores import require_personal

from django.db.models import Sum, Count, F, Q, Case, When, Value

import json

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from catalogos.models import Calidad, Tamano



@login_required()
def captura_caja(request):
    operacion_diaria = (
        OperacionDiaria.objects
        .filter(
            abierta=True,
            iniciada=True
        )
        .first()
    )

    lote_empaque = None
    variedad = None

    if operacion_diaria:

        relacion = (
            operacion_diaria.lotes_empaque
            .select_related(
                'lote_empaque',
                'lote_empaque__variedad',
                'lote_empaque__lote_huerta'
            )
            .first()
        )

        if relacion:
            lote_empaque = relacion.lote_empaque
            variedad = lote_empaque.variedad

    return render(
        request,
        'operaciones/captura_caja.html',
        {
            'title': 'Captura de cajas',
            'operacion_diaria': operacion_diaria,
            'lote_empaque': lote_empaque,
            'variedad': variedad,
        }
    )


# ==========================================================
# VISTA: CONSULTAR EMPLEADO ASIGNADO A ESTACIÓN
#
# Identifica al empleado asignado a una estación de trabajo
# dentro de una operación diaria específica.
#
# La búsqueda se realiza mediante el ID de la operación
# diaria y el ID de la estación de trabajo, consultando
# el modelo EmpleadosPuestoOperacion.
#
# Devuelve el identificador de la estación y el empleado
# asignado en formato JSON.
#
# Si no existe una asignación, devuelve el mensaje
# correspondiente con código HTTP 404.
#
# La consulta es de solo lectura y requiere autenticación.
# ==========================================================

@login_required
@require_GET
def obtener_empleado_estacion(request):

    operacion_id = request.GET.get('operacion_diaria_id')
    estacion_id = request.GET.get('estacion_trabajo_id')

    if not operacion_id or not estacion_id:
        return JsonResponse({
            'success': False,
            'mensaje': 'Se requiere la operación diaria y la estación de trabajo.'
        }, status=400)

    asignacion = (
        EmpleadosPuestoOperacion.objects
        .filter(
            operacion_diaria_id=operacion_id,
            estacion_trabajo_id=estacion_id,
        )
        .values(
            'estacion_trabajo_id',
            'empleado_id',
        )
        .first()
    )

    if not asignacion:
        return JsonResponse({
            'success': False,
            'mensaje': 'No existe una asignación para esta estación en la operación diaria.'
        }, status=404)

    return JsonResponse({
        'success': True,
        'estacion_trabajo_id': asignacion['estacion_trabajo_id'],
        'empleado_id': asignacion['empleado_id'],
    })


# ==========================================================
# VISTA: CONSULTAR PRODUCTO DE EMPAQUE POR CÓDIGO
#
# Busca un producto de empaque mediante su código.
# Únicamente considera productos activos.
#
# Devuelve los datos del producto para utilizarlos
# en el proceso de captura.
# ==========================================================

@login_required
@require_GET
def obtener_producto_empaque(request):

    codigo = request.GET.get('codigo', '').strip()

    if not codigo:
        return JsonResponse({
            'success': False,
            'mensaje': 'Debe proporcionar el código del producto.'
        }, status=400)

    producto = (
        ProductoEmpaque.objects
        .select_related('calidad')
        .filter(
            codigo=codigo,
            activo=True
        )
        .values(
            'id',
            'codigo',
            'nombre',
            'costo_empaque',
            'calidad_id',
            'calidad__nombre',
        )
        .first()
    )

    if not producto:
        return JsonResponse({
            'success': False,
            'mensaje': 'No se encontró un producto activo con ese código.'
        }, status=404)

    return JsonResponse({
        'success': True,
        'producto': producto
    })
# ==========================================================
# VISTA: CONSULTAR TARIMAS ABIERTAS
#
# Obtiene las tarimas abiertas de una operación diaria
# y un lote de empaque específicos.
#
# Prioriza las tarimas cuyo tamaño coincide con el tamaño
# del producto de empaque seleccionado.
#
# Si no existen coincidencias, devuelve las demás tarimas
# abiertas disponibles.
#
# Calcula las cajas registradas sin considerar las
# cajas canceladas.
# ==========================================================

@login_required
@require_GET
def obtener_tarimas_abiertas(request):

    operacion_id = request.GET.get('operacion_diaria_id')
    lote_empaque_id = request.GET.get('lote_empaque_id')
    tamano_id = request.GET.get('tamano_id')

    if not operacion_id or not lote_empaque_id:
        return JsonResponse({
            'success': False,
            'mensaje': 'Se requiere la operación diaria y el lote de empaque.'
        }, status=400)

    tarimas = (
        Tarima.objects
        .filter(
            operacion_lote_empaque__operacion_diaria_id=operacion_id,
            operacion_lote_empaque__lote_empaque_id=lote_empaque_id,
            operacion_lote_empaque__operacion_diaria__abierta=True,
            operacion_lote_empaque__lote_empaque__abierto=True,
            abierta=True,
        )
        .annotate(
            total_cajas=Count(
                'cajas',
                filter=Q(cajas__cancelada=False)
            )
        )
        .annotate(
            prioridad_tamano=Case(
                When(tamano_id=tamano_id, then=Value(0)),
                default=Value(1),
            )
        )
        .select_related(
            'codigo_tarima',
            'tamano',
        )
        .order_by(
            'prioridad_tamano',
            'codigo_tarima__consecutivo',
        )
    )

    resultado = []

    for tarima in tarimas:

        resultado.append({
            'id': tarima.id,
            'codigo_tarima': tarima.codigo_tarima.codigo_tarima,
            'consecutivo': tarima.codigo_tarima.consecutivo,
            'tamano_id': tarima.tamano_id,
            'capacidad_maxima': tarima.capacidad_maxima,
            'total_cajas': tarima.total_cajas,
            'espacios_disponibles': max(
                tarima.capacidad_maxima - tarima.total_cajas,
                0
            ),
        })

    return JsonResponse({
        'success': True,
        'total': len(resultado),
        'tarimas': resultado,
    })


@login_required
@require_GET
def obtener_tamano(request):

    nombre = request.GET.get('nombre', '').strip()

    if not nombre:
        return JsonResponse({
            'success': False,
            'mensaje': 'Debe proporcionar el nombre del tamaño.'
        }, status=400)

    tamano = (
        Tamano.objects
        .filter(
            nombre=nombre,
            activo=True
        )
        .values('id', 'nombre')
        .first()
    )

    if not tamano:
        return JsonResponse({
            'success': False,
            'mensaje': 'No se encontró un tamaño activo con ese nombre.'
        }, status=404)

    return JsonResponse({
        'success': True,
        'tamano': tamano
    })


	###################
@login_required
@ensure_csrf_cookie
def hola_mundo_vue(request):
    return render(
        request,
        'operaciones/hola_mundo_vue.html',
    )


@login_required
@require_GET
def hola_mundo_api(request):
    return JsonResponse({
        'success': True,
        'mensaje': 'Hola desde Django. La comunicación con Vue funciona.',
        'framework': 'Django',
    })


@login_required
@require_POST
def hola_mundo_post_api(request):
    try:
        datos = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'mensaje': 'El JSON enviado no es válido.',
        }, status=400)

    mensaje = datos.get('mensaje', '')

    return JsonResponse({
        'success': True,
        'mensaje': 'Django recibió correctamente el POST.',
        'dato_recibido': mensaje,
        'metodo': request.method,
    })


@login_required
def captura_caja_vue(request):

    operacion_diaria = (
        OperacionDiaria.objects
        .filter(
            abierta=True,
            iniciada=True
        )
        .first()
    )

    lote_empaque = None
    variedad = None

    if operacion_diaria:
        relacion = (
            operacion_diaria.lotes_empaque
            .select_related(
                'lote_empaque',
                'lote_empaque__variedad',
                'lote_empaque__lote_huerta'
            )
            .first()
        )

        if relacion:
            lote_empaque = relacion.lote_empaque
            variedad = lote_empaque.variedad

    return render(
        request,
        'operaciones/captura_caja_vue.html',
        {
            'title': 'Captura de cajas Vue',
            'operacion_diaria': operacion_diaria,
            'lote_empaque': lote_empaque,
            'variedad': variedad,
        }
    )