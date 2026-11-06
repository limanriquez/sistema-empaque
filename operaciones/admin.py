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

from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse

from personas.models import Empleado
from django.db.models import Q
from django.db.models import Count

from .forms import (
    ComponenteEmpaqueForm,
    ComponenteEmpaqueFormSet,
    ProductoEmpaqueForm,
    OperacionDiariaForm,
    TarimaAdminForm
)
from .models import (
    ComponenteEmpaque,
    ProductoEmpaque,
    OperacionDiaria,
    LoteEmpaque,
    EmpleadosPuestoOperacion,
    OperacionLoteEmpaque,
    Tarima,
)


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
# ADMINISTRADOR: OPERACIÓN DIARIA
#
# RESPONSABILIDADES:
# - Registrar operaciones diarias pendientes.
# - Consultar el estado de las jornadas.
# - Iniciar una operación diaria.
# - Cerrar una operación diaria.
# - Confirmar la continuidad del LoteEmpaque abierto.
# - Advertir sobre tarimas que permanecen abiertas.
#
# REGLAS:
# - Una operación se registra inicialmente como pendiente.
# - El inicio se ejecuta exclusivamente mediante iniciar().
# - El cierre se ejecuta exclusivamente mediante cerrar().
# - No se permite eliminar operaciones.
# - El cierre diario no cierra automáticamente el lote.
# - Las tarimas abiertas no impiden cerrar la jornada.
# ==========================================================

