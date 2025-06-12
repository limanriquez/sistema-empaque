from rest_framework import serializers
from catalogos.models import *

class PuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puesto
        exclude = []

class ZonaNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaNotificacion
        exclude = []

class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProducto
        exclude = []
        