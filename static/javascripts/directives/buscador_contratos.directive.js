(function () {
	'use strict';

	angular.module('agricola.directives').directive('buscadorContratos', BuscadorContratos);

	BuscadorContratos.$inject = ['$http'];

	function BuscadorContratos($http){
		return {
			template: ' <div dx-select-box="selectBox.contratosReaseguro"></div>  ',
			scope: {
				viewmodel: '=viewModel',
				ciclo_inicio: '=cicloInicio',
				ciclo_fin: '=cicloFin',
				inprogress: '=inprogress',
				extra_logic: '=extraLogic',
				cmb_contratos: '=cmbContratos',
				value_changed_handler: '=valueChangedHandler'
			},
			link: function(scope, elem, attrs){
				let cargado_primera_vez = false;

				var sourceCmbContratos, arrayCmbContratos, instanceCmbContratos;

				arrayCmbContratos = [];
				sourceCmbContratos = new DevExpress.data.DataSource({ store: arrayCmbContratos });

				scope.$watch('ciclo_inicio', function(new_val, old_val){
					if(new_val && cargado_primera_vez && new_val != old_val){
						get_contratos();
					}
				});
				scope.$watch('ciclo_fin', function( new_val, old_val){
					if(new_val && cargado_primera_vez && new_val != old_val){
						get_contratos();
					}
				});


				function get_contratos(){
					if(scope.ciclo_inicio && scope.ciclo_fin){
						scope.viewmodel.inprogress = true;
						$http.get('/api/v1/contratos_reaseguro/por_ciclo?ciclo_inicio=' + scope.ciclo_inicio + '&ciclo_fin=' + scope.ciclo_fin).then(
							function(response){
								arrayCmbContratos.length = 0;
								for(let i = 0; i < response.data.length; i++)
									arrayCmbContratos.push(response.data[i]);
								
								sourceCmbContratos.load().done(function(results) {
									if(results.length > 0){
										scope.cmb_contratos = results[0].pk;
									}
									else{
										scope.cmb_contratos = -1;
									}
									scope.viewmodel.inprogress = false;
								});
								
							}, 
							function(response){
								DevExpress.ui.notify('Ocurrió un error al cargar los contratos', 'error');
							}
						);
					}else{
						scope.viewmodel.inprogress = false;
					}
				}

				function cargar_contratos_primera_vez(){
					if(scope.ciclo_inicio && scope.ciclo_fin){
						cargado_primera_vez = true;
						get_contratos();
					}else{
						setTimeout(function(){
							cargar_contratos_primera_vez();
						}, 25);	
					}
				}
				cargar_contratos_primera_vez();

				scope.selectBox = {
					contratosReaseguro: {
						dataSource: sourceCmbContratos,
						displayExpr: 'fields.NumeroContratoReaseguro',
						valueExpr: 'pk',
						placeholder: 'Seleccione un contrato de reaseguro',
						noDataText: 'Sin contratos para el cíclo',
						bindingOptions: {
							value: 'cmb_contratos',
							disabled: 'inprogress'
						},
						onInitialized: function(e) { instanceCmbContratos = e.component; },
						onValueChanged: function (argument) {
							/*Se aplica el timeout para poder llamar a $apply y se propague el
							 *cambio de valor de la variable bindeada a los controladores.*/
							setTimeout(function(){
								scope.$apply();
								if(scope.value_changed_handler && typeof(scope.value_changed_handler) == 'function'){
									scope.viewmodel.inprogress = true;
									scope.value_changed_handler();
								}
							},1);
						}
					}
				}

			}
		}
	}
})();