@admin.register(OperacionDiaria)
class OperacionDiariaAdmin(admin.ModelAdmin):
    # ------------------------------------------------------
    # FORMULARIO
    # ------------------------------------------------------

    form = OperacionDiariaForm

    # ------------------------------------------------------
    # LISTADO
    # ------------------------------------------------------

    list_display = (
        "id",
        "fecha",
        "estado_operacion",
        "hora_apertura",
        "hora_cierre",
        "abierto_por",
        "cerrado_por",
    )

    list_filter = (
        "abierta",
        "iniciada",
        "fecha",
    )

    search_fields = (
        "id",
        "observaciones",
        "abierto_por__nombres",
        "cerrado_por__nombres",
    )

    ordering = (
        "-fecha",
        "-id",
    )

    # ------------------------------------------------------
    # ACCIONES
    # ------------------------------------------------------

    actions = (
        "iniciar_operacion",
        "cerrar_operacion",
    )

    # ------------------------------------------------------
    # CAMPOS DE SOLO LECTURA
    # ------------------------------------------------------

    readonly_fields = (
        "abierta",
        "iniciada",
        "hora_apertura",
        "hora_cierre",
        "abierto_por",
        "cerrado_por",
    )

    # ------------------------------------------------------
    # ORGANIZACIÓN DEL FORMULARIO
    # ------------------------------------------------------

    fieldsets = (
        (
            "Información de la jornada",
            {
                "fields": (
                    "fecha",
                    "observaciones",
                )
            },
        ),
        (
            "Control de operación",
            {
                "fields": (
                    "abierta",
                    "iniciada",
                    "hora_apertura",
                    "hora_cierre",
                    "abierto_por",
                    "cerrado_por",
                )
            },
        ),
    )

    # ======================================================
    # CONSULTAS
    # ======================================================

    def get_queryset(self, request):

        return (
            super()
            .get_queryset(request)
            .select_related(
                "abierto_por",
                "cerrado_por",
            )
        )

    # ======================================================
    # ESTADO DE LA OPERACIÓN
    # ======================================================

    @admin.display(
        description="Estado",
        ordering="iniciada",
    )
    def estado_operacion(self, obj):

        if obj.pendiente:
            return "Pendiente"

        if obj.activa:
            return "Activa"

        if obj.cerrada:
            return "Cerrada"

        return "Estado desconocido"

    # ======================================================
    # IDENTIFICACIÓN DE LA PERSONA AUTENTICADA
    # ======================================================

    def obtener_persona(self, request):

        try:
            empleado = request.user.perfil_empleado

        except Empleado.DoesNotExist:
            raise ValidationError(
                "El usuario autenticado no tiene un empleado asociado."
            )

        if not empleado.activo:
            raise ValidationError(
                "El empleado asociado al usuario está inactivo."
            )

        return empleado.persona

    # ======================================================
    # MENSAJES DE VALIDACIÓN
    # ======================================================

    def mostrar_error(self, request, error):

        if isinstance(error, ValidationError):
            for mensaje in error.messages:
                self.message_user(
                    request,
                    mensaje,
                    level=messages.ERROR,
                )
        else:
            self.message_user(
                request,
                str(error),
                level=messages.ERROR,
            )

    # ======================================================
    # VALIDAR SELECCIÓN INDIVIDUAL
    # ======================================================

    def obtener_operacion_seleccionada(self, request, queryset):

        if queryset.count() != 1:

            self.message_user(
                request,
                "Debe seleccionar una sola operación diaria.",
                level=messages.ERROR,
            )

            return None

        return queryset.first()

       # ======================================================
    # ACCIÓN: INICIAR OPERACIÓN
    # ======================================================

    @admin.action(
        description="Iniciar operación seleccionada",
    )
    def iniciar_operacion(self, request, queryset):

        # --------------------------------------------------
        # VALIDAR SELECCIÓN INDIVIDUAL
        # --------------------------------------------------

        operacion = self.obtener_operacion_seleccionada(
            request,
            queryset,
        )

        if operacion is None:
            return None

        # --------------------------------------------------
        # VALIDAR ESTADO DE LA OPERACIÓN
        # --------------------------------------------------

        if not operacion.pendiente:

            self.message_user(
                request,
                "Solamente se pueden iniciar operaciones pendientes.",
                level=messages.ERROR,
            )

            return None

        # --------------------------------------------------
        # BUSCAR EL LOTE DE EMPAQUE ABIERTO
        # --------------------------------------------------

        lote = (
            LoteEmpaque.objects
            .filter(abierto=True)
            .first()
        )

        if lote is None:

            self.message_user(
                request,
                "No existe un lote de empaque abierto. "
                "Debe abrir un lote antes de iniciar la operación.",
                level=messages.ERROR,
            )

            return None

        # --------------------------------------------------
        # CONFIRMAR E INICIAR OPERACIÓN
        # --------------------------------------------------

        if request.POST.get("confirmar_inicio") == "1":

            try:

                # Obtener la persona asociada al usuario autenticado.
                persona = self.obtener_persona(request)

                # El modelo se encarga de:
                # - Preparar las estaciones de trabajo.
                # - Recuperar las asignaciones anteriores.
                # - Evitar registros duplicados.
                # - Validar empleados activos.
                # - Iniciar la operación si existe personal.
                iniciado = operacion.iniciar(
                    persona=persona,
                    lote_empaque=lote,
                )

                # --------------------------------------------------
                # CONTAR ESTACIONES REGISTRADAS
                # --------------------------------------------------

                asignaciones = (
                    EmpleadosPuestoOperacion.objects
                    .filter(
                        operacion_diaria=operacion,
                        estacion_trabajo__isnull=False,
                    )
                )

                total_estaciones = asignaciones.count()

                # --------------------------------------------------
                # CONTAR ESTACIONES VACANTES
                # --------------------------------------------------

                estaciones_vacantes = (
                    asignaciones
                    .filter(
                        Q(empleado__isnull=True)
                        | Q(empleado__activo=False)
                        | Q(empleado__persona__activo=False)
                    )
                    .count()
                )

                # --------------------------------------------------
                # RESULTADO: OPERACIÓN INICIADA
                # --------------------------------------------------

                if iniciado:

                    self.message_user(
                        request,
                        (
                            f"Operación diaria #{operacion.pk} "
                            f"iniciada correctamente con el lote {lote}."
                        ),
                        level=messages.SUCCESS,
                    )

                    # Advertir sobre estaciones sin empleado.
                    if estaciones_vacantes:

                        self.message_user(
                            request,
                            (
                                f"Advertencia: existen "
                                f"{estaciones_vacantes} de "
                                f"{total_estaciones} estaciones "
                                "sin empleado asignado."
                            ),
                            level=messages.WARNING,
                        )

                # --------------------------------------------------
                # RESULTADO: ESTACIONES PREPARADAS
                # PERO OPERACIÓN TODAVÍA PENDIENTE
                # --------------------------------------------------

                else:

                    self.message_user(
                        request,
                        (
                            f"Se prepararon {total_estaciones} "
                            "estaciones de trabajo. La operación "
                            "permanece pendiente porque no existen "
                            "empleados activos asignados. "
                            "Realice las asignaciones desde "
                            "Empleados por puesto de operación "
                            "y vuelva a iniciar."
                        ),
                        level=messages.WARNING,
                    )

            except (
                ValidationError,
                Empleado.DoesNotExist,
            ) as error:

                self.mostrar_error(
                    request,
                    error,
                )

            return None

        # --------------------------------------------------
        # MOSTRAR CONFIRMACIÓN ANTES DE INICIAR
        # --------------------------------------------------

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Confirmar inicio de operación diaria",
            "operacion": operacion,
            "lote": lote,
            "action_name": "iniciar_operacion",
            "selected_ids": [operacion.pk],
            "action_checkbox_name": ACTION_CHECKBOX_NAME,
            "media": self.media,
        }

        return TemplateResponse(
            request,
            "operaciones/operaciondiaria/confirmar_inicio.html",
            context,
        )

    # ======================================================
    # ACCIÓN: CERRAR OPERACIÓN
    # ======================================================

    @admin.action(
        description="Cerrar operación seleccionada",
    )
    def cerrar_operacion(self, request, queryset):

        operacion = self.obtener_operacion_seleccionada(
            request,
            queryset,
        )

        if operacion is None:
            return None

        if not operacion.activa:

            self.message_user(
                request,
                "Solamente se pueden cerrar operaciones activas.",
                level=messages.ERROR,
            )

            return None

        # Obtener el lote relacionado con la jornada.
        relacion = (
            OperacionLoteEmpaque.objects
            .filter(operacion_diaria=operacion)
            .select_related("lote_empaque")
            .first()
        )

        # Contar tarimas abiertas de esta operación.
        tarimas_abiertas = Tarima.objects.filter(
            operacion_lote_empaque__operacion_diaria=operacion,
            abierta=True,
        ).count()

        # Si se confirmó el cierre, ejecutar el método del modelo.
        if request.POST.get("confirmar_cierre") == "1":

            try:

                persona = self.obtener_persona(request)

                operacion.cerrar(persona)

                if request.POST.get("recordar_cierre_lote") == "si":

                    self.message_user(
                        request,
                        (
                            "Operación diaria cerrada correctamente. "
                            "Recuerde cerrar manualmente el LoteEmpaque "
                            "desde su propia administración."
                        ),
                        level=messages.WARNING,
                    )

                else:

                    self.message_user(
                        request,
                        (
                            "Operación diaria cerrada correctamente. "
                            "El LoteEmpaque permanece abierto."
                        ),
                        level=messages.SUCCESS,
                    )

                if tarimas_abiertas:

                    self.message_user(
                        request,
                        (
                            f"Advertencia: existen {tarimas_abiertas} "
                            "tarimas abiertas. Permanecen abiertas "
                            "para continuar su proceso."
                        ),
                        level=messages.WARNING,
                    )

            except ValidationError as error:

                self.mostrar_error(request, error)

            return None

        # Mostrar confirmación antes de cerrar.
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Confirmar cierre de operación diaria",
            "operacion": operacion,
            "relacion": relacion,
            "tarimas_abiertas": tarimas_abiertas,
            "action_name": "cerrar_operacion",
            "selected_ids": [operacion.pk],
            "action_checkbox_name": ACTION_CHECKBOX_NAME,
            "media": self.media,
        }

        return TemplateResponse(
            request,
            "operaciones/operaciondiaria/confirmar_cierre.html",
            context,
        )

    # ======================================================
    # SEGURIDAD
    # ======================================================

    def has_delete_permission(self, request, obj=None):

        # Las operaciones diarias forman parte de la trazabilidad
        # histórica. No se permite su eliminación física.
        return False
    
    # ======================================================
    # CONTROL DE CREACIÓN
    # ======================================================

    def has_add_permission(self, request):

        # Solo puede existir una operación diaria vigente:
        # pendiente o activa.
        operacion_vigente = OperacionDiaria.objects.filter(
            Q(iniciada=False) | Q(abierta=True)
        ).exists()

        return (
            super().has_add_permission(request)
            and not operacion_vigente
        )



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





