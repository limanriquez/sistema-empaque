from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from operaciones.serializer import *
from rest_framework import viewsets
from inventario.permissions import IsAdminOrReadOnly

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClientesSerializer
    permission_classes = [IsAdminOrReadOnly]  # Aplica el permiso personalizado
   
# Create your views here.
@login_required()
def clientes(request):
	return render(request, 'operaciones/clientes.html',{
			'title':"Clientes"})

@login_required()
def cotizaciones(request):
	return render(request, 'operaciones/cotizaciones.html',{
			'title':"Cotizaciones"})

@login_required
def existeTelefono(request, telefono):
    # Verificar si el teléfono no es vacío
    if not telefono:
        return JsonResponse({"error": "El teléfono es requerido"}, status=400)
    
    # Buscar solo el teléfono en la base de datos para hacer la consulta más ligera
    existe = Cliente.objects.filter(telefono=telefono).values('telefono').exists()

    # Retornar la respuesta en formato JSON con el estado de existencia del teléfono
    return JsonResponse({"Existe": existe})
	