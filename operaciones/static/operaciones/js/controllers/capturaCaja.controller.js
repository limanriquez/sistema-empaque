(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers')
        .controller('CapturaCaja', CapturaCajaController);

    CapturaCajaController.$inject = ['$http', '$q'];

    function CapturaCajaController($http, $q) {

        var vm = this;

        // --------------------------------------------------
        // VARIABLES DE LA OPERACIÓN
        // --------------------------------------------------

        vm.operacionDiariaId = null;
        vm.loteEmpaqueId = null;
        vm.variedadId = null;

        vm.txtCodigoCaptura = '';
        vm.txtCodigoUnico = '';

        vm.txtEstacion = '';
        vm.txtEmpleado = '';

        vm.txtClaveProducto = '';
        vm.txtProductoEmpaque = '';
        vm.txtPrecioCaja = '';

        vm.txtCalidad = '';
        vm.txtTamano = '';
        vm.txtVariedad = '';

        vm.cmbTarima = null;

        vm.isLoadPanelVisible = false;

        // --------------------------------------------------
        // INICIALIZACIÓN
        // Recibe los parámetros enviados desde ng-init
        // --------------------------------------------------

        vm.inicializar = function (operacionId, loteId, variedadId) {

            vm.operacionDiariaId = operacionId;
            vm.loteEmpaqueId = loteId;
            vm.variedadId = variedadId;

            vm.txtCodigoCaptura = '';

            vm.txtEstacion = '';
            vm.txtEmpleado = '';

            vm.txtClaveProducto = '';
            vm.txtProductoEmpaque = '';
            vm.txtPrecioCaja = '';

            vm.txtCalidad = '';
            vm.txtTamano = '';
            vm.txtVariedad = '';

            vm.cmbTarima = null;

            vm.isLoadPanelVisible = false;

        };

        // --------------------------------------------------
        // CONSULTAR CÓDIGO DE CAPTURA
        // --------------------------------------------------

        function consultarCodigoCaptura() {

            var codigo = (vm.txtCodigoCaptura || '')
                .replace(/\s/g, '')
                .toUpperCase();

            // Evitar consultas cuando el campo está vacío
            if (!codigo) {
                return;
            }

            // Validar estructura del código: 01CS110
            if (!/^\d{2}[A-Z0-9]{2}\d{3}$/.test(codigo)) {

                alert('El código debe tener el formato 01CS110.');

                limpiarResultados();
                return;
            }

            // ----------------------------------------------
            // 1. FRAGMENTAR CÓDIGO
            // ----------------------------------------------

            var idEstacion = parseInt(codigo.substring(0, 2), 10);

            var codigoProducto = codigo.substring(2, 4);

            var nombreTamano = codigo.substring(4, 7);

            // ----------------------------------------------
            // 2. OBTENER OPERACIÓN DIARIA
            // ----------------------------------------------

            var operacionDiariaId = vm.operacionDiariaId;

            if (!operacionDiariaId) {

                alert('No se ha identificado la operación diaria.');

                limpiarResultados();
                return;
            }

            // ----------------------------------------------
            // 3. LIMPIAR RESULTADOS ANTERIORES
            // ----------------------------------------------

            limpiarResultados();

            vm.isLoadPanelVisible = true;

            // ----------------------------------------------
            // 4. EJECUTAR LAS TRES CONSULTAS EN PARALELO
            // ----------------------------------------------

            $q.all([

                // Consulta 1: empleado asignado a estación
                $http.get('/obtener_empleado_estacion/', {
                    params: {
                        operacion_diaria_id: operacionDiariaId,
                        estacion_trabajo_id: idEstacion
                    }
                }),

                // Consulta 2: producto de empaque
                $http.get('/obtener_producto_empaque/', {
                    params: {
                        codigo: codigoProducto
                    }
                }),

                // Consulta 3: tamaño
                $http.get('/obtener_tamano/', {
                    params: {
                        nombre: nombreTamano
                    }
                })

            ]).then(function (responses) {

                // ------------------------------------------
                // 5. RECUPERAR RESPUESTAS
                // ------------------------------------------

                var empleado = responses[0].data;

                var producto = responses[1].data.producto;

                var tamano = responses[2].data.tamano;

                // ------------------------------------------
                // GUARDAR IDENTIFICADORES
                // ------------------------------------------

                vm.idEstacion = empleado.estacion_trabajo_id;
                vm.empleadoId = empleado.empleado_id;
                vm.productoId = producto.id;
                vm.tamanoId = tamano.id;

                // ------------------------------------------
                // MOSTRAR INFORMACIÓN EN LOS CONTROLES
                // ------------------------------------------

                vm.txtEstacion = vm.idEstacion;
                vm.txtEmpleado = vm.empleadoId;

                vm.txtClaveProducto = producto.codigo;
                vm.txtProductoEmpaque = producto.nombre;

                // Costo del producto de empaque
                vm.txtPrecioCaja = producto.costo_empaque;

                // Calidad asociada al producto
                vm.calidadId = producto.calidad_id;
                vm.txtCalidad = producto.calidad__nombre;

                // Tamaño consultado del catálogo
                vm.txtTamano = tamano.nombre;

                // Variedad recibida desde Django mediante ng-init
                vm.txtVariedad = vm.variedadId;
                // ------------------------------------------
                // 8. MOSTRAR RESULTADOS EN ALERT
                // ------------------------------------------

                alert(
                    'CONSULTAS EXITOSAS\n\n' +

                    'ID Estación: ' + vm.idEstacion + '\n' +

                    'ID Empleado: ' + vm.empleadoId + '\n' +

                    'ID Producto: ' + vm.productoId + '\n' +

                    'ID Tamaño: ' + vm.tamanoId
                );

            }).catch(function (error) {

                // ------------------------------------------
                // 9. MANEJO DE ERRORES
                // ------------------------------------------

                var mensaje = 'Error al consultar los datos.';

                if (error.data && error.data.mensaje) {
                    mensaje = error.data.mensaje;
                }

                alert(mensaje);

                console.error('Error en consultas de captura:', error);

                limpiarResultados();

            }).finally(function () {

                // ------------------------------------------
                // 10. OCULTAR INDICADOR DE CARGA
                // ------------------------------------------

                vm.isLoadPanelVisible = false;

            });

        }

        // --------------------------------------------------
        // LIMPIAR RESULTADOS DE LAS CONSULTAS
        // --------------------------------------------------

        function limpiarResultados() {

            vm.idEstacion = null;
            vm.empleadoId = null;
            vm.productoId = null;
            vm.tamanoId = null;

            vm.txtEstacion = '';
            vm.txtEmpleado = '';

            vm.txtClaveProducto = '';
            vm.txtProductoEmpaque = '';
            vm.txtPrecioCaja = '';

            vm.txtCalidad = '';
            vm.txtTamano = '';

        }

        // --------------------------------------------------
        // LIMPIAR TODA LA CAPTURA
        // --------------------------------------------------

        function limpiarCampos() {

            vm.txtCodigoCaptura = '';
            vm.txtCodigoUnico = '';

            limpiarResultados();

            vm.txtVariedad = '';

            vm.cmbTarima = null;

        }

        // --------------------------------------------------
        // LOAD PANEL
        // --------------------------------------------------

        vm.loadPanels = {

            basicOptions: {
                shading: true,
                showIndicator: true,
                showPane: true,
                visible: false,
                message: 'Procesando...',

                bindingOptions: {
                    visible: 'vm.isLoadPanelVisible'
                }
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
                text: 'Guardar',
                disabled: false
            }

        };

        // --------------------------------------------------
        // TEXT BOXES
        // --------------------------------------------------

        vm.textBox = {

            // ----------------------------------------------
            // CÓDIGO DE CAPTURA
            // Ejemplo: 01CS110
            // ----------------------------------------------

            TxtCodigoCapturaOptions: {

                disabled: false,
                readOnly: false,
                showClearButton: true,
                maxLength: 7,
                placeholder: 'Ejemplo: 01CS110',
                valueChangeEvent: 'input',

                bindingOptions: {
                    value: 'vm.txtCodigoCaptura'
                },

                onValueChanged: function (e) {

                    var codigo = (e.value || '')
                        .replace(/\s/g, '')
                        .toUpperCase()
                        .substring(0, 7);

                    if (e.value !== codigo) {
                        e.component.option('value', codigo);
                    }

                },

                onFocusOut: function (e) {

                    consultarCodigoCaptura();

                }

            },

            // ----------------------------------------------
            // CÓDIGO ÚNICO
            // ----------------------------------------------

            TxtCodigoUnicoOptions: {

                disabled: false,
                readOnly: false,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtCodigoUnico'
                }

            },

            // ----------------------------------------------
            // ESTACIÓN DE TRABAJO
            // ----------------------------------------------

            TxtEstacionOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtEstacion'
                }

            },

            // ----------------------------------------------
            // EMPLEADO
            // ----------------------------------------------

            TxtEmpleadoOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtEmpleado'
                }

            },

            // ----------------------------------------------
            // CLAVE DEL PRODUCTO
            // ----------------------------------------------

            TxtClaveProductoOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtClaveProducto'
                }

            },

            // ----------------------------------------------
            // NOMBRE DEL PRODUCTO DE EMPAQUE
            // ----------------------------------------------

            TxtProductoEmpaqueOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtProductoEmpaque'
                }

            },

            // ----------------------------------------------
            // PRECIO DE CAJA
            // ----------------------------------------------

            TxtPrecioCajaOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,
                format: '$ #,##0.00',

                bindingOptions: {
                    value: 'vm.txtPrecioCaja'
                }

            },

            // ----------------------------------------------
            // CALIDAD
            // ----------------------------------------------

            TxtCalidadOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtCalidad'
                }

            },

            // ----------------------------------------------
            // TAMAÑO
            // ----------------------------------------------

            TxtTamanoOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtTamano'
                }

            },

            // ----------------------------------------------
            // VARIEDAD
            // ----------------------------------------------

            TxtVariedadOptions: {

                disabled: false,
                readOnly: true,
                showClearButton: false,

                bindingOptions: {
                    value: 'vm.txtVariedad'
                }

            }

        };

        // --------------------------------------------------
        // SELECT BOXES
        // --------------------------------------------------

        vm.selectBox = {

            // ----------------------------------------------
            // TARIMAS DISPONIBLES
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
                    value: 'vm.cmbTarima'
                }

            }

        };

        // --------------------------------------------------
        // EXPONER FUNCIONES AL HTML
        // --------------------------------------------------

        vm.consultarCodigoCaptura = consultarCodigoCaptura;

        vm.limpiarCampos = limpiarCampos;

    }

})();