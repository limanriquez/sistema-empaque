(function(){
	angular.module('agricola.directives')
	.directive('avisosArraigo', fncAvisosArraigo)
	.directive('avisosSiniestroRecoleccion', fncAvisosSiniestroYRecoleccion);

	fncAvisosArraigo.$inject = ['$http']
	function fncAvisosArraigo($http) {
		return {
			templateUrl: '/directives_templates/avisos/arraigo',
			

			scope: {
				id_solicitud: '=idSolicitud'
			},
			link: function(scope, element, attrs){

				//Verificando cuando cambia de solicitud de aseguramiento(se selecciona una nueva acta, existente o no)
				scope.$watch('id_solicitud', function (new_val, old_val) {
					if(new_val > 0){
						$http.get('/api/v1/aviso_arraigo/?IdToIdSolicitudAseguramiento=' + scope.id_solicitud).then(
							function(resp){
								scope.avisos_arraigo = resp.data.results;
							},
							function(resp){
								alertify.error('Ocurrió un error al cargar los avisos de arraigo');
							}
						);
					}else{
						scope.avisos_arraigo = [];
					}
				});
				
			}
		};
	}

	fncAvisosSiniestroYRecoleccion.$inject = ['$http'];
	function fncAvisosSiniestroYRecoleccion($http){
		return {
			templateUrl: '/directives_templates/avisos/siniestro_recoleccion',
			scope: {
				id_solicitud: '=idSolicitud',
				aviso_para_acta: '=avisoParaActa',
				idAvisoActa:'=idAvisoActa'
			},
			link: function(scope, element, attrs){
				
				/*scope.$watch('aviso_acta', (new_val, old_val) => {
					idAvisoActa = new_val;
				});*/
	
				scope.$watch('id_solicitud', function(new_val, old_val){

					if(new_val){
						scope.tipos_avisos = [];
						scope.avisos = {};

						$http.get('/api/v1/tipo_aviso').then(function(resp){
							for(let i = 0; i < resp.data.results.length; i++){
								let tipo_aviso = resp.data.results[i]
								scope.tipos_avisos.push(tipo_aviso);
								$http.get("/get_informacion_aviso_por_solicitud_y_tipo_aviso/" + 
										  scope.id_solicitud + '/' + tipo_aviso.IdAviso)
								.then(function(resp){
									scope.avisos[tipo_aviso.Descripcion] = resp.data;
									for(let aviso_tmp of resp.data){
										$http.get('/api/v1/superficies_aviso_siniestro?IdToIdAviso=' + aviso_tmp.IdAviso)
										.then(function(resp_predios){
											scope.avisos[tipo_aviso.Descripcion + '_aviso_' + aviso_tmp.IdAviso + '_predios'] = resp_predios.data.results;
										}, function(error_predios){
											DevExpress.ui.notify("Error al traer los predios de los avisos");
										});

									}
								}, function(resp){
									DevExpress.ui.notify('Error al traer los avisos', 'error');
								});
							}
						}, function(resp){
							DevExpress.ui.notify('Error al traer los tipos de avisos', 'error');
						});
					}else{
						scope.avisos = scope.tipos_avisos = [];
					}

				});
				
				scope.get_avisos_por_tipo = function(tipo_desc){
					return scope.avisos[tipo_desc];
				}

				scope.hay_avisos = function(){
					if(scope.avisos && scope.tipos_avisos){
						var tiene = false;
						for(let i = 0; i < scope.tipos_avisos.length; i++){
							if(scope.avisos[scope.tipos_avisos[i].Descripcion] && scope.avisos[scope.tipos_avisos[i].Descripcion].length > 0 ){
								tiene = true;
								break;
							}
						}
						return tiene;
					}
					else
						return false;
				}

			}	
		}
	}

})();