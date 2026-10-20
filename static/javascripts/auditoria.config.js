(function (){
	'use strict';

	angular
		.module('inventarios.config', [])
		.config(config);

	config.$inject = ['$locationProvider', '$interpolateProvider'];

	/**
	* @name config
	* @desc Enable HTML5 routing
	*/
	function config( $locationProvider, $interpolateProvider){
		$locationProvider.html5Mode({
			  enabled: false,
			  requireBase: false
		});
		$locationProvider.hashPrefix('');
		$interpolateProvider.startSymbol('{[{');
		$interpolateProvider.endSymbol('}]}');
	}
})();