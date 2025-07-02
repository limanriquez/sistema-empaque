from django.db import models

# Create your models here.
class Mensaje(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre or 'Anónimo'} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"