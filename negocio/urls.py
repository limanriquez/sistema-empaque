from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'negocio'

urlpatterns = [
    path('', include(router.urls)),
]