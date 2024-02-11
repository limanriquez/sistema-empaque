(function (){
	'use strict';

	angular
		.module('inventarios.authentication', [
			'dx',
			'inventarios.config',
			'inventarios.authentication.controllers',
			'inventarios.profiles.services'
			]);

	angular
		.module('inventarios.config', []);

	angular
		.module('inventarios.authentication.controllers',[]);

	angular
		.module('inventarios.profiles.services',[]);

	angular
		.module('inventarios.authentication')
		.run(run);

	run.$inject = ['$http'];

	/**
	* @name
	* @desc Update xsrf $http headers to align with Django's defaults
	*/
	function run($http){
		$http.defaults.xsrfHeaderName = 'X-CSRFToken';
		$http.defaults.xsrfCookieName = 'csrftoken';
	}

})();