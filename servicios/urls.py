from django.urls import path, include
from rest_framework.routers import DefaultRouter
from servicios.views import MensajeViewSet, loadImage, subirImagenFtp, guestBook

router = DefaultRouter()
router.register('mensaje', MensajeViewSet)

app_name = 'servicios'

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('loadImage/', loadImage, name='loadImage'),
    path('subir-imagen/', subirImagenFtp, name='subir_imagen'),
    path('guestBook/', guestBook, name='guestBook'),
]
