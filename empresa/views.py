from empresa.serializer import TelefonoSerializer, ProductosAutorizadosSerializer, ClienteSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .models import Telefonos, ProductosAutorizados, Cliente
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

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

@login_required
def clientesPorEmpresa(request):
    empresa_id = request.GET.get('empresa')
    estatus = request.GET.get('estatus')

    if not empresa_id:
        return JsonResponse({"error": "La empresa es obligatoria"}, status=400)

    try:
        empresa_id = int(empresa_id)
    except ValueError:
        return JsonResponse({"error": "El ID de la empresa no es válido"}, status=400)

    estatus_bool = estatus.lower() in ['true', '1', 'yes'] if estatus else True

    clientes = Cliente.objects.filter(empresa=empresa_id, estatus=estatus_bool)

    clientes_data = []
    for c in clientes:
        clientes_data.append({
            "id": c.id,
            "nombre": c.nombre,
            "apellido_paterno": c.apellido_paterno,
            "apellido_materno": c.apellido_materno,
            "full_name": f"{c.nombre} {c.apellido_paterno or ''} {c.apellido_materno or ''}".strip(),
            "telefono": c.telefono,
            "telefono_adicional": c.telefono_adicional,
            "correo_electronico": c.correo_electronico,
            "direccion": c.direccion,
            "rfc": c.rfc,
            "tipo_persona": c.tipo_persona,
            "estatus": c.estatus,
            "fecha_registro": c.fecha_registro.isoformat() if c.fecha_registro else None,
            "empresa_id": c.empresa_id,
        })

    return JsonResponse(clientes_data, safe=False)

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