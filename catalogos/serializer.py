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