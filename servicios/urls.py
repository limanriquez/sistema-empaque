from servicios.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('mensaje',MensajeViewSet)

app_name = 'servicios'

urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('loadImage/', loadImage, name="loadImage"),
    path('subir-imagen/', subirImagenFtp, name='subir_imagen'),
    path('guestBook/', guestBook, name='guestBook'),
    # Rutas comentadas se pueden habilitar cuando estén listas o separarlas en otro archivo
]