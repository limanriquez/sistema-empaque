from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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