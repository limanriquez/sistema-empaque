from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Puesto, TipoContacto, Modelo, TipoCristal
from .serializer import PuestoSerializer, TipoContactoSerializer, ModeloSerializer, TipoCristalSerializer

class PuestoViewSet(viewsets.ModelViewSet):
    queryset = Puesto.objects.all()
    serializer_class = PuestoSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(estatus=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

class TipoContactoViewSet(viewsets.ModelViewSet):
    queryset = TipoContacto.objects.all()
    serializer_class = TipoContactoSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(status=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

class ModeloViewSet(viewsets.ModelViewSet):
    queryset = Modelo.objects.all().select_related('marca')
    serializer_class = ModeloSerializer

    @action(detail=False, methods=['get'])
    def modelos_con_marca(self, request):
        modelos = self.get_queryset()
        serializer = self.get_serializer(modelos, many=True)
        return Response(serializer.data)

class TipoCristalViewSet(viewsets.ModelViewSet):
    queryset = TipoCristal.objects.all()
    serializer_class = TipoCristalSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(status=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

        