(function () {
    'use strict';
    angular
        .module('inventarios.inventario.controllers')
        .controller('MovimientoInventario', MovimientoInventarioController);
    MovimientoInventarioController.$inject = ['$http', '$scope', '$filter'];
    function MovimientoInventarioController($http, $scope, $filter) {
        let vm = this;
        let grdInventariosInstance, BtnIngresarInstance, BtnSalidaInstance,
            popIngresarInventarioInstance, BtnAgregarInventarioInstance,
            NumBoxCantidad, BtnRegresarInstance, descripcionInstance,
            disminuirDescripcionInstance, BtnDisminuirInventarioInstance,
            popDisminuirInventarioInstance, BtnDisminuirRegresarInstance,
            NumBoxDisminuirCantidad, BtnMovimientosPorCorteInstance,
            popBuscarMovimientosPorCorteInstance, BtnRegresarCortesInstance,
            gridMovimientosPorCorteInstance, CmbCortesInstance, BtnBuscarVentasInstance;
        let inventarioSeleccionado = null;
        let ArrayInventarios = [];
        let ArrayMovimientosInventario = [];
        let ArrayCortes = []
        let maximoDisminuir = 0;
        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;

        function showLoading() {
            Swal.fire({
                title: 'Cargando...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        }
        // Ocultar loading
        function hideLoading() {
            Swal.close();
        }
        getInventariosPorEmpresa();
        function getInventariosPorEmpresa() {
            showLoading();
            const url = "/inventario_por_empresa/";
            $http.get(url).then(
                function (response) {
                    hideLoading();
                    ArrayInventarios.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayInventarios.push(response.data[i]);
                    }
                    grdInventariosInstance.refresh();
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                    hideLoading();
                }
            );
        };
        function incrementarInventario(stockItemId, cantidad, descripcion) {
            $scope.isLoadPanelVisible = true;
            descripcion = descripcion ?? "";
            const params = new URLSearchParams({
                id: stockItemId,
                cantidad: cantidad,
                descripcion: descripcion
            });
            const url = `/incrementar_Stock/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    $scope.isLoadPanelVisible = false;
                    Swal.fire({
                        icon: 'success',
                        title: 'Inventario guardado',
                        text: 'El inventario fue registrado exitosamente.',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');

                            // Mantener el popup encima del popup de DevExtreme
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }
                        }
                    }).then(() => {
                        $scope.numBoxCantidad = 1;
                        $scope.descripcion = "";
                        popIngresarInventarioInstance.hide();
                        getInventariosPorEmpresa();
                    });
                },
                function (error) {
                    $scope.isLoadPanelVisible = false;
                    Swal.fire({
                        icon: 'error',
                        title: 'Error al guardar el inventario',
                        text: 'Hubo un problema al intentar guardar la información del inventario.',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');

                            // Mantener el popup encima del popup de DevExtreme
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }
                        }
                    });
                }
            );
        }
        function disminuirInventario(stockItemId, cantidad, descripcion) {
            $scope.isLoadPanelVisible = true;
            descripcion = descripcion ?? "";
            const params = new URLSearchParams({
                id: stockItemId,
                cantidad: cantidad,
                descripcion: descripcion
            });
            const url = `/disminuir_Stock/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    $scope.isLoadPanelVisible = false;
                    Swal.fire({
                        icon: 'success',
                        title: 'Inventario guardado',
                        text: 'La salida de inventario fue registrada exitosamente.',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');

                            // Mantener el popup encima del popup de DevExtreme
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }
                        }
                    }).then(() => {
                        $scope.numBoxCantidad = 1;
                        $scope.descripcion = "";
                        popDisminuirInventarioInstance.hide();
                        getInventariosPorEmpresa();
                    });
                },
                function (error) {
                    $scope.isLoadPanelVisible = false;
                    Swal.fire({
                        icon: 'error',
                        title: 'Error al guardar el inventario',
                        text: 'Hubo un problema al intentar guardar la información del inventario.',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');

                            // Mantener el popup encima del popup de DevExtreme
                            if (popup) {
                                popup.style.zIndex = '999999';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }
                        }
                    });
                }
            );
        }

        // Función auxiliar para obtener el token CSRF
        function getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
        }


        //  function incrementarStock(){
        //    incrementar_Stock
        // }
        function validarInventario() {
            if (inventarioSeleccionado) {
                if ($scope.numBoxCantidad) {
                    incrementarInventario(inventarioSeleccionado.stock_item_id, $scope.numBoxCantidad, $scope.descripcion);
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Advertencia',
                        text: 'Ingrese una cantidad para incrementar el inventario',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');
                            // Forzar que quede por encima de cualquier modal/popup
                            if (popup) {
                                popup.style.zIndex = '999999';
                                //  popup.style.fontSize = '1.3rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }

                        }
                    });
                }

            }
        }
        function validarDisminuirInventario() {
            if (inventarioSeleccionado) {
                if ($scope.numBoxDisminuirCantidad) {
                    disminuirInventario(inventarioSeleccionado.stock_item_id, $scope.numBoxDisminuirCantidad, $scope.DisminuirDescripcion);
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Advertencia',
                        text: 'Ingrese una cantidad para disminuir el inventario',
                        showConfirmButton: true,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            const overlay = document.querySelector('.swal2-container');
                            // Forzar que quede por encima de cualquier modal/popup
                            if (popup) {
                                popup.style.zIndex = '999999';
                                //  popup.style.fontSize = '1.3rem';
                                popup.style.padding = '2rem';
                                popup.style.width = '450px';
                                popup.style.textAlign = 'center';
                            }
                            if (overlay) {
                                overlay.style.zIndex = '999998';
                            }

                        }
                    });
                }

            }
        }

        function getCortesCaja() {
            $scope.isLoadPanelVisible = true;
            $http.get('/cortes_por_empresa/', { params: { empresa: vm.empresaId } })
                .then(
                    function (response) {
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

        function getMovimientosInventarioPorCorte() {
            const params = new URLSearchParams({
                corteCaja: $scope.cmbCortes,
            });
            $scope.isLoadPanelVisible = true;
            const url = `/movimiento_Inventario_Por_Corte_Caja/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    ArrayMovimientosInventario.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayMovimientosInventario.push(response.data[i]);
                    }

                    if ($scope.movimientos_inventario_source && $scope.movimientos_inventario_source.reload) {
                        $scope.movimientos_inventario_source.reload();
                    }
                    gridMovimientosPorCorteInstance.refresh();
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                }
            );
        };

        $scope.inventarios_source = new DevExpress.data.DataSource({
            store: ArrayInventarios
        });
        $scope.movimientos_inventario_source = new DevExpress.data.DataSource({
            store: ArrayMovimientosInventario
        });

        $scope.cortes_source = new DevExpress.data.DataSource({
            store: ArrayCortes
        });
        vm.lookup = {
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
        }
        vm.numberBox = {
            NumBoxCantidadOptions: {
                bindingOptions: {
                    value: 'numBoxCantidad'
                },
                placeholder: 'Cantidad',
                showClearButton: true,
                showSpinButtons: true,
                min: 1,
                max: 1000,
                step: 1,
                format: '#,##0', // formato numérico (sin símbolo de moneda)
                inputAttr: {
                    id: 'numBoxCantidad',
                    style: "text-align:right; font-weight:bold;"
                },
                buttons: ['clear', 'spins'],
                onValueChanged: function (e) {
                    if (e.value <= 0 || !Number.isInteger(e.value)) {
                        e.component.option('isValid', false);
                        e.component.option('validationError', { message: 'Debe ser un número entero mayor que 0' });
                    } else {
                        e.component.option('isValid', true);
                    }
                },
                onInitialized: function (e) {
                    NumBoxCantidad = e.component;
                },
                onKeyDown: function (e) {
                    if (e.event.key === "Enter" || e.event.which === 13) {
                        setTimeout(() => {
                            if (descripcionInstance) {
                                descripcionInstance.focus();
                            }
                        }, 30);
                    }
                }
            },
            NumBoxDisminuirCantidadOptions: {
                bindingOptions: {
                    value: 'numBoxDisminuirCantidad'
                },
                placeholder: 'Cantidad',
                showClearButton: true,
                showSpinButtons: true,
                min: 1,
                max: 1000,
                step: 1,
                format: '#,##0', // formato numérico (sin símbolo de moneda)
                inputAttr: {
                    id: 'numBoxCantidad',
                    style: "text-align:right; font-weight:bold;"
                },
                buttons: ['clear', 'spins'],
                onValueChanged: function (e) {
                    if (e.value <= 0 || !Number.isInteger(e.value)) {
                        e.component.option('isValid', false);
                        e.component.option('validationError', { message: 'Debe ser un número entero mayor que 0' });
                    } else {
                        e.component.option('isValid', true);
                    }
                },
                onInitialized: function (e) {
                    NumBoxDisminuirCantidad = e.component;
                },
                onKeyDown: function (e) {
                    if (e.event.key === "Enter" || e.event.which === 13) {
                        setTimeout(() => {
                            if (disminuirDescripcionInstance) {
                                disminuirDescripcionInstance.focus();
                            }
                        }, 30);
                    }
                }
            }
        };
        vm.textArea = {
            descripcionOptions: {
                height: 90,
                maxLength: 500,
                placeholder: "Escribe la descripción...",
                bindingOptions: {
                    value: "descripcion"  // variable del scope
                },
                onInitialized: function (e) {
                    descripcionInstance = e.component;
                },
                onKeyDown: function (e) {
                    if (e.event.key === "Enter" || e.event.which === 13) {
                        e.event.preventDefault();
                        setTimeout(() => {
                            validarInventario();
                        }, 30);
                    }
                }
            },
            disminuirDescripcionOptions: {
                height: 90,
                maxLength: 500,
                placeholder: "Escribe la descripción...",
                bindingOptions: {
                    value: "descripcion"  // variable del scope
                },
                onInitialized: function (e) {
                    disminuirDescripcionInstance = e.component;
                },
                onKeyDown: function (e) {
                    if (e.event.key === "Enter" || e.event.which === 13) {
                        e.event.preventDefault();
                        setTimeout(() => {
                            validarDisminuirInventario();
                        }, 30);
                    }
                }
            }
        };
        vm.button = {
            BtnBuscarMovimientosOptions: {
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
                        getMovimientosInventarioPorCorte();
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

            BtnRegresarCortesOptions: {
                icon: 'fa fa-arrow-left',
                type: 'success',
                width: 125,
                text: 'Regresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnRegresarCortesInstance = e.component;
                },
                onClick: function () {
                    popBuscarMovimientosPorCorteInstance.hide();
                    ArrayMovimientosInventario.length = 0;
                    if ($scope.movimientos_inventario_source && $scope.movimientos_inventario_source.reload) {
                        $scope.movimientos_inventario_source.reload();
                    }
                    gridMovimientosPorCorteInstance.refresh();
                }
            },
            BtnMovimientosPorCorteOptions: {
                icon: 'fa fa-search',
                type: 'default',
                width: 110,
                hint: 'Buscar corte',  // <-- texto del tooltip
                showTooltip: true,                // <-- activa el toolti
                text: 'Buscar',
                disabled: false,
                onInitialized: function (e) {
                    BtnMovimientosPorCorteInstance = e.component;
                },
                onClick: function () {
                    popBuscarMovimientosPorCorteInstance.show();
                }
            },
            BtnAgregarInventarioOptions: {
                icon: 'fas fa-save',
                type: 'success',
                width: 120,
                text: 'Guardar',
                disabled: false,
                onInitialized: function (e) {
                    BtnAgregarInventarioInstance = e.component;
                },
                onClick: function () {
                    validarInventario();
                }
            },
            BtnDisminuirInventarioOptions: {
                icon: 'fas fa-save',
                type: 'success',
                width: 120,
                text: 'Guardar',
                disabled: false,
                onInitialized: function (e) {
                    BtnDisminuirInventarioInstance = e.component;
                },
                onClick: function () {
                    validarDisminuirInventario();
                }
            },

            BtnRegresarOptions: {
                icon: 'fa fa-arrow-left',
                type: 'danger',
                width: 120,
                text: 'Regresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnRegresarInstance = e.component;
                },
                onClick: function () {
                    $scope.numBoxCantidad = 1;
                    $scope.descripcion = "";
                    popIngresarInventarioInstance.hide();

                }
            },
            BtnDisminuirRegresarOptions: {
                icon: 'fa fa-arrow-left',
                type: 'danger',
                width: 120,
                text: 'Regresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnDisminuirRegresarInstance = e.component;
                },
                onClick: function () {
                    $scope.numBoxDisminuirCantidad = 1;
                    $scope.disminuirDescripcion = "";
                    popDisminuirInventarioInstance.hide();

                }
            },
            BtnIngresarOptions: {
                icon: 'fa fa-plus',
                type: 'success',
                width: 135,
                text: 'Ingresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnIngresarInstance = e.component;
                },
                onClick: function () {
                    if (inventarioSeleccionado) {
                        //      incrementarInventario();
                        popIngresarInventarioInstance.show();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Advertencia',
                            text: 'Seleccione un elemento para continuar',
                            showConfirmButton: true,
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            didOpen: () => {
                                const popup = Swal.getPopup();
                                const overlay = document.querySelector('.swal2-container');
                                // Forzar que quede por encima de cualquier modal/popup
                                if (popup) {
                                    popup.style.zIndex = '999999';
                                    //  popup.style.fontSize = '1.3rem';
                                    popup.style.padding = '2rem';
                                    popup.style.width = '450px';
                                    popup.style.textAlign = 'center';
                                }
                                if (overlay) {
                                    overlay.style.zIndex = '999998';
                                }

                            }
                        });
                    }

                }
            },
            BtnSalidaOptions: {
                icon: 'fa fa-minus',
                type: 'danger',
                width: 135,
                text: 'Salida',
                disabled: false,
                onInitialized: function (e) {
                    BtnSalidaInstance = e.component;
                },
                onClick: function () {
                    if (inventarioSeleccionado) {
                        popDisminuirInventarioInstance.show();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Advertencia',
                            text: 'Seleccione un elemento para continuar',
                            showConfirmButton: true,
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            didOpen: () => {
                                const popup = Swal.getPopup();
                                const overlay = document.querySelector('.swal2-container');
                                // Forzar que quede por encima de cualquier modal/popup
                                if (popup) {
                                    popup.style.zIndex = '999999';
                                    //  popup.style.fontSize = '1.3rem';
                                    popup.style.padding = '2rem';
                                    popup.style.width = '450px';
                                    popup.style.textAlign = 'center';
                                }
                                if (overlay) {
                                    overlay.style.zIndex = '999998';
                                }

                            }
                        });
                    }
                }
            },
        }
        vm.grid = {
            gridMovimientosPorCorteOptions: {
                dataSource: $scope.movimientos_inventario_source,
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
                    cellNavigationEnabled: false,
                    editOnKeyPress: false
                },
                filterRow: {
                    visible: true,
                    applyFilter: "auto"
                },
                showBorders: true,
                groupPanel: {
                    visible: true,
                    emptyPanelText: "Arrastra una columna aquí para agrupar"
                },
                columns: [
                    { dataField: "id", dataType: "number", caption: "ID", width: 70, visible: false },
                    { dataField: "stock_item_id", dataType: "number", caption: "ID Producto", width: 100, visible: false },
                    { dataField: "stock_item_nombre", dataType: "string", caption: "Producto", width: 200 },
                    {
                        dataField: "tipo", dataType: "string", caption: "Tipo", width: 100, cellTemplate: function (container, options) {
                            if (options.value === "Entrada") {
                                container.css({
                                    "background-color": "#d4edda", // verde clarito
                                    "font-weight": "bold"
                                });
                            } else if (options.value === "Salida") {
                                container.css({
                                    "background-color": "#f8d7da", // rojo clarito
                                    "font-weight": "bold"
                                });
                            }
                            container.text(options.value);
                        }
                    },
                    { dataField: "cantidad", dataType: "number", caption: "Cantidad", width: 100, format: "#,##0" },
                    { dataField: "descripcion", dataType: "string", caption: "Descripción", width: 250 },
                    { dataField: "personal", dataType: "string", caption: "Personal", width: 200 },
                    { dataField: "fecha", dataType: "date", caption: "Fecha", width: 180, format: "yyyy-MM-dd HH:mm:ss" }
                ],
                onInitialized: function (e) {
                    gridMovimientosPorCorteInstance = e.component;
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
                export: {
                    enabled: true,
                    fileName: "MovimientosInventario"
                },
                toolbar: {
                    items: [
                        "groupPanel",
                        "exportButton" // botón para exportar
                    ]
                },
                columnAutoWidth: true,
                allowColumnResizing: true,
                height: 500,
                rowAlternationEnabled: true,
                showRowLines: true
            },
            grdInventarioOptions: {
                dataSource: $scope.inventarios_source,
                paging: {
                    pageSize: 20
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [20, 40, 60],
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
                showColumnLines: true,
                allowColumnResizing: true,
                columnAutoWidth: true,
                rowAlternationEnabled: true,
                columnFixing: {
                    enabled: true
                },
                allowColumnReordering: true,
                grouping: {
                    autoExpandAll: false
                },
                columns: [
                    { dataField: 'stock_item_id', caption: 'ID Stock', visible: false },
                    { dataField: 'nombre_producto', caption: 'Nombre Producto' },
                    {
                        dataField: 'total_stock',
                        caption: 'Existencia',
                        dataType: 'number',
                        cellTemplate: function (container, options) {
                            var value = options.value;
                            if (value < 15) {
                                container.css({
                                    "background-color": "#ffd6d6",
                                    "font-weight": "bold"
                                });
                            }
                            container.text(value);
                        }
                    }
                ],
                onInitialized: function (e) {
                    grdInventariosInstance = e.component;
                },
                onRowClick: function (e) {
                    inventarioSeleccionado = e.data;
                },
                noDataText: "Sin datos",
                scrolling: {
                    mode: 'standard',
                    showScrollbar: 'always'
                }
            }


        };
        vm.popups = {
            popIngresarInvenarioOptions: {
                showTitle: true,
                width: 500,
                height: 300,
                title: "Ingresar inventario",
                dragEnabled: false,
                closeOnOutsideClick: false,
                bindingOptions: {
                    visible: "showPopIngresarInvenario",
                },
                onInitialized: function (e) {
                    popIngresarInventarioInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onShown: function () {
                    setTimeout(() => {
                        if (NumBoxCantidad) {
                            NumBoxCantidad.focus();
                        }
                    }, 50);
                }
            },
            popDisminuirInvenarioOptions: {
                showTitle: true,
                width: 500,
                height: 300,
                title: "Disminuir inventario",
                dragEnabled: false,
                closeOnOutsideClick: false,
                bindingOptions: {
                    visible: "showPopDisminuirInvenario",
                },
                onInitialized: function (e) {
                    popDisminuirInventarioInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onShown: function () {
                    setTimeout(() => {
                        if (NumBoxDisminuirCantidad) {
                            $scope.numBoxDisminuirCantidad = 1;
                            NumBoxDisminuirCantidad.option("max", inventarioSeleccionado.total_stock);
                            NumBoxDisminuirCantidad.focus();
                        }
                    }, 50);
                }
            },
            popBuscarMovimientosPorCorteOptions: {
                showTitle: true,
                width: 1200,
                height: 800,
                title: "Buscar movimientos de inventario",
                dragEnabled: false,
                closeOnOutsideClick: false,
                showCloseButton: false, // <--- Aquí se quita la X
                bindingOptions: {
                    visible: "showPopBuscar",
                },
                onInitialized: function (e) {
                    popBuscarMovimientosPorCorteInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onShowing: function (e) {
                    // Esto se ejecuta cada vez que el popup se va a mostrar
                },
                onContentReady: function (e) {
                    getCortesCaja();
                }
            },

        };

    }
})();