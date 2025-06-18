from operaciones.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
#from django.contrib.auth import views as auth_views

#router = DefaultRouter()
#router.register('catalogoElementoInventario',CatalogoElementoInventarioViewSet)
router = DefaultRouter()
router.register('clientes',ClientesViewSet)

app_name = 'operaciones'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('clientes/', clientes, name="clientes"),
    path('punto_de_venta/', punto_de_venta, name="punto_de_venta"),
    path('existeTelefono/<str:telefono>/', existeTelefono, name="existeTelefono"),
    path('ventas_abiertas_corte_empresas/', ventasAbiertasCorteEmpresas, name='ventasAbiertasCorteEmpresas'),
  #  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]