from xml.parsers.expat import model
from rest_framework import serializers
from inventarios.models import *

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        exclude = []

class ProductoZonaNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoZonaNotificacion
        exclude = []

