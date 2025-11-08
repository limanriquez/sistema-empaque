(function () {
    'use strict';
    angular
        .module('inventarios.inventario.controllers')
        .controller('MovimientoInventario', MovimientoInventarioController);
    MovimientoInventarioController.$inject = ['$http', '$scope', '$filter'];
    function MovimientoInventarioController($http, $scope, $filter) {
        let vm = this;
        let grdInventariosInstance, BtnIngresarInstance, BtnSalidaInstance;
        let inventarioSeleccionado = null;
        let ArrayInventarios = [];
        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;

        console.log(vm.empresaId);

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
                        console.log(response.data[i]);
                        ArrayInventarios.push(response.data[i]);
                    }
                    grdInventariosInstance.refresh();
                    $scope.isLoadPanelVisible = false;
                }, function (response) {
                    hideLoading();
                }
            );
        };
        function incrementarInventario() {
            Swal.fire({
                title: 'Incrementar Inventario',
                text: 'Ingresa la cantidad a incrementar:',
                input: 'number',
                inputAttributes: {
                    min: 1,
                    step: 1,
                    inputmode: 'numeric',
                    pattern: '\\d*'
                },
                showCancelButton: true,
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancelar',
                reverseButtons: true,
                allowOutsideClick: false,  // NO cerrar al hacer clic fuera
                allowEscapeKey: false,     // NO cerrar con ESC
                inputValidator: (value) => {
                    if (!value) {
                        return 'Debes ingresar un valor';
                    }
                    if (!Number.isInteger(Number(value)) || Number(value) <= 0) {
                        return 'Ingresa un número entero válido mayor que 0';
                    }
                },
                didOpen: () => {
                    const input = Swal.getInput();
                    input.style.textAlign = "center";
                    input.style.fontSize = "1.2em";
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    //const cantidad = parseInt(result.value);
                    //Swal.fire({
                     //   icon: 'success',
                      //  title: '¡Correcto!',
                       // text: `Se incrementó el inventario en ${cantidad}`
                    //});
                }
            });
        }
      
      //  function incrementarStock(){
        //    incrementar_Stock
       // }

        $scope.inventarios_source = new DevExpress.data.DataSource({
            store: ArrayInventarios
        });
        vm.button = {
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
                        incrementarInventario();
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
                    console.log(inventarioSeleccionado);

                }
            },
        }
        vm.grid = {
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
                groupPanel: {
                    visible: true,
                    emptyPanelText: "Arrastra una columna aquí para agrupar",
                    allowColumnDragging: true
                },
                allowColumnReordering: true,
                grouping: {
                    autoExpandAll: false
                },
                columns: [
                    { dataField: 'producto_id', caption: 'ID Producto', visible: false },
                    { dataField: 'stock_item_id', caption: 'ID Stock', visible: false },
                    { dataField: 'nombre_producto', caption: 'Nombre Producto' },
                    { dataField: 'tipo_producto', caption: 'Tipo Producto' },
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


        }



    }
})();