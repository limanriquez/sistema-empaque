from django.db import models
from catalogos.validators import validar_rfc, validar_telefono

# Modelo de Almacen
class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.ForeignKey('empresa.Empresa', on_delete=models.CASCADE)  # Corregido
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Almacen'
        verbose_name_plural = 'Almacenes'


# Modelo de Estante
class Estante(models.Model):
    nombre = models.CharField(max_length=100)
    id_almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)  # Relación con Almacen
    status = models.BooleanField(default=True)  # Estatus del estante

    def __str__(self):
        return f"{self.nombre} - {self.id_almacen.nombre}"

    class Meta:
        verbose_name = "Estante"
        verbose_name_plural = "Estantes"


# Modelo de Seccion
class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    id_estante = models.ForeignKey(Estante, on_delete=models.CASCADE)  # Relación con Estante
    status = models.BooleanField(default=True)  # Estatus de la sección

    def __str__(self):
        return f"{self.nombre} - {self.id_estante.nombre}"

    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"

class Puesto(models.Model):
    nombre_puesto = models.CharField(max_length=30, blank=False)
    descripcion = models.CharField(max_length=200,  blank=False)
    estatus = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_puesto

class Marca(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Modelo(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    marca = models.ForeignKey('Marca', on_delete=models.PROTECT, related_name='modelos')

    class Meta:
        verbose_name = "Modelo"
        verbose_name_plural = "Modelos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"

class Servicios(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    descripcion = models.CharField(max_length=100, unique=True)
    seguimiento_bitacora = models.BooleanField(default=True)
    estatus = models.BooleanField(default=True)  # True si está activo, False si está inactivo

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Seguros(models.Model):
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=13, unique=True, validators=[validar_rfc])  # RFC con validación
    direccion = models.TextField()  # Cambiado a TextField para direcciones más largas
    telefono = models.CharField(max_length=10, validators=[validar_telefono])
    telefono_adicional = models.CharField(max_length=10, blank=True, null=True, validators=[validar_telefono])  # Teléfono adicional opcional
    correo_electronico = models.EmailField(max_length=254)  # Correo electrónico
    contacto = models.CharField(max_length=200)  # Podría considerarse TextField si es más largo
    estatus = models.BooleanField(default=True)  # True si está activo, False si está inactivo

    class Meta:
        verbose_name = "Seguro"
        verbose_name_plural = "Seguros"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

