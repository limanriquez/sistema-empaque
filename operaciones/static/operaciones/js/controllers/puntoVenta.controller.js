// panel.controller.js
(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers', [])
        .controller('PuntoVenta', PuntoVentaController);
    PuntoVentaController.$inject = ['$http', '$scope', '$filter'];

    function PuntoVentaController($http, $scope, $filter) {
        var gridDesgloseVentaInstance, CmbMesaInstance, BtnCrearVentaInstance, CmbClienteInstance, PopPagosInstance,
            BtnRegresarInstance, CmbMetodoPagoInstance;
        var ArrayDesgloseVenta = [], ArrayMesa = [], ArrayEmpresasVenta = [], ArrayClientes = [], ArrayMetodoPago = [];
        var strEmpresasVenta = ""
        var vm = this;
        var tab = 0;
        var idVentaActiva = 0;
        var desgloseVentaSeleccionado;
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

        function getmetodoPago() {
            $scope.isLoadPanelVisible = true;
            $http.get('/api/v1/metodoPago/activos/').then(
                function (response) {
                    ArrayMetodoPago.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        console.log(response.data[i])
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
                        productosVenta($scope.ventaActiva)
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
                    $scope.txtSubtotal = $filter('currency')(subTotal, '$', 2);
                    $scope.txtDescuento = $filter('currency')(descuento, '$', 2);
                    $scope.txtTotal = $filter('currency')(total, '$', 2);

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
            $scope.ventaActiva = ventaId;
            productosVenta($scope.ventaActiva)
        };
        // Función para mostrar alertify con el id del predio
        vm.mostrarAlertId = function (id) {
            if ($scope.ventaActiva > 0) {
                transaccionVentaProducto(id, $scope.ventaActiva)
                DevExpress.ui.notify("Se puede vender " + id, "success", 3500);
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



        vm.textBox = {
            TxtCobroCambioOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtCobroCambio'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtCobroPagoOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtCobroPago'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtCobroPagadoOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtCobroPagado'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtCobroPendienteOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtCobroPendiente'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtCobroTotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtCobroTotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtCobroDescuentoOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtCobroDescuento'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtCobroSubtotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtCobroSubTotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtSubtotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtSubtotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtDescuentoOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtDescuento'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            },
            TxtTotalOptions: {
                readOnly: true,
                showClearButton: true,
                inputAttr: {
                    style: "text-align: right; font-weight: bold; font-size: 18px;"
                },
                bindingOptions: {
                    value: 'txtTotal'
                },
                format: {
                    type: "currency",
                    precision: 2
                },
                onValueChanged: function (data) {
                    // Lógica adicional si se requiere
                }
            }
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

            BtnRegresarOptions: {
                icon: 'fa fa-arrow-left',
                type: 'success',
                width: 125,
                text: 'Regresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnRegresarInstance = e.component;
                },
                onClick: function () {
                    PopPagosInstance.hide();
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
        }
        vm.popups = {
            popPagosOptions: {
                showTitle: true,
                width: 800,
                height: 600,
                title: "Pagar cuenta",
                dragEnabled: false,
                closeOnOutsideClick: false,
                bindingOptions: {
                    visible: "showPopPagos",
                },
                onInitialized: function (e) {
                    PopPagosInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onContentReady: function (e) {
                   getmetodoPago();
                }
            },
        };
    }
})();
