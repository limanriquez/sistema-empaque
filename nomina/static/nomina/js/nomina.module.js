(function () {
    'use strict';

    angular
        .module('nominas.nomina', [
            'dx',
            'ui.bootstrap',
            'inventarios.config',
            'inventarios.directives',
            'inventarios.services',
            'nominas.nomina.controllers'
        ]);

    angular.module('nominas.nomina.controllers', []);
    angular.module('inventarios.directives', []);
    angular.module('inventarios.services', []);

    angular
        .module('nominas.nomina') // ✅ Módulo correcto
        .run(run);

    run.$inject = ['$http'];

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }
})();