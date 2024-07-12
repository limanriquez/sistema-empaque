from django.db import models
from users.models import *
#from users import models

class SuperUsuario(models.Model):
    Id = models.AutoField(primary_key=True)
    #verbose_name="TokenCondusef" Sirve para mostrar de esa manera el campo en el panel de administracion
    TokenCondusef = models.CharField(max_length=30,verbose_name="TokenCondusef")
    Nombre = models.CharField(max_length=30,null=True,blank=True,verbose_name="Nombre")
    Password = models.CharField(max_length=10,null=True,blank=True,verbose_name="Password")
    Token = models.CharField(max_length=800, verbose_name="Token")
    User = models.ForeignKey(User,related_name = 'superusuario',null=True,blank=True,on_delete=models.CASCADE)
    def __str__(self):
        return self.Nombre
