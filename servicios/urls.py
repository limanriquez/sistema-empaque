from servicios.views import *
from django.urls import path
from .views import get_csrf_cookie

app_name = 'servicios'

urlpatterns = [
    path('loadImage/', loadImage, name="loadImage"),
    path('subir-imagen/', subirImagenFtp, name='subir_imagen'),
    path('get-csrf-cookie/', get_csrf_cookie, name='get-csrf-cookie'),  # agregar name para consistencia
    # Rutas comentadas se pueden habilitar cuando estén listas o separarlas en otro archivo
]