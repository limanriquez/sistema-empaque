from inventarios.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('productos',ProductosViewSet)
router.register('productoZonaNotificacion',ProductoZonaNotificacionViewSet)

app_name = 'inventario'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('productos_activos_empresas/', productosActivosEmpresas, name='productosActivosEmpresas'),
]