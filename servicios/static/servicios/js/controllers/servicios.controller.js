(function () {
	'use strict';
	angular
		.module('servicios.servicio.controllers')
		.controller('CargarArchivoFtpController', CargarArchivoFtpController);

	CargarArchivoFtpController.$inject = ['$http', '$scope'];

	function CargarArchivoFtpController($http, $scope) {
		var vm = this;
		var btnSubirImagenInstance;

		function subirImagen(file) {
			$scope.isLoadPanelVisible = true;

			const formData = new FormData();
			formData.append('imagen', file, file.name);  // Mantiene el nombre original

			$http.post('/subir-imagen/', formData, {
				transformRequest: angular.identity,
				headers: { 'Content-Type': undefined }
			}).then(function (response) {
				DevExpress.ui.notify("Imagen subida correctamente: " + response.data.nombre_archivo, "success", 3000);
				$scope.isLoadPanelVisible = false;
			}, function (error) {
				const msg = error.data?.error || error.statusText || 'Error desconocido';
				DevExpress.ui.notify("Error al subir la imagen: " + msg, "error", 3000);
				$scope.isLoadPanelVisible = false;
			});
		}

		vm.buttons = {
			btnSubirImagenOptions: {
				icon: 'fa fa-camera',
				type: 'default',
				text: "Tomar o seleccionar foto",
				width: 220,
				onInitialized: function (e) {
					btnSubirImagenInstance = e.component;
				},
				onClick: function () {
					const input = document.getElementById('inputImagen');
					input.value = '';
					input.click();
				}
			}
		};

		document.getElementById('inputImagen').addEventListener('change', function (event) {
			const archivo = event.target.files[0];
			if (!archivo) {
				DevExpress.ui.notify("Debe seleccionar una imagen", "warning", 2500);
				return;
			}
			subirImagen(archivo);
		});

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
