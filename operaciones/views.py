# Librerías estándar de Python
from decimal import Decimal, InvalidOperation

# Librerías de Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from pytz import timezone as pytz_timezone  # opcional si quieres zona específica


# Django REST Framework
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Importaciones propias / locales
from inventarios.models import Producto, BOM, StockItem
from operaciones.models import DesgloseVenta, Ventas
from operaciones.serializer import *
from inventario.permissions import IsAdminOrReadOnly
from authentication.decoradores import require_personal


class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClientesSerializer

    @action(detail=False, methods=['get'])
    def activos_por_empresa(self, request):
        empresa_id = request.query_params.get('empresa')
        if not empresa_id:
            return Response({"error": "Parámetro 'empresa' es requerido."}, status=400)

        queryset = self.queryset.filter(estatus=True, empresa_id=empresa_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class VentasViewSet(viewsets.ModelViewSet):
    queryset = Ventas.objects.all()  # necesario para que el router funcione
    serializer_class = VentasSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        venta_id = self.request.query_params.get('venta_id')
        if venta_id:
            queryset = queryset.filter(id=venta_id)
        return queryset

class PagoVentaViewSet(viewsets.ModelViewSet):
    queryset = PagoVenta.objects.all()
    serializer_class = PagoVentaSerializer

    @action(detail=False, methods=['get'], url_path='activos')
    def activos(self, request):
        pagos_activos = self.get_queryset().filter(activo=True)
        serializer = self.get_serializer(pagos_activos, many=True)
        return Response(serializer.data)


class NotificacionZonaSerializerViewSet(viewsets.ModelViewSet):
    queryset = NotificacionZona.objects.all()
    serializer_class = NotificacionZonaSerializer
   
    @action(detail=False, methods=['get'])
    def activos(self, request):
        queryset = self.queryset.filter(activo=True)

        zona_id = request.query_params.get('zona_id')
        if zona_id:
            queryset = queryset.filter(zona_id=zona_id)

        venta_id = request.query_params.get('venta_id')
        if venta_id:
            queryset = queryset.filter(venta_id=venta_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
   # permission_classes = [IsAdminOrReadOnly]  # Aplica el permiso personalizado


# Create your views here.
@login_required()
@require_personal
def clientes(request):
	return render(request, 'operaciones/clientes.html',{
			'title':"Clientes"})
@login_required()
@require_personal
def corte_caja(request):
    user = request.user.personal
    empresa = user.empresa
    corte_abierto = CorteCaja.objects.filter(
        estatus=1,
        empresa=empresa.id
    ).first()
    return render(request, 'operaciones/corte_caja.html',{
			'title': "Corte de caja ",
            'empresa': empresa,
            'corte_caja': corte_abierto.id if corte_abierto else None,
            'personaId': user.id,
            'nombre_personal': f"{user.nombre} {user.apellido_paterno} {user.apellido_materno}"
            })

# Create your views here.
@login_required()
@require_personal
def comandaPorZona(request):
    user = request.user.personal
    empresa = user.empresa

    # Verificar si el usuario tiene un corte abierto
    corte_abierto = CorteCaja.objects.filter(
        estatus=1,
        empresa=empresa.id
    ).first()

    return render(request, 'operaciones/comanda_por_zona.html', {
        'title': "Comanda por zona",
        'empresa': empresa,
        'corte_caja': corte_abierto.id if corte_abierto else None,
        'personaId': user.id,
        'nombre_personal': f"{user.nombre} {user.apellido_paterno} {user.apellido_materno}"
    })

@login_required()
def imprimirTicketVenta(request):
    # Obtener la venta activa
    venta_id = request.GET.get('venta_id')
    venta = get_object_or_404(Ventas, id=venta_id, activo=True, pagada = True)
    # Traer todos los productos del desglose con select_related para evitar queries N+1
    desglose = venta.desglose.select_related('producto').all()

    # Calcular subtotal sumando precios unitarios sin descuentos
    subtotal = sum(item.precio_unitario for item in desglose)

    context = {
        'venta': venta,
        'desglose': desglose,
        'subtotal': subtotal,
        'descuento': venta.descuento,
        'total': venta.total,
        'cambio': venta.cambio,
    }
    
    return render(request, 'operaciones/ticket_venta.html', context)
   
@login_required()
@require_personal
def punto_de_venta(request):
    user = request.user.personal
    empresa = user.empresa
    # Verificar si el usuario tiene un corte abierto
    corte_abierto = CorteCaja.objects.filter(
        estatus = 1,
        empresa = empresa.id
    ).first()
    if not corte_abierto:
        messages.warning(request, "No tienes un corte de caja abierto. Ábrelo en el administrador.")
        # Redirige directamente a la vista de agregar CorteCaja en el admin
        return redirect(reverse('admin:%s_%s_add' % (CorteCaja._meta.app_label, CorteCaja._meta.model_name)))

    return render(request, 'operaciones/punto_venta.html', {
        'title': "Punto de venta",
        'empresa': empresa,
        'empresa_id':empresa.id,
        'corte_caja':corte_abierto.id,
        'personal_id':user.id,
        'nombre_personal': f"{user.nombre} {user.apellido_paterno} {user.apellido_materno}"
    })

@login_required
def existeTelefono(request, telefono):
    # Verificar si el teléfono no es vacío
    if not telefono:
        return JsonResponse({"error": "El teléfono es requerido"}, status=400)
    
    # Buscar solo el teléfono en la base de datos para hacer la consulta más ligera
    existe = Cliente.objects.filter(telefono=telefono).values('telefono').exists()

    # Retornar la respuesta en formato JSON con el estado de existencia del teléfono
    return JsonResponse({"Existe": existe})
	

@login_required
def ventasAbiertasCorteEmpresas(request):
    corte_caja = request.GET.get('corteCaja')
    ventas = Ventas.objects.filter(corte_caja = corte_caja, activo = True, pagada = False)
    ventas_data = []
    for v in ventas:
        ventas_data.append({
            "id": v.id,
            "cliente_id": v.cliente_id,
            "corte_caja_id": v.corte_caja_id,
            "fecha_venta": v.fecha_venta.isoformat() if v.fecha_venta else None,
            "total": str(v.total),
            "lugar_entrega_id": v.lugar_entrega_id,
            "atencion_id": v.atencion_id,
            "observaciones": v.observaciones,
            "activo": v.activo,
            "personal": f"{v.atencion.nombre} {v.atencion.apellido_paterno} {v.atencion.apellido_materno}"
        })

    return JsonResponse(ventas_data, safe=False)


@login_required
def transaccionVentaProducto(request):
    producto_id = request.GET.get('producto')
    venta_id = request.GET.get('venta')
    precio_venta = request.GET.get('precio')
    descuento_raw = request.GET.get('descuento', '0.00')
    empresa = request.GET.get('empresa')
    observaciones = request.GET.get('observaciones', '')

    if not producto_id or not venta_id or not precio_venta:
        return HttpResponseBadRequest("Faltan parámetros obligatorios")

    try:
        producto_id = int(producto_id)
        venta_id = int(venta_id)
        precio_unitario = Decimal(precio_venta)
        descuento = Decimal(descuento_raw)

        if precio_unitario < 0 or descuento < 0:
            return JsonResponse({'error': 'El precio y el descuento deben ser mayores o iguales a 0'})
        if descuento > precio_unitario:
            return JsonResponse({'error': 'El descuento no puede ser mayor al precio'})
    except (ValueError, InvalidOperation):
        return HttpResponseBadRequest("Parámetros inválidos")

    boms = BOM.objects.select_related('stock_item').filter(producto_id=producto_id)
    if not boms.exists():
        return JsonResponse({'error': 'El producto no es compuesto o no tiene componentes'})

    # Validar stock antes de la transacción
    for bom in boms:
        if bom.stock_item.existencia < bom.cantidad:
            return JsonResponse({'error': f'Stock insuficiente para {bom.stock_item.nombre}'})

    producto = get_object_or_404(Producto, pk=producto_id)
    venta = get_object_or_404(Ventas, pk=venta_id)

    total = precio_unitario - descuento

    with transaction.atomic():
        # Bloquear stock items para evitar condición de carrera
        stock_items = StockItem.objects.select_for_update().filter(
            id__in=[bom.stock_item_id for bom in boms]
        )
        stock_map = {si.id: si for si in stock_items}

        # Actualizar stock y verificar de nuevo dentro del lock
        for bom in boms:
            stock_item = stock_map[bom.stock_item_id]
            stock_item.existencia -= bom.cantidad
            if stock_item.existencia < 0:
                transaction.set_rollback(True)
                return JsonResponse({'error': f'Stock insuficiente para {stock_item.nombre} (concurrency)'})
            stock_item.save()

        # Registrar desglose
        DesgloseVenta.objects.create(
            venta = venta,
            producto = producto,
            precio_unitario = precio_unitario,
            descuento = descuento,
            total = total,
            empresa_id = empresa,
            observaciones = observaciones or None
        )

    return JsonResponse({'success': 'Producto vendido y registrado correctamente'})
            
@login_required
def transaccionCancelarDesgloseVenta(request):
    desglose_id = request.GET.get('idDesgloce')

    if not desglose_id:
        return HttpResponseBadRequest("Falta el ID del desglose")

    try:
        desglose_id = int(desglose_id)
    except ValueError:
        return HttpResponseBadRequest("ID inválido")

    desglose = get_object_or_404(DesgloseVenta, pk=desglose_id)
    producto = desglose.producto

    # Validar que el producto sea compuesto
  #  if not producto.es_compuesto:
   #     return JsonResponse({'error': 'El producto no es compuesto, no se puede revertir stock por BOM'})

    # Obtener los componentes BOM
    boms = BOM.objects.select_related('stock_item').filter(producto=producto)
    if not boms.exists():
        return JsonResponse({'error': 'No hay componentes registrados en el BOM para este producto'})

    with transaction.atomic():
        # Bloquear los stock_items que serán modificados
        stock_items = StockItem.objects.select_for_update().filter(
            id__in=[bom.stock_item_id for bom in boms]
        )
        stock_map = {si.id: si for si in stock_items}

        # Revertir el stock según la definición BOM
        for bom in boms:
            stock_item = stock_map[bom.stock_item_id]
            stock_item.existencia += bom.cantidad  # Aumenta la cantidad usada en la venta
            stock_item.save()

        # Eliminar el desglose
        desglose.delete()

    return JsonResponse({'success': 'Desglose anulado y stock revertido correctamente'})


@login_required
def productosVenta(request):
    venta_id = request.GET.get('venta')
    # Traer todos los registros del desglose de una venta específica, incluyendo el producto
    desglose = DesgloseVenta.objects.select_related('producto').filter(venta_id=venta_id)
    # Ejemplo: construir una respuesta JSON con datos de producto
    desglose_data = []
    for item in desglose:
        desglose_data.append({
            'id_desglose': item.id,
            'producto_id': item.producto.id,
            'producto_nombre': item.producto.nombre,
            'precio_unitario': float(item.precio_unitario),
            'descuento': float(item.descuento),
            'total': float(item.total),
        })

    return JsonResponse(desglose_data, safe=False)

@login_required
def pagosPorVenta(request):
    venta_id = request.GET.get('venta')
    if not venta_id:
        return JsonResponse({'error': "Parámetro 'venta' es requerido."}, status=400)

    # Traer todos los pagos relacionados con la venta_id, incluyendo el método de pago
    pagos = PagoVenta.objects.select_related('metodo_pago').filter(venta_id=venta_id, activo=True)

    pagos_data = []
    for pago in pagos:
        pagos_data.append({
            'id_pago': pago.id,
            'metodo_pago_id': pago.metodo_pago.id,
            'metodo_pago_nombre': pago.metodo_pago.nombre,
            'monto': float(pago.monto),
            'referencia': pago.referencia,
            'fecha_pago': pago.fecha_pago.isoformat(),
            'observaciones': pago.observaciones,
        })

    return JsonResponse(pagos_data, safe=False)


@login_required
def comandasPendientes(request):
    zona_id = request.GET.get('zona')
    estado = request.GET.get('estado')
    corteCaja = request.GET.get('corteCaja')
    notificaciones = NotificacionZona.objects.select_related(
        'desglose_venta', 
        'desglose_venta__venta',
        'producto',
        'zona'
    ).filter(
        estado=int(estado),
        zona_id=int(zona_id),
        desglose_venta__venta__corte_caja_id=int(corteCaja)
    ).order_by('id')
    
    data = []
    for n in notificaciones:
        # Convertir a hora local de Django
        hora_local = timezone.localtime(n.creada_en)  # usa la zona de Django settings
        # o si quieres forzar México: 
        # hora_local = n.creada_en.astimezone(pytz_timezone("America/Mexico_City"))
        data.append({
            "id": n.id,
            "estado": n.get_estado_display(),
            "cantidad": n.cantidad,
            "creada_en": hora_local.isoformat(),
            "hora_inicial": hora_local.strftime("%H:%M:%S"),
            "zona": n.zona.id,
            "producto": n.producto.nombre,
            "desglose_venta": n.desglose_venta.id,
            "venta_id": n.desglose_venta.venta.id
        })

    return JsonResponse(data, safe=False)

@login_required
def cortesPorEmpresa(request):
    # Obtener parámetro empresa desde GET
    empresa_id = request.GET.get('empresa')
    if not empresa_id:
        return JsonResponse({"detail": "Debe proporcionar ?empresa=<id>"}, status=400)

    cortes = CorteCaja.objects.filter(empresa_id=empresa_id)
    cortes_data = []

    for c in cortes:
        cortes_data.append({
            "id": c.id,
            "empresa_id": c.empresa_id,
            "personal_id": c.personal_id,
            "personal": f"{c.personal.nombre} {c.personal.apellido_paterno} {c.personal.apellido_materno}",
            "saldo_inicial": str(c.saldo_inicial),
            "saldo_final": str(c.saldo_final) if c.saldo_final is not None else None,
            "ingresos_efectivo": str(c.ingresos_efectivo),
            "ingresos_tarjeta": str(c.ingresos_tarjeta),
            "ingresos_transferencia": str(c.ingresos_transferencia),
            "egresos": str(c.egresos),
            "fecha_apertura": c.fecha_apertura.strftime('%d/%m/%Y') if c.fecha_apertura else None,
            "fecha_cierre": c.fecha_cierre.strftime('%d/%m/%Y') if c.fecha_cierre else None,
            "observaciones": c.observaciones,
            "estatus": c.get_estatus_display(),  # Devuelve "Abierto", "Cerrado" o "Cancelado"
        })

    return JsonResponse(cortes_data, safe=False)

@login_required
def ventasPorCorteCaja(request):
    # Obtener parámetro corte_caja desde GET
    corte_id = request.GET.get('corteCaja')
    if not corte_id:
        return JsonResponse({"detail": "Debe proporcionar ?corteCaja=<id>"}, status=400)

    # Filtrar ventas del corte de caja específico
    ventas = Ventas.objects.filter(corte_caja_id=corte_id, activo=True).order_by('-id')[:10] 
    ventas_data = []

    for v in ventas:
        ventas_data.append({
            "id_venta": v.id,
            "corte_caja_id": v.corte_caja_id,
            "cliente_id": v.cliente_id,
            "cliente": f"{v.cliente.nombre} {v.cliente.apellido_paterno} {v.cliente.apellido_materno}" if v.cliente else None,
            "personal_id": v.atencion_id,
            "personal": f"{v.atencion.nombre} {v.atencion.apellido_paterno} {v.atencion.apellido_materno}" if v.atencion else None,
            "fecha_venta": v.fecha_venta.strftime('%d/%m/%Y') if v.fecha_venta else None,
            "total": str(v.total),
            "pagada": v.pagada,
            "activo": v.activo,
            "observaciones": v.observaciones,
            "lugar_entrega_id": v.lugar_entrega_id,
            # Puedes agregar más campos que necesites mostrar
        })

    return JsonResponse(ventas_data, safe=False)


@login_required
def corteCajaAbierto(request):
    empresa_id = request.GET.get('empresa')
    if not empresa_id:
        return JsonResponse({"advertencia": "Debe proporcionar ?empresa=<id>"}, status=200)

    try:
        corte_abierto = CorteCaja.objects.get(empresa_id=empresa_id, estatus=1)
    except CorteCaja.DoesNotExist:
        return JsonResponse({"advertencia": "No existe un corte de caja abierto para esta empresa."}, status=200)

    # Verificar si hay ventas activas no pagadas
    ventas_abiertas = Ventas.objects.filter(
        corte_caja=corte_abierto,
        activo=True,
        pagada=False
    ).exists()

    if ventas_abiertas:
        return JsonResponse({"advertencia": "Existen ventas activas no pagadas en este corte de caja."}, status=200)

    # Calcular ingresos por tipo de pago usando IDs (1: Efectivo, 2: Tarjeta Crédito, 3: Tarjeta Débito)
    ingresos_efectivo = PagoVenta.objects.filter(
        venta__corte_caja=corte_abierto,
        venta__activo=True,
        venta__pagada=True,
        metodo_pago_id=1
    ).aggregate(total=Sum('monto'))['total'] or 0

    ingresos_tarjeta = PagoVenta.objects.filter(
        venta__corte_caja=corte_abierto,
        venta__activo=True,
        venta__pagada=True,
        metodo_pago_id__in=[2, 3]  # ambos tipos de tarjeta
    ).aggregate(total=Sum('monto'))['total'] or 0

    ingresos_transferencia = PagoVenta.objects.filter(
        venta__corte_caja=corte_abierto,
        venta__activo=True,
        venta__pagada=True,
        metodo_pago_id=4  # si tienes transferencia con id=4
    ).aggregate(total=Sum('monto'))['total'] or 0

    # Serializar corte
    corte_data = {
        "id": corte_abierto.id,
        "empresa_id": corte_abierto.empresa_id,
        "personal_id": corte_abierto.personal_id,
        "saldo_inicial": str(corte_abierto.saldo_inicial),
        "saldo_final": str(corte_abierto.saldo_final) if corte_abierto.saldo_final is not None else None,
        "ingresos_efectivo": str(ingresos_efectivo),
        "ingresos_tarjeta": str(ingresos_tarjeta),
        "ingresos_transferencia": str(ingresos_transferencia),
        "egresos": str(corte_abierto.egresos),
        "fecha_apertura": corte_abierto.fecha_apertura.strftime('%d/%m/%Y') if corte_abierto.fecha_apertura else None,
        "fecha_cierre": corte_abierto.fecha_cierre.strftime('%d/%m/%Y') if corte_abierto.fecha_cierre else None,
        "observaciones": corte_abierto.observaciones,
        "estatus": corte_abierto.get_estatus_display(),
    }

    return JsonResponse(corte_data, safe=False)
