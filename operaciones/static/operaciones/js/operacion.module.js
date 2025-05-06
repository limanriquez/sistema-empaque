(function () {
    'use strict';

    angular
        .module('operaciones.operacion', [
            'dx',
            'ui.bootstrap',
            'inventarios.config',
            'inventarios.directives',
            'inventarios.services',
            'operaciones.operacion.controllers'
        ]);

    angular.module('operaciones.operacion.controllers', []);
    angular.module('inventarios.directives', []);
    angular.module('inventarios.services', []);

    angular
        .module('operaciones.operacion') // ✅ Módulo correcto
        .run(run);

    run.$inject = ['$http'];

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }
})();