from servicios.views import *
from django.urls import path

app_name = 'servicios'

urlpatterns = [
    path('loadImage/', loadImage, name="loadImage"),
    path('subir-imagen/', subirImagenFtp, name='subir_imagen'),
    path('guestBook/', guestBook, name='guestBook'),
    # Rutas comentadas se pueden habilitar cuando estén listas o separarlas en otro archivo
]