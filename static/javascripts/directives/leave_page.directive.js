(function () {
	'use strict';

	angular.module('agricola.directives').directive('leavePage', LeavePage);

	function LeavePage(){
		return  {
			scope:{
				element_to_save: '=elementToSave'
			},
			link: function (scope, element, attrs) {
					window.onbeforeunload = function() {
						if(!scope.element_to_save ){
							return "los cambios no han sido guardados ¿Está seguro de abandonar la página?";
						}
						else{
							return;
						}
					};
				}//Fin link function
		}//Fin return's object	
	}//Fin LeavePage function

})();