from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventarios.serializer import *
from rest_framework import viewsets
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery

from authentication.decoradores import require_personal
from .models import Producto, StockItem
from operaciones.models import CorteCaja

@login_required()
@require_personal
def movimientoInventario(request):
    user = request.user.personal
    empresa = user.empresa
    return render(request, 'inventarios/movimiento_inventario.html',{
			'title':"Movimiento inventario",
            'empresa': empresa,
            'personaId': user.id,
            'nombre_personal': f"{user.nombre} {user.apellido_paterno} {user.apellido_materno}"
            })
            

class ProductosViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(activo=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='activos_por_tipo')
    def activos_por_tipo(self, request):
        tipo_id = request.query_params.get('categoria')
        empresa_id = request.query_params.get('empresa')

        if not tipo_id or not empresa_id:
            return Response(
                {"error": "El tipo de producto y empresa son requeridos"},
                status=400
            )

        productos = self.queryset.filter(
            activo=True,
            tipo_producto_id=tipo_id,
            empresa_id=empresa_id,
        ).order_by('orden')

        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

class ProductoZonaNotificacionViewSet(viewsets.ModelViewSet):
    queryset = ProductoZonaNotificacion.objects.all()
    serializer_class = ProductoZonaNotificacionSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(activo=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)


@login_required
def productosActivosEmpresas(request):
    empresas_str = request.GET.get('empresas')
    tipoProducto = request.GET.get('categoria')

    if not empresas_str:
        return JsonResponse({"error": "Se requiere el parámetro 'empresas'"}, status=400)

    try:
        ids_empresas = list(map(int, empresas_str.split('-')))
    except ValueError:
        return JsonResponse({"error": "Formato inválido en 'empresas'. Deben ser enteros separados por '-'."}, status=400)

    try:
        tipoProducto = int(tipoProducto)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Parámetro 'categoria' inválido o ausente."}, status=400)

    precio_subquery = PrecioProducto.objects.filter(
        producto=OuterRef('pk'),
        activo=True
    ).order_by('id').values('precio')[:1]

    productos = Producto.objects.filter(
        tipo_producto=tipoProducto,
        activo=True,
        vendible=True,
        empresa__in=ids_empresas,
        precios__isnull=False 
    ).select_related('empresa').annotate(
        primer_precio=Subquery(precio_subquery)
    ).order_by('orden')  # Aquí agregas la anotación

    resultado = []
    for p in productos:
        resultado.append({
            "id": p.id,
            "nombre": p.nombre,
            "codigo": p.codigo,
            "descripcion": p.descripcion,
            "empresa": p.empresa_id,
            "empresa_nombre": p.empresa.nombre,
            "tipo_producto": p.tipo_producto_id,
            "vendible": p.vendible,
            "primer_precio": p.primer_precio,
        })

    return JsonResponse(resultado, safe=False)

@login_required
def inventarioPorEmpresa(request):
    empresa = request.user.personal.empresa
    stockItems = StockItem.objects.filter(bom__producto__empresa=empresa).distinct()
   
    inventario_data = []
    for s in stockItems:
      #  stock_item = StockItem.objects.filter(nombre=p.nombre).first()
        total_stock = s.existencia if s else 0
        stock_id = s.id if s else None
        inventario_data.append({
           # "producto_id": p.id,
            "stock_item_id": stock_id,
            "nombre_producto": s.nombre,
            "total_stock": total_stock,
           # "tipo_producto": p.tipo_producto.tipo_producto if p.tipo_producto else None
        })

    return JsonResponse(inventario_data, safe=False)


from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def incrementarStock(request):
    stock_item_id = request.GET.get("id")
    cantidad = request.GET.get("cantidad")
    descripcion = request.GET.get("descripcion") or ""
    personal = request.user.personal
    corteCaja = CorteCaja.objects.filter(estatus = 1).first()

    try:
        with transaction.atomic():
            stock_item = StockItem.objects.select_for_update().get(id=stock_item_id)
            # Convertir cantidad a entero y validar
            cantidad = int(cantidad)
            if cantidad <= 0:
                return JsonResponse({"success": False, "error": "Cantidad inválida."})

            # Crear registro de movimiento (Entrada)
            MovimientoInventario.objects.create(
                stock_item=stock_item,
                tipo=1,  # 1 = Entrada
                cantidad=cantidad,
                descripcion=descripcion,
                personal = personal,
                corte_caja = corteCaja
            )
            # Actualizar existencia
            stock_item.existencia += cantidad
            stock_item.save()

        # Si todo fue bien, la transacción se confirma automáticamente
        return JsonResponse({
            "success": True,
            "stock_item_id": stock_item.id,
            "nombre": stock_item.nombre,
            "nueva_existencia": stock_item.existencia
        })
    
    except StockItem.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item no encontrado."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def disminuirStock(request):
    stock_item_id = request.GET.get("id")
    cantidad = request.GET.get("cantidad")
    descripcion = request.GET.get("descripcion") or ""
    personal = request.user.personal
    corteCaja = CorteCaja.objects.filter(estatus = 1).first()

    try:
        with transaction.atomic():
            stock_item = StockItem.objects.select_for_update().get(id=stock_item_id)
            # Convertir cantidad a entero y validar
            cantidad = int(cantidad)
            if cantidad <= 0:
                return JsonResponse({"success": False, "error": "Cantidad inválida."})

            # Crear registro de movimiento (Entrada)
            MovimientoInventario.objects.create(
                stock_item=stock_item,
                tipo=0,  # 0 = Salida
                cantidad=cantidad,
                descripcion=descripcion,
                personal = personal,
                corte_caja = corteCaja
            )
            # Actualizar existencia
            stock_item.existencia -= cantidad
            stock_item.save()

        # Si todo fue bien, la transacción se confirma automáticamente
        return JsonResponse({
            "success": True,
            "stock_item_id": stock_item.id,
            "nombre": stock_item.nombre,
            "nueva_existencia": stock_item.existencia
        })
    
    except StockItem.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item no encontrado."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def movimientoInventarioPorCorteCaja(request):
    # Obtener parámetro corte_caja desde GET
    corte_id = request.GET.get('corteCaja')
    if not corte_id:
        return JsonResponse({"detail": "Debe proporcionar ?corteCaja=<id>"}, status=400)

    # Filtrar ventas del corte de caja específico
    movimientos = MovimientoInventario.objects.filter(
        corte_caja_id=corte_id
    ).select_related('stock_item', 'personal').order_by('-id')[:10]
    movimientos_inventario_data = []
    from django.utils import timezone
    for m in movimientos:
        fecha_local = timezone.localtime(m.fecha) 
        movimientos_inventario_data.append({
            "id": m.id,
            "stock_item_id": m.stock_item.id,
            "stock_item_nombre": getattr(m.stock_item, "nombre", ""),
            "tipo": "Entrada" if m.tipo == 1 else "Salida",
            "cantidad": m.cantidad,
            "descripcion": m.descripcion or "",
            "personal": f"{m.personal.nombre} {m.personal.apellido_paterno} {m.personal.apellido_materno}",
            "fecha": fecha_local.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return JsonResponse(movimientos_inventario_data, safe=False)
