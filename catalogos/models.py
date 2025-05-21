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

#Gestiona la marca delvehiculo (Nissan, Ford)
class Marca(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

#Gestiona el modelo del vehiculo (Altima, F150)
class Modelo(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    marca = models.ForeignKey('Marca', on_delete=models.PROTECT, related_name='modelos')

    class Meta:
        verbose_name = "Modelo"
        verbose_name_plural = "Modelos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.marca.nombre} {self.nombre}"

#Tipos de servicio que maneja la empresa, cristales sueltos, seguros, particulares 
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
#Modelo que se encarga de gestionar los seguros con los que la empresa realiza transacciones, banamex, qualitas, etc
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

#Modelo gestiona como el cliente nos localiza, facebook, telefono watss app, instagram etc. 
class TipoContacto(models.Model):
    tipo = models.CharField(
        max_length=100,
        null=False,  # requerido a nivel de base de datos
        blank=False,  # requerido en formularios
        validators=[MinLengthValidator(1)],  # evita strings vacíos o solo espacios
        verbose_name="Tipo de contacto"
    )
    status = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Tipo de contacto"
        verbose_name_plural = "Tipos de contacto"

    def __str__(self):
        return self.tipo

#Este modelo se encarga de clasificar los tipos de cristales de los vehiculos por ejemplo, parabrisas, luneta, quemacocos etc.
class TipoCristal(models.Model):
    tipo_cristal = models.CharField(max_length=30, unique=True)
    status = models.BooleanField(default=True)  # True si está activo, False si está inactivo

    class Meta:
        verbose_name = "Tipo de Cristal"
        verbose_name_plural = "Tipos de Cristal"
        ordering = ['tipo_cristal']  # Corregido: minúscula y coincide con el atributo

    def __str__(self):
        return self.tipo_cristal  # Mostrar el texto del campo

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