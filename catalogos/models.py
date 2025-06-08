from django.db import models
from catalogos.validators import validar_rfc, validar_telefono
from django.core.validators import MinLengthValidator

# Modelo de Almacen
class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.ForeignKey('empresa.Empresa', on_delete=models.PROTECT)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Almacen'
        verbose_name_plural = 'Almacenes'


# Modelo de Estante
class Estante(models.Model):
    nombre = models.CharField(max_length=100)
    id_almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT)  # Relación con Almacen
    status = models.BooleanField(default=True)  # Estatus del estante

    def __str__(self):
        return f"{self.nombre} - {self.id_almacen.nombre}"

    class Meta:
        verbose_name = "Estante"
        verbose_name_plural = "Estantes"


# Modelo de Seccion
class Seccion(models.Model):
    nombre = models.CharField(max_length=100)
    id_estante = models.ForeignKey(Estante, on_delete=models.PROTECT)  # Relación con Estante
    status = models.BooleanField(default=True)  # Estatus de la sección

    def __str__(self):
        return f"{self.nombre} - {self.id_estante.nombre}"

    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
#Gestiona los puestos de la empresa(Ventas, Instalador, Seguros, Cristales sueltos)
class Puesto(models.Model):
    nombre_puesto = models.CharField(max_length=30, blank=False)
    descripcion = models.CharField(max_length=200,  blank=False)
    estatus = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_puesto

#Este modelo se encarga de clasificar los tipos de productos de la empresa por ejemplo, cristales, pegamentos, piezas de colición, molduras etc.
class TipoProducto(models.Model):
    tipo_producto = models.CharField(max_length=30, unique=True)
    status = models.BooleanField(default=True)  # True si está activo, False si está inactivo

    class Meta:
        verbose_name = "Tipo de producto"
        verbose_name_plural = "Tipos de productos"
        ordering = ['tipo_producto']  # Corregido: minúscula y coincide con el atributo

    def __str__(self):
        return self.tipo_producto  # Mostrar el texto del campo

# Este modelo indica los tipos de precio que pueden manejar un producto: Público, Mayoreo, Distribuidor, Descuento, Especial, etc.
class TipoPrecio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=True)  # True si está activo, False si está inactivo

    class Meta:
        verbose_name = "Tipo de precio"
        verbose_name_plural = "Tipos de precios"
        ordering = ['nombre']  # Orden alfabético por nombre

    def __str__(self):
        return self.nombre  # Muestra el nombre del tipo de precio

#Almacena la zona en donde se realizara las notificaciones, por ejemplo parrilla, plancha, refrigeradores, etc.
class ZonaNotificacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
            verbose_name = "Zona de notificación"
            verbose_name_plural = "Zonas de notificación"
            ordering = ['nombre']  # ordena alfabéticamente por nombre

    def __str__(self):
        return self.nombre
