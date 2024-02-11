from django.db import models

class Categoria(models.Model):
    Id = models.AutoField(primary_key=True)
    Categoria = models.CharField(max_length=300,verbose_name="Categoria")
    Descripcion = models.CharField(max_length=300,verbose_name="Descripción")
    Estado = models.BooleanField(default=True)

    def __str__(self):
        return self.Categoria
        
class Departamento(models.Model):
    Id = models.AutoField(primary_key=True)
    Descripcion = models.CharField(max_length=300,null=True,blank=True,verbose_name="Descripción")
    Estado = models.BooleanField(default=True)
    def __str__(self):
        return self.Descripcion

class Inventario(models.Model):
    Id = models.AutoField(primary_key=True)
    #verbose_name="Apellido Paterno" Sirve para mostrar de esa manera el campo en el panel de administracion
    NoInventario = models.CharField(max_length=300,verbose_name="Número de inventario")
    Descripcion = models.CharField(max_length=300,null=True,blank=True,verbose_name="Descripción")
    Observaciones = models.CharField(max_length=300,null=True,blank=True,verbose_name="Observaciones")
    Ubicacion = models.CharField(max_length=300, verbose_name="Ubicación")
    FechaAdquisicion = models.DateField(null=True,blank=True,verbose_name="Fecha de adquisición")
    Precio = models.DecimalField(max_digits=12,null=True,blank=True,decimal_places=4)
    Categoria = models.ForeignKey(Categoria,related_name = 'inventario',null=True,blank=True,on_delete=models.CASCADE)
    Departamento = models.ForeignKey(Departamento,related_name = 'inventario',null=True,blank=True,on_delete=models.CASCADE)
    URL = models.CharField(max_length=300,null=True,blank=True,verbose_name="URL")

    def __str__(self):
        return self.NoInventario

class CatalogoElementoInventario(models.Model):
    Id = models.AutoField(primary_key=True)
    Descripcion = models.CharField(max_length=300,null=True,blank=True,verbose_name="Descripción")
    Estado = models.BooleanField(default=True)
    def __str__(self):
        return self.Descripcion

class ElementoInventario(models.Model):
    Id = models.AutoField(primary_key=True)
    Categoria = models.ForeignKey(CatalogoElementoInventario,related_name = 'elementosInventario',null=True,blank=True,on_delete=models.CASCADE)
    Descripcion = models.CharField(max_length=300,null=True,blank=True,verbose_name="Descripción")
    Inventario = models.ForeignKey(Inventario,related_name = 'elementosInventario',null=True,blank=True,on_delete=models.CASCADE)
    def __str__(self):
        return self.Descripcion



