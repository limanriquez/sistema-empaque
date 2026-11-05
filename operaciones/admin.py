from django.contrib import admin, messages
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.html import format_html

from .models import OperacionDiaria
from .forms import OperacionDiariaForm

from .models import LoteEmpaque
from .forms import LoteEmpaqueForm
from personas.models import Empleado

from django.urls import path
from django.http import JsonResponse
from django.apps import apps
from django.db.models import Sum
from django.urls import reverse


from .forms import (
    ComponenteEmpaqueForm,
    ComponenteEmpaqueFormSet,
    ProductoEmpaqueForm,
    OperacionDiariaForm,
)
from .models import ComponenteEmpaque, ProductoEmpaque, OperacionDiaria

# Tabla de materiales dentro del producto: se elige el material, se
# captura la cantidad por unidad empacada y se ve su unidad. El
# producto debe tener al menos un material.
class ComponenteEmpaqueInline(admin.TabularInline):
    model = ComponenteEmpaque
    form = ComponenteEmpaqueForm
    formset = ComponenteEmpaqueFormSet
    extra = 1
    autocomplete_fields = ("material",)
    fields = ("material", "cantidad_material", "unidad")
    readonly_fields = ("unidad",)

    # Evita una consulta adicional por fila para la unidad.
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "material__unidad_medida"
        )

    # Muestra la unidad del material elegido.
    @admin.display(description="Unidad")
    def unidad(self, obj):
        if obj.pk:
            return obj.material.unidad_medida.abreviatura

        return "-"


# Administra los productos que se empacan, con su costo, precio de
# cobro, tamaño y su BOM. La lista muestra solo los productos;
# al abrir uno se ven y editan los materiales que descuenta por cada
# unidad empacada.
# La calidad se captura directamente en el registro de cada caja,
# no pertenece al catálogo de productos.
# No habilita la eliminación: un producto fuera de uso se desactiva.

@admin.register(ProductoEmpaque)
class ProductoEmpaqueAdmin(admin.ModelAdmin):

    form = ProductoEmpaqueForm

    list_display = (
        "id",
        "codigo",
        "nombre",
        "tamano",
        "mostrar_costo",
        "mostrar_precio",
        "mostrar_margen",
        "num_materiales",
        "activo",
    )

    list_display_links = ("id", "nombre")

    list_filter = (
        "activo",
        "tamano",
    )

    search_fields = (
        "codigo",
        "nombre",
        "descripcion",
        "tamano__nombre",
    )

    inlines = [ComponenteEmpaqueInline]

    fields = (
        "codigo",
        "nombre",
        "descripcion",
        "tamano",
        "costo_empaque",
        "precio_cobro",
        "margen",
        "activo",
    )

    readonly_fields = ("margen",)

    # Cuenta los materiales del BOM sin una consulta por fila.
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "tamano",
        ).annotate(
            _num_materiales=Count("componentes")
        )

    @admin.display(description="Costo", ordering="costo_empaque")
    def mostrar_costo(self, obj):
        return f"$ {obj.costo_empaque:,.2f}"

    @admin.display(description="Precio de cobro", ordering="precio_cobro")
    def mostrar_precio(self, obj):
        return f"$ {obj.precio_cobro:,.2f}"

    @admin.display(description="Margen")
    def mostrar_margen(self, obj):
        return f"$ {obj.margen_unitario:,.2f}"

    # Cantidad de materiales del BOM; 0 indica un producto sin configurar.
    @admin.display(description="Materiales en el BOM", ordering="_num_materiales")
    def num_materiales(self, obj):
        return obj._num_materiales

    # Ganancia por unidad, solo para consulta dentro del formulario.
    @admin.display(description="Margen por unidad")
    def margen(self, obj):
        if obj.pk:
            return f"$ {obj.margen_unitario:,.2f}"

        return "-"

    # Impide eliminar productos desde Django Admin.
    def has_delete_permission(self, request, obj=None):
        return False


        
# ==========================================================
# ADMIN: OPERACIÓN DIARIA
#
# Si no existe una operación abierta, permite crear una
# nueva y la abre automáticamente.
#
# Si existe una operación abierta, permite editarla y
# al guardar registra su cierre.
#
# Las operaciones cerradas permanecen como historial.
# ==========================================================

