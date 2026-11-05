
from itertools import product

from django.db import transaction, connection
from django.core.exceptions import ValidationError

from .models import CodigoCaja


# ==========================================================
# CONFIGURACIÓN DEL GENERADOR
# ==========================================================

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

LONGITUD_CODIGO = 4

TAMANO_BLOQUE = 10_000

CAPACIDAD_TOTAL = len(ALFABETO) ** LONGITUD_CODIGO

# Nombre de bloqueo exclusivo en MySQL.
NOMBRE_BLOQUEO = "generador_catalogo_codigo_caja"


# ==========================================================
# BLOQUEO DE EJECUCIÓN
# ==========================================================

def adquirir_bloqueo():

    """
    Evita que dos procesos ejecuten simultáneamente
    la generación del catálogo.

    MySQL utiliza GET_LOCK para exclusión entre procesos.
    """

    if connection.vendor != "mysql":
        raise ValidationError(
            "El generador requiere MySQL para utilizar "
            "el mecanismo de bloqueo configurado."
        )

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT GET_LOCK(%s, 0)",
            [NOMBRE_BLOQUEO],
        )

        resultado = cursor.fetchone()[0]

    if resultado != 1:
        raise ValidationError(
            "Ya existe otro proceso generando códigos de caja."
        )


def liberar_bloqueo():

    """
    Libera el bloqueo exclusivo de MySQL.
    """

    if connection.vendor != "mysql":
        return

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT RELEASE_LOCK(%s)",
            [NOMBRE_BLOQUEO],
        )


# ==========================================================
# GENERADOR DE CÓDIGOS DE CAJA
# ==========================================================

def generar_codigos_caja(longitud=4):

    """
    Genera todas las combinaciones posibles de códigos
    alfanuméricos de cuatro caracteres.

    REGLAS:

    1. Solo permite cuatro caracteres.
    2. La tabla CodigoCaja debe estar completamente vacía.
    3. Permite repetir letras y números dentro del código.
    4. No permite códigos completos duplicados.
    5. Inserta mediante bloques de 10,000 registros.
    6. Verifica que se hayan insertado todas las combinaciones.
    """

    # ------------------------------------------------------
    # VALIDAR LONGITUD
    # ------------------------------------------------------

    if longitud != LONGITUD_CODIGO:

        raise ValidationError(
            "Actualmente solo está permitida la generación "
            "de códigos de cuatro caracteres."
        )

    generados = 0
    bloque = []

    bloqueo_adquirido = False

    try:

        # --------------------------------------------------
        # ADQUIRIR BLOQUEO
        # --------------------------------------------------

        adquirir_bloqueo()
        bloqueo_adquirido = True

        # --------------------------------------------------
        # VALIDAR QUE LA TABLA ESTÉ VACÍA
        # --------------------------------------------------

        if CodigoCaja.objects.exists():

            raise ValidationError(
                "No se puede generar el catálogo porque la "
                "tabla CodigoCaja ya contiene registros. "
                "Debe estar completamente vacía."
            )

        # --------------------------------------------------
        # GENERAR COMBINACIONES
        # --------------------------------------------------

        for combinacion in product(
            ALFABETO,
            repeat=LONGITUD_CODIGO,
        ):

            codigo = "".join(combinacion)

            bloque.append(
                CodigoCaja(
                    codigo=codigo,
                    usado=False,
                )
            )

            # ----------------------------------------------
            # INSERTAR BLOQUE
            # ----------------------------------------------

            if len(bloque) >= TAMANO_BLOQUE:

                with transaction.atomic():

                    CodigoCaja.objects.bulk_create(
                        bloque,
                        batch_size=TAMANO_BLOQUE,
                    )

                generados += len(bloque)

                bloque.clear()

        # --------------------------------------------------
        # INSERTAR ÚLTIMO BLOQUE
        # --------------------------------------------------

        if bloque:

            with transaction.atomic():

                CodigoCaja.objects.bulk_create(
                    bloque,
                    batch_size=TAMANO_BLOQUE,
                )

            generados += len(bloque)

            bloque.clear()

        # --------------------------------------------------
        # VERIFICAR RESULTADO
        # --------------------------------------------------

        total_final = CodigoCaja.objects.count()

        if total_final != CAPACIDAD_TOTAL:

            raise ValidationError(
                f"Generación incompleta. "
                f"Esperados: {CAPACIDAD_TOTAL:,}. "
                f"Encontrados: {total_final:,}."
            )

        # --------------------------------------------------
        # RESULTADO
        # --------------------------------------------------

        return {
            "longitud": LONGITUD_CODIGO,
            "capacidad": CAPACIDAD_TOTAL,
            "generados": generados,
            "total_final": total_final,
            "pendientes": CAPACIDAD_TOTAL - total_final,
            "mensaje": "Catálogo generado correctamente.",
        }

    finally:

        # --------------------------------------------------
        # LIBERAR BLOQUEO
        # --------------------------------------------------

        if bloqueo_adquirido:
            liberar_bloqueo()
