from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.contrib import admin
from catalogos.validators import validar_rfc, validar_telefono, validar_curp, validar_telefono_mx_usa, validar_correo
from django.core.validators import EmailValidator
from catalogos.models import Puesto, Marca, Modelo
from empresa.validators import validar_unicidad_cliente
from users.models import User
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
    estatus = models.BooleanField(default=True)  # Si está activo o no
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
        
class Cliente(models.Model):
    TIPO_PERSONA = (
        (1, 'Física'),
        (2, 'Moral'),
    )
    
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(
        max_length=10, 
        blank=True,  # Permitimos que esté vacío en formularios
        null=True,  # Permitimos valores nulos en la base de datos
        validators=[validar_telefono, validar_unicidad_cliente]  # Validación de teléfono
    )  # Teléfono (opcional)
    
    telefono_adicional = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        validators=[validar_telefono]  # Validación de teléfono adicional
    )
    correo_electronico = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    rfc = models.CharField(max_length=13, blank=True, null=True)  # RFC opcional al principio
    tipo_persona = models.IntegerField(choices=TIPO_PERSONA, blank=True, null=True)
    estatus = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"



class Personal(models.Model):
    # Campos básicos del empleado
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    curp = models.CharField(max_length=18, unique=True, validators=[validar_curp])  # Validación para CURP
    rfc = models.CharField(max_length=13, unique=True, validators=[validar_rfc])  # RFC con validación
    puesto = models.ForeignKey(Puesto, on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=10, validators=[RegexValidator(r'^[0-9]{10}$', 'Teléfono no válido')])  # Validación teléfono
    telefono_emergencia = models.CharField(max_length=10, validators=[RegexValidator(r'^[0-9]{10}$', 'Teléfono de emergencia no válido')])
    contacto_emergencia = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    fecha_ingreso = models.DateField()
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    estatus = models.BooleanField(default=True)  # Si está activo o no
    # Relación con el modelo User (usuario)
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    class Meta:
        verbose_name = "Personal"
        verbose_name_plural = "Personal"
        ordering = ['apellido_paterno', 'apellido_materno', 'nombre']


class Proveedor(models.Model):
    TIPO_PERSONA = (
        (1, 'Física'),
        (2, 'Moral'),
    )

    nombre = models.CharField(max_length=150)  # Puede ser nombre o razón social
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    tipo_persona = models.IntegerField(choices=TIPO_PERSONA, blank=True, null=True)
    rfc = models.CharField(max_length=13, unique=True, validators=[validar_rfc])
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=14, validators=[validar_telefono_mx_usa])
    telefono_alternativo = models.CharField(max_length=14,blank=True,null=True, validators=[validar_telefono_mx_usa])
    correo_electronico = models.EmailField(max_length=254,validators=[EmailValidator()])
    contacto_principal = models.CharField(max_length=200)
    estatus = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

class VehiculoFlotilla(models.Model):
    TIPO_VEHICULO = (
        ('sedan', 'Sedán'),
        ('suv', 'SUV'),
        ('pickup', 'Pickup'),
        ('van', 'Van'),
        ('camion', 'Camión'),
        ('camioneta', 'Camioneta'),
        ('furgoneta', 'Furgoneta'),
        # Puedes añadir más tipos de vehículos si lo deseas
    )
    
    # Relación con las tablas de Marca y Modelo
    marca = models.ForeignKey('catalogos.Marca', on_delete=models.PROTECT)
    modelo = models.ForeignKey('catalogos.Modelo', on_delete=models.PROTECT)
    
    # Campos adicionales
    placa = models.CharField(max_length=10, unique=True)  # Placa única
    vin = models.CharField(max_length=20, unique=True)  # VIN de 17 caracteres
    año = models.IntegerField()
    color = models.CharField(max_length=20)
    tipo_vehiculo = models.CharField(max_length=10, choices=TIPO_VEHICULO)
    estatus = models.BooleanField(default=True)  # True si está activo, False si está inactivo
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    def __str__(self):
        return f'{self.marca.nombre} {self.modelo.nombre} - {self.placa} ({self.tipo_vehiculo})'

    class Meta:
        verbose_name = 'Vehículo Flotilla'
        verbose_name_plural = 'Vehículos Flotilla'


class Telefonos(models.Model):
    numero = models.CharField(max_length=15)
    empresa = models.ForeignKey('empresa.Empresa', on_delete=models.PROTECT)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Teléfono'
        verbose_name_plural = 'Teléfonos'

    def clean(self):
        super().clean()
        pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not pattern.match(self.numero):
            raise ValidationError({
                'numero': "Número inválido. Debe tener entre 9 y 15 dígitos y puede comenzar con '+'."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
