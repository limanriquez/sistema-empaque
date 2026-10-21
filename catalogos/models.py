from django.db import models


class GoHome(models.Model):
    class Meta:
        managed = False
        app_label = "catalogos"
        verbose_name = "A inicio"
        verbose_name_plural = "A inicio"

