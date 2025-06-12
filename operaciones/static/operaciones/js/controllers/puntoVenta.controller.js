// panel.controller.js
(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers', [])
        .controller('PuntoVenta', PuntoVentaController);
    PuntoVentaController.$inject = ['$http', '$scope', '$filter'];

    function PuntoVentaController($http, $scope, $filter) {
        var gridSiniestrosInstance;
        var ArraySiniestros = [];
        var vm = this;

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
                        // Opcional: luego cargar productos para cada categoría
                        vm.categorias.forEach(function (cat,index) {
                            const color = vm.coloresCategoria[index % vm.coloresCategoria.length];
                            getProductosPorCategoria(1, cat.id, color);
                        });
                    } else {
                        vm.categorias = [];
                    }
                }, function (error) {
                    console.error("Error al cargar categorías", error);
                    vm.categorias = [];
                });
        }

        // Definición de la función para inicializar productos
        function inicializarProductos() {
            cargarCategorias()
        }

        inicializarProductos();
        function getProductosPorCategoria(empresa, categoriaId, color) {
            $scope.isLoadPanelVisible = true;

            const params = new URLSearchParams({
                empresa: empresa,
                categoria: categoriaId
            });

            const url = `/api/v1/productos/activos_por_tipo/?${params.toString()}`;

            $http.get(url).then(
                function (response) {
                    let categoria = vm.categorias.find(cat => cat.id === categoriaId);
                    if (!categoria) {
                        console.warn(`Categoría con ID ${categoriaId} no encontrada`);
                        $scope.isLoadPanelVisible = false;
                        return;
                    }
                    categoria.productos = [];
                    if (response.data && response.data.length > 0) {
                        console.log(response.data);
                        categoria.productos = response.data.map(producto => ({
                            id: producto.id,
                            nombre: producto.nombre,
                            color: color || '#e0e0e0', // usa el color asignado o por defecto
                            data: producto
                        }));
                    } else {
                        DevExpress.ui.notify("La consulta no generó información, intente con otros parámetros", "warning", 3500);
                    }

                    $scope.isLoadPanelVisible = false;
                },
                function (error) {
                    $scope.isLoadPanelVisible = false;
                    console.error(`Error al obtener productos para categoría ${categoriaId}:`, error);
                }
            );
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

        // Función para mostrar alertify con el id del predio
        vm.mostrarAlertId = function (id) {
            DevExpress.ui.notify("El ID seleccionado es: " + id, "success", 3500);
        };
        $scope.siniestros_source = new DevExpress.data.DataSource({
            store: ArraySiniestros
        });
        vm.grids = {
            gridSiniestrosOptions: {
                dataSource: $scope.siniestros_source,
                paging: {
                    pageSize: 14
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [10, 14, 20],
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
                    { visible: true, cellTemplate: '<div class="btn btn-success">Add imagen</div>', cssClass: 'sin-padding', headerCellTemplate: "<i class='fa fa-cogs' aria-hidden='true'></i>", width: '105px', allowSorting: false },
                    {
                        headerCellTemplate: "<i class='fa fa-cogs' aria-hidden='true'></i>",
                        cellTemplate: function (container, options) {
                            $("<div>")
                                .append($("<button>")
                                    .addClass("btn btn-primary")
                                    .attr("style", "width: 100px; height: 34px; color: #fff; background-color: #337ab7; border-color: #2e6da4; padding: 0 !important;") // Agregamos la propiedad padding en línea con !important
                                    .text("Ver imagenes")
                                    .dxButton({
                                        visible: options.data.Imagen,
                                        onClick: function (e) {
                                            get_imagenes_por_siniestro(options.data.IdSiniestro)
                                        }
                                    })
                                )
                                .appendTo(container);
                        },
                        cssClass: 'sin-padding',
                        width: '102px',
                    },
                    { dataField: 'IdSiniestro', caption: 'Id. siniestro', visible: true },
                    { dataField: 'IdConstancia', caption: 'Id. constancia' },
                    { dataField: 'ConsecutivoConstancia', caption: 'No. constancia' },
                    { dataField: 'Asegurado', caption: 'Asegurado' },
                    { dataField: 'Cultivo', caption: 'Cultivo' },
                    { dataField: 'TipoCultivo', caption: 'Tipo cultivo' },
                    { dataField: 'MetodoEvaluacion', caption: 'Metodo de evaluación' },
                    { dataField: 'Indemnizacion', caption: 'Indemnizacion', format: { type: 'currency', precision: 2 }, dataType: 'number' },
                    { dataField: 'Observaciones', caption: 'Observaciones' },

                ],
                onInitialized: function (e) {
                    gridSiniestrosInstance = e.component;
                },
                onCellClick: function (e) {
                    if (e.columnIndex == 0) {
                        if (e.rowIndex > -1) {
                            siniestroSeleccionado = e.data;
                            if (siniestroSeleccionado.NoImagenes < 5) {
                                vm.id = siniestroSeleccionado.IdSiniestro;
                                $scope.seleccionado = true;
                                alertify.success('Seleccione la imagen en el componente para continuar')
                            } else {
                                DevExpress.ui.notify("Este inciso ya alcanzo el limite de 5 imagenes cargadas, imposible continuar", "warning", 3500);
                            }

                        }
                    }
                },
                onRowClick: function (e) {

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
            },
        }
    }
})();
