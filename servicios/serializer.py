from rest_framework import serializers
from servicios.models import *

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = "__all__"