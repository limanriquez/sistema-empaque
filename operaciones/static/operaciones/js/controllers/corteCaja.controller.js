(function () {
    'use strict';

    // Definición del controlador dentro del módulo 'operaciones.operacion.controllers'
    angular
        .module('operaciones.operacion.controllers') // Asegúrate de que el módulo 'operaciones.operacion.controllers' ya esté creado
        .controller('CorteCaja', CorteCajaController); // Se cambió 'Cliente' por 'ClienteController' para que coincida con el nombre correcto

    // Inyección de dependencias
    CorteCajaController.$inject = ['$http', '$scope', '$filter'];

    // Definición del controlador
    function CorteCajaController($http, $scope, $filter) {
        var BtnConsultarInstance, BtnCerrarInstance, BtnBuscarImprimirInstance;
        var vm = this;
        $scope.modoEdicion = false;

        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;
        vm.corteCajaId = $scope.corteCajaId;
        getCorteCajaAbierto();

        console.log(vm.corteCajaId);

        function getCorteCajaAbierto() {
            const params = new URLSearchParams({
                empresa: vm.empresaId // o el ID que tengas en el scope
            });

            $scope.isLoadPanelVisible = true;
            const url = `/corteCajaAbierto/?${params.toString()}`;

            $http.get(url).then(
                function (response) {
                    $scope.isLoadPanelVisible = false;

                    // Si el servidor envía una advertencia
                    if (response.data.advertencia) {
                        Swal.fire({
                            icon: 'warning',
                            title: 'Atención',
                            text: response.data.advertencia,
                            confirmButtonText: 'Aceptar'
                        });
                    } else {
                        // Datos del corte abierto
                        $scope.corteCajaAbierto = response.data;
                        cargarCorteCajaAbierto(response.data);
                    }
                },
                function (error) {
                    $scope.isLoadPanelVisible = false;
                    // Error de red o inesperado
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'No se pudo obtener el corte de caja abierto.',
                        confirmButtonText: 'Aceptar'
                    });
                    console.error("Error al obtener el corte de caja abierto:", error);
                }
            );
        }
        function cargarCorteCajaAbierto(data) {
            // Asignar valores al $scope
            const hoy = new Date();
            hoy.setHours(0, 0, 0, 0);
            $scope.txtNombre =  vm.nombrePersonal; //data.personal_id ? `Personal ${data.personal_id}` : '';
            $scope.saldoInicial = parseFloat(data.saldo_inicial || 0);
            $scope.saldoFinal = parseFloat(data.saldo_final || 0);
            $scope.ingresosEfectivo = parseFloat(data.ingresos_efectivo || 0);
            $scope.ingresosTarjeta = parseFloat(data.ingresos_tarjeta || 0);
            $scope.ingresosTransferencia = parseFloat(data.ingresos_transferencia || 0);
            $scope.egresos = parseFloat(data.egresos || 0);
            $scope.fechaApertura = data.fecha_apertura ? new Date(data.fecha_apertura.split('/').reverse().join('-')) : null;
            $scope.fechaCierre = hoy;
            //  $scope.fechaCierre = data.fecha_cierre ? new Date(data.fecha_cierre.split('/').reverse().join('-')) : null;
            $scope.observaciones = data.observaciones || '';

            // Actualizar DevExtreme manually si es necesario
            if (vm.textBox) {
                vm.textBox.TxtNombreOptions.value = $scope.txtNombre;
            }

            if (vm.numberBox) {
                vm.numberBox.SaldoInicialOptions.value = $scope.saldoInicial;
                vm.numberBox.SaldoFinalOptions.value = $scope.saldoFinal;
                vm.numberBox.IngresosEfectivoOptions.value = $scope.ingresosEfectivo;
                vm.numberBox.IngresosTarjetaOptions.value = $scope.ingresosTarjeta;
                vm.numberBox.IngresosTransferenciaOptions.value = $scope.ingresosTransferencia;
                vm.numberBox.EgresosOptions.value = $scope.egresos;
            }

            if (vm.dateBox) {
                vm.dateBox.FechaAperturaOptions.value = $scope.fechaApertura;
                vm.dateBox.FechaCierreOptions.value = $scope.fechaCierre;
            }

            if (vm.textArea) {
                vm.textArea.ObservacionesOptions.value = $scope.observaciones;
            }
        }
        vm.textBox = {
            TxtNombreOptions: {
                disabled: true,
                showClearButton: true,
                maxLength: 100,
                bindingOptions: {
                    value: 'txtNombre'
                },
                onValueChanged: function (data) {
                    // vm.corte.nombre = data.value.toUpperCase();
                }
            }
        };
        vm.numberBox = {
            SaldoInicialOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'saldoInicial' },
                onValueChanged: function (e) {
                    //  $scope.saldoInicial = e.value;
                }
            },
            SaldoFinalOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'saldoFinal' },
                onValueChanged: function (e) {
                    // $scope.saldoFinal = e.value;
                }
            },
            IngresosEfectivoOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'ingresosEfectivo' },
                //   onValueChanged: function (e) { $scope.ingresosEfectivo = e.value; }
            },
            IngresosTarjetaOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'ingresosTarjeta' },
                //  onValueChanged: function (e) { $scope.ingresosTarjeta = e.value; }
            },
            IngresosTransferenciaOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'ingresosTransferencia' },
                // onValueChanged: function (e) { $scope.ingresosTransferencia = e.value; }
            },
            EgresosOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'egresos' },
                // onValueChanged: function (e) { $scope.egresos = e.value; }
            }
        };
        vm.dateBox = {
            FechaAperturaOptions: {
                type: "date",              // solo fecha, sin hora
                displayFormat: "dd/MM/yyyy", // cómo se muestra en el calendario
                disabled: true,
                bindingOptions: { value: 'fechaApertura' }
            },
            FechaCierreOptions: {
                type: "date",              // solo fecha, sin hora
                displayFormat: "dd/MM/yyyy", // cómo se muestra en el calendario
                disabled: true,
                bindingOptions: { value: 'fechaCierre' },
                onValueChanged: function (e) {
                    //      $scope.fechaCierre = e.value;
                }
            }
        };
        vm.textArea = {
            ObservacionesOptions: {
                disabled: false,
                height: 90,
                bindingOptions: { value: 'observaciones' },
                onValueChanged: function (e) {
                    // $scope.observaciones = e.value;
                }
            }
        };
        vm.button = {
            BtnConsultarOptions: {
                icon: 'fas fa-search',
                type: 'success',
                width: 135,
                text: 'Consultar',
                disabled: false,
                onInitialized: function (e) {
                    BtnConsultarInstance = e.component;
                },
                onClick: function () {
                    // consultarCorteCaja();
                }
            },
            BtnCerrarOptions: {
                icon: 'fas fa-lock',
                type: 'danger',
                width: 135,
                text: 'Cerrar',
                disabled: false,
                onInitialized: function (e) {
                    BtnCerrarInstance = e.component;
                },
                onClick: function () {
                    // cerrarCorteCaja();
                }
            },
            BtnBuscarImprimirOptions: {
                icon: 'fas fa-print',
                type: 'default',
                width: 135,
                text: 'Imprimir',
                disabled: false,
                onInitialized: function (e) {
                    BtnBuscarImprimirInstance = e.component;
                },
                onClick: function () {
                    //buscarImprimirCorteCaja();
                }
            }
        };

    }
})();