from rest_framework import serializers
from .models import Calidad


class CalidadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Calidad
        fields = [
            'id',
            'nombre',
            'descripcion',
            'activo',
        ]