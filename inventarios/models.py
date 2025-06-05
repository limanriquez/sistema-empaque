from django.db import models
from catalogos.models import TipoProducto, TipoPrecio, Seccion
from empresa.models import Empresa, Proveedor


class Producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Código de barras o SKU
    descripcion = models.TextField(blank=True, null=True)
    tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT) #Relacionado a la empresa a la cual pertenece este producto
    seccion = models.ForeignKey(Seccion, on_delete=models.PROTECT, blank=True, null=True)
    es_compuesto = models.BooleanField(default=False)
    vendible = models.BooleanField(default=True)  # Si se usa directamente en ventas o no
    activo = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre

class PrecioProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='precios')
    tipo_precio = models.ForeignKey(TipoPrecio, on_delete=models.PROTECT)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Dos decimales, max 99999999.99 aprox
    activo = models.BooleanField(default=True)  # Opcional para desactivar precios sin eliminar

    class Meta:
        unique_together = ('producto', 'tipo_precio')  # Para evitar duplicados por combinación

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo_precio.nombre}: ${self.precio}"


class StockItem(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    existencia = models.PositiveIntegerField(default=0)  # No puede ser negativo
    proveedores = models.ManyToManyField(Proveedor, related_name='stock_items', blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.existencia})"

# Bill of Materials (en español: Lista de Materiales). Son los insumos para armar un producto de venta.
class BOM(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='componentes')
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()

    class Meta:
        unique_together = ('producto', 'stock_item')

    def __str__(self):
        return f"{self.cantidad} x {self.stock_item.nombre} para {self.producto.nombre}"