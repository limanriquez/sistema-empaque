
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from operaciones.views import (
    reporte_top_cinco,
    obtener_empleado_estacion,
    obtener_producto_empaque,
    obtener_tarimas_abiertas,
    hola_mundo_vue,
    hola_mundo_api,
    hola_mundo_post_api,
    captura_caja_vue,
)

router = DefaultRouter()

app_name = 'operaciones'

urlpatterns = [
    path(
        'reporte_top_cinco/',
        reporte_top_cinco,
        name='reporte_top_cinco',
    ),
    path(
        'obtener_empleado_estacion/',
        obtener_empleado_estacion,
        name='obtener_empleado_estacion',
    ),
    path(
        'obtener_producto_empaque/',
        obtener_producto_empaque,
        name='obtener_producto_empaque',
    ),
    path(
        'obtener_tarimas_abiertas/',
        obtener_tarimas_abiertas,
        name='obtener_tarimas_abiertas',
    ),
    path(
        'hola-mundo-vue/',
        hola_mundo_vue,
        name='hola_mundo_vue',
    ),
    path(
        'hola_mundo_api/',
        hola_mundo_api,
        name='hola_mundo_api',
    ),
    path(
        'hola_mundo_post_api/',
        hola_mundo_post_api,
        name='hola_mundo_post_api',
    ),

    path(
        'captura-caja-vue/',
        captura_caja_vue,
        name='captura_caja_vue',
    ),
]
