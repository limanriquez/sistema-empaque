
(function () {
    'use strict';

    angular
        .module('nominas.nomina.controllers')
        .controller('Nomina', NominaController);
    NominaController.$inject = ['$http', '$q'];
    function NominaController($http, $q) {
        var vm = this;

        // --------------------------------------------------
        // VARIABLES
        // --------------------------------------------------

        vm.fechaInicio = null;
        vm.fechaFin = null;

        // --------------------------------------------------
        // INICIALIZACIÓN
        // --------------------------------------------------

        vm.inicializar = function () {

            vm.fechaInicio = null;
            vm.fechaFin = null;

        };
        // --------------------------------------------------
        // INICIAR NÓMINA
        // --------------------------------------------------

        // --------------------------------------------------
        // INICIAR NÓMINA
        // --------------------------------------------------

        function iniciarNomina() {

            // Validar fechas
            if (!vm.fechaInicio || !vm.fechaFin) {

                Swal.fire({
                    icon: 'warning',
                    title: 'Fechas requeridas',
                    text: 'Debe seleccionar la fecha de inicio y fin de la nómina.'
                });

                return;
            }

            // Validar rango de fechas
            if (vm.fechaInicio > vm.fechaFin) {

                Swal.fire({
                    icon: 'warning',
                    title: 'Rango de fechas inválido',
                    text: 'La fecha de inicio no puede ser posterior a la fecha de fin.'
                });

                return;
            }

            vm.isLoadPanelVisible = true;

            $http.post('/iniciar_nomina/', {
                fecha_inicio: vm.fechaInicio,
                fecha_fin: vm.fechaFin
            }).then(function (response) {

                Swal.fire({
                    icon: 'success',
                    title: 'Validación correcta',
                    text: response.data.mensaje
                });

            }).catch(function (error) {

                var mensaje = 'Error al validar las fechas.';

                if (error.data && error.data.mensaje) {
                    mensaje = error.data.mensaje;
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: mensaje
                });

                console.error('Error al iniciar nómina:', error);

            }).finally(function () {

                vm.isLoadPanelVisible = false;

            });

        }
        // --------------------------------------------------
        // BOTONES
        // --------------------------------------------------

        vm.button = {

            BtnIniciarNominaOptions: {

                icon: 'fas fa-play',
                type: 'success',
                width: 160,
                text: 'Iniciar nómina',
                disabled: false,

                onClick: function () {
                    iniciarNomina();
                    // Pendiente: implementar inicio de nómina.

                }

            }

        };

        // --------------------------------------------------
        // DATE BOXES
        // --------------------------------------------------

        vm.dateBox = {

            DteFechaInicioOptions: {

                type: 'date',
                displayFormat: 'dd/MM/yyyy',
                dateSerializationFormat: 'yyyy-MM-dd',
                placeholder: 'Fecha inicial',
                showClearButton: true,
                useMaskBehavior: true,

                bindingOptions: {
                    value: 'vm.fechaInicio'
                }

            },

            DteFechaFinOptions: {

                type: 'date',
                displayFormat: 'dd/MM/yyyy',
                dateSerializationFormat: 'yyyy-MM-dd',
                placeholder: 'Fecha final',
                showClearButton: true,
                useMaskBehavior: true,

                bindingOptions: {
                    value: 'vm.fechaFin'
                }

            }

        };

    }

})();
