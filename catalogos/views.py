from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Puesto
from .serializer import PuestoSerializer

class PuestoViewSet(viewsets.ModelViewSet):
    queryset = Puesto.objects.all()
    serializer_class = PuestoSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(estatus=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)


        