from rest_framework import serializers
from empresa.models import *

class TelefonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefonos
        exclude = []
