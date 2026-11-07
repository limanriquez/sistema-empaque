
(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers')
        .controller('CapturaCaja', CapturaCajaController);

    CapturaCajaController.$inject = ['$scope'];

    function CapturaCajaController($scope) {

        var vm = this;

        // --------------------------------------------------
        // VARIABLES DE LA OPERACIÓN
        // --------------------------------------------------

        vm.operacionDiariaId = null;
        vm.loteEmpaqueId = null;
        vm.variedadId = null;

        // --------------------------------------------------
        // INICIALIZACIÓN
        // Recibe los tres parámetros enviados desde ng-init
        // --------------------------------------------------

        vm.inicializar = function (operacionId, loteId, variedadId) {

            vm.operacionDiariaId = operacionId;
            vm.loteEmpaqueId = loteId;
            vm.variedadId = variedadId;

            $scope.txtCodigoCaptura = '';

            $scope.txtEstacion = '';
            $scope.txtEmpleado = '';

            $scope.txtClaveProducto = '';
            $scope.txtProductoEmpaque = '';
            $scope.txtPrecioCaja = '';

            $scope.txtCalidad = '';
            $scope.txtTamano = '';
            $scope.txtVariedad = '';

            $scope.cmbTarima = null;

        };

        // --------------------------------------------------
        // LOAD PANEL
        // --------------------------------------------------

        vm.loadPanels = {
            basicOptions: {
                shading: true,
                showIndicator: true,
                showPane: true,
                visible: false,
                message: 'Procesando...'
            }
        };

        // --------------------------------------------------
        // BOTONES
        // --------------------------------------------------

        vm.button = {

            BtnLimpiarOptions: {
                icon: 'fas fa-eraser',
                type: 'default',
                width: 135,
                text: 'Limpiar',
                disabled: false,

                onClick: function () {
                    limpiarCampos();
                }
            },

            BtnGuardarCajaOptions: {
                icon: 'fas fa-save',
                type: 'success',
                width: 135,
                text: 'Guardar caja',
                disabled: false
            }

        };

        // --------------------------------------------------
        // TEXT BOXES
        // --------------------------------------------------

        vm.textBox = {

            // ----------------------------------------------
            // Código de captura: estación + producto
            // Ejemplo: 01S114
            // ----------------------------------------------

            TxtCodigoCapturaOptions: {
                disabled: false,
                readOnly: false,
                showClearButton: true,
                maxLength: 8,
                placeholder: 'Ejemplo: 01S114',
                valueChangeEvent: 'input',

                bindingOptions: {
                    value: 'txtCodigoCaptura'
                },

                onValueChanged: function (e) {

                    var codigo = (e.value || '')
                        .replace(/\s/g, '')
                        .toUpperCase()
                        .substring(0, 8);

                    $scope.txtCodigoCaptura = codigo;

                    if (e.value !== codigo) {
                        e.component.option('value', codigo);
                    }

                }
            },

            // ----------------------------------------------
            // Estación de trabajo
            // ----------------------------------------------

            TxtEstacionOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'txtEstacion'
                }
            },

            // ----------------------------------------------
            // Empleado
            // ----------------------------------------------

            TxtEmpleadoOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'txtEmpleado'
                }
            },

            // ----------------------------------------------
            // Clave del producto
            // ----------------------------------------------

            TxtClaveProductoOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'txtClaveProducto'
                }
            },

            // ----------------------------------------------
            // Nombre del producto de empaque
            // ----------------------------------------------

            TxtProductoEmpaqueOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'txtProductoEmpaque'
                }
            },

            // ----------------------------------------------
            // Precio de caja
            // ----------------------------------------------

            TxtPrecioCajaOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,
                format: '$ #,##0.00',

                bindingOptions: {
                    value: 'txtPrecioCaja'
                }
            },

            // ----------------------------------------------
            // Calidad
            // ----------------------------------------------

            TxtCalidadOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'txtCalidad'
                }
            },

            // ----------------------------------------------
            // Tamaño
            // ----------------------------------------------

            TxtTamanoOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'txtTamano'
                }
            },

            // ----------------------------------------------
            // Variedad
            // ----------------------------------------------

            TxtVariedadOptions: {
                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'txtVariedad'
                }
            }

        };

        // --------------------------------------------------
        // SELECT BOXES
        // --------------------------------------------------

        vm.selectBox = {

            // ----------------------------------------------
            // Tarimas disponibles
            // ----------------------------------------------

            CmbTarimaOptions: {
                dataSource: [],
                displayExpr: 'codigo_tarima',
                valueExpr: 'id',
                placeholder: 'Seleccionar tarima',
                noDataText: 'Sin tarimas disponibles',
                showClearButton: true,
                searchEnabled: true,
                disabled: true,

                bindingOptions: {
                    value: 'cmbTarima'
                }
            }

        };

        // --------------------------------------------------
        // LIMPIAR CAPTURA
        // --------------------------------------------------

        function limpiarCampos() {

            $scope.txtCodigoCaptura = '';

            $scope.txtEstacion = '';
            $scope.txtEmpleado = '';

            $scope.txtClaveProducto = '';
            $scope.txtProductoEmpaque = '';
            $scope.txtPrecioCaja = '';

            $scope.txtCalidad = '';
            $scope.txtTamano = '';
            $scope.txtVariedad = '';

            $scope.cmbTarima = null;

        }

    }

})();
