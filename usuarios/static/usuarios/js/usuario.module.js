(function (){
	'use strict';
	angular
		.module('inventarios.usuario', [//..............
			'dx',
			'ui.bootstrap',
			'inventarios.config',
			'inventarios.directives',//+++++++
			'inventarios.services',//--------
			'inventarios.usuario.controllers'//******
			]);//Esta instrucción crea un modulo de angular llamado control, ese es el primer parametro, el segundo parametro 
				//son directivas que se estan incluyendo, las cuales estan estre corchetes, estas directivas son modulos que se crean en las
				//lineas de abajo...

	angular
		.module('inventarios.usuario.controllers', []);//********* // aqui se crea este modulo que a su vez se agrega en las directivas del modulo
																//creado en la parte superior
	angular
		.module('inventarios.directives', []);//+++++++
	angular
		.module('inventarios.services', []);//--------
	angular
		.module('inventarios.usuario')//.............
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