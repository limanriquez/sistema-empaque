# utils/validators.py
import re
from django.core.exceptions import ValidationError

def validar_correo(value):
    # Expresión regular para validar correo electrónico
    # Este patrón es bastante estándar para un correo electrónico.
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if not re.match(regex, value):
        raise ValidationError(f"El correo '{value}' no tiene un formato válido.")
        

def validar_curp(curp):
    patron = re.compile(
        r'^[A-Z][AEIOU][A-Z]{2}'        # Letras iniciales
        r'\d{2}(0[1-9]|1[0-2])'         # Año y mes de nacimiento
        r'(0[1-9]|[12]\d|3[01])'        # Día de nacimiento
        r'[HM]'                         # Sexo
        r'(AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|'
        r'GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|'
        r'QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS)'  # Entidad federativa
        r'[B-DF-HJ-NP-TV-Z]{3}'         # Consonantes internas
        r'[A-Z\d]\d$'                   # Homoclave
    )
    return bool(patron.match(curp.upper()))
        
def validar_rfc(value):
    value = value.upper()

    regex = re.compile(
        r'^([A-ZÑ&]{3}|[A-ZÑ&]{4})'         # 3 para moral, 4 para física
        r'([0-9]{2}(0[1-9]|1[0-2])'         # Año y mes válidos
        r'(0[1-9]|[12][0-9]|3[01]))'        # Día válido
        r'[A-Z0-9]{3}$'                     # Homoclave
    )

    if not regex.match(value):
        raise ValidationError('RFC no válido')

# Función de validación para el teléfono
def validar_telefono(value):
    # Expresión regular para validar el teléfono mexicano de 10 dígitos
    # Se asegura de que el teléfono tenga 10 dígitos y empiece con un número entre 1 y 9
    if not re.match(r'^[0-9]{10}$', value):
        raise ValidationError(f"El teléfono '{value}' no tiene un formato válido. Debe tener 10 dígitos.")

def validar_telefono_mx_usa(value):
    """
    Valida números de teléfono para México y Estados Unidos.
    Formatos válidos:
      - 10 dígitos: 5551234567 (México o EE. UU. sin prefijo)
      - Prefijo internacional +52 o +1: +525551234567, +15551234567
    """
    # Expresión regular para validar teléfono con prefijo internacional o sin él
    pattern = r'^(\+52|\+1)?\d{10}$'  # Prefijo +52 para México o +1 para EE.UU. y luego 10 dígitos
    if not re.match(pattern, value):
        raise ValidationError(
            f"El teléfono '{value}' no tiene un formato válido. "
            "Debe ser un número de 10 dígitos o con prefijo internacional (+52 o +1)."
        )