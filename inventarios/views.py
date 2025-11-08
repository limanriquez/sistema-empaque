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
    productos = Producto.objects.filter(empresa=empresa, activo=True).select_related('tipo_producto')

    inventario_data = []

    for p in productos:
        stock_item = StockItem.objects.filter(nombre=p.nombre).first()
        total_stock = stock_item.existencia if stock_item else 0
        stock_id = stock_item.id if stock_item else None

        inventario_data.append({
            "producto_id": p.id,
            "stock_item_id": stock_id,
            "nombre_producto": p.nombre,
            "total_stock": total_stock,
            "tipo_producto": p.tipo_producto.tipo_producto if p.tipo_producto else None
        })

    return JsonResponse(inventario_data, safe=False)


@login_required
def incrementarStock(request):
    stock_item_id = request.POST.get("id")
    cantidad = request.POST.get("cantidad")

    try:
        stock_item = StockItem.objects.get(id=stock_item_id)
        stock_item.existencia += int(cantidad)
        stock_item.save()
        return JsonResponse({
            "success": True,
            "stock_item_id": stock_item.id,
            "nombre": stock_item.nombre,
            "nueva_existencia": stock_item.existencia
        })
    except:
        return JsonResponse({"success": False})