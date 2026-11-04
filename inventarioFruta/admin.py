from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join

from .models import (
    RecepcionFruta,
    DetalleRecepcionFruta,
    MovimientoFruta,
    ExistenciaFruta,
)

from .forms import (
    RecepcionFrutaForm,
    DetalleRecepcionFrutaForm,
    SalidaProduccionForm,
    TrasladoFrutaForm,
    MermaFrutaForm,
    AjusteEntradaFrutaForm,
    AjusteSalidaFrutaForm,
)


# ============================================================
# ACCESO EXCLUSIVO A SUPERUSUARIOS
# ============================================================

class SuperuserAdminMixin:

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser


# ============================================================
# FORMSET DE DISTRIBUCION DE RECEPCION
# ============================================================

class DetalleRecepcionFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()

        ubicaciones = set()
        total_distribuido = 0
        errores = []

        for form in self.forms:

            if not hasattr(form, "cleaned_data"):
                continue

            datos = form.cleaned_data

            if not datos or datos.get("DELETE"):
                continue

            seccion = datos.get("seccion")
            estiba = datos.get("estiba")
            cantidad = datos.get("cantidad_cajones")

            # Ignorar formularios completamente vacíos.
            if not seccion and not estiba and not cantidad:
                continue

            # Los errores individuales ya los presenta el formulario.
            if form.errors:
                continue

            if not seccion:
                errores.append(
                    "Todas las distribuciones deben tener una sección."
                )
                continue

            if cantidad is None:
                continue

            total_distribuido += cantidad

            # Evitar ubicaciones duplicadas.
            ubicacion = (
                seccion.pk,
                estiba.pk if estiba else None,
            )

            if ubicacion in ubicaciones:

                errores.append(
                    f"La sección '{seccion}' y la estiba "
                    f"'{estiba or 'Sin estiba'}' están duplicadas."
                )

            ubicaciones.add(ubicacion)

        cantidad_recibida = getattr(
            self.instance,
            "cantidad_cajones",
            None,
        )

        if cantidad_recibida is not None:

            if total_distribuido != cantidad_recibida:

                errores.append(
                    f"La cantidad recibida es {cantidad_recibida} "
                    f"cajones, pero la distribución suma "
                    f"{total_distribuido} cajones. "
                    f"La diferencia es "
                    f"{abs(cantidad_recibida - total_distribuido)}."
                )

        if errores:
            raise ValidationError(errores)


# ============================================================
# INLINE DE DISTRIBUCION
# ============================================================

class DetalleRecepcionInline(admin.TabularInline):

    model = DetalleRecepcionFruta
    form = DetalleRecepcionFrutaForm
    formset = DetalleRecepcionFormSet

    extra = 1

    fields = (
        "seccion",
        "estiba",
        "cantidad_cajones",
    )

    def recepcion_confirmada(self, obj):

        if not obj or not obj.pk:
            return False

        return MovimientoFruta.objects.filter(
            detalle_recepcion__recepcion_id=obj.pk,
            tipo=MovimientoFruta.Tipo.RECEPCION,
        ).exists()

    def get_readonly_fields(self, request, obj=None):

        if self.recepcion_confirmada(obj):
            return (
                "seccion",
                "estiba",
                "cantidad_cajones",
            )

        return ()

    def has_add_permission(self, request, obj=None):

        if self.recepcion_confirmada(obj):
            return False

        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):

        if self.recepcion_confirmada(obj):
            return False

        return super().has_delete_permission(request, obj)


# ============================================================
# RECEPCIONES DE FRUTA
#
# Admin para registrar, consultar y confirmar las recepciones.
# Incluye cliente, lote agrícola y variedad como datos de origen.
# ============================================================

