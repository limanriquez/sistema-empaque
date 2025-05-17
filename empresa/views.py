from empresa.serializer import TelefonoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .models import Telefonos
from rest_framework import viewsets


class TelefonoViewSet(viewsets.ModelViewSet):
    queryset = Telefonos.objects.all()
    serializer_class = TelefonoSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(status=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)
