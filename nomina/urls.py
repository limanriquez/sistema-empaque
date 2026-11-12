from django.urls import path, include
from rest_framework.routers import DefaultRouter

from nomina.views import nomina, iniciar_nomina

router = DefaultRouter()

app_name = 'nomina'

urlpatterns = [
    path(
        'nomina/',
        nomina,
        name='nomina',
    ),

    path(
        'api/',
        include(router.urls),
    ),

    path(
        'iniciar_nomina/',
        iniciar_nomina,
        name='iniciar_nomina',
    ),
]