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
            BtnEnviarVentaInstance;

        var ArrayDesgloseVenta = [], ArrayMesa = [], ArrayEmpresasVenta = [], ArrayClientes = [], ArrayMetodoPago = [],
            ArrayPagosPorVenta = [];
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
            apiKey: "AIzaSyCOmQFHQlVFPIiBUyx1k7eshNW4JM-Z-rg",
            authDomain: "signals-test-lasser.firebaseapp.com",
            projectId: "signals-test-lasser",
            storageBucket: "signals-test-lasser.appspot.com",
            messagingSenderId: "901814785470",
            appId: "1:901814785470:web:221e517efbd5f4a40d15ef",
            databaseURL: "https://signals-test-lasser-default-rtdb.firebaseio.com"
        };

        if (!firebase.apps.length) {
            firebase.initializeApp(firebaseConfig);
        }

        const db = firebase.database();

        // Nodo fijo
        const nodo = db.ref('alertas/centro/');

        function actualizarMensaje() {
            const segundos = segundosDesdeMedianoche();
            nodo.set({ mensaje: segundos })  // Actualiza el valor en Firebase
                .then(() => console.log("Mensaje actualizado:", segundos))
                .catch(err => console.error("Error al actualizar:", err));
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

        function getPagosPorVenta(venta) {
            $scope.isLoadPanelVisible = true;

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
            console.log(ventaId);
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
                    console.log(fullVentaActiva);
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
            console.log(ventaId);
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
            if (productoEncontrado) {
                console.log(productoEncontrado.data.empresa);
            }
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
                    console.log(response);
                    productosVenta(idVenta);
                    var mensaje = response.data.success;
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
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
                    console.log(response);
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
                    DevExpress.ui.notify("Se puede vender " + id, "success", 3500);
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

        vm.textBox = {

        }
        vm.button = {
            BtnCrearVentaOptions: {
                icon: 'fas fa-plus',
                type: 'default',
                width: 135,
                text: 'Venta',
                disabled: false,
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
                width: 135,
                text: 'Cobrar',
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
            BtnEnviarVentaOptions: {
                icon: 'fa fa-credit-card',
                type: 'success',
                width: 135,
                text: 'Enviar comanda',
                disabled: false,
                onInitialized: function (e) {
                    BtnEnviarVentaInstance = e.component;
                },
                onClick: function () {
                    if (total > 0) {
                        actualizarMensaje();
                    } else {
                        DevExpress.ui.notify("No existe comandas pora enviar", "warning", 5000);
                    }
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
                    mode: 'single'
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
                    if (e.columnIndex == 0) {
                        if (e.rowIndex > -1) {
                            desgloseVentaSeleccionado = e.data;

                            if (fullVentaActiva.abonada == false && fullVentaActiva.pagada == false) {
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
                                    html: `<p style="font-size:1.1rem;">No se puede elliminar el producto de la venta, ya cuenta con pagos registrados.</p>`,
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
                    mode: 'standar',
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
                    mode: 'standar',
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
                onContentReady: function (e) {
                    getMetodoPago();
                    getPagosPorVenta($scope.ventaActiva);
                }
            },
        };
    }
})();
