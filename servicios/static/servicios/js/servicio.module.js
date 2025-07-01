(function () {
    'use strict';

    angular
        .module('servicios.servicio', [
            'dx',
            'ui.bootstrap',
            'inventarios.config',
            'inventarios.directives',
            'inventarios.services',
            'servicios.servicio.controllers'
        ]);

    angular.module('servicios.servicio.controllers', []);
    angular.module('inventarios.directives', []);
    angular.module('inventarios.services', []);

    angular
        .module('servicios.servicio') // ✅ Módulo correcto
        .run(run);

    run.$inject = ['$http'];

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }
})();