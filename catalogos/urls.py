from inventarios.views import *
from catalogos.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('puesto',PuestoViewSet)
router.register('tipoContacto',TipoContactoViewSet)
router.register('modelo',ModeloViewSet)

app_name = 'catalogos'
urlpatterns = [
    path('api/v1/',include(router.urls)),
]