# ==========================================================
# ADMINISTRADOR: EMPLEADOS POR PUESTO DE OPERACIÓN
#
# Administra la distribución del personal en las estaciones
# de trabajo de una operación diaria.
#
# FUNCIONALIDAD:
# - Consultar una operación diaria mediante un selector.
# - Mostrar únicamente sus estaciones registradas.
# - Consultar resumen de estaciones y empleados asignados.
# - Asignar empleados activos y disponibles.
# - Reasignar empleados mediante edición del registro.
# - Liberar empleados sin eliminar registros.
# - Consultar operaciones cerradas sin modificarlas.
#
# REGLAS:
# - No permite crear ni eliminar asignaciones manualmente.
# - Las estaciones se generan desde OperacionDiaria.iniciar().
# - Un empleado no puede ocupar dos estaciones dentro
#   de la misma operación.
# - Los empleados asignados a otras estaciones no aparecen
#   como opciones disponibles.
# - Las operaciones cerradas son de solo lectura.
# ==========================================================

@admin.register(EmpleadosPuestoOperacion)
class EmpleadosPuestoOperacionAdmin(admin.ModelAdmin):

    # ------------------------------------------------------
    # CONFIGURACIÓN DEL LISTADO
    # ------------------------------------------------------

    change_list_template = (
        "operaciones/empleadospuestooperacion/change_list.html"
    )

    list_display = (
        "id",
        "operacion_diaria",
        "estacion_trabajo",
        "empleado",
        "estado_asignacion",
    )

    list_display_links = ("id",)

    # El empleado se puede cambiar directamente en la tabla.
    # Dejar el combo vacío significa liberar la estación.
    list_editable = (
        "empleado",
    )

    ordering = (
        "estacion_trabajo__nombre",
        "id",
    )

    list_per_page = 100

    actions = (
        "quitar_empleados",
    )

    # ======================================================
    # PERMITIR FILTRO PERSONALIZADO DE OPERACIÓN
    # ======================================================

    def lookup_allowed(self, lookup, value, request):

        if lookup == "operacion_diaria__id__exact":
            return True

        return super().lookup_allowed(
            lookup,
            value,
            request,
        )

    # ======================================================
    # CONSULTAR SOLAMENTE LA OPERACIÓN SELECCIONADA
    # ======================================================

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        operacion_id = request.GET.get(
            "operacion_diaria__id__exact"
        )

        # No cargar asignaciones mientras no se seleccione
        # una operación diaria.
        if not operacion_id:
            return queryset.none()

        try:

            operacion_id = int(operacion_id)

        except (TypeError, ValueError):

            return queryset.none()

        return (
            queryset
            .filter(
                operacion_diaria_id=operacion_id
            )
            .select_related(
                "operacion_diaria",
                "estacion_trabajo",
                "empleado",
                "empleado__persona",
            )
        )

    # ======================================================
    # FORMULARIO EDITABLE DE CADA FILA
    # ======================================================
    

    def get_changelist_form(self, request, **kwargs):

        FormClass = super().get_changelist_form(
            request,
            **kwargs,
        )

        class FormAsignacion(FormClass):

            def __init__(self, *args, **form_kwargs):

                super().__init__(
                    *args,
                    **form_kwargs,
                )

                if "empleado" not in self.fields:
                    return

                asignacion = self.instance

                if not asignacion.pk:
                    return

                # --------------------------------------------------
                # EMPLEADOS OCUPADOS EN OTRAS ESTACIONES
                # --------------------------------------------------

                empleados_ocupados = (
                    EmpleadosPuestoOperacion.objects
                    .filter(
                        operacion_diaria_id=(
                            asignacion.operacion_diaria_id
                        ),
                        empleado__isnull=False,
                    )
                    .exclude(
                        pk=asignacion.pk
                    )
                    .values_list(
                        "empleado_id",
                        flat=True,
                    )
                )

                # --------------------------------------------------
                # EMPLEADOS ACTIVOS Y DISPONIBLES
                # --------------------------------------------------

                empleados_disponibles = (
                    Empleado.objects
                    .filter(
                        Q(
                            activo=True,
                            persona__activo=True,
                        )
                        | Q(
                            pk=asignacion.empleado_id,
                        )
                    )
                    .exclude(
                        pk__in=empleados_ocupados
                    )
                    .distinct()
                    .order_by("id")
                )

                campo = self.fields["empleado"]

                campo.queryset = empleados_disponibles

                campo.empty_label = (
                    "— Sin empleado asignado —"
                )

                # --------------------------------------------------
                # OCULTAR ACCESOS DEL CAMPO RELACIONADO
                # No afecta el selector ni su guardado.
                # --------------------------------------------------

                widget = campo.widget

                widget.can_add_related = False
                widget.can_change_related = False
                widget.can_delete_related = False
                widget.can_view_related = False

                # --------------------------------------------------
                # OPERACIONES CERRADAS: SOLO LECTURA
                # --------------------------------------------------

                if asignacion.operacion_diaria.cerrada:

                    campo.disabled = True

        return FormAsignacion

    # ======================================================
    # CONTEXTO Y RESUMEN DE OPERACIÓN DIARIA
    # ======================================================

    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}

        # --------------------------------------------------
        # CONSULTAR OPERACIONES DIARIAS
        # --------------------------------------------------

        operaciones = (
            OperacionDiaria.objects
            .all()
            .order_by("-fecha", "-id")
        )

        # --------------------------------------------------
        # RECUPERAR OPERACIÓN SELECCIONADA
        # --------------------------------------------------

        operacion_id = request.GET.get(
            "operacion_diaria__id__exact",
            "",
        )

        operacion_seleccionada = None

        if operacion_id:

            try:

                operacion_seleccionada = (
                    OperacionDiaria.objects
                    .filter(
                        pk=int(operacion_id)
                    )
                    .first()
                )

            except (TypeError, ValueError):

                operacion_seleccionada = None

        # --------------------------------------------------
        # INICIALIZAR CONTADORES
        # --------------------------------------------------

        total_estaciones = 0
        empleados_asignados = 0
        estaciones_vacantes = 0

        # --------------------------------------------------
        # CALCULAR RESUMEN DE LA OPERACIÓN
        # --------------------------------------------------

        if operacion_seleccionada:

            resumen = (
                EmpleadosPuestoOperacion.objects
                .filter(
                    operacion_diaria=operacion_seleccionada,
                    estacion_trabajo__isnull=False,
                )
                .aggregate(
                    total_estaciones=Count(
                        "estacion_trabajo_id",
                        distinct=True,
                    ),
                    empleados_asignados=Count(
                        "empleado_id",
                        distinct=True,
                    ),
                )
            )

            total_estaciones = (
                resumen["total_estaciones"] or 0
            )

            empleados_asignados = (
                resumen["empleados_asignados"] or 0
            )

            estaciones_vacantes = (
                total_estaciones - empleados_asignados
            )

        # --------------------------------------------------
        # PREPARAR CONTEXTO PARA LA PLANTILLA
        # --------------------------------------------------

        extra_context.update({

            "operaciones_disponibles": operaciones,

            "operacion_seleccionada": operacion_seleccionada,

            "operacion_seleccionada_id": (
                str(operacion_seleccionada.pk)
                if operacion_seleccionada
                else ""
            ),

            "total_estaciones": total_estaciones,

            "empleados_asignados": empleados_asignados,

            "estaciones_vacantes": estaciones_vacantes,

        })

        # --------------------------------------------------
        # PROCESAR CONSULTA O GUARDADO
        # --------------------------------------------------

        if request.method == "POST":

            # El guardado de las asignaciones debe ejecutarse
            # dentro de una sola transacción.
            with transaction.atomic():

                response = super().changelist_view(
                    request,
                    extra_context=extra_context,
                )

        else:

            response = super().changelist_view(
                request,
                extra_context=extra_context,
            )

        # Garantizar que las variables personalizadas
        # estén disponibles en la plantilla.
        if hasattr(response, "context_data"):

            response.context_data.update(
                extra_context
            )

        return response

    # ======================================================
    # ESTADO DE LA ASIGNACIÓN
    # ======================================================

    @admin.display(
        description="Estado",
    )
    def estado_asignacion(self, obj):

        if not obj.empleado_id:
            return "Vacante"

        if (
            not obj.empleado.activo
            or not obj.empleado.persona.activo
        ):
            return "Empleado inactivo"

        return "Asignado"

    # ======================================================
    # ACCIÓN: QUITAR EMPLEADOS
    # ======================================================

    @admin.action(
        description="Quitar empleados de las estaciones seleccionadas",
    )
    def quitar_empleados(self, request, queryset):

        operacion_id = request.GET.get(
            "operacion_diaria__id__exact"
        )

        if not operacion_id:

            self.message_user(
                request,
                "Primero debe seleccionar una operación diaria.",
                level=messages.ERROR,
            )

            return

        try:

            with transaction.atomic():

                # Bloquear la operación antes de modificar
                # cualquiera de sus asignaciones.
                operacion = (
                    OperacionDiaria.objects
                    .select_for_update()
                    .get(
                        pk=int(operacion_id)
                    )
                )

                if operacion.cerrada:

                    self.message_user(
                        request,
                        "No se pueden modificar asignaciones "
                        "de una operación diaria cerrada.",
                        level=messages.ERROR,
                    )

                    return

                # Bloquear los registros seleccionados.
                asignaciones = (
                    queryset
                    .select_for_update()
                    .filter(
                        operacion_diaria=operacion,
                        empleado__isnull=False,
                    )
                )

                # Obtener los identificadores de los registros.
                ids_asignaciones = list(
                    asignaciones.values_list(
                        "pk",
                        flat=True,
                    )
                )

                cantidad = len(ids_asignaciones)

                # Liberar las estaciones sin eliminar registros.
                if cantidad:

                    EmpleadosPuestoOperacion.objects.filter(
                        pk__in=ids_asignaciones,
                    ).update(
                        empleado=None
                    )

            if cantidad:

                self.message_user(
                    request,
                    (
                        f"Se liberaron {cantidad} estación(es). "
                        "Los registros permanecen asociados "
                        "a la operación diaria."
                    ),
                    level=messages.SUCCESS,
                )

            else:

                self.message_user(
                    request,
                    "Las estaciones seleccionadas ya estaban vacantes.",
                    level=messages.WARNING,
                )

        except (
            ValueError,
            OperacionDiaria.DoesNotExist,
        ):

            self.message_user(
                request,
                "La operación diaria seleccionada no es válida.",
                level=messages.ERROR,
            )

    # ======================================================
    # PERMISOS
    # ======================================================

    def has_add_permission(self, request):

        # Las asignaciones se generan automáticamente
        # al preparar las estaciones de la operación.
        return False

    def has_delete_permission(self, request, obj=None):

        # Nunca se eliminan registros de estaciones.
        return False

