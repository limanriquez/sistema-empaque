(function () {
	'use strict';
	angular
		.module('servicios.servicio.controllers')
		.controller('CargarArchivoFtpController', CargarArchivoFtpController);

	CargarArchivoFtpController.$inject = ['$http', '$scope'];

	function CargarArchivoFtpController($http, $scope) {
		var vm = this;
		var btnSubirImagenInstance;

		function comprimirImagen(file, callback) {
			const reader = new FileReader();
			reader.onload = function (event) {
				const img = new Image();
				img.onload = function () {
					const canvas = document.createElement('canvas');
					const maxWidth = 1024;
					const maxHeight = 1024;
					let width = img.width;
					let height = img.height;

					if (width > height && width > maxWidth) {
						height *= maxWidth / width;
						width = maxWidth;
					} else if (height > maxHeight) {
						width *= maxHeight / height;
						height = maxHeight;
					}

					canvas.width = width;
					canvas.height = height;
					const ctx = canvas.getContext('2d');
					ctx.drawImage(img, 0, 0, width, height);

					canvas.toBlob(function (blob) {
						callback(blob);
					}, 'image/jpeg', 0.7);  // Calidad 70%
				};
				img.src = event.target.result;
			};
			reader.readAsDataURL(file);
		}

		function enviarImagen(blob, filename) {
			const formData = new FormData();
			formData.append('imagen', blob, filename);

			$http.post('/subir-imagen/', formData, {
				transformRequest: angular.identity,
				headers: { 'Content-Type': undefined }
			}).then(function (response) {
				DevExpress.ui.notify("Imagen subida correctamente: " + response.data.nombre_archivo, "success", 3000);
				$scope.isLoadPanelVisible = false;
			}, function (error) {
				const msg = error.status === 413
					? "La imagen es demasiado grande para el servidor"
					: (error.data?.error || error.statusText || 'Error desconocido');
				DevExpress.ui.notify("Error al subir la imagen: " + msg, "error", 3000);
				$scope.isLoadPanelVisible = false;
			});
		}

		function subirImagen(file) {
			const MAX_SIZE_MB = 4;
			const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024;
			$scope.isLoadPanelVisible = true;

			if (file.size > MAX_BYTES) {
				comprimirImagen(file, function (blob) {
					enviarImagen(blob, 'foto_comprimida.jpg');
				});
			} else {
				enviarImagen(file, file.name);
			}
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
