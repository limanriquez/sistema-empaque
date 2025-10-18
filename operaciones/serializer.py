from rest_framework import serializers
from empresa.models import *
from operaciones.models import *

class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
    
class NotificacionZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionZona
        fields = '__all__'

    
class VentasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ventas
        fields = '__all__'


class PagoVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoVenta
        fields = '__all__'

class CorteCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorteCaja
        fields = '__all__'
        
