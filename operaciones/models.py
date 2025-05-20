from django.db import models
from empresa.models import Cliente, Personal, Telefonos, Empresa
from catalogos.models import TipoContacto,Marca, Modelo

class Cotizacion(models.Model):
    STATUS = (
        (1, 'Creada'),
        (2, 'Seguimiento'),
        (3, 'Cancelada'),
        (4, 'Finalizada'),
    ) 
    fecha_creacion = models.DateTimeField(auto_now_add=True) #Fecha en que se esta creando la cotización es automaticamente
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT) #Relacionado al cliente que solicita la cotización si el cliente es anonimo se pondra el 1 que es cleinte General
    personal = models.ForeignKey(Personal, on_delete=models.PROTECT) #Relacionado a la persona que se encuentra loogeada
    telefono = models.ForeignKey(Telefonos, on_delete=models.PROTECT) #Realacionado al telefono de la empresa por el cual surgio el contacto del cliente
    tipo_contacto = models.ForeignKey(TipoContacto, on_delete=models.PROTECT) #Relacionado al catalogo, informa como nos conoce el cliente
    fecha_expiracion = models.DateTimeField(null=True, blank=True) #Se puede almacenar información que informe hasta cuando esta vigente la cotización.
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT) #Relacionado a la empresa a la cual pertenece esta cotización
    venta_realizada = models.BooleanField(default=False) # Indica si la cotización se concreto en venta realizada
    status = models.IntegerField(choices=STATUS, blank=False, default=1) #Indica la etapa en la que esta la cotización, los datos se encuentran el la tupla definida al inicio de este modelo. 

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
    
    def __str__(self):
        return f'Cotización {self.id} - Cliente: {self.cliente}'

class DesgloseCotizacion(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.PROTECT)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='desgloses_marca')
    modelo = models.ForeignKey(Modelo, on_delete=models.PROTECT, related_name='desgloses_modelo')
    anio = models.IntegerField()
    observaciones = models.TextField(blank=True, null=True)
    nags = models.CharField(max_length=10)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Desglose Cotizacion"
        verbose_name_plural = "Desglose Cotizaciones"
    
    def __str__(self):
        return f'{self.marca} {self.modelo} - Año {self.anio}'