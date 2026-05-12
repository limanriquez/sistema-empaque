// panel.controller.js
(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers', [])
        .controller('PuntoVenta', PuntoVentaController);
    PuntoVentaController.$inject = ['$http', '$scope', '$filter'];

    function PuntoVentaController($http, $scope, $filter) {
        var gridDesgloseVentaInstance, CmbMesaInstance, BtnCrearVentaInstance, CmbClienteInstance, PopPagosInstance,
            BtnRegresarInstance, CmbMetodoPagoInstance, BtnPagarInstance, gridDesglosePagoVentaInstance, BtnImprimirInstance,
            BtnEnviarVentaInstance, BtnCancelarVentaInstance, BtnBuscarVentaInstance, gridVentasPorCorteInstance,
            CmbCortesInstance, PopBuscarVentasInstance, BtnRegresarCortesInstance, BtnBuscarVentasInstance,
            BtnHomeOptionsInstance, BtnEgresosInstance, BtnIngresosInstance, gridEgresosPorCorteInstance,
            popEgresosInstance, verEgresosInstance, BtnCerrarEgresosInstance, popIngresosInstance,
            BtnCerrarIngresosInstance, gridIngresosPorCorteInstance, verIngresosInstance,
            BtnInformacionEnvioInstance, popEnvioDomicilioInstance, BtnCerrarDomicilioInstance,
            BtnGuardarDomicilioInstance, txtTelefonoInstance, txtNombreInstance, txtAPInstance,
            txtAMInstance;

        var ArrayDesgloseVenta = [], ArrayMesa = [], ArrayEmpresasVenta = [], ArrayClientes = [], ArrayMetodoPago = [],
            ArrayPagosPorVenta = [], ArrayVentasCorte = [], ArrayCortes = [], ArrayEgresosPorCorte = [], ArrayIngresosPorCorte = [];
        var strEmpresasVenta = ""
        var vm = this;
        var tab = 0;
        var idVentaActiva = 0;
        var existePago = false;
        var fullVentaActiva = null;
        var desgloseVentaSeleccionado;
        var pagoSeleccionado;
        var subTotal = 0;
        var descuento = 0;
        var total = 0;
        var clienteExiste = false;
        var fullName = "";
        var clienteId = null;
        var envioExiste = false;
        var cobroSubTotal, cobroDescuento, cobroTotal, cobroPendientePago, cobroPagado, coboMetodoPago, cobroPago, cobroCambio;
        $scope.ventas = [];
        $scope.ventaActiva = null;

        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;
        vm.corteCajaId = $scope.corteCajaId;
        vm.personaId = $scope.personaId;
        // console.log("Empresa:", vm.empresaId);
        //  console.log("Nombre:", vm.nombrePersonal);
        const firebaseConfig = {
            apiKey: "AIzaSyB5eHzqMNt-8rtY509ACnQr1Eo023RWzBM",
            authDomain: "arco-de-rosas.firebaseapp.com",
            projectId: "arco-de-rosas",
            storageBucket: "arco-de-rosas.firebasestorage.app",
            messagingSenderId: "640067846329",
            appId: "1:640067846329:web:6cdc7a1f801c4b3ecadb68"
        };

        if (!firebase.apps.length) {
            firebase.initializeApp(firebaseConfig);
        }

        const db = firebase.database();
        // Nodo fijo
        //      const nodo = db.ref('alertas/centro/');
        //
        //    function actualizarMensaje() {
        //      const segundos = segundosDesdeMedianoche();
        //    nodo.set({ mensaje: segundos })  // Actualiza el valor en Firebase
        //      .then(() => console.log("Mensaje actualizado:", segundos))
        //    .catch(err => console.error("Error al actualizar:", err));
        // }
        function crearAlerta() {
            const segundos = segundosDesdeMedianoche();
            // Referencia directa al nodo fijo
            const nodo = db.ref('alertas/' + vm.empresaId + '/');

            nodo.set({ mensaje: segundos })
                .then(() => console.log("Alerta creada o actualizada:", segundos))
                .catch(err => console.error("Error al crear/actualizar:", err));
        }


        function segundosDesdeMedianoche() {
            const ahora = new Date();
            return ahora.getHours() * 3600 + ahora.getMinutes() * 60 + ahora.getSeconds();
        }
        vm.coloresCategoria = [
            '#d6e9f8', // azul claro
            '#d8f3dc', // verde claro
            '#fcefc7', // amarillo claro
            '#f9d6d5', // rojo claro
            '#e3d4f5'  // morado claro
        ];

        function cargarCategorias() {
            $http.get('/api/v1/TipoProducto')  // endpoint que devuelve las categorías
                .then(function (response) {
                    if (response.data && response.data.length) {
                        vm.categorias = response.data.map(function (cat) {
                            return {
                                id: cat.id,
                                nombre: cat.tipo_producto,
                                productos: []
                            };
                        });
                        cargarProductosSecuencialmente();
                    } else {
                        vm.categorias = [];
                    }
                }, function (error) {
                    console.error("Error al cargar categorías", error);
                    vm.categorias = [];
                });
        }

        async function cargarProductosSecuencialmente() {
            for (let index = 0; index < vm.categorias.length; index++) {
                const cat = vm.categorias[index];
                const color = vm.coloresCategoria[index % vm.coloresCategoria.length];
                await getProductosPorCategoria(cat.id, color);  // espera a que termine antes de continuar
            }
        }

        function getMetodoPago() {
            $scope.isLoadPanelVisible = true;
            $http.get('/api/v1/metodoPago/activos/').then(
                function (response) {
                    ArrayMetodoPago.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayMetodoPago.push(response.data[i]);
                    }
                    $scope.metodo_pago_source.load().done(function (response) {
                        $scope.cmbMetodoPago = 1;
                    });
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                }
            );
        };

        function vaciarInformacionEnvio() {
            clienteExiste = false;
            fullName = "";
            $scope.txtTelefono = "";
            $scope.txtNombre = "";
            $scope.txtApellidoParterno = "";
            $scope.txtApellidoMaterno = "";
            $scope.txtDomicilio = "";
            $scope.txtObservaciones = "";
            clienteId = null;
            envioExiste = false;
            txtTelefonoInstance.option("disabled", false);
            txtNombreInstance.option("disabled", false);
            txtAPInstance.option("disabled", false);
            txtAMInstance.option("disabled", false);
        }

        function getCortesCaja() {
            $scope.isLoadPanelVisible = true;
            $http.get('/cortes_por_empresa/', { params: { empresa: vm.empresaId } })
                .then(
                    function (response) {
                        console.log(response)
                        ArrayCortes.length = 0;
                        for (let i = 0; i < response.data.length; i++) {
                            ArrayCortes.push(response.data[i]);
                        }
                        $scope.cortes_source.load().done(function (response) {
                            $scope.cmbCortes = 1;
                        });
                        $scope.isLoadPanelVisible = false;
                    }, function (response) {
                    }
                );
        };



        function getIngresosPorCorte(venta) {
            $scope.isLoadPanelVisible = true;
            const params = new URLSearchParams({
                idCorte: vm.corteCajaId,
            });
            const url = `/ingresos_por_corte/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    ArrayIngresosPorCorte.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayIngresosPorCorte.push(response.data[i]);
                    }
                    if (gridIngresosPorCorteInstance)
                        gridIngresosPorCorteInstance.refresh();
                },
                function (error) {
                    console.error("Error al obtener loe ingresos del corte:", error);
                    $scope.isLoadPanelVisible = false;
                }
            );
        }

        function getEgresosPorCorte(venta) {
            $scope.isLoadPanelVisible = true;
            const params = new URLSearchParams({
                idCorte: vm.corteCajaId,
            });
            const url = `/egresos_por_corte/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    ArrayEgresosPorCorte.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayEgresosPorCorte.push(response.data[i]);
                    }
                    if (gridEgresosPorCorteInstance)
                        gridEgresosPorCorteInstance.refresh();
                },
                function (error) {
                    console.error("Error al obtener loe egresos del corte:", error);
                    $scope.isLoadPanelVisible = false;
                }
            );
        }

        function getPagosPorVenta(venta) {
            $scope.isLoadPanelVisible = true;
            console.log(venta);
            const params = new URLSearchParams({
                venta: venta,
            });
            const url = `/pagos_por_venta/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    cobroPagado = 0;
                    cobroCambio = 0;
                    cobroPago = 0;
                    $scope.numberCobroPago = 0;
                    ArrayPagosPorVenta.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        console.log(response.data[i]);
                        ArrayPagosPorVenta.push(response.data[i]);
                        cobroPagado = cobroPagado + response.data[i].monto;
                    }

                    gridDesglosePagoVentaInstance.refresh();

                    $scope.numberCobroSubTotal = subTotal;
                    $scope.numberCobroDescuento = descuento;
                    $scope.numberCobroTotal = cobroTotal;
                    $scope.isLoadPanelVisible = false;
                    if (cobroTotal - cobroPagado >= 0) {
                        cobroPendientePago = total - descuento - cobroPagado;
                        cobroCambio = 0;
                        $scope.numberCobroCambio = 0;
                    } else {
                        cobroCambio = cobroPagado - cobroTotal
                        $scope.numberCobroCambio = cobroCambio;
                        cobroPendientePago = 0;
                    }
                    $scope.numberCobroPendiente = cobroPendientePago;
                    $scope.numberCobroPagado = cobroPagado;

                },
                function (error) {
                    console.error("Error al obtener pagos por venta:", error);
                    $scope.isLoadPanelVisible = false;
                }
            );
        }

        function getVentaPorNumero(ventaId) {
            if (!ventaId) {
                Swal.fire('Error', 'Debes proporcionar un número de venta', 'warning');
                return;
            }
            $scope.isLoadPanelVisible = true;
            $http.get(`/api/v1/ventas/?venta_id=${ventaId}`)
                .then(function (response) {
                    if (!response.data || response.data.length === 0) {
                        Swal.fire('No encontrada', 'No existe venta con ese número', 'info');
                        return;
                    }

                    fullVentaActiva = response.data[0];  // DRF devuelve lista, tomamos el primer elemento
                })
                .catch(function (error) {
                    console.error('❌ Error al obtener la venta:', error);
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo obtener la venta',
                        icon: 'error',
                        allowOutsideClick: false,
                        allowEscapeKey: false
                    });
                })
                .finally(function () {
                    $scope.isLoadPanelVisible = false;
                });
        }
        function getVentaPorNumeroDespuesDePago(ventaId) {
            if (!ventaId) {
                Swal.fire('Error', 'Debes proporcionar un número de venta', 'warning');
                return;
            }
            $scope.isLoadPanelVisible = true;
            $http.get(`/api/v1/ventas/?venta_id=${ventaId}`)
                .then(function (response) {
                    if (!response.data || response.data.length === 0) {
                        Swal.fire('No encontrada', 'No existe venta con ese número', 'info');
                        return;
                    }
                    fullVentaActiva = response.data[0];  // DRF devuelve lista, tomamos el primer elemento
                    if (fullVentaActiva.pagada) {
                        BtnPagarInstance.option("disabled", true);
                        BtnImprimirInstance.option("disabled", false);
                    }
                })
                .catch(function (error) {
                    console.error('❌ Error al obtener la venta:', error);
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo obtener la venta',
                        icon: 'error',
                        allowOutsideClick: false,
                        allowEscapeKey: false
                    });
                })
                .finally(function () {
                    $scope.isLoadPanelVisible = false;
                });
        }
        function getMesas() {
            $scope.isLoadPanelVisible = true;
            $http.get('/api/v1/lugarEntrega/activos/').then(
                function (response) {
                    ArrayMesa.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayMesa.push(response.data[i]);
                    }
                    $scope.mesa_source.load().done(function (response) {
                        $scope.cmbMesa = 1;
                    });
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                }
            );
        };
        function getCrearVenta() {
            const ventaData = {
                cliente: $scope.cmbCliente,
                corte_caja: vm.corteCajaId,
                total: 0,
                cambio: 0,
                atencion: vm.personaId,
                lugar_entrega_id: $scope.cmbMesa,
                observaciones: 'Ninguna'
            };

            if (!ventaData.cliente || !ventaData.atencion || !ventaData.lugar_entrega_id) {
                Swal.fire('Campos incompletos', 'Revisa cliente, atención o mesa', 'warning');
                return;
            }
            $http.post('/api/v1/ventas/', ventaData)
                .then(function (response) {
                    getVentasAbiertasCorteEmpresas();
                })
                .catch(function (error) {
                    console.error("Error creando venta:", error);
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo crear la venta',
                        icon: 'error',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            if (popup) {
                                popup.style.fontSize = '1.2rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '400px';
                            }

                            const confirmBtn = Swal.getConfirmButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.5rem';
                                confirmBtn.style.padding = '0.75rem 2rem';
                            }
                        }
                    });
                });
        }

        function getCrearPago() {
            const pagoData = {
                venta: $scope.ventaActiva,                 // ID de la venta asociada
                metodo_pago: $scope.cmbMetodoPago,      // ID del método de pago seleccionado
                monto: $scope.numberCobroPago,   // Valor decimal del pago
                referencia: null, // Para tarjetas, transferencias, etc.
                observaciones: null, // Opcional
                // activo: true                           // Puede omitirse si el backend lo setea por defecto
            };
            $http.post('/api/v1/pagoVenta/', pagoData)
                .then(function (response) {
                    getPagosPorVenta($scope.ventaActiva)
                    getVentaPorNumeroDespuesDePago($scope.ventaActiva);//Se trae la data de la venta activa
                })
                .catch(function (error) {
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo crear el pago',
                        icon: 'error',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            if (popup) {
                                popup.style.fontSize = '1.2rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '400px';
                            }

                            const confirmBtn = Swal.getConfirmButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.5rem';
                                confirmBtn.style.padding = '0.75rem 2rem';
                            }
                        }
                    });
                });
        }

        function imprimirTicketVenta() {
            if (!$scope.ventaActiva) {
                console.warn("No hay venta seleccionada para imprimir.");
                return;
            }
            $scope.isLoadPanelVisible = true;
            $http.get('/imprimir_ticket_venta/', {
                params: { venta_id: $scope.ventaActiva }
                //params: { venta_id: 60 }
            }).then(
                function (response) {
                    // HTML del ticket desde Django
                    const ticketHTML = response.data;

                    // Abrir ventana de impresión
                    const printWindow = window.open('', '_blank');
                    printWindow.document.write(ticketHTML);
                    printWindow.document.close();
                    printWindow.focus();
                    printWindow.print();
                    $scope.isLoadPanelVisible = false;
                },
                function (error) {
                    console.error("Error al obtener ticket:", error);
                    $scope.isLoadPanelVisible = false;
                }
            );
        };

        function imprimirTicket(idVenta) {
            $scope.isLoadPanelVisible = true;
            $http.get('/imprimir_ticket_venta/', {
                params: { venta_id: idVenta }
                //params: { venta_id: 60 }
            }).then(
                function (response) {
                    // HTML del ticket desde Django
                    const ticketHTML = response.data;

                    // Abrir ventana de impresión
                    const printWindow = window.open('', '_blank');
                    printWindow.document.write(ticketHTML);
                    printWindow.document.close();
                    printWindow.focus();
                    printWindow.print();
                    $scope.isLoadPanelVisible = false;
                },
                function (error) {
                    console.error("Error al obtener ticket:", error);
                    $scope.isLoadPanelVisible = false;
                }
            );
        };


        function getVentasPorCorte() {
            const params = new URLSearchParams({
                corteCaja: $scope.cmbCortes,
            });
            $scope.isLoadPanelVisible = true;
            const url = `/ventas_por_corte_caja/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    ArrayVentasCorte.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayVentasCorte.push(response.data[i]);
                    }

                    if ($scope.ventas_corte_source && $scope.ventas_corte_source.reload) {
                        $scope.ventas_corte_source.reload();
                    }
                    gridVentasPorCorteInstance.refresh();

                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                }
            );
        };

        function buscarClientePorTelefono(telefono) {
            const params = new URLSearchParams({
                telefono: telefono,
                empresa: vm.empresaId
            });
            $scope.isLoadPanelVisible = true;
            const url = `/buscar_cliente_por_telefono/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    // Si existe el cliente
                    console.log(response.data);
                    if (response.data.exists) {
                        const nombre = response.data.nombre || "";
                        const ap = response.data.apellido_paterno || "";
                        const am = response.data.apellido_materno || "";
                        $scope.txtNombre = nombre;
                        $scope.txtApellidoParterno = ap;
                        $scope.txtApellidoMaterno = am;
                        clienteExiste = true;
                        clienteId = response.data.id;
                        fullName = `${nombre} ${ap} ${am}`.trim().replace(/\s+/g, " ");
                    } else {
                        clienteExiste = false;
                    }
                    $scope.isLoadPanelVisible = false;
                },
                function () {
                    $scope.isLoadPanelVisible = false;
                }
            );
        };

        function consultarEnvioDomicilio(ventaId) {
            const params = new URLSearchParams({
                venta_id: $scope.ventaActiva
            });
            $scope.isLoadPanelVisible = true;
            const url = `/consultar_Envio_Domicilio/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    if (response.data.existe) {
                        const data = response.data;
                        $scope.txtTelefono = data.telefono || "";
                        $scope.txtNombre = data.nombre || "";
                        $scope.txtApellidoParterno = data.apellido_paterno || "";
                        $scope.txtApellidoMaterno = data.apellido_materno || "";
                        $scope.txtDomicilio = data.domicilio || "";
                        $scope.txtObservaciones = data.observaciones || "";
                        txtTelefonoInstance.option("disabled", true);
                        txtNombreInstance.option("disabled", true);
                        txtAPInstance.option("disabled", true);
                        txtAMInstance.option("disabled", true);
                        envioExiste = true;
                    } else {
                        if (txtTelefonoInstance) {
                            txtTelefonoInstance.focus();
                        }
                        envioExiste = false;
                    }

                    $scope.isLoadPanelVisible = false;
                },
                function () {
                    $scope.isLoadPanelVisible = false;
                }
            );
        }
        function guardarEnvioDomicilio() {
            const params = new URLSearchParams({
                venta_id: $scope.ventaActiva,
                empresa_id: vm.empresaId,
                telefono: $scope.txtTelefono || "",
                nombre: $scope.txtNombre || "",
                apellido_paterno: $scope.txtApellidoParterno || "",
                apellido_materno: $scope.txtApellidoMaterno || "",
                domicilio: $scope.txtDomicilio || "",
                observaciones: $scope.txtObservaciones || "",
                cliente_id: clienteExiste ? clienteId : ""   // si tú guardas el ID del cliente
            });
            $scope.isLoadPanelVisible = true;
            const url = `/guardar_envio_domicilio/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    if (response.data.success) {
                        DevExpress.ui.notify("Envío guardado correctamente", "success", 2000);
                        vaciarInformacionEnvio()
                        popEnvioDomicilioInstance.hide();
                    } else {
                        DevExpress.ui.notify("Error al guardar envío", "error", 2000);
                    }
                    $scope.isLoadPanelVisible = false;
                },
                function () {
                    DevExpress.ui.notify("Fallo la conexión con el servidor", "error", 2000);
                    $scope.isLoadPanelVisible = false;
                }
            );
        }

        function modificarEnvioDomicilio() {
            const params = new URLSearchParams({
                venta_id: $scope.ventaActiva,
                telefono: $scope.txtTelefono || "",
                nombre: $scope.txtNombre || "",
                apellido_paterno: $scope.txtApellidoParterno || "",
                apellido_materno: $scope.txtApellidoMaterno || "",
                domicilio: $scope.txtDomicilio || "",
                observaciones: $scope.txtObservaciones || ""
            });

            $scope.isLoadPanelVisible = true;
            const url = `/modificar_envio_domicilio/?${params.toString()}`;

            $http.get(url).then(
                function (response) {
                    if (response.data.success) {
                        DevExpress.ui.notify("Envío modificado correctamente", "success", 2000);
                        vaciarInformacionEnvio();
                        popEnvioDomicilioInstance.hide();
                    } else {
                        DevExpress.ui.notify("Error al modificar envío", "error", 2000);
                    }
                    $scope.isLoadPanelVisible = false;
                },
                function () {
                    DevExpress.ui.notify("Fallo la conexión con el servidor", "error", 2000);
                    $scope.isLoadPanelVisible = false;
                }
            );
        }


        function getVentasAbiertasCorteEmpresas() {
            const params = new URLSearchParams({
                corteCaja: vm.corteCajaId,
            });
            $scope.isLoadPanelVisible = true;
            const url = `/ventas_abiertas_corte_empresas/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    $scope.ventas = [];
                    ArrayEmpresasVenta.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayEmpresasVenta.push(response.data[i]);
                        agregarVenta(response.data[i].id);  // <--- AQUI las fusionas
                    }
                    if (ArrayEmpresasVenta.length == 0) {
                        $scope.ventaActiva = null;
                        ArrayDesgloseVenta.length = 0;
                        total = 0
                        cobroSubTotal = 0;
                        cobroDescuento = 0;
                        cobroTotal = 0;
                        subTotal = 0;
                        descuento = 0;
                        $scope.numberSubtotal = 0;
                        $scope.numberDescuento = 0;
                        $scope.numberTotal = 0;
                        BtnCancelarVentaInstance.option("disabled", true);
                        if ($scope.desglose_venta_source && $scope.desglose_venta_source.reload) {
                            $scope.desglose_venta_source.reload();
                        }
                        gridDesgloseVentaInstance.refresh();
                    }
                    if ($scope.ventaActiva > 0) {
                        getVentaPorNumero($scope.ventaActiva);//Se trae la data de la venta activa
                        productosVenta($scope.ventaActiva);
                    }
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                }
            );
        };


        function productosVenta(venta) {
            const params = new URLSearchParams({
                venta: venta,
            });
            $scope.isLoadPanelVisible = true;
            const url = `/productos_venta/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    subTotal = 0;
                    descuento = 0;
                    total = 0;
                    ArrayDesgloseVenta.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayDesgloseVenta.push(response.data[i]);
                        subTotal = subTotal + response.data[i].precio_unitario;
                        descuento = descuento + response.data[i].descuento;
                        total = total + response.data[i].total;
                    }
                    if (ArrayDesgloseVenta == 0) {
                        BtnCancelarVentaInstance.option("disabled", false);
                    } else {
                        BtnCancelarVentaInstance.option("disabled", true);
                    }
                    //descuento = 150;
                    cobroSubTotal = subTotal;
                    cobroDescuento = descuento;
                    cobroTotal = total - descuento;
                    $scope.numberSubtotal = subTotal;
                    $scope.numberDescuento = descuento;
                    $scope.numberTotal = cobroTotal;
                    gridDesgloseVentaInstance.refresh();
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                }
            );
        };

        function transaccionVentaProducto(idProducto, idVenta) {
            const productoEncontrado = findProductoById(vm.categorias, idProducto);
            //  if (productoEncontrado) {
            //    console.log(productoEncontrado.data.empresa);
            // }
            let localPrecio = 0;
            let localEmpresa = 0;
            let descuento = 0;
            let observaciones = "Sin observaciones";
            if (productoEncontrado) {
                localPrecio = productoEncontrado.precio
                localEmpresa = productoEncontrado.data.empresa
            }

            const params = new URLSearchParams({
                producto: idProducto,
                venta: idVenta,
                precio: localPrecio,
                descuento: descuento,
                empresa: localEmpresa,
                observaciones: observaciones,
            });
            $scope.isLoadPanelVisible = true;
            const url = `/transaccion_venta_producto/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    if (response.data && response.data.error && response.data.error.includes('Stock insuficiente')) {
                        Swal.fire({
                            title: '⚠️ Stock insuficiente',
                            html: `<p style="font-size:1.1rem;">No hay suficiente inventario para el producto <strong>${response.data.error.replace('Stock insuficiente para ', '')}</strong>.</p>`,
                            icon: 'warning',
                            showConfirmButton: true,
                            confirmButtonText: 'Entendido',
                            confirmButtonColor: '#d33',
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            didOpen: () => {
                                const popup = Swal.getPopup();
                                if (popup) {
                                    popup.style.fontSize = '1.3rem';
                                    popup.style.padding = '2rem';
                                    popup.style.width = '450px';
                                    popup.style.textAlign = 'center';
                                }
                                const confirmBtn = Swal.getConfirmButton();
                                if (confirmBtn) {
                                    confirmBtn.style.fontSize = '1.2rem';
                                    confirmBtn.style.padding = '0.8rem 2rem';
                                }
                            }
                        });
                        return;
                    }
                    productosVenta(idVenta);
                    var mensaje = response.data.success;
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                    Swal.fire({
                        title: '⚠️ Se presento un error al agregar el producto',
                        html: `<p style="font-size:1.1rem;">No hay suficiente inventario para el producto <strong>${response.data.error.replace('Stock insuficiente para ', '')}</strong>.</p>`,
                        icon: 'warning',
                        showConfirmButton: true,
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#d33',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            if (popup) {
                                popup.style.fontSize = '1.3rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            const confirmBtn = Swal.getConfirmButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.2rem';
                                confirmBtn.style.padding = '0.8rem 2rem';
                            }
                        }
                    });
                }
            );
        };
        //Metodo que busca por medio del id del produucto en el arreglo y regresa la información del mismo para evitar petición al server
        function findProductoById(categorias, productoId) {
            for (let categoria of categorias) {
                if (categoria.productos && categoria.productos.length) {
                    for (let producto of categoria.productos) {
                        if (producto.id === productoId) {
                            return producto;
                        }
                    }
                }
            }
            return null; // no encontrado
        }

        function getClientes() {
            const params = new URLSearchParams({
                empresa: vm.empresaId,
                estatus: true,
            });
            $scope.isLoadPanelVisible = true;
            const url = `/clientes_por_empresa/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    ArrayClientes.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayClientes.push(response.data[i]);
                    }
                    $scope.cliente_source.load().done(function (response) {
                        $scope.cmbCliente = 1;
                    });
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                }
            );
        };

        function transaccionEliminarProductoVenta(idDesgloce) {
            const params = new URLSearchParams({
                idDesgloce: idDesgloce,
            });
            $scope.isLoadPanelVisible = true;
            const url = `/transaccion_cancelar_desglose_venta/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    //    console.log(response);
                    productosVenta($scope.ventaActiva);
                    $scope.isLoadPanelVisible = false;
                }, function (response) {

                }
            );
        }
        function empresasVenta() {
            $scope.isLoadPanelVisible = true;
            const params = new URLSearchParams({
                empresa: vm.empresaId,
            });
            const url = `/empresas_autorizadas/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    strEmpresasVenta = response.data;
                    cargarCategorias();
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                    $scope.isLoadPanelVisible = false;
                }
            );
        };
        // Definición de la función para inicializar productos
        function inicializarProductos() {
            empresasVenta()
            getMesas();
            getClientes();
            getVentasAbiertasCorteEmpresas();
            getEgresosPorCorte();
            getIngresosPorCorte();
            //cargarCategorias();
            // 
        }

        inicializarProductos();
        function getProductosPorCategoria(categoriaId, color) {
            $scope.isLoadPanelVisible = true;
            const params = new URLSearchParams({
                empresas: strEmpresasVenta,
                categoria: categoriaId
            });
            //const url = `/api/v1/productos/activos_por_tipo/?${params.toString()}`;
            const url = `/productos_activos_empresas/?${params.toString()}`;
            // Retornar la promesa para poder usar await
            return $http.get(url).then(
                function (response) {
                    let categoria = vm.categorias.find(cat => cat.id === categoriaId);
                    if (!categoria) {
                        console.warn(`Categoría con ID ${categoriaId} no encontrada`);
                        return;
                    }

                    if (response.data && response.data.length > 0) {
                        categoria.productos = response.data.map(producto => ({
                            id: producto.id,
                            nombre: producto.nombre,
                            color: color || '#e0e0e0',
                            empresa: producto.empresa_nombre,
                            precio: producto.primer_precio,
                            data: producto
                        }));
                    } else {
                        // DevExpress.ui.notify("La consulta no generó información, intente con otros parámetros", "warning", 3500);
                    }
                },
                function (error) {
                    console.error(`Error al obtener productos para categoría ${categoriaId}:`, error);
                }
            ).finally(function () {
                $scope.isLoadPanelVisible = false;
            });
        }

        vm.categoriaActiva = 1;

        vm.setCategoria = function (id) {
            vm.categoriaActiva = id;
        };

        vm.filtro = '';

        vm.prediosFiltrados = function () {
            var filtro = vm.filtro ? vm.filtro.toLowerCase() : '';
            if (!filtro) return [];

            var resultados = [];
            vm.categorias.forEach(function (cat) {
                cat.productos.forEach(function (producto) {
                    if (
                        (producto.nombre && producto.nombre.toLowerCase().includes(filtro)) //||
                        //  (producto.cultivo && producto.cultivo.toLowerCase().includes(filtro)) ||
                        //  (producto.id && producto.id.toLowerCase().includes(filtro))
                    ) {
                        resultados.push(producto);
                    }
                });
            });
            return resultados;
        };

        function agregarVenta(idVenta) {
            if (!idVenta) return;
            if (!$scope.ventas) $scope.ventas = [];

            if ($scope.ventas.indexOf(idVenta) === -1) {
                $scope.ventas.push(idVenta);
            }
            $scope.ventaActiva = idVenta;  // Para activar la pestaña recién creada
        }

        $scope.setVentaActiva = function (idVenta) {
            $scope.ventaActiva = idVenta;
            //  $scope.ventaActiva = idVenta;
        };

        $scope.consultarVenta = function (ventaId) {
            alertify.success("Venta seleccionada: " + ventaId);
            getVentaPorNumero(ventaId)
            $scope.ventaActiva = ventaId;
            productosVenta($scope.ventaActiva)
        };


        // Función para mostrar alertify con el id del predio
        vm.mostrarAlertId = function (id) {
            if ($scope.ventaActiva > 0) {
                if (fullVentaActiva.abonada == false && fullVentaActiva.pagada == false) {
                    transaccionVentaProducto(id, $scope.ventaActiva)
                    //  DevExpress.ui.notify("Se puede vender " + id, "success", 3500);
                } else {
                    Swal.fire({
                        title: '❌ Imposible agregar el producto',
                        html: `<p style="font-size:1.1rem;">No se puede agregar el producto a la venta, ya cuenta con pagos registrados.</p>`,
                        icon: 'error',
                        showConfirmButton: true,
                        confirmButtonText: 'Aceptar',
                        confirmButtonColor: '#d33',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            if (popup) {
                                popup.style.fontSize = '1.3rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            const confirmBtn = Swal.getConfirmButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.2rem';
                                confirmBtn.style.padding = '0.8rem 2rem';
                            }
                        }
                    });
                }

            } else {
                Swal.fire({
                    title: '¿Iniciar venta?',
                    text: 'Se va a iniciar una venta.',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonText: 'Sí',
                    cancelButtonText: 'No',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        const popup = Swal.getPopup();
                        if (popup) {
                            popup.style.fontSize = '1.2rem';
                            popup.style.padding = '2rem';
                            popup.style.width = '400px';
                        }

                        const confirmBtn = Swal.getConfirmButton();
                        const cancelBtn = Swal.getCancelButton();

                        if (confirmBtn) {
                            confirmBtn.style.fontSize = '1.5rem';
                            confirmBtn.style.padding = '0.75rem 2rem';
                        }
                        if (cancelBtn) {
                            cancelBtn.style.fontSize = '1.5rem';
                            cancelBtn.style.padding = '0.75rem 2rem';
                        }
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        getCrearVenta();
                    }
                });
            }

        };
        function eliminarPago(pagoId) {
            if (!pagoId) return;
            $http.delete(`/api/v1/pagoVenta/${pagoId}/`)
                .then(function (response) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Pago eliminado',
                        text: 'El pago se eliminó correctamente',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');

                            // Forzar que quede por encima de cualquier modal/popup
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.fontSize = '1.3rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }

                            const confirmBtn = Swal.getConfirmButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.2rem';
                                confirmBtn.style.padding = '0.8rem 2rem';
                            }
                        }
                    });
                    BtnPagarInstance.option("disabled", false);
                    BtnImprimirInstance.option("disabled", true);
                    getPagosPorVenta($scope.ventaActiva); // refresca lista de pagos
                })
                .catch(function (error) {

                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'No se pudo eliminar el pago',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');

                            // Forzar que quede por encima de cualquier modal/popup
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.fontSize = '1.3rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }

                            const confirmBtn = Swal.getConfirmButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.2rem';
                                confirmBtn.style.padding = '0.8rem 2rem';
                            }
                        }
                    });
                    console.error("Error al eliminar pago:", error);
                });
        }

        function modificarVenta() {
            const ventaData = {
                activo: false
            };

            $http({
                method: 'PATCH',
                url: `/api/v1/ventas/${$scope.ventaActiva}/`,
                data: ventaData
            }).then(
                function (response) {
                    DevExpress.ui.notify('Venta eliminada satisfactoriamente', "success", 5000);
                    getVentasAbiertasCorteEmpresas();
                },
                function (error) {
                    DevExpress.ui.notify('No se pudo eliminar la venta', "error", 5000);
                }
            );
        }


        $scope.ventas_corte_source = new DevExpress.data.DataSource({
            store: ArrayVentasCorte
        });
        $scope.cortes_source = new DevExpress.data.DataSource({
            store: ArrayCortes
        });
        $scope.desglose_venta_source = new DevExpress.data.DataSource({
            store: ArrayDesgloseVenta
        });
        $scope.mesa_source = new DevExpress.data.DataSource({
            store: ArrayMesa
        });
        $scope.cliente_source = new DevExpress.data.DataSource({
            store: ArrayClientes
        });

        $scope.ventas_source = new DevExpress.data.DataSource({
            store: ArrayEmpresasVenta

        });

        $scope.metodo_pago_source = new DevExpress.data.DataSource({
            store: ArrayMetodoPago
        });

        $scope.pagos_por_venta_source = new DevExpress.data.DataSource({
            store: ArrayPagosPorVenta
        });

        $scope.egresos_por_corte_source = new DevExpress.data.DataSource({
            store: ArrayEgresosPorCorte
        });

        $scope.ingresos_por_corte_source = new DevExpress.data.DataSource({
            store: ArrayIngresosPorCorte
        });




        vm.numberBox = {
            NbrCobroPagoOptions: {
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberCobroPago'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                min: 0, // evita valores negativos si aplica
                step: 1, // paso de incremento opcional
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrCobroPendienteOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberCobroPendiente'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                //  min: 0, // evita valores negativos si aplica
                // step: 1, // paso de incremento opcional
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrCobroPagadoOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberCobroPagado'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrCobroCambioOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberCobroCambio'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrCobroTotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberCobroTotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrCobroDescuentoOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberCobroDescuento'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrCobroSubtotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberCobroSubTotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },

            NbrSubtotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberSubtotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrDescuentoOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberDescuento'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            NbrTotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'numberTotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            }

        };
        vm.textArea = {
            TxtDomicilioOptions: {
                disabled: false,
                showClearButton: true,
                height: 60,
                maxLength: 300,
                bindingOptions: {
                    value: 'txtDomicilio'
                },
                onValueChanged: function (data) {
                    $scope.txtDomicilio = $filter('uppercase')(data.value);
                }
            },
            TxtObservacionesOptions: {
                disabled: false,
                showClearButton: true,
                height: 60,
                maxLength: 300,
                bindingOptions: {
                    value: 'txtObservaciones'
                },
                onValueChanged: function (data) {
                    $scope.txtObservaciones = $filter('uppercase')(data.value);
                }
            }
        }
        vm.textBox = {
            TxtNombreOptions: {
                disabled: false,
                showClearButton: true,
                maxLength: 100,
                bindingOptions: {
                    value: 'txtNombre'
                },
                onInitialized: function (e) {
                    txtNombreInstance = e.component;
                },
                onValueChanged: function (data) {
                    $scope.txtNombre = $filter('uppercase')(data.value);
                },

            },
            TxtApellidoPaternoOptions: {
                disabled: false,
                showClearButton: true,
                maxLength: 100,
                bindingOptions: {
                    value: 'txtApellidoParterno'
                },
                onInitialized: function (e) {
                    txtAPInstance = e.component;
                },
                onValueChanged: function (data) {
                    $scope.txtApellidoParterno = $filter('uppercase')(data.value);
                },
            },
            TxtApellidoMaternoOptions: {
                disabled: false,
                showClearButton: true,
                maxLength: 100,
                bindingOptions: {
                    value: 'txtApellidoMaterno'
                },
                onInitialized: function (e) {
                    txtAMInstance = e.component;
                },
                onValueChanged: function (data) {
                    $scope.txtApellidoMaterno = $filter('uppercase')(data.value);
                },
            },
            TxtTelefonoOptions: {
                disabled: false,
                showClearButton: true,
                maxLength: 10,
                bindingOptions: {
                    value: 'txtTelefono'
                },
                mode: 'tel',
                onKeyDown: function (e) {
                    const key = e.event.key;
                    // Permitir solo dígitos, teclas de navegación, borrar, tab
                    const allowedKeys = ['Backspace', 'Tab', 'ArrowLeft', 'ArrowRight', 'Delete'];
                    if (!/^\d$/.test(key) && !allowedKeys.includes(key)) {
                        e.event.preventDefault();
                    }
                },
                onInitialized: function (e) {
                    txtTelefonoInstance = e.component;
                },
                onValueChanged: function (e) {
                    // Puedes agregar validación adicional aquí si deseas
                },
                onFocusOut: function (e) {
                    const valor = e.component.option("value") || "";

                    // Bloquear si está vacío
                    if (valor.length === 0) {
                        DevExpress.ui.notify("El teléfono no puede estar vacío", "warning", 2000);
                        setTimeout(() => e.component.focus());
                        return;
                    }

                    //  Bloquear si tiene menos de 10 caracteres
                    if (valor.length < 10) {
                        DevExpress.ui.notify("El teléfono debe tener 10 dígitos", "warning", 2000);
                        setTimeout(() => e.component.focus());
                        return;
                    }

                    //  Tiene 10 dígitos → correr búsqueda
                    buscarClientePorTelefono($scope.txtTelefono);
                }
            },
        }
        vm.button = {
            BtnCrearVentaOptions: {
                icon: 'fas fa-plus',
                type: 'default',
                width: 110,
                text: 'Venta',
                disabled: false,
                hint: 'Iniciar una nueva venta',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                onInitialized: function (e) {
                    BtnCrearVentaInstance = e.component;
                },
                onClick: function () {
                    Swal.fire({
                        title: '¿Iniciar venta?',
                        text: 'Se va a iniciar una venta.',
                        icon: 'question',
                        showCancelButton: true,
                        confirmButtonText: 'Sí',
                        cancelButtonText: 'No',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            if (popup) {
                                popup.style.fontSize = '1.2rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '400px';
                            }

                            const confirmBtn = Swal.getConfirmButton();
                            const cancelBtn = Swal.getCancelButton();

                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.5rem';
                                confirmBtn.style.padding = '0.75rem 2rem';
                            }
                            if (cancelBtn) {
                                cancelBtn.style.fontSize = '1.5rem';
                                cancelBtn.style.padding = '0.75rem 2rem';
                            }
                        }
                    }).then((result) => {
                        if (result.isConfirmed) {
                            getCrearVenta();
                        }
                    });
                }
            },
            BtnCobrarVentaOptions: {
                icon: 'fa fa-credit-card',
                type: 'success',
                width: 110,
                text: 'Cobrar',
                hint: 'Cobrar la venta',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    BtnCrearVentaInstance = e.component;
                },
                onClick: function () {
                    if (total > 0) {
                        PopPagosInstance.show();
                    } else {
                        DevExpress.ui.notify("No existe cuenta por cobrar", "warning", 5000);
                    }

                }
            },
            BtnVerEgresosOptions: {
                icon: 'fa fa-chart-bar',
                type: 'danger',
                width: 130,
                text: 'Egresos',
                hint: 'Ver los egresos',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    verEgresosInstance = e.component;
                },
                onClick: function () {
                    popEgresosInstance.show();
                }
            },
            BtnVerIngresosOptions: {
                icon: 'fa fa-chart-bar',
                type: 'success',
                width: 130,
                text: 'Ingresos',
                hint: 'Ver los ingresos',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    verIngresosInstance = e.component;
                },
                onClick: function () {
                    popIngresosInstance.show();
                }
            },
            BtnInformacionEnvioOptions: {
                icon: 'fa fa-motorcycle',
                type: 'default',
                width: 130,
                text: 'Domicilio',
                hint: 'Envio a domicilio',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    BtnInformacionEnvioInstance = e.component;
                },
                onClick: function () {
                    popEnvioDomicilioInstance.show();
                }
            },
            BtnCerrarEgresosOptions: {
                icon: 'fa fa-arrow-left',
                type: 'default',
                width: 130,
                text: 'Regresar',
                hint: 'Regresar a punto de venta',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    BtnCerrarEgresosInstance = e.component;
                },
                onClick: function () {
                    popEgresosInstance.hide();
                }
            },
            BtnCerrarIngresosOptions: {
                icon: 'fa fa-arrow-left',
                type: 'default',
                width: 130,
                text: 'Regresar',
                hint: 'Regresar a punto de venta',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    BtnCerrarIngresosInstance = e.component;
                },
                onClick: function () {
                    popIngresosInstance.hide();
                }
            },

            BtnCerrarDomicilioOptions: {
                icon: 'fa fa-arrow-left',
                type: 'default',
                width: 130,
                text: 'Regresar',
                hint: 'Regresar a punto de venta',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    BtnCerrarDomicilioInstance = e.component;
                },
                onClick: function () {
                    vaciarInformacionEnvio();
                    popEnvioDomicilioInstance.hide();
                }
            },

            BtnGuardarDomicilioOptions: {
                icon: 'fa fa-save',
                type: 'success',
                width: 130,
                text: 'Guardar',
                hint: 'Guardar información del envio',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    BtnGuardarDomicilioInstance = e.component;
                },
                onClick: function () {
                    if (envioExiste == false) {
                        guardarEnvioDomicilio();
                    } else {
                        modificarEnvioDomicilio();
                    }
                }
            },

            BtnEnviarVentaOptions: {
                icon: 'fa fa-paper-plane',
                type: 'success',
                width: 110,
                text: 'Enviar',
                hint: 'Enviar comandas',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el tooltip
                disabled: false,
                onInitialized: function (e) {
                    BtnEnviarVentaInstance = e.component;
                },
                onClick: function () {
                    if (total > 0) {
                        //actualizarMensaje();
                        crearAlerta();
                    } else {
                        DevExpress.ui.notify("No existe comandas por enviar", "warning", 5000);
                    }
                }
            },
            BtnCancelarVentaOptions: {
                icon: 'fa fa-trash',
                type: 'danger',
                width: 110,
                hint: 'Cancelar la venta',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el toolti
                text: 'Borrar',
                disabled: false,
                onInitialized: function (e) {
                    BtnCancelarVentaInstance = e.component;
                },
                onClick: function () {
                    modificarVenta();
                }
            },
            BtnHomeOptions: {
                icon: 'fa fa-home',
                type: 'success',
                width: 100,
                hint: 'Home',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el toolti
                // text: 'H',
                disabled: false,
                onInitialized: function (e) {
                    BtnHomeOptionsInstance = e.component;
                },
                onClick: function () {
                    window.location.href = '/';
                }
            },

            BtnBuscarVentaOptions: {
                icon: 'fa fa-search',
                type: 'success',
                width: 110,
                hint: 'Buscar ventas',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el toolti
                text: 'Buscar',
                disabled: false,
                onInitialized: function (e) {
                    BtnBuscarVentaInstance = e.component;
                },
                onClick: function () {
                    PopBuscarVentasInstance.show();
                }
            },
            BtnRegresarOptions: {
                icon: 'fa fa-arrow-left',
                type: 'default',
                width: 125,
                text: 'Regresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnRegresarInstance = e.component;
                },
                onClick: function () {
                    PopPagosInstance.hide();
                    getVentasAbiertasCorteEmpresas();
                }
            },

            BtnRegresarCortesOptions: {
                icon: 'fa fa-arrow-left',
                type: 'default',
                width: 125,
                text: 'Regresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnRegresarCortesInstance = e.component;
                },
                onClick: function () {
                    PopBuscarVentasInstance.hide();
                    ArrayVentasCorte.length = 0;
                    if ($scope.ventas_corte_source && $scope.ventas_corte_source.reload) {
                        $scope.ventas_corte_source.reload();
                    }
                    gridVentasPorCorteInstance.refresh();
                }
            },

            BtnIngresosOptions: {
                icon: 'fas fa-money-bill-wave',
                type: 'success',
                width: 125,
                text: 'Ingresos',
                disabled: false,
                onInitialized: function (e) {
                    BtnIngresosInstance = e.component;
                },
                onClick: function () {
                    Swal.fire({
                        title: '💰 Registrar Ingreso',
                        html: `
        <form id="formIngreso" class="text-start" style="font-size: 1.4rem;">
            <div class="mb-4">
                <label for="montoIngreso" class="form-label fw-semibold" style="font-size: 1.5rem;">Monto del ingreso</label>
                <input id="montoIngreso" type="number" min="0" step="0.01"
                    class="form-control form-control-lg"
                    placeholder="Ej. 1500.00"
                    style="font-size: 1.6rem; height: 3.5rem; padding: 0.75rem 1rem;">
            </div>

            <div class="mb-4">
                <label for="obsIngreso" class="form-label fw-semibold" style="font-size: 1.5rem;">Observación</label>
                <textarea id="obsIngreso" rows="4"
                        class="form-control form-control-lg"
                        placeholder="Motivo o descripción del ingreso"
                        style="font-size: 1.6rem; padding: 1rem;"></textarea>
            </div>
        </form>
    `,
                        showCancelButton: true,
                        confirmButtonText: '<i class="fa-solid fa-floppy-disk"></i> Guardar',
                        cancelButtonText: '<i class="fa-solid fa-xmark"></i> Cerrar',
                        focusConfirm: false,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.fontSize = '1.4rem';
                                popup.style.padding = '3rem';
                                popup.style.width = '650px';
                                popup.style.textAlign = 'left';
                                popup.style.borderRadius = '1rem';
                            }
                            if (overlay) overlay.style.zIndex = '999998';
                            const confirmBtn = Swal.getConfirmButton();
                            const cancelBtn = Swal.getCancelButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.3rem';
                                confirmBtn.style.padding = '1rem 2.6rem';
                            }
                            if (cancelBtn) {
                                cancelBtn.style.fontSize = '1.3rem';
                                cancelBtn.style.padding = '1rem 2.6rem';
                            }

                            // Foco inicial en Monto
                            const montoInput = document.getElementById('montoIngreso');
                            const obsInput = document.getElementById('obsIngreso');
                            montoInput.focus();

                            // Enter en Monto → pasar a Observación
                            montoInput.addEventListener('keydown', function (e) {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    obsInput.focus();
                                }
                            });

                            // Enter en Observación → disparar confirm
                            obsInput.addEventListener('keydown', function (e) {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    Swal.clickConfirm();
                                }
                            });
                        },
                        preConfirm: () => {
                            const monto = parseFloat(document.getElementById('montoIngreso').value.trim());
                            const obs = document.getElementById('obsIngreso').value.trim();

                            if (!monto || monto <= 0) {
                                Swal.showValidationMessage('⚠️ Ingrese un monto válido.');
                                return false;
                            }
                            if (!obs) {
                                Swal.showValidationMessage('⚠️ Ingrese una observación.');
                                return false;
                            }

                            return $http.post('/api/v1/ingreso/', {
                                corte_caja: vm.corteCajaId,
                                personal: vm.personaId,
                                monto: monto,
                                descripcion: obs
                            }).then(response => getIngresosPorCorte())
                                .catch(err => {
                                    Swal.showValidationMessage('❌ No se pudo crear el ingreso');
                                    return false;
                                });
                        }
                    }).then((result) => {
                        if (result.isConfirmed && result.value) {
                            const ingreso = result.value;
                            Swal.fire({
                                icon: 'success',
                                title: '💾 Ingreso registrado',
                                html: `<p style="
                                font-size: 1.3rem; 
                                margin-top: 0.5rem; 
                                color: #333;
                                line-height: 1.4;
                                text-align: center;
                            "></p>`,
                                showConfirmButton: false,
                                timer: 1000,
                                timerProgressBar: true,
                                position: 'center',
                                background: '#f8f9fa',
                                iconColor: '#e6772eff',
                                customClass: {
                                    popup: 'shadow-2xl rounded-3xl p-5 animate__animated animate__fadeInDown',
                                    title: 'fw-bold fs-4 text-center',
                                    htmlContainer: 'text-center'
                                }
                            });
                        }
                    });


                }
            },
            BtnEgresosOptions: {
                icon: 'fas fa-money-bill-wave',
                type: 'danger',
                width: 125,
                text: 'Egresos',
                disabled: false,
                onInitialized: function (e) {
                    BtnEgresosInstance = e.component;
                },
                onClick: function () {
                    Swal.fire({
                        title: '💰 Registrar Egreso',
                        html: `
                        <form id="formEgreso" class="text-start" style="font-size: 1.4rem;">
                            <div class="mb-4">
                                <label for="montoEgreso" class="form-label fw-semibold" style="font-size: 1.5rem;">Monto del egreso</label>
                                <input id="montoEgreso" type="number" min="0" step="0.01"
                                    class="form-control form-control-lg"
                                    placeholder="Ej. 1500.00"
                                    style="font-size: 1.6rem; height: 3.5rem; padding: 0.75rem 1rem;">
                            </div>

                            <div class="mb-4">
                                <label for="obsEgreso" class="form-label fw-semibold" style="font-size: 1.5rem;">Observación</label>
                                <textarea id="obsEgreso" rows="4"
                                        class="form-control form-control-lg"
                                        placeholder="Motivo o descripción del egreso"
                                        style="font-size: 1.6rem; padding: 1rem;"></textarea>
                            </div>
                        </form>
                        `,
                        showCancelButton: true,
                        confirmButtonText: '<i class="fa-solid fa-floppy-disk"></i> Guardar',
                        cancelButtonText: '<i class="fa-solid fa-xmark"></i> Cerrar',
                        focusConfirm: false,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.fontSize = '1.4rem';
                                popup.style.padding = '3rem';
                                popup.style.width = '650px';
                                popup.style.textAlign = 'left';
                                popup.style.borderRadius = '1rem';
                            }
                            if (overlay) overlay.style.zIndex = '999998';

                            const confirmBtn = Swal.getConfirmButton();
                            if (confirmBtn) {
                                confirmBtn.style.fontSize = '1.3rem';
                                confirmBtn.style.padding = '1rem 2.6rem';
                            }
                            const cancelBtn = Swal.getCancelButton();
                            if (cancelBtn) {
                                cancelBtn.style.fontSize = '1.3rem';
                                cancelBtn.style.padding = '1rem 2.6rem';
                            }

                            // Foco inicial en Monto
                            const montoInput = document.getElementById('montoEgreso');
                            const obsInput = document.getElementById('obsEgreso');
                            montoInput.focus();

                            // Enter en Monto → pasar a Observación
                            montoInput.addEventListener('keydown', function (e) {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    obsInput.focus();
                                }
                            });

                            // Enter en Observación → disparar confirm
                            obsInput.addEventListener('keydown', function (e) {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    Swal.clickConfirm();
                                }
                            });
                        },
                        preConfirm: () => {
                            const monto = parseFloat(document.getElementById('montoEgreso').value.trim());
                            const obs = document.getElementById('obsEgreso').value.trim();

                            if (!monto || monto <= 0) {
                                Swal.showValidationMessage('⚠️ Ingrese un monto válido.');
                                return false;
                            }
                            if (!obs) {
                                Swal.showValidationMessage('⚠️ Ingrese una observación.');
                                return false;
                            }

                            return $http.post('/api/v1/egreso/', {
                                corte_caja: vm.corteCajaId,
                                personal: vm.personaId,
                                monto: monto,
                                descripcion: obs
                            }).then(response => getEgresosPorCorte())
                                .catch(err => {
                                    Swal.showValidationMessage('❌ No se pudo crear el egreso');
                                    return false;
                                });
                        }
                    }).then((result) => {
                        if (result.isConfirmed && result.value) {
                            const egreso = result.value;
                            Swal.fire({
                                icon: 'success',
                                title: '💾 Egreso registrado',
                                html: `<p style="
                                    font-size: 1.3rem; 
                                    margin-top: 0.5rem; 
                                    color: #333;
                                    line-height: 1.4;
                                "></p>`,
                                showConfirmButton: false,
                                timer: 1000,
                                timerProgressBar: true,
                                position: 'center',
                                background: '#ebebebff',
                                iconColor: '#e6772eff',
                                customClass: {
                                    popup: 'shadow-2xl rounded-3xl p-5 animate__animated animate__fadeInDown',
                                    title: 'fw-bold fs-4 text-center',
                                    htmlContainer: 'text-center'
                                }
                            });
                        }
                    });
                }
            },
            BtnBuscarVentasOptions: {
                icon: 'fa fa-search',
                type: 'success',
                width: 50,
                //text: 'Buscar',
                disabled: false,
                onInitialized: function (e) {
                    BtnBuscarVentasInstance = e.component;
                },
                onClick: function () {
                    if ($scope.cmbCortes > 0) {
                        getVentasPorCorte();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Advertencia',
                            text: 'Seleccione un corte de caja para continuar',
                            showConfirmButton: true,
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            didOpen: () => {
                                const popup = Swal.getPopup();
                                const overlay = document.querySelector('.swal2-container');

                                // Forzar que quede por encima de cualquier modal/popup
                                if (popup) {
                                    popup.style.zIndex = '999999';
                                    popup.style.fontSize = '1.3rem';
                                    popup.style.padding = '2rem';
                                    popup.style.width = '450px';
                                    popup.style.textAlign = 'center';
                                }
                                if (overlay) {
                                    overlay.style.zIndex = '999998';
                                }

                                const confirmBtn = Swal.getConfirmButton();
                                if (confirmBtn) {
                                    confirmBtn.style.fontSize = '1.2rem';
                                    confirmBtn.style.padding = '0.8rem 2rem';
                                }
                            }
                        });
                    }

                }
            },


            BtnImprimirOptions: {
                icon: 'fa fa-print',
                type: 'default',
                width: 125,
                text: 'Imprimir',
                disabled: true,
                onInitialized: function (e) {
                    BtnImprimirInstance = e.component;
                },
                onClick: function () {
                    imprimirTicketVenta();
                }
            },
            BtnPagarOptions: {
                icon: 'fa fa-credit-card',
                type: 'success',
                width: 125,
                text: 'Pagar',
                disabled: false,
                onInitialized: function (e) {
                    BtnPagarInstance = e.component;
                },
                onClick: function () {
                    if ($scope.numberCobroPago > 0) {
                        getCrearPago();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Advertencia',
                            text: 'El pago debe ser mayor a 0',
                            showConfirmButton: true,
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            didOpen: () => {
                                const popup = Swal.getPopup();
                                const overlay = document.querySelector('.swal2-container');

                                // Forzar que quede por encima de cualquier modal/popup
                                if (popup) {
                                    popup.style.zIndex = '999999';
                                    popup.style.fontSize = '1.3rem';
                                    popup.style.padding = '2rem';
                                    popup.style.width = '450px';
                                    popup.style.textAlign = 'center';
                                }
                                if (overlay) {
                                    overlay.style.zIndex = '999998';
                                }

                                const confirmBtn = Swal.getConfirmButton();
                                if (confirmBtn) {
                                    confirmBtn.style.fontSize = '1.2rem';
                                    confirmBtn.style.padding = '0.8rem 2rem';
                                }
                            }
                        });
                    }

                }
            },

        }
        vm.lookup = {
            CmbMetodoPagoOptions: {
                dataSource: $scope.metodo_pago_source,
                searchEnabled: true,
                placeholder: 'Seleccione el metodo de pago',
                displayExpr: 'nombre',
                valueExpr: 'id',
                value: '',
                dropDownOptions: {
                    title: 'Metodo de pago',
                },
                cancelButtonText: 'Cancelar',
                searchPlaceholder: 'Buscar metodo',
                noDataText: "Sin datos",
                bindingOptions: {
                    value: 'cmbMetodoPago',
                },
                onInitialized: function (e) {
                    CmbMetodoPagoInstance = e.component;
                },
                onValueChanged: function (e) {

                },
            },
            CmbMesaOptions: {
                dataSource: $scope.mesa_source,
                searchEnabled: true,
                placeholder: 'Seleccione la mesa',
                displayExpr: 'nombre',
                valueExpr: 'id',
                value: '',
                dropDownOptions: {
                    title: 'Mesa',
                },
                cancelButtonText: 'Cancelar',
                searchPlaceholder: 'Buscar mesa',
                noDataText: "Sin datos",
                bindingOptions: {
                    value: 'cmbMesa',
                },
                onInitialized: function (e) {
                    CmbMesaInstance = e.component;
                },
                onValueChanged: function (e) {

                },
            },

            CmbCortesOptions: {
                dataSource: $scope.cortes_source,
                searchEnabled: true,
                placeholder: 'Seleccione el corte',
                displayExpr: 'fecha_apertura',
                valueExpr: 'id',
                value: '',
                dropDownOptions: {
                    title: 'Corte',
                },
                cancelButtonText: 'Cancelar',
                searchPlaceholder: 'Buscar corte',
                noDataText: "Sin datos",
                bindingOptions: {
                    value: 'cmbCortes',
                },
                onInitialized: function (e) {
                    CmbCortesInstance = e.component;
                },
                onValueChanged: function (e) {

                },
            },
            CmbClienteOptions: {
                dataSource: $scope.cliente_source,
                searchEnabled: true,
                placeholder: 'Seleccione el cliente',
                displayExpr: 'full_name',
                valueExpr: 'id',
                value: '',
                dropDownOptions: {
                    title: 'Cliente',
                },
                cancelButtonText: 'Cancelar',
                searchPlaceholder: 'Buscar cliente',
                noDataText: "Sin datos",
                bindingOptions: {
                    value: 'cmbCliente',
                },
                onInitialized: function (e) {
                    CmbClienteInstance = e.component;
                },
                onValueChanged: function (e) {
                    //var selectedId = e.value; // id del modelo seleccionado
                    //	var selectedModelo = ArrayModelo.find(function(item) {
                    //      return item.id === selectedId;
                    // });
                    //	if (selectedModelo) {
                    //		$scope.txtMarca = selectedModelo.marca_nombre ;
                    //	}
                },
            },
        }
        vm.grids = {
            gridDesgloseventaOptions: {
                dataSource: $scope.desglose_venta_source,
                paging: {
                    pageSize: 1000
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [1000, 2000, 6000],
                    showInfo: true
                },
                selection: {
                    mode: 'single',
                    selectByRowClick: true
                },
                keyboardNavigation: {
                    enabled: true,
                    cellNavigationEnabled: false, // ❌ desactiva moverse entre celdas
                    editOnKeyPress: false
                },
                filterRow: {
                    visible: true,
                    applyFilter: "auto"
                },
                showBorders: true,

                columns: [
                    { visible: true, cellTemplate: '<div class="btn btn-danger">Eliminar</div>', cssClass: 'sin-padding', headerCellTemplate: "<i class='fa fa-cogs' aria-hidden='true'></i>", width: '85px', allowSorting: false },
                    { dataField: 'id_desglose', caption: 'Id', width: 40, visible: true, },
                    { dataField: 'producto_nombre', caption: 'Producto', width: 170 },
                    { dataField: 'precio_unitario', caption: 'Precio', width: 80, format: { type: 'fixedPoint', precision: 2 } },
                    { dataField: 'descuento', caption: 'Desc.', width: 80, format: { type: 'fixedPoint', precision: 2 } },
                    {
                        dataField: 'total',
                        caption: 'Total',
                        width: 80,
                        format: { type: 'fixedPoint', precision: 2 },
                        cellTemplate: function (container, options) {
                            container.css({
                                'background-color': '#50b3d3',
                                'color': '#003366',
                                'font-weight': 'bold'
                            });
                            container.text(options.text);
                        }
                    },
                    { dataField: 't', caption: ' ', width: 20 },
                ],
                onInitialized: function (e) {
                    gridDesgloseVentaInstance = e.component;
                },
                onCellClick: function (e) {
                    // Verifica que haya datos (no encabezado ni fila vacía)
                    if (!e.data || e.rowType !== "data") {
                        return; // 🔒 ignora clics en encabezado o agrupaciones
                    }

                    if (e.columnIndex === 0) {
                        desgloseVentaSeleccionado = e.data;

                        if (fullVentaActiva.abonada === false && fullVentaActiva.pagada === false) {
                            Swal.fire({
                                title: '¿Eliminar producto?',
                                text: 'Se va a eliminar el producto.',
                                icon: 'question',
                                showCancelButton: true,
                                confirmButtonText: 'Sí',
                                cancelButtonText: 'No',
                                allowOutsideClick: false,
                                allowEscapeKey: false,
                                didOpen: () => {
                                    const popup = Swal.getPopup();
                                    if (popup) {
                                        popup.style.fontSize = '1.2rem';
                                        popup.style.padding = '2rem';
                                        popup.style.width = '400px';
                                    }

                                    const confirmBtn = Swal.getConfirmButton();
                                    const cancelBtn = Swal.getCancelButton();

                                    if (confirmBtn) {
                                        confirmBtn.style.fontSize = '1.5rem';
                                        confirmBtn.style.padding = '0.75rem 2rem';
                                    }
                                    if (cancelBtn) {
                                        cancelBtn.style.fontSize = '1.5rem';
                                        cancelBtn.style.padding = '0.75rem 2rem';
                                    }
                                }
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    transaccionEliminarProductoVenta(desgloseVentaSeleccionado.id_desglose);
                                }
                            });
                        } else {
                            Swal.fire({
                                title: '❌ Imposible eliminar el producto',
                                html: `<p style="font-size:1.1rem;">No se puede eliminar el producto de la venta, ya cuenta con pagos registrados.</p>`,
                                icon: 'error',
                                showConfirmButton: true,
                                confirmButtonText: 'Aceptar',
                                confirmButtonColor: '#d33',
                                allowOutsideClick: false,
                                allowEscapeKey: false,
                                didOpen: () => {
                                    const popup = Swal.getPopup();
                                    if (popup) {
                                        popup.style.fontSize = '1.3rem';
                                        popup.style.padding = '2rem';
                                        popup.style.width = '450px';
                                        popup.style.textAlign = 'center';
                                    }
                                    const confirmBtn = Swal.getConfirmButton();
                                    if (confirmBtn) {
                                        confirmBtn.style.fontSize = '1.2rem';
                                        confirmBtn.style.padding = '0.8rem 2rem';
                                    }
                                }
                            });
                        }
                    }
                },
                onRowClick: function (e) {

                },
                onContentReady: function (e) {
                    const grid = e.component;
                    const totalCount = grid.totalCount();

                    if (totalCount > 0) {
                        // Seleccionar la última fila
                        grid.selectRowsByIndexes([totalCount - 1]);

                        // Mover scroll vertical al fondo
                        const scrollable = grid.getScrollable();
                        if (scrollable) {
                            scrollable.scrollTo({ y: scrollable.scrollHeight() });
                        }
                    }
                },
                noDataText: "Sin datos",
                scrolling: {
                    mode: 'standard',
                    showScrollbar: 'always'
                },
                columnFixing: {
                    enabled: true
                },
                columnAutoWidth: true,
                allowColumnResizing: true,
                height: 515,
                rowAlternationEnabled: true,
                showRowLines: true
            },


            gridVentasPorCorteOptions: {
                dataSource: $scope.ventas_corte_source,
                paging: {
                    pageSize: 10
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [10, 20],
                    showInfo: true
                },
                selection: {
                    mode: 'single',
                    selectByRowClick: true
                },
                keyboardNavigation: {
                    enabled: true,
                    cellNavigationEnabled: false, // ❌ desactiva moverse entre celdas
                    editOnKeyPress: false
                },
                filterRow: {
                    visible: true,
                    applyFilter: "auto"
                },
                showBorders: true,

                columns: [
                    {
                        visible: true,
                        cellTemplate: function (container, options) {
                            // Crear botón de imprimir
                            const btn = $('<div>')
                                .addClass('btn btn-primary btn-sm')
                                .css({ width: '70px' })
                                .text('Imprimir')
                                .on('click', function () {
                                    imprimirTicket(options.data.id_venta);
                                });
                            container.append(btn);
                        },
                        cssClass: 'sin-padding',
                        headerCellTemplate: "<i class='fa fa-print' aria-hidden='true'></i>",
                        width: '85px',
                        allowSorting: false
                    },
                    { dataField: 'id_venta', caption: 'Venta', width: 50 },
                    { dataField: 'cliente', caption: 'Cliente', width: 200 },
                    { dataField: 'personal', caption: 'Atendido por', width: 200 },
                    { dataField: 'total', caption: 'Total', width: 100, format: { type: 'fixedPoint', precision: 2 } },
                    { dataField: 'fecha_venta', caption: 'Fecha Venta', width: 100 },
                    { dataField: 'observaciones', caption: 'Observaciones', width: 200 },
                    { dataField: 'lugar_entrega_id', caption: 'Lugar Entrega', width: 100 },
                    { dataField: 'corte_caja_id', caption: 'Corte Caja', width: 100 }
                ],
                onInitialized: function (e) {
                    gridVentasPorCorteInstance = e.component;
                },
                onRowClick: function (e) {

                },

                noDataText: "Sin datos",
                scrolling: {
                    mode: 'standard',
                    showScrollbar: 'always'
                },
                columnFixing: {
                    enabled: true
                },
                columnAutoWidth: true,
                allowColumnResizing: true,
                height: 500,
                rowAlternationEnabled: true,
                showRowLines: true
            },
            gridDesglosePagoVentaOptions: {
                dataSource: $scope.pagos_por_venta_source,
                paging: {
                    pageSize: 1000
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [1000, 2000, 6000],
                    showInfo: true
                },
                selection: {
                    mode: 'single'
                },
                filterRow: {
                    visible: true,
                    applyFilter: "auto"
                },
                showBorders: true,

                columns: [
                    { visible: true, cellTemplate: '<div class="btn btn-danger">Eliminar</div>', cssClass: 'sin-padding', headerCellTemplate: "<i class='fa fa-cogs' aria-hidden='true'></i>", width: '85px', allowSorting: false },
                    { dataField: 'id_pago', caption: 'Id', width: 40, visible: true, },
                    { dataField: 'metodo_pago_nombre', caption: 'Metodo de pago', width: 170 },
                    {
                        dataField: 'monto',
                        caption: 'Monto',
                        width: 80,
                        format: { type: 'fixedPoint', precision: 2 },
                        cellTemplate: function (container, options) {
                            container.css({
                                'background-color': '#50b3d3',
                                'color': '#003366',
                                'font-weight': 'bold'
                            });
                            container.text(options.text);
                        }
                    },
                    { dataField: 't', caption: ' ', width: 20 },
                ],
                onInitialized: function (e) {
                    gridDesglosePagoVentaInstance = e.component;
                },
                onCellClick: function (e) {
                    if (e.columnIndex == 0) {
                        if (e.rowIndex > -1) {
                            pagoSeleccionado = e.data;
                            Swal.fire({
                                title: '¿Eliminar pago?',
                                text: 'Se va a eliminar el pago.',
                                icon: 'question',
                                showCancelButton: true,
                                confirmButtonText: 'Sí',
                                cancelButtonText: 'No',
                                allowOutsideClick: false,
                                allowEscapeKey: false,
                                didOpen: () => {
                                    const popup = Swal.getPopup();
                                    const overlay = document.querySelector('.swal2-container');

                                    // Forzar que quede por encima de cualquier otro popup/modal
                                    if (popup) {
                                        popup.style.zIndex = '999999';  // Muy alto
                                        popup.style.fontSize = '1.2rem';
                                        popup.style.padding = '2rem';
                                        popup.style.width = '400px';
                                        popup.style.textAlign = 'center';
                                    }
                                    if (overlay) {
                                        overlay.style.zIndex = '999998';
                                    }

                                    const confirmBtn = Swal.getConfirmButton();
                                    const cancelBtn = Swal.getCancelButton();

                                    if (confirmBtn) {
                                        confirmBtn.style.fontSize = '1.5rem';
                                        confirmBtn.style.padding = '0.75rem 2rem';
                                    }
                                    if (cancelBtn) {
                                        cancelBtn.style.fontSize = '1.5rem';
                                        cancelBtn.style.padding = '0.75rem 2rem';
                                    }
                                }
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    eliminarPago(pagoSeleccionado.id_pago)
                                }
                            });
                        }
                    }
                },
                onRowClick: function (e) {

                },
                onContentReady: function (e) {
                },
                noDataText: "Sin datos",
                scrolling: {
                    mode: 'standard',
                    showScrollbar: 'always'
                },
                columnFixing: {
                    enabled: true
                },
                columnAutoWidth: true,
                allowColumnResizing: true,
                height: 400,
                rowAlternationEnabled: true,
                showRowLines: true
            },
            gridEgresosPorCorteOptions: {
                dataSource: $scope.egresos_por_corte_source, // tu data de egresos
                // Paginación
                paging: {
                    pageSize: 1000
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [1000, 2000, 6000],
                    showInfo: true
                },

                // Solo lectura
                selection: {
                    mode: 'none'
                },

                // Filtro por fila
                filterRow: {
                    visible: true,
                    applyFilter: "auto"
                },

                showBorders: true,
                rowAlternationEnabled: true,
                showRowLines: true,
                height: 400,
                columnAutoWidth: true,
                allowColumnResizing: true,
                columnFixing: {
                    enabled: true
                },

                // Columnas ejemplo para egresos
                columns: [
                    { dataField: 'id_egreso', caption: 'ID', width: 40 },
                    { dataField: 'descripcion', caption: 'Concepto', width: 300 },
                    {
                        dataField: 'monto',
                        caption: 'Monto',
                        width: 60,
                        format: { type: 'fixedPoint', precision: 2 },
                        cellTemplate: function (container, options) {
                            container.css({
                                'background-color': '#f2a0a0',
                                'color': '#800000',
                                'font-weight': 'bold'
                            });
                            container.text(options.text);
                        }
                    }
                ],

                // Totalización de la columna "monto"
                summary: {
                    totalItems: [
                        {
                            column: "monto",
                            summaryType: "sum",
                            displayFormat: "Total: {0}",
                            valueFormat: { type: "fixedPoint", precision: 2 }
                        }
                    ]
                },

                onInitialized: function (e) {
                    gridEgresosPorCorteInstance = e.component;
                },
                // Mensaje cuando no hay datos
                noDataText: "Sin egresos registrados",

                // Scroll
                scrolling: {
                    mode: 'standard',
                    showScrollbar: 'always'
                }
            },
            gridIngresosPorCorteOptions: {
                dataSource: $scope.ingresos_por_corte_source, // tu data de egresos
                // Paginación
                paging: {
                    pageSize: 1000
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [1000, 2000, 6000],
                    showInfo: true
                },

                // Solo lectura
                selection: {
                    mode: 'none'
                },

                // Filtro por fila
                filterRow: {
                    visible: true,
                    applyFilter: "auto"
                },

                showBorders: true,
                rowAlternationEnabled: true,
                showRowLines: true,
                height: 400,
                columnAutoWidth: true,
                allowColumnResizing: true,
                columnFixing: {
                    enabled: true
                },

                // Columnas ejemplo para egresos
                columns: [
                    { dataField: 'id_ingreso', caption: 'ID', width: 40 },
                    { dataField: 'descripcion', caption: 'Concepto', width: 300 },
                    {
                        dataField: 'monto',
                        caption: 'Monto',
                        width: 60,
                        format: { type: 'fixedPoint', precision: 2 },
                        cellTemplate: function (container, options) {
                            container.css({
                                'background-color': '#9af392ff',
                                'color': '#008055ff',
                                'font-weight': 'bold'
                            });
                            container.text(options.text);
                        }
                    }
                ],

                // Totalización de la columna "monto"
                summary: {
                    totalItems: [
                        {
                            column: "monto",
                            summaryType: "sum",
                            displayFormat: "Total: {0}",
                            valueFormat: { type: "fixedPoint", precision: 2 }
                        }
                    ]
                },

                onInitialized: function (e) {
                    gridIngresosPorCorteInstance = e.component;
                },
                // Mensaje cuando no hay datos
                noDataText: "Sin egresos registrados",

                // Scroll
                scrolling: {
                    mode: 'standard',
                    showScrollbar: 'always'
                }
            }


        }
        vm.popups = {
            popPagosOptions: {
                showTitle: true,
                width: 800,
                height: 800,
                title: "Pagar cuenta",
                dragEnabled: false,
                closeOnOutsideClick: false,
                showCloseButton: false, // <--- Aquí se quita la X
                bindingOptions: {
                    visible: "showPopPagos",
                },
                onInitialized: function (e) {
                    PopPagosInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onShowing: function (e) {
                    // Esto se ejecuta cada vez que el popup se va a mostrar
                    getMetodoPago();
                    getPagosPorVenta($scope.ventaActiva);
                    if (subTotal > 0) {
                        BtnPagarInstance.option("disabled", false);
                    } else {
                        BtnPagarInstance.option("disabled", true);
                    }

                },
                // onContentReady: function (e) {
                //   getMetodoPago();
                // getPagosPorVenta($scope.ventaActiva);
                //if (subTotal > 0) {
                //       BtnPagarInstance.option("disabled", false);
                // } else {
                //   BtnPagarInstance.option("disabled", true);
                // }

                //}
            },
            popBuscarVentasOptions: {
                showTitle: true,
                width: 1200,
                height: 800,
                title: "Buscar ventas",
                dragEnabled: false,
                closeOnOutsideClick: false,
                showCloseButton: false, // <--- Aquí se quita la X
                bindingOptions: {
                    visible: "showPopBuscar",
                },
                onInitialized: function (e) {
                    PopBuscarVentasInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onShowing: function (e) {
                    // Esto se ejecuta cada vez que el popup se va a mostrar
                    // getMetodoPago();
                    // getPagosPorVenta($scope.ventaActiva);
                    // if (subTotal > 0) {
                    //   BtnPagarInstance.option("disabled", false);
                    // } else {
                    //   BtnPagarInstance.option("disabled", true);
                    // }
                },
                onContentReady: function (e) {
                    getCortesCaja();
                    // getPagosPorVenta($scope.ventaActiva);
                    //if (subTotal > 0) {
                    //       BtnPagarInstance.option("disabled", false);
                    // } else {
                    //   BtnPagarInstance.option("disabled", true);
                }

                //}
            },
            popEgresosOptions: {
                showTitle: true,
                width: 800,
                height: 600,
                title: "Egresos",
                dragEnabled: false,
                closeOnOutsideClick: false,
                showCloseButton: false, // <--- Aquí se quita la X
                bindingOptions: {
                    visible: "showPopEgresos",
                },
                onInitialized: function (e) {
                    popEgresosInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },

                onContentReady: function (e) {

                }
            },

            popIngresosOptions: {
                showTitle: true,
                width: 800,
                height: 600,
                title: "Ingresos",
                dragEnabled: false,
                closeOnOutsideClick: false,
                showCloseButton: false, // <--- Aquí se quita la X
                bindingOptions: {
                    visible: "showPopingresos",
                },
                onInitialized: function (e) {
                    popIngresosInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },

                onContentReady: function (e) {

                }
            },

            popEnvioDomicilioOptions: {
                showTitle: true,
                width: 800,
                height: 600,
                title: "Envio a domicilio",
                dragEnabled: false,
                closeOnOutsideClick: false,
                showCloseButton: false, // <--- Aquí se quita la X
                bindingOptions: {
                    visible: "showPopDomicilio",
                },
                onInitialized: function (e) {
                    popEnvioDomicilioInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onContentReady: function (e) {

                },
                onShown: function () {
                    vaciarInformacionEnvio();
                    consultarEnvioDomicilio();
                },
            },


        };
    }
})();
