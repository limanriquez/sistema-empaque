
import itertools
import logging

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, RequestContext
from django.urls import path, reverse

from .models import CodigoCaja, CodigoTarima
from .forms import (
    GenerarCodigosCajaForm,
    GenerarCodigosTarimaForm,
)


logger = logging.getLogger(__name__)


# ==========================================================
# CONFIGURACIÓN DEL GENERADOR DE TARIMAS
# ==========================================================

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
LONGITUD_CODIGO = 4
TOTAL_CODIGOS = len(ALFABETO) ** LONGITUD_CODIGO

# Tamaño de cada bloque de inserción.
TAMANO_BLOQUE = 10000

LOCK_CODIGO_TARIMA = "generador_catalogo_codigo_tarima"


def generar_catalogo_tarimas():

    # ------------------------------------------------------
    # VALIDAR MOTOR DE BASE DE DATOS
    # ------------------------------------------------------

    if connection.vendor != "mysql":
        raise ValidationError(
            "El generador de códigos de tarima requiere MySQL."
        )

    # ------------------------------------------------------
    # OBTENER BLOQUEO DE MYSQL
    # ------------------------------------------------------

    with connection.cursor() as cursor:

        cursor.execute(
            "SELECT GET_LOCK(%s, 0)",
            [LOCK_CODIGO_TARIMA],
        )

        resultado_lock = cursor.fetchone()[0]

    if resultado_lock != 1:
        raise ValidationError(
            "No fue posible obtener el bloqueo del generador. "
            "Posiblemente existe otra generación en ejecución."
        )

    generados = 0
    consecutivo = 1
    bloque = []

    try:

        # --------------------------------------------------
        # VALIDAR QUE LA TABLA ESTÉ VACÍA
        # --------------------------------------------------

        if CodigoTarima.objects.exists():
            raise ValidationError(
                "La tabla de códigos de tarima ya contiene registros. "
                "No se puede ejecutar nuevamente la generación."
            )

        # --------------------------------------------------
        # GENERAR COMBINACIONES
        # --------------------------------------------------

        combinaciones = itertools.product(
            ALFABETO,
            repeat=LONGITUD_CODIGO,
        )

        for combinacion in combinaciones:

            codigo = "".join(combinacion)

            bloque.append(
                CodigoTarima(
                    codigo_tarima=codigo,
                    consecutivo=consecutivo,
                    usado=False,
                )
            )

            # Consecutivo visual del 01 al 99.
            consecutivo += 1

            if consecutivo > 99:
                consecutivo = 1

            # ----------------------------------------------
            # INSERTAR BLOQUE
            # ----------------------------------------------

            if len(bloque) >= TAMANO_BLOQUE:

                with transaction.atomic():

                    CodigoTarima.objects.bulk_create(
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

                CodigoTarima.objects.bulk_create(
                    bloque,
                    batch_size=TAMANO_BLOQUE,
                )

            generados += len(bloque)
            bloque.clear()

        # --------------------------------------------------
        # VALIDAR RESULTADO FINAL
        # --------------------------------------------------

        total_final = CodigoTarima.objects.count()

        if total_final != TOTAL_CODIGOS:

            raise ValidationError(
                (
                    f"Generación incompleta. "
                    f"Esperados: {TOTAL_CODIGOS:,}. "
                    f"Registrados: {total_final:,}."
                )
            )

        return {
            "generados": generados,
            "total_final": total_final,
        }

    finally:

        # --------------------------------------------------
        # LIBERAR BLOQUEO DE MYSQL
        # --------------------------------------------------

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT RELEASE_LOCK(%s)",
                [LOCK_CODIGO_TARIMA],
            )


# ==========================================================
# ADMIN BASE: GENERADORES DE CATÁLOGOS
# ==========================================================

