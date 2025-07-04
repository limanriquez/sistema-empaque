from rest_framework import serializers
from django.utils.timezone import localtime
from servicios.models import *

class MensajeSerializer(serializers.ModelSerializer):
    fecha_hora = serializers.SerializerMethodField()

    class Meta:
        model = Mensaje
        fields = "__all__"

    def get_fecha_hora(self, obj):
        if obj.fecha_hora:
            fecha_local = localtime(obj.fecha_hora)
            return fecha_local.strftime('%Y-%m-%d %H:%M:%S')
        return None