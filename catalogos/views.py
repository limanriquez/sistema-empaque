from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Puesto, ZonaNotificacion, TipoProducto
from .serializer import PuestoSerializer, ZonaNotificacionSerializer, TipoProductoSerializer

class PuestoViewSet(viewsets.ModelViewSet):
    queryset = Puesto.objects.all()
    serializer_class = PuestoSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(estatus=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

class ZonaNotificacionViewSet(viewsets.ModelViewSet):
    queryset = ZonaNotificacion.objects.all()
    serializer_class = ZonaNotificacionSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(activo=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

class TipoProductoViewSet(viewsets.ModelViewSet):
    queryset = TipoProducto.objects.all()
    serializer_class = TipoProductoSerializer

        