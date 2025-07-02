(function () {
    'use strict';
    angular
        .module('servicios.servicio.controllers')
        .controller('GuestBookController', GuestBookController);

    GuestBookController.$inject = ['$http', '$scope'];

    function GuestBookController($http, $scope) {
        var vm = this;
        var btnSubirImagenInstance, txtAreaObservacionesInstance;
        
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
				onValueChanged: function(e) {
					let value = e.value || '';
					$scope.txtAreaObservaciones = value.toUpperCase();
				},
				onInitialized: function(e) {
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
				onValueChanged: function(data){
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
