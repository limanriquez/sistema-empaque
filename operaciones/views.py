from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse
from operaciones.serializer import *
from rest_framework import viewsets
from inventario.permissions import IsAdminOrReadOnly
from authentication.decoradores import require_personal

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClientesSerializer
   # permission_classes = [IsAdminOrReadOnly]  # Aplica el permiso personalizado


# Create your views here.
@login_required()
@require_personal
def clientes(request):
	return render(request, 'operaciones/clientes.html',{
			'title':"Clientes"})
   

@login_required
def existeTelefono(request, telefono):
    # Verificar si el teléfono no es vacío
    if not telefono:
        return JsonResponse({"error": "El teléfono es requerido"}, status=400)
    
    # Buscar solo el teléfono en la base de datos para hacer la consulta más ligera
    existe = Cliente.objects.filter(telefono=telefono).values('telefono').exists()

    # Retornar la respuesta en formato JSON con el estado de existencia del teléfono
    return JsonResponse({"Existe": existe})
	