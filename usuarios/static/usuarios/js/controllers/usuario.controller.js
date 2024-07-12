(function (){
	'use strict';
	angular
		.module('inventarios.usuario.controllers')
		.controller('Usuario',UsuarioController);
        UsuarioController.$inject = ['$http', '$scope','$filter'];
	function UsuarioController($http, $scope,$filter){
        var vm = this;
		var BtnRenovarInstance;
		

		function nuevo(){
			$scope.TxtTokenCondusef = "";
			$scope.TxtNombreSuperUsuario = "";
			$scope.TxtContrasenia = "";
			$scope.TxtConfirmContrasenia = "";
			$scope.TxtTokenSuperUsuario = "";
		
			if(BtnRenovarInstance)
				BtnRenovarInstance.option("disabled",false);
			getSuperUsuarioPorEmpresa();
		}
		
		nuevo();
		function getSuperUsuarioPorEmpresa(){
			$scope.isLoadPanelVisible = true;
			$http.get('/getSuperUsuarioPorEmpresa/').then(
				function(response){
					if(response.data.length>0){
						console.log(response.data[0]);
						$scope.TxtTokenCondusef = response.data[0].TokenCondusef;
						$scope.TxtNombreSuperUsuario = response.data[0].Nombre;
						$scope.TxtContrasenia = response.data[0].Password;
						$scope.TxtConfirmContrasenia = response.data[0].Password;
						$scope.TxtTokenSuperUsuario = response.data[0].Token;
		
					}
					
					$scope.isLoadPanelVisible = false;
				}, function(response){
					//console.log('Error al traer las categorias')
				}
			);
		};
		vm.textBox = {
			TxtTokenCondusefOptions: {
				disabled: true,
				showClearButton: true,
				maxLength: 30,
				bindingOptions: {
					value: 'TxtTokenCondusef'
				},
				onValueChanged: function(data){
					$scope.TxtTokenCondusef = $filter('uppercase')(data.value);
				},
			},
			TxtNombreSuperUsuarioOptions: {
				disabled: true,
				showClearButton: true,
				maxLength: 30,
				bindingOptions: {
					value: 'TxtNombreSuperUsuario'
				},
				onValueChanged: function(data){
					$scope.TxtNombreSuperUsuario = $filter('uppercase')(data.value);
				},
			},
			
			TxtContraseniaOptions: {
				disabled: true,
				showClearButton: true,
				maxLength: 10,
				bindingOptions: {
					value: 'TxtContrasenia'
				},
				onValueChanged: function(data){
					$scope.TxtContrasenia = $filter('uppercase')(data.value);
				},
			},
			TxtConfirmContraseniaOptions: {
				disabled: true,
				showClearButton: true,
				maxLength: 10,
				bindingOptions: {
					value: 'TxtConfirmContrasenia'
				},
				onValueChanged: function(data){
					$scope.TxtConfirmContrasenia = $filter('uppercase')(data.value);
				},
			},
			TxtTokenSuperUsuarioOptions: {
				disabled: false,
				showClearButton: false,
				maxLength: 1000,
				bindingOptions: {
					value: 'TxtTokenSuperUsuario'
				},
				onValueChanged: function(data){
					$scope.TxtTokenSuperUsuario = $filter('uppercase')(data.value);
				},
			}
			
		}
	
		vm.button = {
			BtnRenovarOptions: {
				icon: 'fa fa-save',
				type: 'default',
				width: 180,
				text: 'Renovar token',
				disabled: false,	
				onInitialized: function(e){
					BtnRenovarInstance = e.component;
				},
				onClick: function(){
					
					
				}
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
		};
		
	}
})();