@admin.register(RecepcionFruta)
class RecepcionFrutaAdmin(
    SuperuserAdminMixin,
    admin.ModelAdmin,
):

    form = RecepcionFrutaForm

    inlines = [
        DetalleRecepcionInline,
    ]

    list_display = (
        "id",
        "fecha_recepcion",
        "cliente",
        "lote_huerta",
        "variedad",
        "fecha_pizca",
        "cantidad_cajones",
        "recibido_por",
        "estado_procesamiento",
    )

    list_display_links = ("id",)

    list_select_related = (
        "cliente__persona",
        "lote_huerta__huerta",
        "variedad",
        "recibido_por__persona",
        "creado_por",
    )

    list_filter = (
        "fecha_recepcion",
        "fecha_pizca",
        "cliente",
        "lote_huerta__huerta",
        "variedad",
    )

    search_fields = (
        "cliente__persona__razon_social",
        "cliente__persona__nombre_comercial",
        "cliente__persona__nombres",
        "cliente__persona__apellido_paterno",
        "lote_huerta__nombre",
        "lote_huerta__huerta__nombre",
        "variedad__nombre",
        "recibido_por__persona__nombres",
        "recibido_por__persona__apellido_paterno",
    )

    readonly_fields = (
        "creado_en",
        "creado_por",
        "estado_procesamiento",
    )

    fieldsets = (
        (
            "Datos de recepción",
            {
                "fields": (
                    "cliente",
                    "lote_huerta",
                    "variedad",
                    "fecha_pizca",
                    "cantidad_cajones",
                    "fecha_recepcion",
                    "recibido_por",
                    "observaciones",
                )
            },
        ),
        (
            "Control del registro",
            {
                "fields": (
                    "estado_procesamiento",
                    "creado_en",
                    "creado_por",
                )
            },
        ),
    )

    actions = (
        "confirmar_recepciones",
    )

    # --------------------------------------------------------
    # ESTADO DE RECEPCION
    # --------------------------------------------------------

    @admin.display(description="Estado")
    def estado_procesamiento(self, obj):

        if not obj.pk:
            return "Pendiente"

        total_detalles = obj.detalles.count()

        movimientos = MovimientoFruta.objects.filter(
            detalle_recepcion__recepcion_id=obj.pk,
            tipo=MovimientoFruta.Tipo.RECEPCION,
        ).count()

        if total_detalles and movimientos == total_detalles:

            return format_html(
                '<strong style="color:green;">Confirmada</strong>'
            )

        if movimientos:

            return format_html(
                '<strong style="color:#b7791f;">Procesamiento parcial</strong>'
            )

        return format_html(
            '<strong style="color:#b7791f;">Pendiente</strong>'
        )

    # --------------------------------------------------------
    # BLOQUEAR RECEPCIONES CONFIRMADAS
    # --------------------------------------------------------

    def recepcion_confirmada(self, obj):

        if not obj or not obj.pk:
            return False

        return MovimientoFruta.objects.filter(
            detalle_recepcion__recepcion_id=obj.pk,
            tipo=MovimientoFruta.Tipo.RECEPCION,
        ).exists()

    def get_readonly_fields(self, request, obj=None):

        campos = list(
            super().get_readonly_fields(request, obj)
        )

        if self.recepcion_confirmada(obj):

            campos.extend([
                "cliente",
                "lote_huerta",
                "variedad",
                "fecha_pizca",
                "cantidad_cajones",
                "fecha_recepcion",
                "recibido_por",
                "observaciones",
            ])

        return campos

    def save_model(self, request, obj, form, change):

        if not change:
            obj.creado_por = request.user

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    # --------------------------------------------------------
    # CONFIRMACION DE RECEPCIONES
    # --------------------------------------------------------

    @admin.action(
        description="Confirmar recepciones seleccionadas"
    )
    def confirmar_recepciones(self, request, queryset):

        confirmadas = 0
        errores = []

        for recepcion in queryset.order_by("pk"):

            try:

                recepcion.confirmar()
                confirmadas += 1

            except ValidationError as exc:

                errores.append(
                    f"Recepción {recepcion.pk}: {exc}"
                )

        if confirmadas:

            self.message_user(
                request,
                f"Se confirmaron {confirmadas} recepción(es).",
                messages.SUCCESS,
            )

        for error in errores:

            self.message_user(
                request,
                error,
                messages.ERROR,
            )

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# MOVIMIENTOS DE FRUTA
# ============================================================

