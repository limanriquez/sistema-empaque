from inventarios.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('catalogoElementoInventario',CatalogoElementoInventarioViewSet)
router.register('categoria',CategoriaViewSet)
router.register('departamento',DepartamentoViewSet)
router.register('elementoInventario',ElementoInventarioViewSet)
router.register('inventario',InventarioViewSet)

app_name = 'inventario'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('inventario/', inventario, name="inventario"),
    path('inventarioVue/', inventarioVue, name="inventarioVue"),
    path('inventarioExistente/', inventarioExistente, name="inventarioExistente"),
    path('elementosInventario/<int:IdInventario>', elementosInventario, name="elementosInventario"),
    path('export/<int:IdInventario>', export_pdf, name="export-pdf" )
]