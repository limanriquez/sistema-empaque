# Librerías estándar de Python
from decimal import Decimal, InvalidOperation

# Librerías de Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

# Django REST Framework
from rest_framework import viewsets
from rest_framework.decorators import action

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

# Create your views here.
@login_required()
@require_personal
def comandaPorZona(request):
	return render(request, 'operaciones/comanda_por_zona.html',{
			'title':"Comanda por zona"})
   
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
        'corte_caja':corte_abierto.id,
        'personaId':user.id,
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
