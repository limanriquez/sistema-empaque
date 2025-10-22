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


app_name = 'operaciones'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('clientes/', clientes, name="clientes"),
    path('comandaPorZona/', comandaPorZona, name="comandaPorZona"),
    path('imprimir_ticket_venta/', imprimirTicketVenta, name="imprimirTicketVenta"),
    path('punto_de_venta/', punto_de_venta, name="punto_de_venta"),
    path('existeTelefono/<str:telefono>/', existeTelefono, name="existeTelefono"),
    path('ventas_abiertas_corte_empresas/', ventasAbiertasCorteEmpresas, name='ventasAbiertasCorteEmpresas'),
    path('transaccion_venta_producto/', transaccionVentaProducto, name='transaccionVentaProducto'),
    path('transaccion_cancelar_desglose_venta/', transaccionCancelarDesgloseVenta, name='transaccionCancelarDesgloseVenta'),
    path('productos_venta/', productosVenta, name='productosVenta'),
    path('pagos_por_venta/', pagosPorVenta, name='pagosPorVenta'),
    path('comandas_pendientes/', comandasPendientes, name='comandasPendientes'),
    path('cortes_por_empresa/', cortesPorEmpresa, name='cortesPorEmpresa'),
    path('ventas_por_corte_caja/', ventasPorCorteCaja, name='ventasPorCorteCaja'),
    path('corteCajaAbierto/', corteCajaAbierto, name='corteCajaAbierto'),
    path('corte_caja/', corte_caja, name='corte_caja'),
    
  #  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]