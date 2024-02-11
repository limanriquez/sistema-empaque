(function(){
	angular.module('inventarios.directives')
	.directive('botonIrArriba', botonIrArriba);

	botonIrArriba.$inject = ['$location', '$anchorScroll'];

	function botonIrArriba($location, $anchorScroll){
		
		html = '<div style="position: fixed; bottom: 0; right: 0; z-index:999; opacity: 0;" ng-class="{\'visible-t\': scrolled, \'novisible-t\': !scrolled}" > \
					<button ng-click="goTop()" class="btn btn-success" scroll ><i class="fa fa-arrow-up"></i></button> \
				</div>';
			
		return {
		    template: html,
		   	link: function(scope, elem, attr){
		   		scope.goTop = function(){
					$anchorScroll();
		   		};
		   	}
		  };
	}
})();