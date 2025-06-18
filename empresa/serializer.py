from rest_framework import serializers
from empresa.models import *

class TelefonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefonos
        fields = '__all__'

class ProductosAutorizadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductosAutorizados
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


        