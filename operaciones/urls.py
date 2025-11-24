from operaciones.views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
#from django.contrib.auth import views as auth_views

#router = DefaultRouter()
#router.register('catalogoElementoInventario',CatalogoElementoInventarioViewSet)
router = DefaultRouter()
router.register('clientes',ClientesViewSet)
router.register('ventas',VentasViewSet)
router.register('pagoVenta',PagoVentaViewSet)
router.register('egreso',EgresoViewSet)
router.register('ingreso', IngresoViewSet)
router.register('notificacionZona',NotificacionZonaSerializerViewSet)
router.register('corteCaja',CorteCajaViewSet)



app_name = 'operaciones'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('clientes/', clientes, name="clientes"),
    path('reporte_top_cinco/', reporte_top_cinco, name="reporte_top_cinco"),
    path('comandaPorZona/', comandaPorZona, name="comandaPorZona"),
    path('imprimir_ticket_venta/', imprimirTicketVenta, name="imprimirTicketVenta"),
    path('punto_de_venta/', punto_de_venta, name="punto_de_venta"),
     path('punto_de_venta_movil/', punto_de_venta_movil, name="punto_de_venta_movil"),
    path('existeTelefono/<str:telefono>/', existeTelefono, name="existeTelefono"),
    path('ventas_abiertas_corte_empresas/', ventasAbiertasCorteEmpresas, name='ventasAbiertasCorteEmpresas'),
    path('transaccion_venta_producto/', transaccionVentaProducto, name='transaccionVentaProducto'),
    path('transaccion_cancelar_desglose_venta/', transaccionCancelarDesgloseVenta, name='transaccionCancelarDesgloseVenta'),
    path('productos_venta/', productosVenta, name='productosVenta'),
    path('pagos_por_venta/', pagosPorVenta, name='pagosPorVenta'),
    path('comandas_pendientes/', comandasPendientes, name='comandasPendientes'),
    path('cortes_por_empresa/', cortesPorEmpresa, name='cortesPorEmpresa'),
    path('ventas_por_corte_caja/', ventasPorCorteCaja, name='ventasPorCorteCaja'),
    path('egresos_por_corte/', egresosPorCorte, name='egresosPorCorte'),
    path('ingresos_por_corte/', ingresosPorCorte, name='ingresosPorCorte'),
    path('corteCajaAbierto/', corteCajaAbierto, name='corteCajaAbierto'),
    path('cortesCajaCerrados/', cortesCajaCerrados, name='cortesCajaCerrados'),
    path('corte_caja/', corte_caja, name='corte_caja'),
    path('corte_caja_pdf/<int:corte_id>/', generar_pdf_corte_caja, name='corte_caja_pdf'),
    path('buscar_cliente_por_telefono/', buscarClientePorTelefono, name='buscarClientePorTelefono'),
    path('guardar_envio_domicilio/', guardarEnvioDomicilio, name='guardarEnvioDomicilio'),
    path('modificar_envio_domicilio/', modificarEnvioDomicilio, name='modificarEnvioDomicilio'),
    path('consultar_Envio_Domicilio/', consultarEnvioDomicilio, name='consultarEnvioDomicilio'), 
  #  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]