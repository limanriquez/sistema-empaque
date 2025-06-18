from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse
from operaciones.serializer import *
from rest_framework import viewsets
from inventario.permissions import IsAdminOrReadOnly
from authentication.decoradores import require_personal
from rest_framework.decorators import action
from django.urls import reverse

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClientesSerializer

    @action(detail=False, methods=['get'])
    def activos_por_empresa(self, request):
        empresa_id = request.query_params.get('empresa')
        if not empresa_id:
            return Response({"error": "Parámetro 'empresa' es requerido."}, status=400)

        queryset = self.queryset.filter(estatus=True, empresa_id=empresa_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NotificacionZonaSerializerViewSet(viewsets.ModelViewSet):
    queryset = NotificacionZona.objects.all()
    serializer_class = NotificacionZonaSerializer
   
    @action(detail=False, methods=['get'])
    def activos(self, request):
        queryset = self.queryset.filter(activo=True)

        zona_id = request.query_params.get('zona_id')
        if zona_id:
            queryset = queryset.filter(zona_id=zona_id)

        venta_id = request.query_params.get('venta_id')
        if venta_id:
            queryset = queryset.filter(venta_id=venta_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
   # permission_classes = [IsAdminOrReadOnly]  # Aplica el permiso personalizado


# Create your views here.
@login_required()
@require_personal
def clientes(request):
	return render(request, 'operaciones/clientes.html',{
			'title':"Clientes"})
   
@login_required()
@require_personal
def punto_de_venta(request):
    user = request.user.personal
    empresa = user.empresa
    # Verificar si el usuario tiene un corte abierto
    corte_abierto = CorteCaja.objects.filter(
        estatus = 1,
        empresa = empresa.id
    ).exists()
    if not corte_abierto:
        messages.warning(request, "No tienes un corte de caja abierto. Ábrelo en el administrador.")
        # Redirige directamente a la vista de agregar CorteCaja en el admin
        return redirect(reverse('admin:%s_%s_add' % (CorteCaja._meta.app_label, CorteCaja._meta.model_name)))

    return render(request, 'operaciones/punto_venta.html', {
        'title': "Punto de venta",
        'empresa': empresa,
        'nombre_personal': f"{user.nombre} {user.apellido_paterno} {user.apellido_materno}"
    })

@login_required
def existeTelefono(request, telefono):
    # Verificar si el teléfono no es vacío
    if not telefono:
        return JsonResponse({"error": "El teléfono es requerido"}, status=400)
    
    # Buscar solo el teléfono en la base de datos para hacer la consulta más ligera
    existe = Cliente.objects.filter(telefono=telefono).values('telefono').exists()

    # Retornar la respuesta en formato JSON con el estado de existencia del teléfono
    return JsonResponse({"Existe": existe})
	