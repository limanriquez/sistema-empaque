// panel.controller.js
(function () {
  'use strict';

  angular
    .module('operaciones.operacion.controllers', [])
    .controller('PuntoVenta', PuntoVentaController);
    PuntoVentaController.$inject = ['$http', '$scope','$filter'];

  function PuntoVentaController($http, $scope,$filter) {
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

    vm.categorias = [
      { id: 1, nombre: 'Municipio 1', predios: [] },
      { id: 2, nombre: 'Municipio 2', predios: [] },
      { id: 3, nombre: 'Municipio 3', predios: [] },
      { id: 4, nombre: 'Municipio 4', predios: [] },
      { id: 5, nombre: 'Municipio 5', predios: [] }
    ];

    const cultivos = ['Maíz', 'Trigo', 'Frijol', 'Café', 'Tomate'];

    function randomInt(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // Generación de predios con color asignado por categoría
    vm.categorias.forEach(function (cat, index) {
      const cantidad = randomInt(10, 60);
      const color = vm.coloresCategoria[index % vm.coloresCategoria.length];

      for (let i = 1; i <= cantidad; i++) {
        const cultivoAleatorio = cultivos[randomInt(0, cultivos.length - 1)];
        cat.predios.push({
          id: `${cat.id}-${i}`,
          cultivo: cultivoAleatorio,
          nombre: `Predio ${i}`,
          color: color // ✅ Se asigna color aquí
        });
      }
    });

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
        cat.predios.forEach(function (predio) {
          if (
            (predio.nombre && predio.nombre.toLowerCase().includes(filtro)) ||
            (predio.cultivo && predio.cultivo.toLowerCase().includes(filtro)) ||
            (predio.id && predio.id.toLowerCase().includes(filtro))
          ) {
            resultados.push(predio);
          }
        });
      });
      return resultados;
    };

    // Función para mostrar alertify con el id del predio
    vm.mostrarAlertId = function(id) {
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
				selection:{
					mode:'single'
				},
				filterRow :{
        			visible: true,
        			applyFilter: "auto"
    			},
				showBorders: true,

				columns: [
                        {visible: true, cellTemplate: '<div class="btn btn-success">Add imagen</div>', cssClass:'sin-padding',headerCellTemplate: "<i class='fa fa-cogs' aria-hidden='true'></i>",width:'105px',allowSorting: false},
                        {
                            headerCellTemplate: "<i class='fa fa-cogs' aria-hidden='true'></i>",
                            cellTemplate: function(container, options){
                                $("<div>")
                                    .append($("<button>")
                                        .addClass("btn btn-primary")
                                        .attr("style", "width: 100px; height: 34px; color: #fff; background-color: #337ab7; border-color: #2e6da4; padding: 0 !important;") // Agregamos la propiedad padding en línea con !important
                                        .text("Ver imagenes")
                                        .dxButton({
                                            visible: options.data.Imagen,
                                            onClick: function(e) {
                                                get_imagenes_por_siniestro(options.data.IdSiniestro)
                                            }
                                        })
                                    )
                                    .appendTo(container);
                            },
                            cssClass:'sin-padding',
                            width:'102px',
                        },
                        {dataField: 'IdSiniestro', caption: 'Id. siniestro', visible: true}, 
						{dataField: 'IdConstancia', caption: 'Id. constancia'} , 
						{dataField: 'ConsecutivoConstancia', caption: 'No. constancia'}, 
                        {dataField: 'Asegurado', caption: 'Asegurado'}, 
						{dataField: 'Cultivo', caption: 'Cultivo'},
						{dataField: 'TipoCultivo', caption: 'Tipo cultivo'},
						{dataField: 'MetodoEvaluacion', caption: 'Metodo de evaluación'},
						{dataField: 'Indemnizacion', caption: 'Indemnizacion', format: {type: 'currency', precision: 2}, dataType: 'number'}, 
                        {dataField: 'Observaciones', caption: 'Observaciones'},  
                     
						],
				onInitialized: function(e){
					gridSiniestrosInstance = e.component;
				},
                onCellClick: function(e){
					if(e.columnIndex == 0){
						if(e.rowIndex >-1){
							siniestroSeleccionado = e.data;
							if(siniestroSeleccionado.NoImagenes < 5){
								vm.id  = siniestroSeleccionado.IdSiniestro;
								$scope.seleccionado = true;
								alertify.success('Seleccione la imagen en el componente para continuar')
							}else{
								DevExpress.ui.notify("Este inciso ya alcanzo el limite de 5 imagenes cargadas, imposible continuar", "warning",3500);
							}
                           
						}
					}
				}, 
				onRowClick: function(e){
            
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
