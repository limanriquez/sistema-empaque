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
		}
		
		nuevo();

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
				showClearButton: true,
				maxLength: 300,
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