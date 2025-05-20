(function () {
    'use strict';

    // Definición del controlador dentro del módulo 'operaciones.operacion.controllers'
    angular
        .module('operaciones.operacion.controllers') // Asegúrate de que el módulo 'operaciones.operacion.controllers' ya esté creado
        .controller('Cotizaciones', CotizacionesController); // Se cambió 'Cliente' por 'ClienteController' para que coincida con el nombre correcto

    // Inyección de dependencias
    CotizacionesController.$inject = ['$http', '$scope', '$filter'];

    // Definición del controlador
    function CotizacionesController($http, $scope, $filter) {
		let cmbTipoPersonaOptionsInstance,btnNuevaCotizacionInstance,btnGuardarCotizacionInstance,
		btnBuscarCotizacionInstance,txtCorreoElectronicoInstance, popConsultarCotizacionInstance,
		BtnSeleccionarCotizacionInstance, BtnRegresarInstance,CmbTelefonoReceptorInstance, 
		CmbTipoContactoInstance,txtTelefonoInstance, grdConsultarInventarioInstance,
		btnNuevoRegistroInstance, btnAgregarRegistroInstance,btnEliminarRegistroInstance,
		CmbModeloInstance, CmbAnioInstance, txtAreaObservacionesInstance;

		let cotizacionSeleccionada = null;
		let ArrayTipoContacto = [];
		let ArrayTelefonos = [];
		let ArrayInventario = [];
		let ArrayModelo = [];
		let ArrayAnio = [];
		let cotizacionCreada = null;
		let clienteCreado = null;
		let el = document.getElementById('cotizaciones-data');
    	$scope.idEmpresa = el.dataset.idEmpresa;
   		$scope.idPersonal = el.dataset.idPersonal;

		var vm = this;
		$scope.modoEdicion = false; 
	

		getTipoContacto();
		getTelefonosEmpresa();
		getModelos();
	//	console.log($scope.idEmpresa);  // tendrá el valor que pasó Django
   	//	console.log($scope.idPersonal);
	//	$scope.tipo_persona_source = new DevExpress.data.DataSource({
	//		store: ArrayTipoPersona
	//	});
		// Método para limpiar los campos
		function limpiarCampos() {
			// Limpiar valores en las cajas de texto
			$scope.txtNombre = "";
			$scope.txtApellidoParterno = "";
			$scope.txtApellidoMaterno = "";
			$scope.txtTelefono = "";
			$scope.txtCorreoElectronico = "";
			$scope.txtDirecion = "";
			$scope.txtRfc = "";
			$scope.cmbTipoPersona = 1; 
			cotizacionSeleccionada = null;

			$scope.modoEdicion = false; 
			if(txtTelefonoInstance){
				txtTelefonoInstance.option("disabled",false);
			}
			if(btnGuardarCotizacionInstance){
				btnGuardarCotizacionInstance.option("text","Guardar");
				btnGuardarCotizacionInstance.option("icon", "fas fa-save");
			}
		}

		function getModelos(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/modelo/modelos_con_marca/').then(
				function(response){
					ArrayModelo.length = 0;
					for(let i = 0; i < response.data.length; i++){
						ArrayModelo.push(response.data[i]);
					}
					$scope.modelo_source.load().done(function(response){
					//	$scope.cmbTelefonoReceptor = ArrayTelefonos.length > 0 ? ArrayTelefonos[0].id : null; // selecciona el primero disponible
        				//$scope.$applyAsync(); // para asegurar que Angular detecte el cambio
					});
					$scope.isLoadPanelVisible = false;
				}, function(response){
				}
			);
		};

		function getTelefonosEmpresa(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/telefonos/activos/').then(
				function(response){
					ArrayTelefonos.length = 0;
					for(let i = 0; i < response.data.length; i++){
						ArrayTelefonos.push(response.data[i]);
					}
					$scope.telefonos_source.load().done(function(response){
						$scope.cmbTelefonoReceptor = ArrayTelefonos.length > 0 ? ArrayTelefonos[0].id : null; // selecciona el primero disponible
        				//$scope.$applyAsync(); // para asegurar que Angular detecte el cambio
					});
					$scope.isLoadPanelVisible = false;
				}, function(response){
				}
			);
		};

		function getTipoContacto(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/tipoContacto.json').then(
				function(response){
					ArrayTipoContacto.length = 0;
					ArrayTipoContacto.push({ id: 0, tipo: 'Ninguno' });
					for(let i = 0; i < response.data.length; i++){
						ArrayTipoContacto.push(response.data[i]);
					}
					$scope.tipo_contacto_source.load().done(function(response){
						$scope.cmbTipoContacto = 0; // selecciona el primero disponible
        				//$scope.$applyAsync(); // para asegurar que Angular detecte el cambio
					});
					$scope.isLoadPanelVisible = false;
				}, function(response){
				}
			);
		};

		function guardarCliente() {
			$scope.isLoadPanelVisible = true;
			var cliente_json = {
				nombre: $scope.txtNombre,
				apellido_paterno: $scope.txtApellidoParterno,
				apellido_materno: $scope.txtApellidoMaterno,
				telefono: $scope.txtTelefono,
				correo_electronico: $scope.txtCorreoElectronico,
				direccion: $scope.txtDirecion,
				tipo_persona: $scope.cmbTipoPersona,
				empresa: $scope.idEmpresa,
				estatus: true,  // o false dependiendo de la lógica de tu negocio
			};

			// Hacer el POST al backend con el JSON del cliente
			$http.post('/api/v1/clientes.json', cliente_json)
				.then(function(response) {
					$scope.isLoadPanelVisible = false;
					clienteCreado = response.data;  // La respuesta del backend que contiene el cliente guardado
					guardarCotizacion(clienteCreado.id);
				}, function(response) {
					$scope.isLoadPanelVisible = false;
					// Usar SweetAlert2 para mostrar la notificación de error
					Swal.fire({
						icon: 'error',  // Tipo de alerta (error)
						title: 'Error al guardar el cliente',
						text: 'Hubo un problema al intentar guardar la información del cliente.',
						confirmButtonText: 'Aceptar'
					});
				});
		}

		function guardarCotizacion(cliente) {
			$scope.isLoadPanelVisible = true;
			var cotizacion_json = {
				cliente: cliente,
				personal: $scope.idPersonal,
				telefono: $scope.cmbTelefonoReceptor, 
				tipo_contacto: $scope.cmbTipoContacto,
				tipo_persona: $scope.cmbTipoPersona,
				empresa: $scope.idEmpresa,
			};
			// Hacer el POST al backend con el JSON del cliente
			$http.post('/api/v1/cotizaciones.json', cotizacion_json)
				.then(function(response) {
					$scope.isLoadPanelVisible = false;
					cotizacionCreada = response.data;  // La respuesta del backend que contiene el cliente guardado
					// Usar SweetAlert2 para mostrar la notificación de éxito
					Swal.fire({
						icon: 'success',  // Tipo de alerta (success, error, warning, info)
						title: 'Mensaje del sistema',
						text: 'Cotización almacenada satisfactoriamente',
						confirmButtonText: 'Aceptar',
						timer: 3500  // Duración de la alerta (en milisegundos)
					});
					//limpiarCampos();
					// Aquí puedes agregar otras acciones si es necesario (por ejemplo, habilitar botones, limpiar campos, etc.)
				}, function(response) {
					$scope.isLoadPanelVisible = false;
					// Usar SweetAlert2 para mostrar la notificación de error
					Swal.fire({
						icon: 'error',  // Tipo de alerta (error)
						title: 'Mensaje del sistema',
						text: 'Cotización almacenada satisfactoriamente',
						confirmButtonText: 'Aceptar'
					});
				});
		}
		
		function getClientes(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/clientes.json').then(
				function(response){
					ArrayClientes.length = 0;
					for(let i = 0; i < response.data.length; i++){
						ArrayClientes.push(response.data[i]);
					}
					$scope.isLoadPanelVisible = false;
				}, function(response){
				
				}
			);
		};

			
		function llenarInformacion(){
			$scope.txtNombre = clienteSeleccionado.nombre;
			$scope.txtApellidoParterno = clienteSeleccionado.apellido_paterno;
			$scope.txtApellidoMaterno = clienteSeleccionado.apellido_materno;
			$scope.txtTelefono = clienteSeleccionado.telefono;
			$scope.txtTelefonoAdicional = clienteSeleccionado.telefono_adicional;
			$scope.txtCorreoElectronico = clienteSeleccionado.correo_electronico;
			$scope.txtDirecion = clienteSeleccionado.direccion;
			$scope.txtRfc = clienteSeleccionado.rfc;
			$scope.cmbTipoPersona = clienteSeleccionado.tipo_persona;
			popConsultarClienteInstance.hide();
			$scope.modoEdicion = true; 
			txtTelefonoInstance.option("disabled",true);
			btnGuardarCotizacionInstance.option("text","Modificar");
			btnGuardarCotizacionInstance.option("icon", "fas fa-edit");
		}
	
		$scope.inventario_source = new DevExpress.data.DataSource({
			store: ArrayInventario
		});
		
		$scope.telefonos_source = new DevExpress.data.DataSource({
			store: ArrayTelefonos
		});

		$scope.tipo_contacto_source = new DevExpress.data.DataSource({
			store: ArrayTipoContacto
		});


		$scope.modelo_source = new DevExpress.data.DataSource({
			store: ArrayModelo
		});
		
		$scope.anio_source = new DevExpress.data.DataSource({
			store: ArrayAnio
		});

		
		var currentYear = new Date().getFullYear();
		for (var year = currentYear; year >= 1980; year--) {
    		ArrayAnio.push({ id: year, anio: year });
		}

		vm.button = {
			BtnNuevaCotizacionOptions: {
				icon: 'fas fa-eraser',
				type: 'default',
				width: 135,
				text: 'Limpiar',
				disabled: false,	
				onInitialized: function(e){
					btnNuevaCotizacionInstance = e.component;
				},
				onClick: function(){
					limpiarCampos();
				}
			},
			BtnGuardarCotizacionOptions: {
				icon: 'fas fa-save',
				type: 'success',
				width: 135,
				text: 'Guardar',
				disabled: false,	
				onInitialized: function(e){
					btnGuardarCotizacionInstance = e.component;
				},
				onClick: function(){
					if($scope.modoEdicion==false){
						if (
							$scope.txtTelefono && $scope.txtTelefono.trim() !== '' &&
							$scope.txtNombre && $scope.txtNombre.trim() !== ''
						) {
							guardarCliente();
						} else {
							// Si el teléfono está vacío o no tiene valor, no hacemos nada
							Swal.fire({
								icon: 'warning',
								title: 'Mensaje del sistema',
								text: 'El Nombre y el No. de Teléfono es información requerida.',
								confirmButtonText: 'Aceptar'
							});
						}
					}
				}
			},
			BtnBuscarCotizacionOptions: {
				icon: 'fas fa-search',
				type: 'default',
				width: 135,
				text: 'Buscar',
				disabled: false,	
				onInitialized: function(e){
					btnBuscarCotizacionInstance = e.component;
				},
				onClick: function(){
					popConsultarCotizacionInstance.show();
					getClientes();
				}
			},
			
			BtnSeleccionarCotizacionOptions: {
				icon: 'fas fa-check-circle',
				type: 'success',
				width: 135,
				text: 'Seleccionar',
				disabled: false,	
				onInitialized: function(e){
					BtnSeleccionarCotizacionInstance = e.component;
				},
				onClick: function(){
					llenarInformacion();
				}
			},
			BtnRegresarOptions: {
				icon: 'fas fa-arrow-left',
				type: 'danger',
				width: 135,
				text: 'Regresar',
				disabled: false,	
				onInitialized: function(e){
					BtnRegresarInstance = e.component;
				},
				onClick: function(){
					popConsultarClienteInstance.hide();
				}
			},
			BtnNuevoRegistroOptions: {
				icon: 'fas fa-eraser',
				type: 'default',
				width: 135,
				text: 'Limpiar',
				disabled: false,	
				onInitialized: function(e){
					btnNuevoRegistroInstance = e.component;
				},
				onClick: function(){
					
				}
			},
			BtnAgregarRegistroOptions: {
				icon: 'fas fa-plus',
				type: 'success',
				width: 135,
				text: 'Agregar',
				disabled: false,	
				onInitialized: function(e){
					btnAgregarRegistroInstance = e.component;
				},
				onClick: function(){
					
				}
			},
			BtnEliminarRegistroOptions: {
				icon: 'fas fa-minus',
				type: 'danger',
				width: 135,
				text: 'Eliminar',
				disabled: false,	
				onInitialized: function(e){
					btnEliminarRegistroInstance = e.component;
				},
				onClick: function(){
			
				}
			},
		}
		vm.textArea = {
			txtAreaObservacionesOptions: {
				height: 38,
				maxLength: 200,
				placeholder: "Escribe las observaciones",
				showClearButton: true,
				autoResizeEnabled: true, // opcional
				bindingOptions: {
					value: 'txtAreaObservaciones'
				},
				onValueChanged: function(e) {
					let value = e.value || '';
					$scope.txtAreaObservaciones = value.toUpperCase();
				},
				onInitialized: function(e) {
					txtAreaObservacionesInstance = e.component;
				}
			}
		};

		vm.textBox = {
			TxtNombreOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 100,
				bindingOptions: {
					value: 'txtNombre'
				},
				onValueChanged: function(data){
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
				onValueChanged: function(data){
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
				onValueChanged: function(data){
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
				onKeyDown: function(e) {
					const key = e.event.key;
					// Permitir solo dígitos, teclas de navegación, borrar, tab
					const allowedKeys = ['Backspace', 'Tab', 'ArrowLeft', 'ArrowRight', 'Delete'];
					if (!/^\d$/.test(key) && !allowedKeys.includes(key)) {
						e.event.preventDefault();
					}
				},
				onInitialized: function(e){
					txtTelefonoInstance = e.component;
				},
				onValueChanged: function(e) {
					// Puedes agregar validación adicional aquí si deseas
				}
			},
	
			TxtCorreoElectronicoOptions: {
				disabled: false,
				showClearButton: true,
				bindingOptions: {
					value: 'txtCorreoElectronico'
				},
				mode: 'email', // usa HTML5 para validación básica
				onInitialized: function(e){
					txtCorreoElectronicoInstance = e.component;
				},
				onValueChanged: function(e) {
					// Validación simple de email (opcional)
				//	const email = e.value;
				//	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
				//	if (email && !emailRegex.test(email)) {
				//		DevExpress.ui.notify("Correo inválido", "warning", 2000);
				//	}
				}
			},
			TxtDireccionOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 255,
				bindingOptions: {
					value: 'txtDirecion'
				},
				onValueChanged: function(data){
					$scope.txtDirecion = $filter('uppercase')(data.value);
				},
			},
			TxtMarcaOptions: {
				disabled: true,
				showClearButton: true,
				maxLength: 100,
				bindingOptions: {
					value: 'txtMarca'
				},
			},
		}
		vm.lookup = {
			CmbModeloOptions: {
				dataSource: $scope.modelo_source,
				searchEnabled: true,
				placeholder:'Seleccione el modelo',
				displayExpr: 'nombre',
				valueExpr: 'id',
				value: '',
				dropDownOptions:{
					title: 'Modelo',
				},
				cancelButtonText: 'Cancelar',
				searchPlaceholder: 'Buscar modelo',
				noDataText: "Sin datos",
				bindingOptions: {
					value: 'cmbModelo',
				},
				onInitialized: function(e){
					CmbModeloInstance = e.component;
				},
				onValueChanged: function(e){
					var selectedId = e.value; // id del modelo seleccionado
					var selectedModelo = ArrayModelo.find(function(item) {
                        return item.id === selectedId;
                    });
					if (selectedModelo) {
						$scope.txtMarca = selectedModelo.marca_nombre ;
					}
				},
			},

			CmbAnioOptions: {
				dataSource: $scope.anio_source,
				searchEnabled: true,
				placeholder:'Seleccionar el año.',
				displayExpr: 'anio',
				valueExpr: 'id',
				value: '',
				dropDownOptions:{
					title: 'Año',
				},
				disabled: true,
				disabled: false,
				noDataText: 'Sin Datos',
				bindingOptions: {
					value: 'cmbAnio'
				},
				onInitialized: function(e){
					CmbAnioInstance = e.component;
				},
			},
		}
		vm.selectBox = {
			CmbTipoPersonaOptions: {
				dataSource:  [
					{ Id: 1, Tipo: 'Persona Física' },
					{ Id: 2, Tipo: 'Persona Moral' }
				],
				displayExpr: 'Tipo',
				valueExpr: 'Id',
				placeholder:'Seleccionar tipo persona',
				disabled: false,
				noDataText: 'Sin Datos',
				bindingOptions: {
					value: 'cmbTipoPersona'
				},
				onInitialized: function(e){
					cmbTipoPersonaOptionsInstance = e.component;
					$scope.cmbTipoPersona = 1; 
				},
			},
			CmbTipoContactoOptions: {
				dataSource: $scope.tipo_contacto_source,
				displayExpr: 'tipo',
				valueExpr: 'id',
				placeholder:'Seleccionar tipo de contacto',
				disabled: false,
				noDataText: 'Sin Datos',
				bindingOptions: {
					value: 'cmbTipoContacto'
				},
				onInitialized: function(e){
					CmbTipoContactoInstance = e.component;
					//$scope.cmbTipoContacto = 1; 
				},
			},
			CmbTelefonoReceptorOptions: {
				dataSource: $scope.telefonos_source,
				displayExpr: 'numero',
				valueExpr: 'id',
				placeholder:'Seleccionar el telefono.',
				disabled: false,
				noDataText: 'Sin Datos',
				bindingOptions: {
					value: 'cmbTelefonoReceptor'
				},
				onInitialized: function(e){
					CmbTelefonoReceptorInstance = e.component;
					//$scope.cmbTelefonoReceptor = 1; 
				},
			},			
		}
		
		vm.grid = {
			grdConsultarInventarioOptions: {
				dataSource: $scope.inventario_source,
				paging: {
					pageSize: 20 
				},
				pager: {
					showPageSizeSelector: true,
					allowedPageSizes: [20, 40, 60],
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
				columns: [{dataField: 'id', visible: false}, 
						{dataField: 'tipoCristal', caption: 'TipoCristal'},
						{dataField: 'existencia', caption: 'Existencia'},
						{dataField: 'NAG', caption: 'NAG'},
						{dataField: 'empresa', caption: 'Empresa'},
						{dataField: 'almacen', caption: 'Almacen'},
					],
				onInitialized: function(e){
					grdConsultarInventarioInstance = e.component;
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
				rowAlternationEnabled: true,
				columnAutoWidth: true,
				allowColumnResizing: true,
			},
		}

		vm.popups = {
			popConsultarCotizacionOptions: {
		        showTitle: true,
		       	width:1200,
		       	height:800,
		        title: "Buscar cliente",    
		        dragEnabled: false,
		        closeOnOutsideClick: false,
		        bindingOptions: {
		            visible: "showPopConsultarCotizacion",
		        },	
		        onInitialized: function(e){
					popConsultarCotizacionInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
		        }
	    	},
		};
    }
})();