from rest_framework import serializers
from catalogos.models import *

class PuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puesto
        fields = "__all__"

class ZonaNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaNotificacion
        fields = "__all__"

class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProducto
        fields = "__all__"

class LugarEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LugarEntrega
        fields = "__all__"