@admin.register(OperacionDiaria)
class OperacionDiariaAdmin(admin.ModelAdmin):

    form = OperacionDiariaForm

    list_display = (
        "id",
        "fecha",
        "estado",
        "hora_apertura",
        "hora_cierre",
    )

    list_filter = (
        "abierta",
        "fecha",
    )

    ordering = (
        "-fecha",
        "-id",
    )

    readonly_fields = (
        "fecha",
        "abierta",
        "hora_apertura",
        "hora_cierre",
        "abierto_por",
        "cerrado_por",
    )

    fields = (
        "fecha",
        "observaciones",
        "abierta",
        "hora_apertura",
        "abierto_por",
        "hora_cierre",
        "cerrado_por",
    )

    # ------------------------------------------------------
    # Estado
    # ------------------------------------------------------

    @admin.display(description="Estado")
    def estado(self, obj):
        return "ABIERTA" if obj.abierta else "CERRADA"

    # ------------------------------------------------------
    # Integración con el usuario autenticado
    # ------------------------------------------------------

    def get_form(self, request, obj=None, **kwargs):

        FormClass = super().get_form(request, obj, **kwargs)

        class FormConRequest(FormClass):

            def __init__(self, *args, **form_kwargs):
                form_kwargs["request"] = request
                super().__init__(*args, **form_kwargs)

        return FormConRequest

    # ------------------------------------------------------
    # Control de creación
    # ------------------------------------------------------

    def has_add_permission(self, request):

        return (
            super().has_add_permission(request)
            and not OperacionDiaria.objects.filter(
                abierta=True
            ).exists()
        )

    # ------------------------------------------------------
    # Control de modificación
    # ------------------------------------------------------

    def get_readonly_fields(self, request, obj=None):

        if obj is not None and not obj.abierta:
            return self.fields

        return self.readonly_fields

    # ------------------------------------------------------
    # Guardar operación
    # ------------------------------------------------------

    @transaction.atomic
    def save_model(self, request, obj, form, change):

        # El formulario ya validó que el empleado exista
        # y que se encuentre activo.
        empleado = request.user.perfil_empleado
        persona = empleado.persona

        if not change:

            # Crear y abrir una operación nueva.
            super().save_model(request, obj, form, change)

            obj.abrir(persona)

            self.message_user(
                request,
                "Operación creada y abierta correctamente.",
                messages.SUCCESS,
            )

        else:

            # Recuperar y bloquear el registro actual.
            operacion = (
                OperacionDiaria.objects
                .select_for_update()
                .get(pk=obj.pk)
            )

            if not operacion.abierta:
                raise ValidationError(
                    "La operación ya está cerrada."
                )

            # Guardar observaciones.
            super().save_model(request, obj, form, change)

            # Cerrar la operación.
            obj.cerrar(persona)

            self.message_user(
                request,
                "Operación cerrada correctamente.",
                messages.SUCCESS,
            )

    # ------------------------------------------------------
    # No permitir eliminar
    # ------------------------------------------------------

    def has_delete_permission(self, request, obj=None):
        return False




# ==========================================================
# ADMINISTRACIÓN: LOTE DE EMPAQUE
#
# Administra las corridas de producción.
#
# CREACIÓN:
# - Permite seleccionar lote agrícola y variedad.
# - Las variedades se consultan dinámicamente mediante AJAX.
# - Muestra el máximo de cajones de la variedad seleccionada.
# - Verifica que no exista otro LoteEmpaque abierto.
# - Crea y abre automáticamente el LoteEmpaque.
#
# CONTROL:
# - maximo_cajones es de solo lectura.
# - El valor definitivo se calcula en abrir().
# - No se permite modificar lote ni variedad después
#   de la apertura.
# - No se permite eliminar físicamente registros.
#
# CIERRE:
# - Se realiza mediante la acción del listado.
# - Utiliza el método cerrar() del modelo.
# - No modifica OperacionDiaria.
# ==========================================================

