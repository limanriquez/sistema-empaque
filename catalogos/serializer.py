from rest_framework import serializers
from catalogos.models import *

class PuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puesto
        exclude = []

class TipoContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoContacto
        exclude = []

class ModeloSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    class Meta:
        model = Modelo
        exclude = []