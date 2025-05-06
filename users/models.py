from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField('Correo electronico', unique=True)
    username = models.CharField(max_length=50,blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        # Cambiar para que se muestre el nombre de usuario o el correo
        return self.email  # O si prefieres: return self.email
    