(function () {
	'use strict';

	angular.module('agricola.directives').directive('vaciarCombo', VaciarCombo);

	function VaciarCombo(){
		return {
			template: "<div dx-button='button_conf'></div>",
			scope: {
				var_combo: '=varCombo'
			},
			link: function(scope, elem, attrs){
				scope.button_conf = {
					icon: 'fa fa-close',
					onClick: function(){
						scope.var_combo = -1;		
					}
				}
			}
		}
	}

})();