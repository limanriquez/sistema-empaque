from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventarios.serializer import *
from rest_framework import viewsets
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string

class ProductosViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