@admin.register(Tarima)
class TarimaAdmin(admin.ModelAdmin):

    form = TarimaAdminForm

    # ------------------------------------------------------
    # LISTADO
    # ------------------------------------------------------

    list_display = (
        "id",
        "codigo_tarima",
        "operacion_diaria",
        "capacidad_maxima",
        "tamano",
        "total_cajas_admin",
        "espacios_disponibles_admin",
        "estado_tarima",
        "seccion_almacen",
        "fecha_creacion",
    )

    list_display_links = ("id",)

    list_filter = (
        "abierta",
        "seccion_almacen",
    )

    ordering = (
        "-fecha_creacion",
        "-id",
    )

    list_per_page = 50

    # Acciones disponibles en el combo de Django Admin.
    actions = (
        "cerrar_tarimas",
    )

    actions_on_top = True
    actions_on_bottom = True

    # ======================================================
    # CAMPOS DEL FORMULARIO
    # ======================================================

    def get_fields(self, request, obj=None):

        if obj is None:

            return (
                "codigo_tarima_display",
                "codigo_tarima_id",
                "operacion_diaria_display",
                "capacidad_maxima",
                "tamano",
                "seccion_almacen",
            )

        return (
            "codigo_tarima_display",
            "operacion_diaria_display",
            "tamano",
            "seccion_almacen",
            "fecha_creacion",
            "capacidad_maxima",
            "abierta",
            "fecha_cierre",
            "abierta_por",
            "cerrada_por",
            "total_cajas_admin",
            "espacios_disponibles_admin",
        )

    # ======================================================
    # CAMPOS DE SOLO LECTURA
    # ======================================================

    def get_readonly_fields(self, request, obj=None):

        if obj is None:
            return ()

        return (
            "codigo_tarima_display",
            "operacion_diaria_display",
            "fecha_creacion",
            "capacidad_maxima",
            "abierta",
            "fecha_cierre",
            "abierta_por",
            "cerrada_por",
            "total_cajas_admin",
            "espacios_disponibles_admin",
        )

    # ======================================================
    # CONSULTA OPTIMIZADA
    # ======================================================

    def get_queryset(self, request):

        return (
            super()
            .get_queryset(request)
            .select_related(
                "codigo_tarima",
                "operacion_lote_empaque",
                "operacion_lote_empaque__operacion_diaria",
                "operacion_lote_empaque__lote_empaque",
                "tamano",
                "seccion_almacen",
                "abierta_por",
                "cerrada_por",
            )
        )

    # ======================================================
    # OPERACIÓN DIARIA
    # ======================================================

    @admin.display(
        description="Operación diaria",
        ordering=(
            "operacion_lote_empaque__operacion_diaria__fecha"
        ),
    )
    def operacion_diaria(self, obj):

        return obj.operacion_lote_empaque.operacion_diaria

    # ======================================================
    # TOTAL DE CAJAS
    # ======================================================

    @admin.display(description="Cajas registradas")
    def total_cajas_admin(self, obj):

        return obj.total_cajas

    # ======================================================
    # ESPACIOS DISPONIBLES
    # ======================================================

    @admin.display(description="Espacios disponibles")
    def espacios_disponibles_admin(self, obj):

        return obj.espacios_disponibles

    # ======================================================
    # ESTADO
    # ======================================================

    @admin.display(description="Estado")
    def estado_tarima(self, obj):

        if obj.abierta:

            return format_html(
                '<span style="'
                'background:#dcfce7;'
                'color:#166534;'
                'padding:4px 10px;'
                'border-radius:20px;'
                'font-weight:600;'
                '">Abierta</span>'
            )

        return format_html(
            '<span style="'
            'background:#fee2e2;'
            'color:#991b1b;'
            'padding:4px 10px;'
            'border-radius:20px;'
            'font-weight:600;'
            '">Cerrada</span>'
        )

    # ======================================================
    # RESPONSABLE
    # ======================================================

    def obtener_persona(self, request):

        return request.user.perfil_empleado.persona

    # ======================================================
    # GUARDAR TARIMA
    # ======================================================

    def save_model(self, request, obj, form, change):

        if change:

            super().save_model(
                request,
                obj,
                form,
                change,
            )

            return

        persona = self.obtener_persona(request)

        with transaction.atomic():

            # Crear mediante el método de negocio del modelo.
            # Este método consume el código y crea la tarima.

            tarima = Tarima.crear(
                codigo_tarima=(
                    form.cleaned_data["codigo_tarima_obj"]
                ),
                operacion_lote_empaque=(
                    form.cleaned_data["operacion_lote_empaque"]
                ),
                persona=persona,
                capacidad_maxima=(
                    form.cleaned_data["capacidad_maxima"]
                ),
            )

            # Información complementaria.

            tarima.tamano = form.cleaned_data.get("tamano")

            tarima.seccion_almacen = (
                form.cleaned_data.get("seccion_almacen")
            )

            tarima.full_clean()

            tarima.save(
                update_fields=[
                    "tamano",
                    "seccion_almacen",
                ]
            )

            # Actualizar instancia de Django Admin.

            obj.pk = tarima.pk
            obj._state.adding = False
            obj._state.db = tarima._state.db
            obj.refresh_from_db()

    # ======================================================
    # ACCIÓN: CERRAR TARIMAS SELECCIONADAS
    # ======================================================

    @admin.action(
        description="Cerrar tarimas seleccionadas"
    )
    def cerrar_tarimas(self, request, queryset):

        persona = self.obtener_persona(request)

        # Recuperar identificadores seleccionados.
        ids_tarimas = list(
            queryset.values_list(
                "pk",
                flat=True,
            )
        )

        cerradas = 0
        ya_cerradas = 0

        # Una transacción para toda la operación de cierre.
        with transaction.atomic():

            # Bloquear las tarimas seleccionadas.
            tarimas = (
                Tarima.objects
                .select_for_update()
                .filter(
                    pk__in=ids_tarimas
                )
                .order_by("pk")
            )

            for tarima in tarimas:

                # No modificar tarimas que ya estén cerradas.
                if not tarima.abierta:

                    ya_cerradas += 1
                    continue

                # Utilizar el método del modelo.
                # Registra automáticamente:
                # - abierta = False
                # - fecha_cierre = timezone.now()
                # - cerrada_por = persona

                tarima.cerrar(persona)

                cerradas += 1

        # --------------------------------------------------
        # NOTIFICACIONES
        # --------------------------------------------------

        if cerradas:

            self.message_user(
                request,
                (
                    f"Se cerraron correctamente {cerradas} "
                    f"tarima(s). La fecha, hora y responsable "
                    f"quedaron registrados automáticamente."
                ),
                level=messages.SUCCESS,
            )

        if ya_cerradas:

            self.message_user(
                request,
                (
                    f"{ya_cerradas} tarima(s) ya estaban cerradas "
                    f"y no fueron modificadas."
                ),
                level=messages.WARNING,
            )

        if not cerradas and not ya_cerradas:

            self.message_user(
                request,
                "No se encontraron tarimas para cerrar.",
                level=messages.WARNING,
            )

    # ======================================================
    # PERMISOS
    # ======================================================

    def has_delete_permission(self, request, obj=None):

        # No se permite eliminar tarimas.
        return False