from inventarios.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('productos',ProductosViewSet)

app_name = 'inventario'
urlpatterns = [
    path('api/v1/',include(router.urls)),
]