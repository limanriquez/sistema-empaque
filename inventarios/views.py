from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventarios.serializer import *
from rest_framework import viewsets
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import action
from rest_framework.response import Response

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
