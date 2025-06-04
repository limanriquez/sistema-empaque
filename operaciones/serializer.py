from rest_framework import serializers
from empresa.models import *
from operaciones.models import *

class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        exclude = []
    