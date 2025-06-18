// panel.controller.js
(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers', [])
        .controller('PuntoVenta', PuntoVentaController);
    PuntoVentaController.$inject = ['$http', '$scope', '$filter'];

    function PuntoVentaController($http, $scope, $filter) {
        var gridSiniestrosInstance, CmbMesaInstance, BtnCrearVentaInstance;
        var ArraySiniestros = [];
        var ArrayMesa = [];
        var ArrayEmpresasVenta = [];
        var strEmpresasVenta = ""
        var vm = this;
        var tab = 0;

        $scope.ventas = [];
        $scope.ventaActiva = null;


        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;

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
                        // Opcional: luego cargar productos para cada categoría
                        //   vm.categorias.forEach(function (cat,index) {
                        //      const color = vm.coloresCategoria[index % vm.coloresCategoria.length];
                        //    getProductosPorCategoria(1, cat.id, color);
                        //  getProductosPorCategoria(2, cat.id, color);
                        // });

                        //  for (let index = 0; index < vm.categorias.length; index++) {
                        //    const cat = vm.categorias[index];
                        //  const color = vm.coloresCategoria[index % vm.coloresCategoria.length];

                        //getProductosPorCategoria(1, cat.id, color);
                        // getProductosPorCategoria(2, cat.id, color);
                        // }
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

            console.log("Se completó la carga de productos por categoría.");
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
                        DevExpress.ui.notify("La consulta no generó información, intente con otros parámetros", "warning", 3500);
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
        };

        $scope.consultarVenta = function (ventaId) {
            alertify.success("Venta seleccionada: " + ventaId);
        };
        // Función para mostrar alertify con el id del predio
        vm.mostrarAlertId = function (id) {
            DevExpress.ui.notify("El ID seleccionado es: " + id, "success", 3500);
        };

        $scope.siniestros_source = new DevExpress.data.DataSource({
            store: ArraySiniestros
        });
        $scope.mesa_source = new DevExpress.data.DataSource({
            store: ArrayMesa
        });

        vm.button = {
            BtnCrearVentaOptions: {
                icon: 'fas fa-plus',
                type: 'default',
                width: 135,
                text: 'Crear',
                disabled: false,
                onInitialized: function (e) {
                    BtnCrearVentaInstance = e.component;
                },
                onClick: function () {
                    tab = tab + 1;
                    agregarVenta(tab);
                }
            },
        }
        vm.lookup = {
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
