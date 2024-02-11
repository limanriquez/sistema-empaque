from xml.parsers.expat import model
from rest_framework import serializers
from inventarios.models import *


class CatalogoElementoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoElementoInventario
        exclude = []

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        exclude = []

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        exclude = []
        
class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        exclude = []

class ElementoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementoInventario
        exclude = []
        


        