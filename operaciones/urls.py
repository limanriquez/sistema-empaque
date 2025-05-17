from operaciones.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

#router = DefaultRouter()
#router.register('catalogoElementoInventario',CatalogoElementoInventarioViewSet)
router = DefaultRouter()
router.register('clientes',ClientesViewSet)

app_name = 'operaciones'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('clientes/', clientes, name="clientes"),
    path('cotizaciones/', cotizaciones, name="cotizaciones"),
    path('existeTelefono/<str:telefono>/', existeTelefono, name="existeTelefono"),
]