class GeneradorCatalogoAdmin(admin.ModelAdmin):

    form_class = None

    titulo_generador = ""
    descripcion_generador = ""
    descripcion_tabla = ""

    list_per_page = 100

    # ------------------------------------------------------
    # PERMISOS
    # ------------------------------------------------------

    def has_add_permission(self, request):

        return True

    def has_change_permission(self, request, obj=None):

        return False

    def has_delete_permission(self, request, obj=None):

        return False

    # ------------------------------------------------------
    # URL DEL LISTADO
    # ------------------------------------------------------

    def get_changelist_url(self):

        opts = self.model._meta

        return reverse(
            f"admin:{opts.app_label}_{opts.model_name}_changelist"
        )

    # ------------------------------------------------------
    # URL DEL GENERADOR
    # ------------------------------------------------------

    def get_generar_url(self):

        opts = self.model._meta

        return reverse(
            f"admin:{opts.app_label}_{opts.model_name}_generar"
        )

    # ------------------------------------------------------
    # URLS PERSONALIZADAS
    # ------------------------------------------------------

    def get_urls(self):

        urls = super().get_urls()

        opts = self.model._meta

        custom_urls = [
            path(
                "generar/",
                self.admin_site.admin_view(
                    self.generar_view
                ),
                name=(
                    f"{opts.app_label}_"
                    f"{opts.model_name}_generar"
                ),
            ),
        ]

        return custom_urls + urls

    # ------------------------------------------------------
    # REDIRECCIONAR BOTÓN AÑADIR
    # ------------------------------------------------------

    def add_view(
        self,
        request,
        form_url="",
        extra_context=None,
    ):

        return HttpResponseRedirect(
            self.get_generar_url()
        )

    # ------------------------------------------------------
    # EJECUTAR GENERADOR
    # ------------------------------------------------------

    def ejecutar_generador(self, form):

        raise NotImplementedError(
            "La clase administradora debe implementar "
            "el método ejecutar_generador()."
        )

    # ------------------------------------------------------
    # VISTA DEL GENERADOR
    # ------------------------------------------------------

    def generar_view(self, request):

        opts = self.model._meta

        context = {
            **self.admin_site.each_context(request),

            "title": self.titulo_generador,

            "opts": opts,

            "changelist_url": self.get_changelist_url(),

            "descripcion_generador": (
                self.descripcion_generador
            ),

            "descripcion_tabla": (
                self.descripcion_tabla
            ),
        }

        # --------------------------------------------------
        # PROCESAR POST
        # --------------------------------------------------

        if request.method == "POST":

            form = self.form_class(request.POST)

            if form.is_valid():

                try:

                    resultado = self.ejecutar_generador(form)

                    self.message_user(
                        request,
                        (
                            "Generación finalizada correctamente. "
                            f"Códigos generados: "
                            f"{resultado['generados']:,}. "
                            f"Total registrado: "
                            f"{resultado['total_final']:,}."
                        ),
                        messages.SUCCESS,
                    )

                    return HttpResponseRedirect(
                        self.get_changelist_url()
                    )

                except ValidationError as error:

                    logger.warning(
                        "Error de validación en generador %s: %r",
                        self.model.__name__,
                        error,
                    )

                    form.add_error(
                        None,
                        error,
                    )

                except Exception as error:

                    # Registrar excepción completa y traceback.
                    logger.exception(
                        "Error inesperado durante la generación "
                        "del catálogo %s.",
                        self.model.__name__,
                    )

                    # Mostrar detalle incluso si str(error) está vacío.
                    detalle = (
                        f"{type(error).__name__}: {repr(error)}"
                    )

                    self.message_user(
                        request,
                        (
                            "Error durante la generación: "
                            f"{detalle}"
                        ),
                        messages.ERROR,
                    )

            else:

                self.message_user(
                    request,
                    "Revisa los errores del formulario.",
                    messages.ERROR,
                )

        else:

            form = self.form_class()

        context["form"] = form

        # --------------------------------------------------
        # PLANTILLA DEL GENERADOR
        # --------------------------------------------------

        template = Template("""
            {% extends "admin/base_site.html" %}

            {% block content %}

            <div id="content-main">

                <h1>{{ title }}</h1>

                <div class="module">

                    <p>
                        {{ descripcion_generador }}
                    </p>

                    <p>
                        Alfabeto permitido:
                        <strong>
                            ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
                        </strong>
                    </p>

                    <p>
                        {{ descripcion_tabla }}
                    </p>

                </div>

                <form method="post">

                    {% csrf_token %}

                    {% if form.non_field_errors %}

                        <div class="errornote">
                            {{ form.non_field_errors }}
                        </div>

                    {% endif %}

                    <fieldset class="module aligned">

                        <div class="form-row">

                            {{ form.longitud.errors }}

                            {{ form.longitud.label_tag }}

                            {{ form.longitud }}

                        </div>

                        <div class="form-row">

                            {{ form.confirmar.errors }}

                            {{ form.confirmar }}

                            {{ form.confirmar.label_tag }}

                        </div>

                    </fieldset>

                    <div class="submit-row">

                        <input
                            type="submit"
                            value="Generar catálogo"
                            class="default"
                        >

                        <a
                            href="{{ changelist_url }}"
                            class="closelink"
                        >
                            Cancelar
                        </a>

                    </div>

                </form>

            </div>

            {% endblock %}
        """)

        return HttpResponse(
            template.render(
                RequestContext(request, context)
            )
        )


# ==========================================================
# ADMIN: CÓDIGOS DE CAJA
# ==========================================================

@admin.register(CodigoCaja)
class CodigoCajaAdmin(GeneradorCatalogoAdmin):

    form_class = GenerarCodigosCajaForm

    titulo_generador = (
        "Generar catálogo de códigos de caja"
    )

    descripcion_generador = (
        "Se generarán 1,679,616 códigos únicos "
        "de cuatro caracteres alfanuméricos."
    )

    descripcion_tabla = (
        "La tabla CodigoCaja debe estar completamente "
        "vacía para permitir la generación. "
        "Si existe algún registro, el proceso será bloqueado."
    )

    list_display = (
        "id",
        "codigo",
        "usado",
    )

    list_filter = (
        "usado",
    )

    search_fields = (
        "codigo",
    )

    ordering = ("id",)

    def ejecutar_generador(self, form):

        return form.generar()


# ==========================================================
# ADMIN: CÓDIGOS DE TARIMA
# ==========================================================

@admin.register(CodigoTarima)
class CodigoTarimaAdmin(GeneradorCatalogoAdmin):

    form_class = GenerarCodigosTarimaForm

    titulo_generador = (
        "Generar catálogo de códigos de tarima"
    )

    descripcion_generador = (
        "Se generarán 1,679,616 códigos técnicos únicos "
        "de cuatro caracteres alfanuméricos. "
        "Cada código tendrá un consecutivo visual del 01 al 99."
    )

    descripcion_tabla = (
        "La tabla CodigoTarima debe estar completamente "
        "vacía para permitir la generación. "
        "El consecutivo visual se reinicia después del 99 "
        "y queda almacenado permanentemente."
    )

    list_display = (
        "id",
        "codigo_tarima",
        "consecutivo",
        "usado",
    )

    list_filter = (
        "usado",
    )

    search_fields = (
        "codigo_tarima",
    )

    ordering = ("id",)

    def ejecutar_generador(self, form):

        # El formulario ya validó la confirmación
        # y que la tabla esté vacía.
        return generar_catalogo_tarimas()
