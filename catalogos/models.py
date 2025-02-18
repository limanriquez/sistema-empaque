from django.db import models

class Puesto(models.Model):
    nombre_puesto = models.CharField(max_length=30, blank=False)
    descripcion = models.CharField(max_length=200,  blank=False)
    estatus = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_puesto

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
    
    # Campos requeridos
    placa = models.CharField(max_length=10, unique=True)  # Placa única
    vin = models.CharField(max_length=17, unique=True)  # VIN de 17 caracteres
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField()
    color = models.CharField(max_length=20)
    tipo_vehiculo = models.CharField(max_length=10, choices=TIPO_VEHICULO)
    estatus = models.BooleanField(default=True)  # True si está activo, False si está inactivo
    
    def __str__(self):
        return f'{self.marca} {self.modelo} - {self.placa} ({self.tipo_vehiculo})'

    class Meta:
        verbose_name = 'Vehículo Flotilla'
        verbose_name_plural = 'Vehículos Flotilla'