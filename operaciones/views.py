# Librerías estándar de Python
from decimal import Decimal, InvalidOperation
from weasyprint import HTML

# Librerías de Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime
from pytz import timezone as pytz_timezone  # opcional si quieres zona específica
from django.template.loader import render_to_string


# Django REST Framework
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from authentication.decoradores import require_personal

from django.db.models import Sum, Count, F



@login_required()
@require_personal
def reporte_top_cinco(request):
	return render(request, 'operaciones/reporte_top_cinco.html',{
			'title':"Reporte"})
