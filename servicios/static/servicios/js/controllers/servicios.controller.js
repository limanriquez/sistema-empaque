(function (){
	'use strict';
	angular
		.module('servicios.servicio.controllers')
		.controller('CargarArchivoFtpController', CargarArchivoFtpController);

	CargarArchivoFtpController.$inject = ['$http', '$scope'];

	function CargarArchivoFtpController($http, $scope){
		var vm = this;
		var btnSubirImagenInstance;

		function comprimirImagen(file, callback) {
			const reader = new FileReader();

			reader.onload = function(event) {
				const img = new Image();

				img.onload = function() {
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

					canvas.toBlob(function(blob) {
						if (!blob || blob.size === 0) {
							DevExpress.ui.notify("La imagen no se pudo procesar correctamente", "error", 3000);
							$scope.isLoadPanelVisible = false;
							return;
						}
						callback(blob);
					}, 'image/jpeg', 0.7);
				};

				img.onerror = function() {
					DevExpress.ui.notify("No se pudo leer la imagen, intenta otra foto", "error", 3000);
					$scope.isLoadPanelVisible = false;
				};

				img.src = event.target.result;
			};

			reader.onerror = function() {
				DevExpress.ui.notify("No se pudo leer el archivo de imagen", "error", 3000);
				$scope.isLoadPanelVisible = false;
			};

			reader.readAsDataURL(file);
		}

		function subirImagen(file) {
			$scope.isLoadPanelVisible = true;
			comprimirImagen(file, function(blob) {
				const formData = new FormData();
				formData.append('imagen', blob, 'foto.jpg'); // Nombre fijo .jpg para evitar problemas

				$http.post('/subir-imagen/', formData, {
					transformRequest: angular.identity,
					headers: { 'Content-Type': undefined }
				}).then(function(response) {
					DevExpress.ui.notify("Imagen subida correctamente: " + response.data.nombre_archivo, "success", 3000);
					$scope.isLoadPanelVisible = false;
				}, function(error) {
					DevExpress.ui.notify("Error al subir la imagen: " + (error.data?.error || 'Desconocido'), "error", 3000);
					$scope.isLoadPanelVisible = false;
				});
			});
		}

		vm.buttons = {
			btnSubirImagenOptions: {
				icon: 'fa fa-camera',
				type: 'default',
				text: "Tomar o seleccionar foto",
				width: 220,
				onInitialized: function(e){
					btnSubirImagenInstance = e.component;
				},
				onClick: function(){
					const input = document.getElementById('inputImagen');
					input.value = '';
					input.click();
				}
			}
		};

		document.getElementById('inputImagen').addEventListener('change', function(event){
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
