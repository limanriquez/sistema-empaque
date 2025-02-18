from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.contrib import admin
import re


# Validación de correo electrónico
def validar_email(correo):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        raise ValidationError("El correo electrónico no tiene un formato válido.")
    return correo

class Empresa(models.Model):
    # Campos básicos de la empresa
    nombre = models.CharField(max_length=100)
    TIPO_EMPRESA = (
        (1, 'Matriz'),
        (2, 'Sucursal'),
    )
    tipo = models.IntegerField(choices=TIPO_EMPRESA)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, blank=True, null=True, validators=[RegexValidator(r'^[0-9]*$', 'Solo se permiten números.')])
    correo_electronico = models.EmailField(blank=True, null=True, validators=[validar_email])  # Validación personalizada para el correo
    fecha_creacion = models.DateField()  # Se puede seleccionar desde un calendario
    activo = models.BooleanField(default=True)
    rfc = models.CharField(max_length=13)
    logo = models.ImageField(
        upload_to='logos/', 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(allowed_extensions=['jpg'])]
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