@admin.register(LoteEmpaque)
class LoteEmpaqueAdmin(admin.ModelAdmin):

    form = LoteEmpaqueForm

    # ------------------------------------------------------
    # LISTADO
    # ------------------------------------------------------

    list_display = (
        "id",
        "lote_huerta",
        "variedad",
        "maximo_cajones",
        "fecha_apertura",
        "abierto_por",
        "mostrar_estado",
    )

    list_filter = (
        "abierto",
        "variedad",
        "fecha_apertura",
    )

    search_fields = (
        "lote_huerta__nombre",
        "variedad__nombre",
    )

    ordering = ("-id",)

    # ------------------------------------------------------
    # CAMPOS DE SOLO LECTURA
    # ------------------------------------------------------

    readonly_fields = (
        "maximo_cajones",
        "abierto",
        "fecha_apertura",
        "fecha_cierre",
        "abierto_por",
        "cerrado_por",
    )

    fields = (
        "lote_huerta",
        "variedad",
        "maximo_cajones",
        "observaciones",
        "abierto",
        "fecha_apertura",
        "abierto_por",
        "fecha_cierre",
        "cerrado_por",
    )

    # ------------------------------------------------------
    # ARCHIVOS ESTÁTICOS
    # ------------------------------------------------------

    class Media:
        js = (
            "operaciones/js/lote_empaque_form.js",
        )

    # ------------------------------------------------------
    # URL PERSONALIZADA PARA CONSULTAR VARIEDADES
    # ------------------------------------------------------

    def get_urls(self):

        urls = super().get_urls()

        urls_personalizadas = [
            path(
                "variedades-disponibles/",
                self.admin_site.admin_view(
                    self.variedades_disponibles
                ),
                name="operaciones_loteempaque_variedades",
            ),
        ]

        return urls_personalizadas + urls

    # ------------------------------------------------------
    # CONSULTAR VARIEDADES Y EXISTENCIAS
    # ------------------------------------------------------

    def variedades_disponibles(self, request):

        ExistenciaFruta = apps.get_model(
            "inventarioFruta",
            "ExistenciaFruta",
        )

        Variedad = apps.get_model(
            "fruticultura",
            "Variedad",
        )

        try:
            lote_id = int(request.GET.get("lote_id"))

        except (TypeError, ValueError):
            return JsonResponse(
                {
                    "error": (
                        "El lote agrícola seleccionado "
                        "no es válido."
                    )
                },
                status=400,
            )

        # --------------------------------------------------
        # 1. PROPIETARIOS CON EXISTENCIA POSITIVA
        # --------------------------------------------------

        propietarios = list(
            ExistenciaFruta.objects
            .filter(
                lote_huerta_id=lote_id,
                cantidad_cajones__gt=0,
            )
            .values("cliente_id")
            .annotate(
                total_cajones=Sum("cantidad_cajones"),
            )
        )

        if not propietarios:
            return JsonResponse({
                "variedades": [],
                "error": (
                    "El lote agrícola no tiene "
                    "cajones disponibles."
                ),
            })

        # --------------------------------------------------
        # 2. VALIDAR PROPIETARIO ÚNICO
        # --------------------------------------------------

        if len(propietarios) != 1:
            return JsonResponse({
                "variedades": [],
                "error": (
                    "El lote agrícola tiene existencias "
                    "de varios clientes. No es posible "
                    "determinar un propietario único."
                ),
            })

        cliente_id = propietarios[0]["cliente_id"]

        # --------------------------------------------------
        # 3. AGRUPAR EXISTENCIAS POR VARIEDAD
        # --------------------------------------------------

        existencias = (
            ExistenciaFruta.objects
            .filter(
                lote_huerta_id=lote_id,
                cliente_id=cliente_id,
                cantidad_cajones__gt=0,
            )
            .values("variedad_id")
            .annotate(
                maximo_cajones=Sum("cantidad_cajones"),
            )
        )

        maximos_por_variedad = {
            registro["variedad_id"]: int(
                registro["maximo_cajones"] or 0
            )
            for registro in existencias
        }

        # --------------------------------------------------
        # 4. OBTENER VARIEDADES ACTIVAS
        # --------------------------------------------------

        variedades = Variedad.objects.filter(
            pk__in=maximos_por_variedad.keys(),
            activo=True,
        ).order_by("nombre")

        resultado = [
            {
                "id": variedad.pk,
                "nombre": str(variedad),
                "maximo_cajones": maximos_por_variedad[
                    variedad.pk
                ],
            }
            for variedad in variedades
        ]

        return JsonResponse({
            "variedades": resultado,
        })

    # ------------------------------------------------------
    # INYECTAR URL AJAX Y VALIDAR CREACIÓN
    # ------------------------------------------------------

    def get_form(self, request, obj=None, **kwargs):

        FormClass = super().get_form(
            request,
            obj,
            **kwargs,
        )

        url_variedades = reverse(
            "admin:operaciones_loteempaque_variedades"
        )

        class FormConUrl(FormClass):

            def __init__(self, *args, **form_kwargs):

                super().__init__(*args, **form_kwargs)

                self.fields[
                    "lote_huerta"
                ].widget.attrs["data-variedades-url"] = (
                    url_variedades
                )

            def clean(self):

                cleaned_data = super().clean()

                # Validación previa: solamente al crear.
                if not self.instance.pk:

                    existe_abierto = (
                        LoteEmpaque.objects
                        .filter(abierto=True)
                        .exists()
                    )

                    if existe_abierto:

                        self.add_error(
                            "lote_huerta",
                            (
                                "No es posible crear otro lote "
                                "de empaque. Ya existe un lote "
                                "abierto. Debe cerrarse antes "
                                "de continuar."
                            ),
                        )

                return cleaned_data

        return FormConUrl

    # ------------------------------------------------------
    # MANEJO DE VALIDACIONES DURANTE LA APERTURA
    # ------------------------------------------------------

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):

        try:

            return super().changeform_view(
                request,
                object_id,
                form_url,
                extra_context,
            )

        except ValidationError as error:

            # Esta protección atiende principalmente
            # una posible condición de concurrencia:
            # otro usuario abrió un lote después de que
            # se validó el formulario.

            for mensaje in error.messages:

                self.message_user(
                    request,
                    mensaje,
                    level=messages.ERROR,
                )

            # La transacción de save_model ya se revirtió.
            # Regresar al formulario sin mostrar HTTP 500.
            if object_id is None:

                return HttpResponseRedirect(
                    reverse(
                        "admin:operaciones_loteempaque_add"
                    )
                )

            return HttpResponseRedirect(
                reverse(
                    "admin:operaciones_loteempaque_change",
                    args=[object_id],
                )
            )

    # ------------------------------------------------------
    # ACCIONES
    # ------------------------------------------------------

    actions = [
        "cerrar_lotes",
    ]

    @admin.action(
        description="Cerrar lote(s) de empaque seleccionados",
        permissions=["change"],
    )
    def cerrar_lotes(self, request, queryset):

        try:
            persona = self.obtener_persona(request)

        except ValidationError as error:

            self.message_user(
                request,
                "; ".join(error.messages),
                level=messages.ERROR,
            )

            return

        cerrados = 0
        omitidos = 0
        errores = []

        for lote in queryset:

            if not lote.abierto:
                omitidos += 1
                continue

            try:

                lote.cerrar(persona)
                cerrados += 1

            except ValidationError as error:

                errores.append(
                    f"Lote #{lote.pk}: "
                    f"{'; '.join(error.messages)}"
                )

        if cerrados:

            self.message_user(
                request,
                f"Se cerraron correctamente {cerrados} lote(s).",
                level=messages.SUCCESS,
            )

        if omitidos:

            self.message_user(
                request,
                (
                    f"Se omitieron {omitidos} lote(s) "
                    "que ya estaban cerrados."
                ),
                level=messages.WARNING,
            )

        if errores:

            self.message_user(
                request,
                "No fue posible cerrar algunos lotes: "
                + " | ".join(errores),
                level=messages.ERROR,
            )

    # ------------------------------------------------------
    # ESTADO VISUAL
    # ------------------------------------------------------

    @admin.display(
        description="Estado",
        ordering="abierto",
    )
    def mostrar_estado(self, obj):

        if obj.abierto:

            return format_html(
                '<span style="color:green;font-weight:bold;">'
                'ABIERTO</span>'
            )

        return format_html(
            '<span style="color:gray;font-weight:bold;">'
            'CERRADO</span>'
        )

    # ------------------------------------------------------
    # IDENTIFICAR PERSONA DEL USUARIO AUTENTICADO
    # ------------------------------------------------------

    def obtener_persona(self, request):

        try:

            empleado = request.user.perfil_empleado

        except Empleado.DoesNotExist:

            raise ValidationError(
                "El usuario autenticado no tiene un empleado "
                "asociado. No es posible realizar esta operación."
            )

        if not empleado.activo:

            raise ValidationError(
                "El empleado asociado al usuario está inactivo."
            )

        if not empleado.persona.activo:

            raise ValidationError(
                "La persona asociada al empleado está inactiva."
            )

        return empleado.persona

    # ------------------------------------------------------
    # CONTROL DE CAMPOS EDITABLES
    # ------------------------------------------------------

    def get_readonly_fields(self, request, obj=None):

        campos = list(
            super().get_readonly_fields(request, obj)
        )

        if obj:

            campos.extend([
                "lote_huerta",
                "variedad",
            ])

            if not obj.abierto:
                campos.append("observaciones")

        return tuple(set(campos))

    # ------------------------------------------------------
    # GUARDAR Y ABRIR AUTOMÁTICAMENTE
    # ------------------------------------------------------

    def save_model(self, request, obj, form, change):

        if change:

            super().save_model(
                request,
                obj,
                form,
                change,
            )

            return

        with transaction.atomic():

            persona = self.obtener_persona(request)

            # Guardar el registro.
            obj.save()

            # Abrirlo y calcular maximo_cajones.
            # Si falla cualquier validación, se revierte
            # también la creación del registro.
            obj.abrir(persona)

    # ------------------------------------------------------
    # PERMISOS
    # ------------------------------------------------------

    def has_delete_permission(self, request, obj=None):
        return False
