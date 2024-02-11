(function(){
	angular.module('agricola.directives')
	.directive("scroll", scroll);

	scroll.$inject = ['$window', '$rootScope'];

	function scroll($window, $rootScope) {
	    return function(scope, element, attrs) {
	        angular.element($window).bind("scroll", function() {
	             if (this.pageYOffset >= 10) {
	                 $rootScope.scrolled = true;
	             } else {
					$rootScope.scrolled = false;
	             }
	             $rootScope.$apply();
	        });
	    };
   	}

})();