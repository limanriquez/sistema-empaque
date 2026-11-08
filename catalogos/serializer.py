from rest_framework import serializers
from .models import Calidad, Tamano


class CalidadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Calidad
        fields = [
            'id',
            'nombre',
            'descripcion',
            'activo',
        ]
    
class TamanoSerializer(serializers.ModelSerializer):

    class Meta:
            model = Tamano
            fields = [
                'id',
                'nombre',
                'descripcion',
                'activo',
            ]