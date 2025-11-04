(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers')
        .controller('ReporteTopCinco', ReporteTopCincoController);

    ReporteTopCincoController.$inject = ['$scope', '$timeout'];

    function ReporteTopCincoController($scope, $timeout) {
        const vm = this;
        let BtnHomeOptionsInstance;
        const container = document.getElementById('empresasContainer');

        // Datos de ejemplo
        vm.empresas = [
            {
                empresa: 'Frutales del Norte',
                top_5_productos: [
                    { producto__nombre: 'Manzana Roja', cantidad_total: 340 },
                    { producto__nombre: 'Cueritos', cantidad_total: 280 },
                    { producto__nombre: 'Refresco 600ml', cantidad_total: 260 },
                    { producto__nombre: 'Palomitas', cantidad_total: 180 },
                    { producto__nombre: 'Papas Fritas', cantidad_total: 150 }
                ]
            },
            {
                empresa: 'Distribuidora del Valle',
                top_5_productos: [
                    { producto__nombre: 'Avena', cantidad_total: 200 },
                    { producto__nombre: 'Manzana Verde', cantidad_total: 170 },
                    { producto__nombre: 'Frijol Pinto', cantidad_total: 160 },
                    { producto__nombre: 'Maíz Amarillo', cantidad_total: 140 },
                    { producto__nombre: 'Cueritos', cantidad_total: 130 }
                ]
            },
            {
                empresa: 'Distribuidora del Valle',
                top_5_productos: [
                    { producto__nombre: 'Avena', cantidad_total: 200 },
                    { producto__nombre: 'Manzana Verde', cantidad_total: 170 },
                    { producto__nombre: 'Frijol Pinto', cantidad_total: 160 },
                    { producto__nombre: 'Maíz Amarillo', cantidad_total: 140 },
                    { producto__nombre: 'Cueritos', cantidad_total: 130 }
                ]
            },
            // Agregar más empresas si es necesario
        ];

        // Renderiza todas las empresas
        function renderEmpresas() {
            container.innerHTML = '';

            vm.empresas.forEach((empresaObj, index) => {
                const card = document.createElement('div');
                card.className = 'card animate__animated';
                card.style.borderRadius = '2rem';       // Más redondeadas
                card.style.padding = '2.5rem';
                card.style.background = 'linear-gradient(180deg, #ff9a76, #ff6f50)';
                card.style.boxShadow = '0 16px 50px rgba(0,0,0,0.5)';

                // Título de la empresa
                const empresaTitle = `<h2 class="empresa-titulo">${empresaObj.empresa}</h2>`;

                // Productos con estrellas
                const productosHTML = empresaObj.top_5_productos.map((p, i) => {
                    const estrellas = '⭐'.repeat(5 - i);
                    return `
                        <div class="producto-item" style="border-radius: 1.5rem; padding:1.2rem; box-shadow:0 6px 20px rgba(0,0,0,0.25); transition: transform 0.3s ease, background 0.3s ease;">
                            <div class="flex justify-between items-center mb-2">
                                <span class="font-semibold text-lg">${i + 1}. ${p.producto__nombre}</span>
                                <span class="text-sm text-gray-700">${p.cantidad_total} ventas</span>
                            </div>
                            <div class="flex mt-1 overflow-hidden">
                                ${estrellas.split('').map(s => `<span class="star">${s}</span>`).join('')}
                            </div>
                        </div>
                    `;
                }).join('');

                card.innerHTML = empresaTitle + productosHTML;
                container.appendChild(card);

                // Animación escalonada y más suave
                $timeout(() => {
                    card.classList.add('animate__fadeInUp');
                    card.style.setProperty('--animate-duration', '0.9s');
                    card.style.setProperty('--animate-delay', `${index * 0.15}s`);
                }, 50);
            });
        }

        renderEmpresas();

        // Botón Home mejorado
        vm.button = {
            BtnHomeOptions: {
                icon: 'fa fa-home',
                type: 'success',
                width: 110,
                hint: 'Ir al Inicio',
                showTooltip: true,
                disabled: false,
                onInitialized: function (e) {
                    BtnHomeOptionsInstance = e.component;
                },
                onClick: function () {
                    window.location.href = '/';
                }
            },
        }
    }
})();
