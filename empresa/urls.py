from empresa.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
#router.register('telefonos',TelefonoViewSet)


app_name = 'empresa'
urlpatterns = [
    path('api/v1/',include(router.urls)),
 #   path('empresas_autorizadas/', empresaAutorizadas, name='empresaAutorizadas'),
#    path('clientes_por_empresa/', clientesPorEmpresa, name='empresaAutorizadas'),   
]