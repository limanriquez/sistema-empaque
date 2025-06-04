# productos/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto, StockItem, BOM

@receiver(post_save, sender=Producto)
def crear_stockitem_y_bom(sender, instance, created, **kwargs):
    if created:
        # Solo para productos simples (no compuestos)
        if not instance.es_compuesto:
            # Crear StockItem con el mismo nombre si no existe
            stock_item, created_stock = StockItem.objects.get_or_create(
                nombre=instance.nombre,
                defaults={'existencia': 0}
            )
            
            # Crear BOM para relacionar producto con StockItem con cantidad=1 si no existe
            if not BOM.objects.filter(producto=instance, stock_item=stock_item).exists():
                BOM.objects.create(producto=instance, stock_item=stock_item, cantidad=1)
