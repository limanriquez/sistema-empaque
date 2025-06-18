from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventarios.serializer import *
from rest_framework import viewsets
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery

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
        empresa__in=ids_empresas
    ).select_related('empresa').annotate(
        primer_precio=Subquery(precio_subquery)
    )  # Aquí agregas la anotación

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