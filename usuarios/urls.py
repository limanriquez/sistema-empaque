from usuarios.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
#router.register('catalogoElementoInventario',CatalogoElementoInventarioViewSet)
#router.register('categoria',CategoriaViewSet)
#router.register('departamento',DepartamentoViewSet)
#router.register('elementoInventario',ElementoInventarioViewSet)
#router.register('inventario',InventarioViewSet)

app_name = 'usuarios'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('usuario/', usuarios, name="usuarios"),
]