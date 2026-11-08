from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated

from .models import Calidad
from .serializer import CalidadSerializer, TamanoSerializer


# ==========================================================
# VIEWSET: CALIDADES
#
# Consulta el catálogo de calidades disponibles para los
# procesos de empaque.
#
# Únicamente devuelve registros activos.
# Es de solo lectura; no permite crear, modificar ni eliminar.
# ==========================================================

class CalidadViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = CalidadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Calidad.objects.filter(
            activo=True
        ).order_by('nombre')

# ==========================================================
# VIEWSET: TAMAÑOS
#
# Consulta el catálogo de tamaños disponibles para los
# procesos de empaque.
#
# Únicamente devuelve registros activos.
# Es de solo lectura; no permite crear, modificar ni eliminar.
# ==========================================================

class TamanoViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = TamanoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Tamano.objects.filter(
            activo=True
        ).order_by('nombre')