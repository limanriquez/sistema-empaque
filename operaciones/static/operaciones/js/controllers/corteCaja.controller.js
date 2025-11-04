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
        let BtnConsultarInstance, BtnCerrarInstance, BtnImprimirInstance, ObservacionesInstance,
            popConsultarCortesInstance, BtnSeleccionarCortesInstance, BtnRegresarInstance,
            grdConsultarCortesInstance;
        let corteSeleccionado = null;
        let ArrayCortes = [];
        let vm = this;
        $scope.modoEdicion = false;

        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;
        vm.corteCajaId = $scope.corteCajaId;

        function showLoading() {
            Swal.fire({
                title: 'Cargando...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        }
        // Ocultar loading
        function hideLoading() {
            Swal.close();
        }

        getCorteCajaAbierto();

        function getCorteCajaAbierto() {
            const params = new URLSearchParams({
                empresa: vm.empresaId // o el ID que tengas en el scope
            });

            showLoading();
            const url = `/corteCajaAbierto/?${params.toString()}`;

            $http.get(url).then(
                function (response) {
                    hideLoading();

                    // Si el servidor envía una advertencia
                    if (response.data.advertencia) {
                        Swal.fire({
                            icon: 'warning',
                            title: 'Atención',
                            text: response.data.advertencia,
                            confirmButtonText: 'Aceptar'
                        });
                        BtnCerrarInstance.option("disabled", true);
                        BtnImprimirInstance.option("disabled", true);
                        ObservacionesInstance.option("disabled", true);
                    } else {
                        // Datos del corte abierto
                        $scope.corteCajaAbierto = response.data;
                        corteSeleccionado = response.data;
                        cargarCorteCajaAbierto(response.data);
                    }
                },
                function (error) {
                    hideLoading();
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

        function getCortesCajaCerrados() {
            const params = new URLSearchParams({
                empresa: vm.empresaId // o el ID que tengas en el scope
            });
            showLoading();
            const url = `/cortesCajaCerrados/?${params.toString()}`;
            $http.get(url).then(
                function (response) {
                    popConsultarCortesInstance.show();
                    ArrayCortes.length = 0;
                    for (let i = 0; i < response.data.length; i++) {
                        ArrayCortes.push(response.data[i]);
                    }
                    hideLoading()
                    if (grdConsultarCortesInstance) {
                        grdConsultarCortesInstance.refresh();
                    }
                }, function (response) {
                    hideLoading()
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'No se pudo obtener los cortes de caja',
                        confirmButtonText: 'Aceptar'
                    });
                }
            );
        };

        function modificarCorteCaja() {
            const ahora = new Date();
            const fechaLocal = new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60000);
            const fechaCierreISO = fechaLocal.toISOString().slice(0, 19);

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
                    BtnImprimirInstance.option("disabled", false);
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
        function llenarInformacion(data) {
            const hoy = new Date();
            hoy.setHours(0, 0, 0, 0);
            $scope.txtNombre = vm.nombrePersonal;
            $scope.saldoInicial = parseFloat(data.saldo_inicial || 0);
            $scope.saldoFinal = parseFloat(data.saldo_final || 0);
            $scope.ingresosEfectivo = parseFloat(data.ingresos_efectivo || 0);
            $scope.ingresosTarjeta = parseFloat(data.ingresos_tarjeta || 0);
            $scope.ingresosTransferencia = parseFloat(data.ingresos_transferencia || 0);
            $scope.egresos = parseFloat(data.total_egresos || 0);
            $scope.ingresos = parseFloat(data.otros_ingresos || 0);
            $scope.saldoFinal = parseFloat(data.tota_caja || 0);
            $scope.totalCaja = parseFloat(data.saldo_final || 0);
            $scope.fechaApertura = data.fecha_apertura ? new Date(data.fecha_apertura.split('/').reverse().join('-')) : null;
            $scope.fechaCierre = data.fecha_cierre ? new Date(data.fecha_cierre.split('/').reverse().join('-')) : null;
            $scope.observaciones = data.observaciones;
        }
        function limpiarCamposCorte() {
            $scope.txtNombre = "";
            $scope.saldoInicial = "";
            $scope.saldoFinal = "";
            $scope.ingresosEfectivo = "";
            $scope.ingresosTarjeta = "";
            $scope.ingresosTransferencia = "";
            $scope.egresos = "";
            $scope.ingresos = "";
            $scope.totalCaja = "";
            $scope.fechaApertura = null;
            $scope.fechaCierre = null;
            $scope.observaciones = "";
            corteSeleccionado = null;
            BtnImprimirInstance.option("disabled", true);
        };
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
        $scope.cortes_source = new DevExpress.data.DataSource({
            store: ArrayCortes
        });
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
            BtnSeleccionarCortesOptions: {
                icon: 'fas fa-check-circle',
                type: 'success',
                width: 135,
                text: 'Seleccionar',
                disabled: false,
                onInitialized: function (e) {
                    BtnSeleccionarCortesInstance = e.component;
                },
                onClick: function () {
                    if (corteSeleccionado) {
                        popConsultarCortesInstance.hide();
                        llenarInformacion(corteSeleccionado);
                        BtnImprimirInstance.option("disabled", false)
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Advertencia',
                            text: 'Seleccione un corte de caja para continuar',
                            showConfirmButton: true,
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            didOpen: () => {
                                const popup = Swal.getPopup();
                                const overlay = document.querySelector('.swal2-container');

                                // Forzar que quede por encima de cualquier modal/popup
                                if (popup) {
                                    popup.style.zIndex = '999999';
                                    popup.style.fontSize = '1.3rem';
                                    popup.style.padding = '2rem';
                                    popup.style.width = '450px';
                                    popup.style.textAlign = 'center';
                                }
                                if (overlay) {
                                    overlay.style.zIndex = '999998';
                                }

                                const confirmBtn = Swal.getConfirmButton();
                                if (confirmBtn) {
                                    confirmBtn.style.fontSize = '1.2rem';
                                    confirmBtn.style.padding = '0.8rem 2rem';
                                }
                            }
                        });
                    }

                }
            },
            BtnRegresarOptions: {
                icon: 'fas fa-arrow-left',
                type: 'danger',
                width: 135,
                text: 'Regresar',
                disabled: false,
                onInitialized: function (e) {
                    BtnRegresarInstance = e.component;
                },
                onClick: function () {
                    popConsultarCortesInstance.hide();
                }
            },
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
                    limpiarCamposCorte();
                    getCortesCajaCerrados();
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
            BtnImprimirOptions: {
                icon: 'fas fa-print',
                type: 'default',
                width: 135,
                text: 'Imprimir',
                disabled: true,
                onInitialized: function (e) {
                    BtnImprimirInstance = e.component;
                },
                onClick: function () {
                    if (corteSeleccionado) {
                        window.open(`/corte_caja_pdf/${corteSeleccionado.id}/`, '_blank');
                    } else {

                    }

                    //buscarImprimirCorteCaja();
                }
            }
        };

        vm.grid = {
            grdConsultarCortesOptions: {
                dataSource: $scope.cortes_source,
                paging: {
                    pageSize: 20
                },
                pager: {
                    showPageSizeSelector: true,
                    allowedPageSizes: [20, 40, 60],
                    showInfo: true
                },
                selection: {
                    mode: 'single'
                },
                filterRow: {
                    visible: true,
                    applyFilter: "auto"
                },
                showBorders: true,
                columns: [
                    { dataField: 'id', visible: false },
                    { dataField: 'empresa_id', caption: 'ID Empresa', dataType: 'number', visible: false },
                    { dataField: 'personal', caption: 'Personal', dataType: 'string', width: 200 },
                    { dataField: 'saldo_inicial', caption: 'Saldo inicial', dataType: 'number', format: { type: 'currency', precision: 2 } },
                    { dataField: 'saldo_final', caption: 'Saldo final', dataType: 'number', format: { type: 'currency', precision: 2 } },
                    { dataField: 'ingresos_efectivo', caption: 'Ingresos efectivo', dataType: 'number', format: { type: 'currency', precision: 2 } },
                    { dataField: 'ingresos_tarjeta', caption: 'Ingresos tarjeta', dataType: 'number', format: { type: 'currency', precision: 2 } },
                    { dataField: 'ingresos_transferencia', caption: 'Ingresos transferencia', dataType: 'number', format: { type: 'currency', precision: 2 } },
                    { dataField: 'egresos', caption: 'Egresos', dataType: 'number', format: { type: 'currency', precision: 2 } },
                    { dataField: 'fecha_apertura', caption: 'Fecha apertura', dataType: 'date', format: 'dd/MM/yyyy', width: 120, alignment: 'center' },
                    { dataField: 'fecha_cierre', caption: 'Fecha cierre', dataType: 'date', format: 'dd/MM/yyyy', width: 120, alignment: 'center' },
                    { dataField: 'estatus', caption: 'Estatus', dataType: 'string', width: 120 },
                    { dataField: 'observaciones', caption: 'Observaciones', dataType: 'string', width: 250 }
                ],
                onInitialized: function (e) {
                    grdConsultarCortesInstance = e.component;
                },
                onRowClick: function (e) {
                    corteSeleccionado = e.data;
                },
                noDataText: "Sin datos",
                scrolling: {
                    mode: 'standar',
                    showScrollbar: 'always'
                },
                columnFixing: {
                    enabled: true
                },
                rowAlternationEnabled: true,
                columnAutoWidth: true,
                allowColumnResizing: true,
            },
        }
        vm.popups = {
            popConsultarCortesOptions: {
                showTitle: true,
                width: 1200,
                height: 800,
                title: "Buscar cortes de caja",
                dragEnabled: false,
                closeOnOutsideClick: false,
                bindingOptions: {
                    visible: "showPopConsultarCortes",
                },
                onInitialized: function (e) {
                    popConsultarCortesInstance = e.component;//Se inicializa el popup para poder darle funcionalidad
                },
                onShown: function (e) {

                },
            },
        };

    }
})();