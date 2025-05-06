(function () {
    'use strict';

    // Definición del controlador dentro del módulo 'operaciones.operacion.controllers'
    angular
        .module('operaciones.operacion.controllers') // Asegúrate de que el módulo 'operaciones.operacion.controllers' ya esté creado
        .controller('Clientes', ClienteController); // Se cambió 'Cliente' por 'ClienteController' para que coincida con el nombre correcto

    // Inyección de dependencias
    ClienteController.$inject = ['$http', '$scope', '$filter'];

    // Definición del controlador
    function ClienteController($http, $scope, $filter) {
		let cmbTipoPersonaOptionsInstance,btnNuevoClienteInstance,btnGuardarClienteInstance,
		btnBuscarClienteInstance,txtCorreoElectronicoInstance, popConsultarClienteInstance,
		BtnSeleccionarClienteInstance, BtnRegresarInstance, grdConsultarClienteInstance;
		let clienteSeleccionado = null;
		let ArrayClientes = [];
        var vm = this;
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
			$scope.txtTelefonoAdicional = "";
			$scope.txtCorreoElectronico = "";
			$scope.txtDirecion = "";
			$scope.txtRfc = "";
			$scope.cmbTipoPersona = 1; 
			clienteSeleccionado = null;
			ArrayClientes.length = 0;;
		}
		function getClientes(){
			$scope.isLoadPanelVisible = true;
			$http.get('/api/v1/clientes.json').then(
				function(response){
					ArrayClientes.length = 0;
					for(let i = 0; i < response.data.length; i++){
						console.log(response.data[i]);
						ArrayClientes.push(response.data[i]);
					}
					grdConsultarClienteInstance.refresh();
					$scope.isLoadPanelVisible = false;
				}, function(response){
				
				}
			);
		};
		$scope.clientes_source = new DevExpress.data.DataSource({
			store: ArrayClientes
		});
		vm.button = {
			BtnNuevoClienteOptions: {
				icon: 'fas fa-eraser',
				type: 'default',
				width: 135,
				text: 'Limpiar',
				disabled: false,	
				onInitialized: function(e){
					btnNuevoClienteInstance = e.component;
				},
				onClick: function(){
					limpiarCampos();
				}
			},
			BtnGuardarClienteOptions: {
				icon: 'fas fa-save',
				type: 'success',
				width: 135,
				text: 'Guardar',
				disabled: false,	
				onInitialized: function(e){
					btnGuardarClienteInstance = e.component;
				},
				onClick: function(){
					
					
				}
			},
			BtnBuscarClienteOptions: {
				icon: 'fas fa-search',
				type: 'default',
				width: 135,
				text: 'Buscar',
				disabled: false,	
				onInitialized: function(e){
					btnBuscarClienteInstance = e.component;
				},
				onClick: function(){
					popConsultarClienteInstance.show();
					getClientes();
				}
			},
			
			BtnSeleccionarClienteOptions: {
				icon: 'fas fa-check-circle',
				type: 'success',
				width: 135,
				text: 'Seleccionar',
				disabled: false,	
				onInitialized: function(e){
					BtnSeleccionarClienteInstance = e.component;
				},
				onClick: function(){
					
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
		}
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
				onValueChanged: function(e) {
					// Puedes agregar validación adicional aquí si deseas
				}
			},
			TxtTelefonoAdicionalOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 10,
				bindingOptions: {
					value: 'txtTelefonoAdicional'
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
				onValueChanged: function(e) {
					// Puedes agregar validación adicional aquí si deseas
				},
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
			TxtRfcOptions: {
				disabled: false,
				showClearButton: true,
				maxLength: 13, // o 12 si es persona moral, 13 para persona física
				bindingOptions: {
					value: 'txtRfc'
				},
				mode: 'text',
				onKeyDown: function(e) {
					const key = e.event.key;
					const allowedKeys = ['Backspace', 'Tab', 'ArrowLeft', 'ArrowRight', 'Delete'];
					const isValidChar = /^[a-zA-Z0-9]$/.test(key);
					if (!isValidChar && !allowedKeys.includes(key)) {
						e.event.preventDefault();
					}
				},
				onValueChanged: function(e) {
					const rfc = e.value ? e.value.toUpperCase() : '';
					$scope.txtRfc = rfc; // Actualiza el modelo en uppercase
				}
			}
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
		}
		
		vm.grid = {
			grdConsultarClienteOptions: {
				dataSource: $scope.clientes_source,
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
						{dataField: 'nombre', caption: 'Nombre'},
						{dataField: 'apellido_paterno', caption: 'Apellido paterno'},
						{dataField: 'apellido_materno', caption: 'Apellido materno'},
						{dataField: 'telefono', caption: 'Telefono'},
						{dataField: 'telefono_adicional', caption: 'Telefono adicional'},
						{dataField: 'direccion', caption: 'Dirección'},
						{dataField: 'rfc', caption: 'RFC'},
						{dataField: 'correo_electronico', caption: 'Email'},
					],
				onInitialized: function(e){
					grdConsultarClienteInstance = e.component;
				},
				onRowClick: function(e){
					clienteSeleccionado = e.data;
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
			popConsultarClienteOptions: {
		        showTitle: true,
		       	width:1200,
		       	height:800,
		        title: "Buscar cliente",    
		        dragEnabled: false,
		        closeOnOutsideClick: false,
		        bindingOptions: {
		            visible: "showPopConsultarcliente",
		        },	
		        onInitialized: function(e){
					popConsultarClienteInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
		        }
	    	},
		};
    }
})();