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
        let BtnConsultarInstance, BtnCerrarInstance, BtnBuscarImprimirInstance, ObservacionesInstance;
        let vm = this;
        $scope.modoEdicion = false;

        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;
        vm.corteCajaId = $scope.corteCajaId;
        getCorteCajaAbierto();

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
                        BtnCerrarInstance.option("disabled", true);
                        BtnBuscarImprimirInstance.option("disabled", true);
                        ObservacionesInstance.option("disabled", true);
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
                }
            );
        }

        function modificarCorteCaja() {
            const hoy = new Date();
            hoy.setHours(0, 0, 0, 0);
            const fechaCierreISO = hoy.toISOString().slice(0, 19);
            const corteCajaData = {
                saldo_final: $scope.saldoFinal,
                ingresos_efectivo: $scope.ingresosEfectivo,
                ingresos_tarjeta: $scope.ingresosTarjeta,
                ingresos_transferencia: $scope.ingresosTransferencia,
                otros_ingresos: $scope.ingresos,
                egresos: $scope.egresos,
                fecha_cierre: fechaCierreISO,
                estatus: 2 // 2 = CERRADO
            };

            $http({
                method: 'PATCH',
                url: `/api/v1/corteCaja/${$scope.corteCajaId}/`,
                data: corteCajaData
            }).then(
                function (response) {
                    BtnCerrarInstance.option("disabled", true);
                    BtnBuscarImprimirInstance.option("disabled", false);
                    ObservacionesInstance.option("disabled", true);
                    Swal.fire({
                        icon: 'success',
                        title: 'Corte cerrado con éxito 🚀',
                        html: `
                            <div style="font-size: 15px; margin-top: 6px;">
                                El corte de caja se registró correctamente.<br>
                                <b>Todo listo para continuar con la operación.</b>
                            </div>
                        `,
                        timer: 5000,               // se cierra automáticamente
                        timerProgressBar: true,     // barra de progreso
                        showConfirmButton: false,   // ❌ quita el botón "OK"
                        allowOutsideClick: false,   // ❌ no cerrar al hacer clic fuera
                        allowEscapeKey: false,      // ❌ no cerrar con Esc
                        background: 'linear-gradient(145deg, #ffffff, #fef3c7)', // blanco + dorado sutil
                        color: '#1e293b',           // texto elegante
                        iconColor: '#f59e0b',       // dorado elegante
                        showClass: { popup: 'animate__animated animate__fadeInDown' },
                        hideClass: { popup: 'animate__animated animate__fadeOutUp' },
                        customClass: { popup: 'rounded-4 shadow-lg border border-amber-200' },
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            popup.style.boxShadow = '0 0 25px rgba(245, 158, 11, 0.3)'; // brillo dorado sutil
                        }
                    });
                },
                function (error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Se genero un error al cerrar el corte de caja.',
                        confirmButtonText: 'Aceptar'
                    });
                }
            );
        }
        function cargarCorteCajaAbierto(data) {
            // Asignar valores al $scope
            const hoy = new Date();
            hoy.setHours(0, 0, 0, 0);
            $scope.txtNombre = vm.nombrePersonal; //data.personal_id ? `Personal ${data.personal_id}` : '';
            $scope.saldoInicial = parseFloat(data.saldo_inicial || 0);
            $scope.saldoFinal = parseFloat(data.saldo_final || 0);
            $scope.ingresosEfectivo = parseFloat(data.ingresos_efectivo || 0);
            $scope.ingresosTarjeta = parseFloat(data.ingresos_tarjeta || 0);
            $scope.ingresosTransferencia = parseFloat(data.ingresos_transferencia || 0);
            $scope.egresos = parseFloat(data.total_egresos || 0);
            $scope.ingresos = parseFloat(data.total_ingresos || 0);
            $scope.saldoFinal = $scope.saldoInicial
                + $scope.ingresosEfectivo
                + $scope.ingresosTarjeta
                + $scope.ingresosTransferencia
                + $scope.ingresos
                - $scope.egresos;

            $scope.totalCaja = $scope.saldoInicial
                + $scope.ingresosEfectivo
                + $scope.ingresos
                - $scope.egresos;

            $scope.fechaApertura = data.fecha_apertura ? new Date(data.fecha_apertura.split('/').reverse().join('-')) : null;
            $scope.fechaCierre = hoy;
            //  $scope.fechaCierre = data.fecha_cierre ? new Date(data.fecha_cierre.split('/').reverse().join('-')) : null;
            //  $scope.observaciones = data.observaciones || '';
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
            OtrosIngresosOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'ingresos' },
                // onValueChanged: function (e) { $scope.egresos = e.value; }
            },
            EgresosOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'egresos' },
                // onValueChanged: function (e) { $scope.egresos = e.value; }
            },
            TotalCajaOptions: {
                disabled: true,
                showSpinButtons: true,
                min: 0,
                format: "#,##0.00",
                bindingOptions: { value: 'totalCaja' },
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
                onInitialized: function (e) {
                    ObservacionesInstance = e.component;
                },
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
                    modificarCorteCaja();
                    // cerrarCorteCaja();
                }
            },
            BtnBuscarImprimirOptions: {
                icon: 'fas fa-print',
                type: 'default',
                width: 135,
                text: 'Imprimir',
                disabled: true,
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