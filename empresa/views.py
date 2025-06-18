from empresa.serializer import TelefonoSerializer, ProductosAutorizadosSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .models import Telefonos, ProductosAutorizados
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse

class TelefonoViewSet(viewsets.ModelViewSet):
    queryset = Telefonos.objects.all()
    serializer_class = TelefonoSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(status=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

class ProductosAutorizadosViewSet(viewsets.ModelViewSet):
    queryset = ProductosAutorizados.objects.all()
    serializer_class = ProductosAutorizadosSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        activos = self.queryset.filter(status=True)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)


@login_required
def empresaAutorizadas(request):
    empresa_id = request.GET.get('empresa')
    if not empresa_id:
        return JsonResponse({"error": "La empresa es obligatoria"}, status=400)

    try:
        empresa_id = int(empresa_id)
    except ValueError:
        return JsonResponse({"error": "El ID de la empresa no es válido"}, status=400)

    ids_autorizadas = ProductosAutorizados.objects.filter(
        empresa_lider=empresa_id,
        activo=True
    ).values_list('empresa_autorizada_id', flat=True)

    todos_ids = [empresa_id] + list(ids_autorizadas)
    resultado = '-'.join(str(i) for i in todos_ids)

    return JsonResponse(resultado, safe=False)