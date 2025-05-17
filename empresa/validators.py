
# utils/validators.py
import re
from django.core.exceptions import ValidationError

def validar_unicidad_cliente(value):
    from empresa.models import Cliente  # import aquí, dentro de la función
    """Valida que el teléfono sea único en la base de datos"""
    if Cliente.objects.filter(telefono=value).exists():
        raise ValidationError(f"El teléfono {value} ya está registrado para otro cliente.")

        