@admin.register(MovimientoFruta)
class MovimientoFrutaAdmin(
    SuperuserAdminMixin,
    admin.ModelAdmin,
):

    form = SalidaProduccionForm

    formularios_operacion = {

        "salida-produccion": (
            SalidaProduccionForm,
            "Registrar salida a producción",
        ),

        "traslado": (
            TrasladoFrutaForm,
            "Registrar traslado de fruta",
        ),

        "merma": (
            MermaFrutaForm,
            "Registrar merma de fruta",
        ),

        "ajuste-entrada": (
            AjusteEntradaFrutaForm,
            "Registrar ajuste de entrada",
        ),

        "ajuste-salida": (
            AjusteSalidaFrutaForm,
            "Registrar ajuste de salida",
        ),
    }

    list_display = (
        "id",
        "fecha",
        "tipo",
        "cliente",
        "lote_huerta",
        "fecha_pizca",
        "cantidad_cajones",
        "ubicacion_origen",
        "ubicacion_destino",
        "responsable",
        "creado_por",
    )

    list_display_links = None

    list_select_related = (
        "cliente__persona",
        "lote_huerta__huerta",
        "seccion_origen",
        "estiba_origen",
        "seccion_destino",
        "estiba_destino",
        "responsable__persona",
        "creado_por",
    )

    list_filter = (
        "tipo",
        "fecha",
        "fecha_pizca",
        "cliente",
        "lote_huerta__huerta",
    )

    search_fields = (
        "cliente__persona__razon_social",
        "cliente__persona__nombre_comercial",
        "cliente__persona__nombres",
        "cliente__persona__apellido_paterno",
        "lote_huerta__nombre",
        "descripcion",
    )

    # --------------------------------------------------------
    # RUTAS DE OPERACIONES INDEPENDIENTES
    # --------------------------------------------------------

    def get_urls(self):

        urls = super().get_urls()

        urls_personalizadas = []

        for slug in self.formularios_operacion:

            urls_personalizadas.append(
                path(
                    f"{slug}/",
                    self.admin_site.admin_view(
                        self.crear_vista_operacion(slug)
                    ),
                    name=(
                        f"inventariofruta_movimientofruta_{slug}"
                    ),
                )
            )

        return urls_personalizadas + urls

    def crear_vista_operacion(self, operacion):

        def vista(request):

            formulario, titulo = (
                self.formularios_operacion[operacion]
            )

            request._formulario_movimiento_fruta = formulario

            return self.add_view(
                request,
                form_url="",
                extra_context={
                    "title": titulo,
                    "titulo_operacion": titulo,
                },
            )

        return vista

    # --------------------------------------------------------
    # SELECCION DEL FORMULARIO
    # --------------------------------------------------------

    def get_form(self, request, obj=None, **kwargs):

        if obj is None:

            formulario = getattr(
                request,
                "_formulario_movimiento_fruta",
                SalidaProduccionForm,
            )

            kwargs["form"] = formulario

        return super().get_form(
            request,
            obj,
            **kwargs,
        )

    # --------------------------------------------------------
    # GUARDAR MOVIMIENTO
    # --------------------------------------------------------

    def save_model(self, request, obj, form, change):

        obj.creado_por = request.user

        super().save_model(
            request,
            obj,
            form,
            change,
        )

    # --------------------------------------------------------
    # UBICACIONES
    # --------------------------------------------------------

    @admin.display(description="Ubicación de origen")
    def ubicacion_origen(self, obj):

        if not obj.seccion_origen:
            return "—"

        if obj.estiba_origen:
            return (
                f"{obj.seccion_origen} / "
                f"{obj.estiba_origen}"
            )

        return obj.seccion_origen

    @admin.display(description="Ubicación de destino")
    def ubicacion_destino(self, obj):

        if not obj.seccion_destino:
            return "—"

        if obj.estiba_destino:
            return (
                f"{obj.seccion_destino} / "
                f"{obj.estiba_destino}"
            )

        return obj.seccion_destino

    # --------------------------------------------------------
    # BOTONES DE OPERACIONES
    # --------------------------------------------------------

    def changelist_view(self, request, extra_context=None):

        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        if (
            request.method == "GET"
            and self.has_add_permission(request)
            and hasattr(response, "context_data")
        ):

            enlaces = [
                (
                    reverse(
                        "admin:inventariofruta_movimientofruta_"
                        + slug
                    ),
                    titulo,
                )
                for slug, (_, titulo)
                in self.formularios_operacion.items()
            ]

            botones = format_html(
                '<style>'
                '.object-tools {{ display:none !important; }}'
                '</style>'
                '<div style="display:flex;flex-wrap:wrap;'
                'gap:10px;margin-bottom:15px;">'
                '{}'
                '</div>',

                format_html_join(
                    "",
                    '<a href="{}" style="display:inline-block;'
                    'padding:9px 14px;background:#198754;'
                    'color:white;border-radius:5px;'
                    'text-decoration:none;font-weight:500;">'
                    '{}'
                    '</a>',
                    enlaces,
                ),
            )

            self.message_user(
                request,
                botones,
                level=messages.INFO,
            )

        return response

    # --------------------------------------------------------
    # HISTORIAL INMUTABLE
    # --------------------------------------------------------

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# EXISTENCIAS DE FRUTA
# ============================================================

@admin.register(ExistenciaFruta)
class ExistenciaFrutaAdmin(
    SuperuserAdminMixin,
    admin.ModelAdmin,
):

    list_display = (
        "cliente",
        "lote_huerta",
        "fecha_pizca",
        "almacen",
        "espacio",
        "seccion",
        "estiba",
        "cantidad_cajones",
        "actualizado_en",
    )

    list_select_related = (
        "cliente__persona",
        "lote_huerta__huerta",
        "seccion__espacio__almacen",
        "estiba",
    )

    list_filter = (
        "cliente",
        "lote_huerta__huerta",
        "fecha_pizca",
        "seccion__espacio__almacen",
        "seccion__espacio",
        "seccion",
    )

    search_fields = (
        "cliente__persona__razon_social",
        "cliente__persona__nombre_comercial",
        "cliente__persona__nombres",
        "cliente__persona__apellido_paterno",
        "lote_huerta__nombre",
        "seccion__nombre",
        "estiba__nombre",
    )

    @admin.display(
        description="Almacén",
        ordering="seccion__espacio__almacen__nombre",
    )
    def almacen(self, obj):
        return obj.seccion.espacio.almacen

    @admin.display(
        description="Espacio",
        ordering="seccion__espacio__nombre",
    )
    def espacio(self, obj):
        return obj.seccion.espacio

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False