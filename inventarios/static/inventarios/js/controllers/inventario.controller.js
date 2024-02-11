(function (){
	'use strict';
	angular
		.module('inventarios.inventario.controllers')
		.controller('Inventario',InventarioController);
        InventarioController.$inject = ['$http', '$scope','$filter'];
	function InventarioController($http, $scope,$filter){
        var vm = this;
		var txtObservacionesInstance, cmbCategoriaInstance,grdElementoInventarioInstance,
		btnGuardarInventarioInstance, btnConsultarInventarioInstance,
		cmbCaracteristicasInstance,btnGuardarCaracteristicaOptionsInstance,
		idInventario, cmbDepartamentoInstance,NumBoxPrecio,mensaje, validador,
		btnNuevoInventarioInstance, inventarioCreado,popConsultaInventarioInstance,
		grdInventarioInstance, inventarioSeleccionado, btnSeleccionarInventarioInstance,
		consulta,btnEliminarCaracteristicaOptionsInstance, elementoInventarioSeleccionado,
		btnImprimirInventarioInstance, btnRegresarInstance;
		var ArrayCategoria = [], ArrayInventario = [],ArrayCaracteristicas = [],
		ArrayDepartamento = [], ArrayElementosInventario = []; 
	
		$scope.elemento_inventario_source = new DevExpress.data.DataSource({
			store: ArrayElementosInventario
		});

		$scope.inventario_source = new DevExpress.data.DataSource({
			store: ArrayInventario
		});

		$scope.categoria_source = new DevExpress.data.DataSource({
			store: ArrayCategoria
		});
		$scope.caracteristicas_source = new DevExpress.data.DataSource({
			store: ArrayCaracteristicas
		});
		$scope.departamento_source = new DevExpress.data.DataSource({
			store: ArrayDepartamento
		});
		
		function getCategoria(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/categoria.json').then(
				function(response){
					ArrayCategoria.length = 0;
					for(let i = 0; i < response.data.length; i++){
						ArrayCategoria.push(response.data[i]);
					}
					$scope.categoria_source.load().done(function(response){
						$scope.cmbUpCategoria = 1;
					});
					$scope.isLoadPanelVisible = false;
				}, function(response){
					//console.log('Error al traer las categorias')
				}
			);
		};
		
		function getCatalogoElementoInventario(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/catalogoElementoInventario.json').then(
				function(response){
					ArrayCaracteristicas.length = 0;
					for(let i = 0; i < response.data.length; i++){
						ArrayCaracteristicas.push(response.data[i]);
					}
					$scope.caracteristicas_source.load().done(function(response){
					});
					$scope.isLoadPanelVisible = false;
				}, function(response){
					//console.log('Error al traer las categorias')
				}
			);
		};

		function getDepartamento(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/departamento.json').then(
				function(response){
					ArrayDepartamento.length = 0;
					for(let i = 0; i < response.data.length; i++){
						ArrayDepartamento.push(response.data[i]);
					}
					$scope.departamento_source.load().done(function(response){
						$scope.cmbDepartamento = 1;
					});
					$scope.isLoadPanelVisible = false;
				}, function(response){
					//console.log('Error al traer las categorias')
				}
			);
		};
		function cargarCaracteristicas(id){
			$scope.isLoadPanelVisible = true;
			ArrayElementosInventario.length = 0;
			let url = '/elementosInventario/'+ id
			$http.get(url).then(
				function(response){
					for(let i = 0; i < response.data.length; i++){
						ArrayElementosInventario.push(response.data[i]);
					}
					$scope.isLoadPanelVisible = false;
					grdElementoInventarioInstance.refresh();
				}, function(response){
					$scope.isLoadPanelVisible = false;
					console.log('Error al traer los elementos del inventario');
				}
			);
		};
		
		function cargarInventarios(){
			inventarioSeleccionado = 0;
			$scope.isLoadPanelVisible = true;
			ArrayInventario.length = 0;
			let url = '/inventarioExistente/'
			$http.get(url).then(
				function(response){
					for(let i = 0; i < response.data.length; i++){
						ArrayInventario.push(response.data[i]);
					}
					$scope.isLoadPanelVisible = false;
					popConsultaInventarioInstance.show();
					if(grdInventarioInstance)
						grdInventarioInstance.refresh();
				}, function(response){
					$scope.isLoadPanelVisible = false;
					console.log('Error al traer el inventario');
				}
			);
		};
		function crearElementoInventario(){
			$scope.isLoadPanelVisible = true;
			let inv;
			if(consulta==0){
				inv = inventarioCreado.Id
			}else{
				inv = inventarioSeleccionado.Id
			}
			console.log(inv);
			var elemento_inventario_json = {
				Categoria: $scope.cmbCaracteristica,
				Descripcion: $scope.txtDescripcionCaracteristica,
				Inventario: inv
			};
		
			$http.post('/api/v1/elementoInventario.json', elemento_inventario_json).then(function(response){
				$scope.isLoadPanelVisible = false;
				DevExpress.ui.notify("Caracteristica especifica agregada satisfactoriamente", "success",5000);
				$scope.txtDescripcionCaracteristica = "";
				$scope.cmbCaracteristica = 0;
				cargarCaracteristicas(inv);
			}, function(response){
				//$scope.isSavePanelVisible = false;
				console.log("Error al agregar el elemento al inventario");
			});
		}
		function modificarInventario(){
			var mes = parseInt($scope.cldFechaAdquisicion.getMonth()) + 1;
			var fecha = $scope.cldFechaAdquisicion.getFullYear() + "-" + mes + "-" + $scope.cldFechaAdquisicion.getDate();
			var inventario_json = {
				NoInventario: $scope.txtNumeroInventario,
				Descripcion: $scope.txtDescripcion,
				Observaciones: $scope.txtObservaciones,
				Ubicacion: $scope.txtUbicacion,
				FechaAdquisicion: fecha,
				Precio: $scope.numBoxPrecio,
				URL: $scope.txtURL,
				Categoria: $scope.cmbUpCategoria,
				Departamento: $scope.cmbDepartamento
			};
			$http({method: 'PATCH',data: inventario_json,
			url: "/api/v1/inventario/" + inventarioSeleccionado.Id + "/"}).then
			(function(response){
				DevExpress.ui.notify('El no de inventario '+ inventarioSeleccionado.NoInventario +' fue modificado satisfactoriamente', "success",5000);
				nuevo();
			}, 
			function(response){
			});	
		}
		
		function eliminarCaracteristicaInventario(idElemento){
			alertify.confirm('Mensaje del sistema','¿Desea eliminar la caracteristica especifica?',
				function(){
					$http({method: 'DELETE',url: '/api/v1/elementoInventario/'+ idElemento}).then(
					function(response){
						cargarCaracteristicas(inventarioSeleccionado.Id);
						DevExpress.ui.notify('Elemento eliminado satisfactoriamente.', 'success', 5000);
					}, 
					function(response){
						DevExpress.ui.notify('Se presento un error la caracteristica especifica.', 'error', 5000);
					});
				},
				function(){	
					elementoInventarioSeleccionado.id = 0;
					btnEliminarCaracteristicaOptionsInstance.option("disabled",true);
					DevExpress.ui.notify("Acción cancelada por el usuario.", "warning",5000);
				}
			);
		}

		function guardarInventario(){
			$scope.isLoadPanelVisible = true;
			var mes = parseInt($scope.cldFechaAdquisicion.getMonth()) + 1;
			var fecha = $scope.cldFechaAdquisicion.getFullYear() + "-" + mes + "-" + $scope.cldFechaAdquisicion.getDate();
			var inventario_json = {
				NoInventario: $scope.txtNumeroInventario,
				Descripcion: $scope.txtDescripcion,
				Observaciones: $scope.txtObservaciones,
				Ubicacion: $scope.txtUbicacion,
				FechaAdquisicion: fecha,
				Precio: $scope.numBoxPrecio,
				URL: $scope.txtURL,
				Categoria: $scope.cmbUpCategoria,
				Departamento: $scope.cmbDepartamento

			};
			$http.post('/api/v1/inventario.json', inventario_json).then(function(response){
				$scope.isLoadPanelVisible = false;
				inventarioCreado = response.data
				DevExpress.ui.notify("Información de inventario guardada satisfactoriamente", "success",3500);
				btnGuardarCaracteristicaOptionsInstance.option("disabled",false);
				btnGuardarInventarioInstance.option("disabled",true);
			}, function(response){
				//$scope.isSavePanelVisible = false;
				console.log("Error al guardar el inventario");
			});
		}
		function nuevo(){
			$scope.txtNumeroInventario = "";
			$scope.txtDescripcion = "";
			$scope.txtObservaciones = "";
			$scope.txtUbicacion = "";
			$scope.numBoxPrecio = "";
			$scope.txtURL = "";
			$scope.cmbDepartamento = 0;
			$scope.cldFechaAdquisicion = new Date();
			$scope.cmbUpCategoria = 0;
			inventarioSeleccionado = 0;
			mensaje = "";
			consulta = 0;
			if(btnGuardarCaracteristicaOptionsInstance)
				btnGuardarCaracteristicaOptionsInstance.option("disabled",true);
			$scope.txtDescripcionCaracteristica = "";
			$scope.cmbCaracteristica = 0;
			inventarioCreado = 0;
			if(btnGuardarInventarioInstance)
				btnGuardarInventarioInstance.option("disabled",false);
			ArrayElementosInventario.length = 0;
			if(grdElementoInventarioInstance)
				grdElementoInventarioInstance.refresh();
			if(btnEliminarCaracteristicaOptionsInstance)
				btnEliminarCaracteristicaOptionsInstance.option("disabled",true);
			if(btnImprimirInventarioInstance)	
				btnImprimirInventarioInstance.option('disabled',true);
		}
		function llenaInformacionInventario(){
			popConsultaInventarioInstance.hide();
			console.log(inventarioSeleccionado.FechaAdquisicion);
			$scope.txtNumeroInventario = inventarioSeleccionado.NoInventario;
			$scope.txtDescripcion = inventarioSeleccionado.Descripcion;
			$scope.txtObservaciones = inventarioSeleccionado.Observaciones,
			$scope.txtUbicacion = inventarioSeleccionado.Ubicacion;
			$scope.numBoxPrecio = inventarioSeleccionado.PrecioAdquisicion;
			$scope.txtURL = inventarioSeleccionado.URL;
			$scope.cmbUpCategoria = inventarioSeleccionado.IdCategoria;
			$scope.cmbDepartamento = inventarioSeleccionado.IdDepartamento;
			$scope.cldFechaAdquisicion = inventarioSeleccionado.FechaAdquisicion;
			btnGuardarCaracteristicaOptionsInstance.option("disabled",false);
			elementoInventarioSeleccionado = 0;
		}
		function validarInformacionEspecifica(){
			mensaje = "";
			if($scope.txtDescripcionCaracteristica == ""){
				mensaje = mensaje + "La descripción específica se encuentra vacia,";
			} 
			if($scope.cmbCaracteristica == 0){
				mensaje = mensaje + " Seleccione alguna caracteristica específica"
			}
			if (mensaje == ""){
				validador = true
			}else{
				validador = false
			}
			return validador
		}
		function validarInformacion(){
			mensaje = "";
			if ($scope.txtNumeroInventario == ""){
				mensaje = mensaje + "El número de inventario se encuentra vacio,"
			}
			if ($scope.txtDescripcion == ""){
				mensaje = mensaje + " La descripción se encuentra vacia,"
			}
			if ($scope.txtObservaciones == ""){
				mensaje = mensaje + " Las observaciones se encuentran vacia,"
			}
			if ($scope.txtUbicacion == ""){
				mensaje = mensaje + " La ubicacion se encuentra vacia,"
			}
			if($scope.cmbUpCategoria == 0){
				mensaje = mensaje + " Seleccione alguna categoria,"
			}
			if($scope.cmbDepartamento == 0){
				mensaje = mensaje + " Seleccione algun departamento,"
			}
			//if(!$scope.cldFechaAdquisicion){
			//	mensaje = mensaje + " Seleccione una fecha valida";
			//}

			if (mensaje == ""){
				validador = true
			}else{
				validador = false
			}
			return validador
		}
		function imprimir(ruta){
			window.open(ruta, "_blank", '');
		}
		nuevo();
		getCategoria();
		getCatalogoElementoInventario();
		getDepartamento();

		$scope.format = '$ #.##';
		vm.numberBox = {
			NumBoxPrecioOptions : {
				bindingOptions: {
					format: 'format',
					value: 'numBoxPrecio'
				},
				showClearButton: true,
				showSpinButtons: true,
				buttons: [{
					name: 'currency',
					location: 'after',
					options: {
						text: '$',
						stylingMode: 'text',
						width: 32,
						elementAttr: {
							class: 'currency'
						},
						onInitialized: function(e){
							NumBoxPrecio = e.component;
						},
					}
				}, 'clear', 'spins']
			}
		}
	
		vm.textBox = {
			TxtNumeroInventarioOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 300,
				bindingOptions: {
					value: 'txtNumeroInventario'
				},
				onValueChanged: function(data){
					$scope.txtNumeroInventario = $filter('uppercase')(data.value);
				},
			},
			TxtDescripcionOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 300,
				bindingOptions: {
					value: 'txtDescripcion'
				},
				onValueChanged: function(data){
					$scope.txtDescripcion = $filter('uppercase')(data.value);
				},
			},
			TxtUbicacionOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 300,
				bindingOptions: {
					value: 'txtUbicacion'
				},
				onValueChanged: function(data){
					$scope.txtUbicacion = $filter('uppercase')(data.value);
				},
			},
			TxtDescripcionCaracteristicaOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 300,
				bindingOptions: {
					value: 'txtDescripcionCaracteristica'
				},
				onValueChanged: function(data){
					$scope.txtDescripcionCaracteristica = $filter('uppercase')(data.value);
				},
			},
			TxtURLOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 300,
				bindingOptions: {
					value: 'txtURL'
				},
				onValueChanged: function(data){
					$scope.txtURL = $filter('uppercase')(data.value);
				},
			}
		}
		vm.textArea = {
			AtxtObservacionesOptions: {
				placeholder: 'Escriba sus observaciones.',
				showClearButton: true,
				maxLength: 300,
				bindingOptions: {
					value: 'txtObservaciones'
				},
				onValueChanged: function(data){
					$scope.txtObservaciones = $filter('uppercase')(data.value);
				},
				onInitialized: function(e){
					txtObservacionesInstance = e.component;
				},
			},
		}
		vm.selectBox = {
			CmbCaracteristicasOptions: {
				dataSource: $scope.caracteristicas_source,
				displayExpr: 'Descripcion',
				valueExpr: 'Id',
				placeholder:'Seleccionar caracteristica',
				disabled: false,
				noDataText: 'Sin Datos',
				bindingOptions: {
					value: 'cmbCaracteristica'
				},
				onInitialized: function(e){
					cmbCaracteristicasInstance = e.component;
				},
			},
			CmbDepartamentoOptions: {
				dataSource: $scope.departamento_source,
				displayExpr: 'Descripcion',
				valueExpr: 'Id',
				placeholder:'Seleccionar departamento',
				disabled: false,
				noDataText: 'Sin Datos',
				bindingOptions: {
					value: 'cmbDepartamento'
				},
				onInitialized: function(e){
					cmbDepartamentoInstance = e.component;
				},
			},
		}
		vm.lookup = {
			CmbCategoriaOptions: {
				dataSource: $scope.categoria_source,
				searchEnabled: true,
				placeholder:'Seleccione la categoria',
				displayExpr: 'Categoria',
				valueExpr: 'Id',
				value: '',
				title: 'Categoria',
				cancelButtonText: 'Cancelar',
				searchPlaceholder: 'Buscar categoria',
				noDataText: "Sin datos",
				bindingOptions: {
					//text: 'cmbUpTextCategoria',
					value: 'cmbUpCategoria',
				},
				onInitialized: function(e){
					cmbCategoriaInstance = e.component;
				},
				onValueChanged: function(){
				
				},
			},
		}
		vm.button = {
			BtnGuardarInventarioOptions: {
				icon: 'fa fa-save',
				type: 'default',
				width: 135,
				text: 'Guardar',
				disabled: false,	
				onInitialized: function(e){
					btnGuardarInventarioInstance = e.component;
				},
				onClick: function(){
					if (consulta == 0){
						if (validarInformacion()){
							guardarInventario();
						}else{
							DevExpress.ui.notify(mensaje, "warning",5000);
						}
					}
					if(consulta == 1){
						if (validarInformacion()){
							modificarInventario();
						}else{
							DevExpress.ui.notify(mensaje, "warning",5000);
						}
					}
					
					
				}
			},
			BtnGuardarCaracteristicaOptions: {
				icon: 'fa fa-plus-circle',
				type: 'default',
				width: 100,
				//text: 'Caracteristica',
				disabled: true,	
				onInitialized: function(e){
					btnGuardarCaracteristicaOptionsInstance = e.component;
				},
				onClick: function(){
					if (validarInformacionEspecifica()){
						crearElementoInventario();
					}else{
						DevExpress.ui.notify(mensaje, "warning",5000);
					}
				}
			},
			BtnEliminarCaracteristicaOptions: {
				icon: 'fa fa-minus-circle',
				type: 'danger',
				width: 100,
				//text: 'Caracteristica',
				disabled: true,	
				onInitialized: function(e){
					btnEliminarCaracteristicaOptionsInstance = e.component;
				},
				onClick: function(){
					if (elementoInventarioSeleccionado.Id > 0){
						eliminarCaracteristicaInventario(elementoInventarioSeleccionado.Id);
					}
					
				}
			},
			BtnConsultarInventarioOptions: {
				icon: 'fa fa-search',
				type: 'success',
				width: 135,
				text: 'Consultar',
				disabled: false,	
				onInitialized: function(e){
					btnConsultarInventarioInstance = e.component;
				},
				onClick: function(){
					nuevo();
					cargarInventarios();
				}
			},
			BtnNuevoInventarioOptions: {
				icon: 'fa fa-newspaper-o',
				type: 'default',
				width: 135,
				text: 'Nuevo',
				disabled: false,	
				onInitialized: function(e){
					btnNuevoInventarioInstance = e.component;
				},
				onClick: function(){
					nuevo();
				}
			},
			BtnSeleccionarInventarioOptions: {
				icon: 'fa fa-check-circle',
				type: 'success',
				width: 135,
				text: 'Seleccionar',
				disabled: false,	
				onInitialized: function(e){
					btnSeleccionarInventarioInstance = e.component;
				},
				onClick: function(){
					consulta = 1;
					ArrayInventario.length = 0;
					if(grdInventarioInstance)
						grdInventarioInstance.refresh();
					llenaInformacionInventario();
					cargarCaracteristicas(inventarioSeleccionado.Id);
					btnImprimirInventarioInstance.option('disabled',false);
				}
			},
			BtnRegresarOptions: {
				icon: 'fa fa-arrow-circle-left',
				type: 'danger',
				width: 135,
				text: 'Regresar',
				disabled: false,	
				onInitialized: function(e){
					btnRegresarInstance = e.component;
				},
				onClick: function(){
					popConsultaInventarioInstance.hide();
				}
			},
			BtnImprimirInventarioOptions: {
				icon: 'fa fa-print',
				type: 'default',
				//stylingMode: 'outlined',
				width: 135,
				text: 'Imprimir',
				disabled: true,	
				onInitialized: function(e){
					btnImprimirInventarioInstance = e.component;
				},
				onClick: function(){
					imprimir("../export/" + inventarioSeleccionado.Id);
				}
			},
			
		}
		vm.calendar = {
			CldFechaAdquisicionOptions: {
                type: 'date',
                displayFormat: 'dd/MM/yyyy',
                bindingOptions: {
					value: 'cldFechaAdquisicion',
				//	min:'minInicioSiembra',
				//	max:'maxFinSiembra',
                }
            },
		}
		vm.grid = {
			GrdElementoInventarioOptions: {
				dataSource: $scope.elemento_inventario_source,
				paging: {
					pageSize: 8 
				},
				pager: {
					showPageSizeSelector: true,
					allowedPageSizes: [2, 4, 8],
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
				columns: [{dataField: 'Id', visible: false}, {dataField: 'Caracteristica', caption: 'Caracteristica'},{dataField: 'Descripcion', caption: 'Descripcion'}],
				onInitialized: function(e){
					grdElementoInventarioInstance = e.component;
				},
				onRowClick: function(e){
					if(btnEliminarCaracteristicaOptionsInstance)
						btnEliminarCaracteristicaOptionsInstance.option("disabled",false);
					elementoInventarioSeleccionado = e.data;
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
			GrdConsultaInventarioOptions: {
				dataSource: $scope.inventario_source,
				paging: {
					pageSize: 8 
				},
				pager: {
					showPageSizeSelector: true,
					allowedPageSizes: [2, 4, 8],
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
				columns: [{dataField: 'Id', visible: false}, {dataField: 'NoInventario', caption: 'No de Inventario'},{dataField: 'Descripcion', caption: 'Descripcion'},{dataField: 'Observaciones', caption: 'Observaciones'}],
				onInitialized: function(e){
					grdInventarioInstance = e.component;
				},
				onRowClick: function(e){
					inventarioSeleccionado = e.data;
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
		vm.loadPanels = {
			basicOptions: {
				closeOnOutsideClick: false,
				message:'Cargando....',
		        bindingOptions: {
		            visible: 'isLoadPanelVisible'
		        }
			}
		},
		vm.popups = {
			popConsultaInvenarioOptions: {
		        showTitle: true,
		       	width:900,
		       	height:600,
		        title: "Buscar inventario",    
		        dragEnabled: false,
		        closeOnOutsideClick: false,
		        bindingOptions: {
		            visible: "showPopConsultaInvenario",
		        },	
		        onInitialized: function(e){
					popConsultaInventarioInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
		        }
	    	},
		};
	}
})();