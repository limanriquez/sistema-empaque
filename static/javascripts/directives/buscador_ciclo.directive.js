(function () {
	'use strict';

	angular.module('agricola.directives').directive('buscadorCiclo', BuscadorCiclo);

	function BuscadorCiclo(){
		var today = new Date();
		return {
			templateUrl: '/directives_templates/buscador_ciclo',
			scope: {
				viewmodel: "=viewModel",
				inicio: "=inicio",
				fin: "=fin",
				inprogress: '=inprogress'
			},
			link: function(scope, element, attrs){

				scope.inicio  = scope.fin = today.getFullYear(); 
				function adelantar_ciclo_vegetativo(e){
					if(scope.inicio == scope.fin)
						scope.fin++;
					else
						scope.inicio++;
				}

				function atrasar_ciclo_vegetativo(e){
					if(scope.inicio == scope.fin)
						scope.inicio--;
					else
						scope.fin--;	
				}

				scope.buttons = {
					atrasarCiclo: {
						icon: 'fa fa-chevron-circle-left',
						type: 'default',
						onClick: atrasar_ciclo_vegetativo,
						bindingOptions: {
							disabled: 'inprogress'
						}
					},
					adelantarCiclo: {
						icon: 'fa fa-chevron-circle-right',
						type: 'default',
						onClick: adelantar_ciclo_vegetativo,
						bindingOptions: {
							disabled: 'inprogress'
						}
					}
				};

				scope.textBox = {
					cicloInicio: {
						disabled: true,
						bindingOptions: {
							value: 'inicio'
						}
					},
					cicloFin: {
						disabled: true,
						bindingOptions: {
							value: 'fin'
						}
					},
				};
			}
		}
	}
})();