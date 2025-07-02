(function () {
    'use strict';
    angular
        .module('servicios.servicio.controllers')
        .controller('GuestBookController', GuestBookController);

    GuestBookController.$inject = ['$http', '$scope'];

    function GuestBookController($http, $scope) {
        var vm = this;
        var btnSubirImagenInstance, txtAreaObservacionesInstance;
        function limpiarCampos() {
            $scope.txtNombre = "";
            $scope.txtAreaObservaciones = "";
        }
        function guardarMensaje() {
            $scope.isLoadPanelVisible = true;
            var mensaje_json = {
                nombre: $scope.txtNombre,
                mensaje: $scope.txtAreaObservaciones,
            };

            // Hacer el POST al backend con el JSON del cliente
            $http.post('/api/v1/mensaje.json', mensaje_json)
                .then(function (response) {
                    $scope.isLoadPanelVisible = false;
                    var mensajeCreado = response.data;  // La respuesta del backend que contiene el cliente guardado

                    // Usar SweetAlert2 para mostrar la notificación de éxito
                    Swal.fire({
                        icon: 'success',  // Tipo de alerta (success, error, warning, info)
                        title: 'Mensaje guardado exitosamente',
                        text: 'Tus deseos se han enviado',
                        confirmButtonText: 'Aceptar',
                        timer: 3500  // Duración de la alerta (en milisegundos)
                    });
                    limpiarCampos();
                    // Aquí puedes agregar otras acciones si es necesario (por ejemplo, habilitar botones, limpiar campos, etc.)
                }, function (response) {
                    $scope.isLoadPanelVisible = false;
                    // Usar SweetAlert2 para mostrar la notificación de error
                    Swal.fire({
                        icon: 'error',  // Tipo de alerta (error)
                        title: 'Error al guardar el mensaje',
                        text: 'Hubo un problema al intentar guardar la información del mensaje.',
                        confirmButtonText: 'Aceptar'
                    });
                });
        }

        vm.textArea = {
            TxtMensajeOptions: {
                height: 80,
                maxLength: 400,
                placeholder: "Escribe tus deseos",
                showClearButton: true,
                autoResizeEnabled: true, // opcional
                bindingOptions: {
                    value: 'txtAreaObservaciones'
                },
                onValueChanged: function (e) {
                    let value = e.value || '';
                    $scope.txtAreaObservaciones = value.toUpperCase();
                },
                onInitialized: function (e) {
                    txtAreaObservacionesInstance = e.component;
                }
            }
        };

        vm.textBox = {
            TxtNombreOptions: {
                placeholder: "Escribe tu nombre",
                disabled: false,
                showClearButton: true,
                maxLength: 100,
                bindingOptions: {
                    value: 'txtNombre'
                },
                onValueChanged: function (data) {
                    //	$scope.txtNombre = $filter('uppercase')(data.value);
                },
            },
        }
        vm.buttons = {
            btnEnviarMensajeOptions: {
                text: "💖 Compartir mensaje",
                width: 400,
                type: 'default',
                elementAttr: {
                    class: `
                bg-gradient-to-r from-pink-400 via-pink-300 to-pink-400
                hover:from-pink-500 hover:to-pink-500
                font-semibold italic text-lg
                rounded-full shadow-xl
                px-8 py-3
                transition duration-300 ease-in-out
                border-2 border-white
                tracking-wide
            `.trim(),
                    style: 'color: rgb(150, 50, 125);'
                },
                onInitialized: function (e) {
                    btnSubirImagenInstance = e.component;
                },
                onClick: function () {
                    if (!$scope.txtNombre || !$scope.txtNombre.trim()) {
                        Swal.fire({
                            title: 'Escribe tu nombre',
                            text: 'Escribe tu nombre para continuar',
                            icon: 'warning',
                            confirmButtonText: 'Aceptar',
                            backdrop: true
                        });
                        return;
                    }

                    if (!$scope.txtAreaObservaciones || !$scope.txtAreaObservaciones.trim()) {
                        Swal.fire({
                            title: 'Escribe el mensaje',
                            text: 'Escribeme un lindo mensaje para continuar',
                            icon: 'warning',
                            confirmButtonText: 'Aceptar',
                            backdrop: true
                        });
                        return;
                    }

                    guardarMensaje(); // se llama solo si pasa validación
                }
            }
        };



        vm.loadPanels = {
            basicOptions: {
                closeOnOutsideClick: false,
                message: 'Enviando imagen',
                bindingOptions: {
                    visible: 'isLoadPanelVisible'
                }
            }
        };
    }
})();
