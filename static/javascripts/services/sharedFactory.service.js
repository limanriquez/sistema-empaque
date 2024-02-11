(function(){
	angular.module('agricola.services').factory('SharedFactory', SharedFactory);

	SharedFactory.$inject = ['$http'];
	
	function SharedFactory($http){
		var vm = this;
		const porcentaje_gastos_operacion = 0.25;
		const porcentaje_rrc_stop_loss = 0.75;

		vm.interfaz = {
			animations : {
				popAnimation: { 
		            show: {
		                type: "pop",
		                from: { 
		                    top: -100,
		                    opacity: 0
		                },
		                to: {
		                    opacity: 1,
		                      top: 0 
		                }
		            },
		            hide: {
		                type: "pop",
		                from: { 
		                      scale: 1,
		                      opacity: 1
		                },
		                to: {
		                    opacity: 0,
		                    scale: 0.1 
		                }
		            }
	    		}
			},
			setTooltips: function(tooltipspMap){
				for(let key in tooltipspMap){
					$(key).hover(function() {
				        $(tooltipspMap[key]).dxTooltip("instance").show();
				    }, function() {
				        $(tooltipspMap[key]).dxTooltip("instance").hide();
				    });
				}
			},
			llenaCmbDx: function (array, datos, source, source_load){
				if(!array || !datos || !source){
					return false;
				}
				array.splice(0, array.length);
				for(let i = 0; i < datos.length; i++){
					array.push(datos[i]);
				}
				if(source_load){
					source.load().done(source_load);
				}
				else{
					source.load();
				}
			},
			llenaGridDx: function(array,datos,grid, extra_logic){
				array.splice(0, array.length);
				for(let i = 0; i < datos.length; i++){
					array.push(datos[i]);
					if(extra_logic && typeof(extra_logic) == 'function')
						extra_logic(i);
				}
				if(grid)
					grid.refresh();
			},
			get_catalogo: function(url, array, source, source_load, extra_logic){
				$http.get(url).then(
					function(response){
						vm.interfaz.llenaCmbDx(array, response.data.results, source, source_load, extra_logic);	
					}, function(response){
						console.log('Error al traer el catálogo.')
					}
				);
			},
			get_catalogo_async: function(url){
				return $http.get(url);
			},
			get_codificado: function (id){
				return $http.get('/get_Codificado/'+ id);
			},
			quita_acentos(cadena){
			   // Quitamos acentos para minúsculas y mayúsculas.
			   cadena = cadena.replace(/á/gi,"a");
			   cadena = cadena.replace(/é/gi,"e");
			   cadena = cadena.replace(/í/gi,"i");
			   cadena = cadena.replace(/ó/gi,"o");
			   cadena = cadena.replace(/ú/gi,"u");
			   cadena = cadena.replace(/Á/gi,"A");
			   cadena = cadena.replace(/É/gi,"E");
			   cadena = cadena.replace(/Í/gi,"I");
			   cadena = cadena.replace(/Ó/gi,"O");
			   cadena = cadena.replace(/Ú/gi,"U");
			   return cadena;
			},
			//Función para buscar un elemento en un array de un data source de devex
			searchInArraySource: function(array, field, value, get_index){
				for(var i = 0; i < array.length; i++)
					if(eval("array[i]." + field + " == value"))
						if(get_index == true)
							return i;
						else
							return array[i];
				return false;
			}, 
			isValidNumber: function(val){
				try{
					if(typeof(val) == "number" && isFinite(val))
						return true;
					else
						return false;
				}catch(e){
					return false;
				}
			},
			isEmptyString: function(string){
				if(!(typeof(string) == 'string') ){
					return true;
				}
				else{
					return string.trim().length == 0;
				}
				
			},
			convertir_decimal_a_sexagesimal: function(latitud, longitud){
				let latGrados, latMinutos, latSegundos, latSentido, 
					lonGrados, lonMinutos, lonSegundos, lonSentido;

				if(latitud){
					let lat = parseFloat(latitud);
					latGrados = Math.abs( Math.floor(Math.abs(lat/1)) );
					latMinutos = Math.abs( Math.floor(Math.abs(lat % 1) * 60) );
					latSegundos = Math.abs( ((Math.abs(lat%1) * 60) % 1) * 60 ).toFixed(4);
					latSentido = lat > 0 ? 'N' : 'S';	
				}
				if(longitud){
					let lon = parseFloat(longitud);
					lonGrados = Math.abs( Math.floor(Math.abs(lon/1)) );
					lonMinutos = Math.abs( Math.floor( Math.abs(lon % 1) * 60) );
					lonSegundos = Math.abs( (( Math.abs(lon%1) * 60) % 1) * 60 ).toFixed(4);
					lonSentido = lon > 0 ? 'E' : 'W';
				}

				return [`${latGrados}° ${latMinutos}' ${latSegundos}'' ${latSentido}`,
						`${lonGrados}° ${lonMinutos}' ${lonSegundos}'' ${lonSentido}`];
			},
			//Este parseo siempre regresa el formato a-m-d
			parseDate: function(date){
				try{
					let mes, dia, fnc_set_dia_mes;
					fnc_set_dia_mes = function(date_fnc){
						mes = date_fnc.getMonth()+1;
						dia = date_fnc.getDate();
						if(mes.toString().length == 1)
							mes = `0${mes}`;
						if(dia.toString().length == 1)
							dia = `0${dia}`;
					}
					if(typeof(date) == 'number'){
						date = new Date(date);
						fnc_set_dia_mes(date)
						return date.getFullYear()+"-"+mes+"-"+ dia;
					}else if(typeof(date) == 'object' && date != null){
						fnc_set_dia_mes(date);
						return date.getFullYear()+"-"+mes+"-"+ dia;
					}else{
						return date;
					}
				}catch(e){
					console.log('Error al intentar parsear la fecha', e);
					return false;
				}
				
			},
			parseErrors: function(errors, outputerror){
				var key, mensaje_error;
				mensaje_error = "";
				if(typeof(errors) == 'string' && errors.length > 250){
						mensaje_error = "Ocurrió un problema con la petición.";
						outputerror.push(mensaje_error);
						console.log(mensaje_error, outputerror);
				}		
				else
					if(typeof(outputerror) == 'object')
						for (key in errors){
							mensaje_error += key + ":   " + errors[key] + ". ";
							outputerror.push(key + ":   " + errors[key]);
							
							
						}
					else
						for (key in errors){
							mensaje_error += key + ": " + errors[key] + ". ";
							
						}
					
				return mensaje_error;
			},
			/**
			* @name range 
			* @desc Función para generar arreglos con rangos específicos.
			* @return Array
			* @memberOf SharedFactory
			*/
			range: function(start, end, step, offset) {
			  var len = (Math.abs(end - start) + ((offset || 0) * 2)) / (step || 1) + 1;
			  var direction = start < end ? 1 : -1;
			  var startingPoint = start - (direction * (offset || 0));
			  var stepSize = direction * (step || 1);
			  
			  return Array(len).fill(0).map(function(_, index) {
			    return startingPoint + (stepSize * index);
			  });
			  
			},
			to_formato_moneda: function(fields_array, $scope){
				for(var i = 0; i < fields_array.length; i++){
					eval("if($scope." + fields_array[i] + " == undefined){$scope." + fields_array[i] + " = 0;}");
					eval("$scope." + fields_array[i] + " = parseFloat($scope." + fields_array[i] +").toLocaleString('es-MX', {minimumFractionDigits: 2});");
				}
			},
			to_formato_numerico: function(fields_array, $scope){
				for(var i = 0; i < fields_array.length; i++){
					eval("if($scope." + fields_array[i] + " == undefined){$scope." + fields_array[i] + " = 0;}");
					eval("$scope." + fields_array[i] + " = $scope." + fields_array[i] + ".toString().replace(/,/g, '');");
				}
			},
			porcentaje_gastos_operacion: porcentaje_gastos_operacion,
			porcentaje_rrc_stop_loss: porcentaje_rrc_stop_loss
		};

		return vm.interfaz;
	}
	
})();