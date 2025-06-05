from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from empresa.models import Personal, Empresa

class CorteCaja(models.Model):
    ABIERTO = 1
    CERRADO = 2
    CANCELADO = 3

    ESTATUS_CHOICES = [
        (ABIERTO, 'Abierto'),
        (CERRADO, 'Cerrado'),
        (CANCELADO, 'Cancelado'),
    ]
    empresa = models.ForeignKey(Empresa,on_delete=models.PROTECT, related_name='cortes')
    personal = models.ForeignKey(Personal,on_delete=models.PROTECT, related_name='cortes')
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingresos_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ingresos_transferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_apertura = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    egresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    estatus = models.IntegerField(
        choices=ESTATUS_CHOICES,
        default=ABIERTO,
        help_text="Estado actual del corte de caja"
    )
    class Meta:
        verbose_name = "Corte de Caja"
        verbose_name_plural = "Cortes de Caja"
        ordering = ['-fecha_apertura']

    def clean(self):
        if self.estatus == self.ABIERTO:
            qs = CorteCaja.objects.filter(estatus=self.ABIERTO, empresa=self.empresa)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Ya existe un corte de caja abierto para esta empresa.")