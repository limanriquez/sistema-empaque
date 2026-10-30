
from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join

from .forms import (
    MaterialForm,
    EntradaInventarioForm,
    SalidaInventarioForm,
    TraspasoAlmacenForm,
    TraspasoClienteForm,
)

from .models import (
    ExistenciaMaterial,
    Material,
    MovimientoInventario,
)

from .services import registrar_movimiento


# ============================================================
# MATERIALES
# ============================================================

# Administra el catálogo general de materiales.
# No administra existencias ni stock mínimo.
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):

    form = MaterialForm

    list_display = (
        "id",
        "codigo",
        "nombre",
        "unidad_medida",
        "activo",
    )

    list_display_links = ("id", "nombre")

    list_select_related = ("unidad_medida",)

    list_filter = ("activo", "unidad_medida")

    search_fields = (
        "codigo",
        "nombre",
        "descripcion",
    )

    fields = (
        "codigo",
        "nombre",
        "descripcion",
        "unidad_medida",
        "activo",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("unidad_medida",)
        return ()

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# EXISTENCIAS
# ============================================================

# Consulta de existencias por material, sección y propietario.
# Es de solo lectura. Los saldos se actualizan mediante movimientos.
@admin.register(ExistenciaMaterial)
class ExistenciaMaterialAdmin(admin.ModelAdmin):

    list_display = (
        "material",
        "cliente",
        "almacen",
        "espacio",
        "seccion",
        "cantidad",
        "stock_minimo",
    )

    list_select_related = (
        "material",
        "cliente__persona",
        "seccion__espacio__almacen",
    )

    list_filter = (
        "cliente",
        "seccion__espacio__almacen",
        "seccion__espacio",
    )

    search_fields = (
        "material__nombre",
        "material__codigo",
        "seccion__nombre",
        "cliente__persona__razon_social",
        "cliente__persona__nombre_comercial",
        "cliente__persona__nombres",
        "cliente__persona__apellido_paterno",
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


# ============================================================
# MOVIMIENTOS DE INVENTARIO
# ============================================================

# Administra el libro histórico de movimientos.
# Las capturas se realizan mediante cuatro formularios especializados.
# Los movimientos registrados no se editan ni se eliminan.
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):

    form = EntradaInventarioForm

    list_display = (
        "id",
        "fecha",
        "tipo",
        "material",
        "mostrar_cantidad",
        "ubicacion_origen",
        "propietario_origen",
        "ubicacion_destino",
        "propietario_destino",
        "proveedor",
        "documento",
    )

    list_display_links = None

    date_hierarchy = "fecha"

    list_select_related = (
        "material__unidad_medida",
        "ubicacion_origen__espacio__almacen",
        "ubicacion_destino__espacio__almacen",
        "propietario_origen__persona",
        "propietario_destino__persona",
        "proveedor__persona",
    )

    list_filter = (
        "tipo",
        "fecha",
        "material__unidad_medida",
        "propietario_origen",
        "propietario_destino",
    )

    search_fields = (
        "material__nombre",
        "material__codigo",
        "documento",
        "descripcion",
        "propietario_origen__persona__razon_social",
        "propietario_origen__persona__nombre_comercial",
        "propietario_origen__persona__nombres",
        "propietario_origen__persona__apellido_paterno",
        "propietario_destino__persona__razon_social",
        "propietario_destino__persona__nombre_comercial",
        "propietario_destino__persona__nombres",
        "propietario_destino__persona__apellido_paterno",
        "proveedor__persona__razon_social",
        "proveedor__persona__nombre_comercial",
        "proveedor__persona__nombres",
        "proveedor__persona__apellido_paterno",
    )

    # --------------------------------------------------------
    # FORMULARIOS SEGÚN LA OPERACIÓN
    # --------------------------------------------------------

    formularios_operacion = {
        "entrada": EntradaInventarioForm,
        "salida": SalidaInventarioForm,
        "traspaso_almacen": TraspasoAlmacenForm,
        "traspaso_cliente": TraspasoClienteForm,
    }

    titulos_operacion = {
        "entrada": "Registrar entrada de materiales",
        "salida": "Registrar salida de materiales",
        "traspaso_almacen": "Traspaso entre almacenes",
        "traspaso_cliente": "Traspaso entre clientes",
    }

    # --------------------------------------------------------
    # RUTAS PERSONALIZADAS
    # --------------------------------------------------------

    def get_urls(self):

        urls = super().get_urls()

        urls_personalizadas = [
            path(
                "entrada/",
                self.admin_site.admin_view(self.entrada_view),
                name="inventarios_movimientoinventario_entrada",
            ),
            path(
                "salida/",
                self.admin_site.admin_view(self.salida_view),
                name="inventarios_movimientoinventario_salida",
            ),
            path(
                "traspaso-almacen/",
                self.admin_site.admin_view(self.traspaso_almacen_view),
                name="inventarios_movimientoinventario_traspaso_almacen",
            ),
            path(
                "traspaso-cliente/",
                self.admin_site.admin_view(self.traspaso_cliente_view),
                name="inventarios_movimientoinventario_traspaso_cliente",
            ),
        ]

        return urls_personalizadas + urls

    # --------------------------------------------------------
    # VISTAS DE CAPTURA
    # --------------------------------------------------------

    def entrada_view(self, request):
        return self._vista_operacion(request, "entrada")

    def salida_view(self, request):
        return self._vista_operacion(request, "salida")

    def traspaso_almacen_view(self, request):
        return self._vista_operacion(request, "traspaso_almacen")

    def traspaso_cliente_view(self, request):
        return self._vista_operacion(request, "traspaso_cliente")

    def _vista_operacion(self, request, operacion):

        request._operacion_inventario = operacion

        return self.add_view(
            request,
            form_url="",
            extra_context={
                "title": self.titulos_operacion[operacion],
                "titulo_operacion": self.titulos_operacion[operacion],
                "operacion_inventario": operacion,
            },
        )

    # --------------------------------------------------------
    # SELECCIÓN DEL FORMULARIO
    # --------------------------------------------------------

    def get_form(self, request, obj=None, **kwargs):

        if obj is None:

            operacion = getattr(
                request,
                "_operacion_inventario",
                "entrada",
            )

            formulario = self.formularios_operacion.get(
                operacion,
                EntradaInventarioForm,
            )

            kwargs["form"] = formulario

        return super().get_form(request, obj, **kwargs)

    # --------------------------------------------------------
    # NAVEGACIÓN DEL HISTORIAL
    # --------------------------------------------------------

    def changelist_view(self, request, extra_context=None):

        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        if request.method == "GET" and self.has_add_permission(request):

            enlaces = [
                (
                    reverse(
                        "admin:inventarios_movimientoinventario_entrada"
                    ),
                    "Registrar entrada",
                ),
                (
                    reverse(
                        "admin:inventarios_movimientoinventario_salida"
                    ),
                    "Registrar salida",
                ),
                (
                    reverse(
                        "admin:inventarios_movimientoinventario_traspaso_almacen"
                    ),
                    "Traspaso entre almacenes",
                ),
                (
                    reverse(
                        "admin:inventarios_movimientoinventario_traspaso_cliente"
                    ),
                    "Traspaso entre clientes",
                ),
            ]

            botones = format_html(
                '<style>'
                '.object-tools {{ display: none !important; }}'
                '</style>'
                '<div style="display:flex; flex-wrap:wrap; gap:10px;">'
                '{}'
                '</div>',
                format_html_join(
                    "",
                    '<a href="{}" style="display:inline-block; '
                    'padding:9px 14px; '
                    'background-color:#198754; '
                    'color:#ffffff; '
                    'border-radius:5px; '
                    'text-decoration:none; '
                    'font-weight:500;">'
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
    # REGISTRO DEL MOVIMIENTO
    # --------------------------------------------------------

    def save_model(self, request, obj, form, change):

        obj.creado_por = request.user

        # El servicio registra el movimiento y actualiza las existencias
        # dentro de una sola transacción.
        registrar_movimiento(obj)

    # --------------------------------------------------------
    # PRESENTACIÓN
    # --------------------------------------------------------

    @admin.display(
        description="Cantidad",
        ordering="cantidad",
    )
    def mostrar_cantidad(self, obj):

        return (
            f"{obj.cantidad:,.3f} "
            f"{obj.material.unidad_medida.abreviatura}"
        )

    # --------------------------------------------------------
    # PROTECCIÓN DEL HISTORIAL
    # --------------------------------------------------------

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


    