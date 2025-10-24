(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers')
        .controller('ComandaPorZona', ComandaPorZonaController);

    ComandaPorZonaController.$inject = ['$http', '$scope', '$timeout'];

    function ComandaPorZonaController($http, $scope, $timeout) {
        const vm = this;
        var arrayComandas = [];
        var zonaSeleccionada = null;

        vm.empresaId = $scope.empresaId;
        vm.nombrePersonal = $scope.nombrePersonal;
        vm.corteCajaId = $scope.corteCajaId;

        const firebaseConfig = {
            apiKey: "AIzaSyCOmQFHQlVFPIiBUyx1k7eshNW4JM-Z-rg",
            authDomain: "signals-test-lasser.firebaseapp.com",
            projectId: "signals-test-lasser",
            storageBucket: "signals-test-lasser.appspot.com",
            messagingSenderId: "901814785470",
            appId: "1:901814785470:web:221e517efbd5f4a40d15ef",
            databaseURL: "https://signals-test-lasser-default-rtdb.firebaseio.com"
        };

        firebase.initializeApp(firebaseConfig);
        const db = firebase.database();
        //   const nodo = db.ref('alertas/centro');

        const MAX_CARDS = 18;
        let alertCount = 0;
        const grid = document.getElementById("grid");
        const carousel = document.getElementById("carousel");

        // ========================
        // Función para convertir segundos a hh:mm:ss
        // ========================
        function formatTime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = seconds % 60;
            return [h, m, s].map(unit => String(unit).padStart(2, '0')).join(':');
        }

        // ========================
        // Función para traer comandas
        // ========================
        function getComandasPendientes() {
            $scope.isLoadPanelVisible = true;
            console.log(zonaSeleccionada);
            const url = "/comandas_pendientes/";
            $http.get(url, { params: { zona: zonaSeleccionada, estado: 1, corteCaja: vm.corteCajaId, } })
                .then(function (response) {
                    arrayComandas.length = 0;
                    grid.innerHTML = "";
                    carousel.innerHTML = "";

                    for (let i = 0; i < response.data.length; i++) {
                        const item = response.data[i];

                        // Parse hora_inicial como fecha de hoy para calcular segundos transcurridos
                        const [h, m, s] = item.hora_inicial.split(':');
                        const horaCreacion = new Date();
                        horaCreacion.setHours(parseInt(h), parseInt(m), parseInt(s), 0);

                        arrayComandas.push({
                            id: item.id,
                            zona: item.zona || "Zona",
                            platillo: item.producto || "Platillo",
                            fecha: item.fecha || new Date().toLocaleDateString(),
                            horaCreacion: horaCreacion,
                            venta_id: item.venta_id,
                            desglose_venta: item.desglose_venta,
                            estado: item.estado,
                        });

                        alertCount = Math.max(alertCount, item.id);
                    }

                    if (arrayComandas.length > 0) {
                        cargarPrediosIniciales();
                    }

                    $scope.isLoadPanelVisible = false;

                }, function (error) {
                    console.error("Error cargando predios:", error);
                    $scope.isLoadPanelVisible = false;
                });
        }

        // ========================
        // Función para crear tarjeta
        // ========================
        const createCard = (comanda, mini = false) => {
            const card = document.createElement("div");
            card.className = "tarjeta" + (mini ? " mini" : "");
            card.dataset.id = comanda.id;

            const ahora = new Date();
            const segundosTranscurridos = Math.floor((ahora - comanda.horaCreacion) / 1000);
            card.dataset.segundos = segundosTranscurridos;

            const hora = comanda.horaCreacion.toLocaleTimeString();

            if (mini) {
                card.innerHTML = `
                    <div class="fw-bold">C#${comanda.venta_id} - E# ${comanda.desglose_venta || ""}</div>
                    <div class="text-secondary">
                        🍽️ ${comanda.platillo}<br>
                        🕒 ${hora}<br>
                        ⏱ <span class="font-monospace segundos">${formatTime(segundosTranscurridos)}</span>
                    </div>
                `;
            } else {
                card.innerHTML = `
                    <div class="fw-bold fs-5 mb-1">Com.#${comanda.venta_id} - Ele.# ${comanda.desglose_venta || ""}</div>
                    <div class="text-secondary flex-grow-1">
                        📍 ${comanda.zona},  ${comanda.estado}<br>
                        🍽️ ${comanda.platillo}<br>
                        📅 ${comanda.fecha}<br>
                        🕒 <span class="font-monospace hora">${hora}</span><br>
                        🕒 <span class="font-monospace segundos">${formatTime(segundosTranscurridos)}</span><br>
                       
                    </div>
                    <div class="mt-2 d-flex gap-1">
                        <button class="btn btn-primary" data-action="ver">Estado</button>
                        <button class="btn btn-success" data-action="mover">Mover</button>
                        <button class="btn btn-danger" data-action="eliminar">Cancelar</button>
                    </div>
                `;

                card.querySelectorAll("button").forEach(btn => {
                    btn.addEventListener("click", () => {
                        const action = btn.dataset.action;
                        if (action === "ver") showCardID(comanda.id);
                        else if (action === "mover") moveCardWithFade(comanda.id);
                        else if (action === "eliminar") modificarEstadoNotificacion(comanda.id);
                    });
                });
            }

            return card;
        };

        // ========================
        // Función para mostrar ID
        // ========================
        function showCardID(id) {
            Swal.fire({
                title: `🆔 Pedido #${id}`,
                html: `
            <p>Selecciona una acción:</p>
            <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
                <button id="btnPendiente" class="swal2-confirm swal2-styled" style="background-color:#ff861c;">Pendiente</button>
                <button id="btnProceso" class="swal2-confirm swal2-styled" style="background-color:#4e73df;">En proceso</button>
                <button id="btnTerminado" class="swal2-confirm swal2-styled" style="background-color:#1cc88a;">Terminado</button>
            </div>
        `,
                showConfirmButton: false,
                allowOutsideClick: false,
                allowEscapeKey: true,
                width: 400,
                didOpen: () => {
                    const btnPendiente = document.getElementById('btnPendiente');
                    const btnProceso = document.getElementById('btnProceso');
                    const btnTerminado = document.getElementById('btnTerminado');

                    btnPendiente.addEventListener('click', () => {
                        Swal.close();
                        marcarPendiente(id, 1);
                    });
                    btnProceso.addEventListener('click', () => {
                        Swal.close();
                        marcarProceso(id, 2);
                    });
                    btnTerminado.addEventListener('click', () => {
                        Swal.close();
                        marcarTerminado(id, 3);
                    });
                }
            });
        }

        function marcarPendiente(id, estado) {
            modificarEstado(id, estado);
        }
        function marcarProceso(id, estado) {
            modificarEstado(id, estado);
        }
        function marcarTerminado(id, estado) {
            modificarEstado(id, estado);
        }
        // ========================
        // Mover tarjeta con fade
        // ========================
        async function moveCardWithFade(id) {
            const card = grid.querySelector(`div[data-id='${id}']`);
            if (!card) return;

            const allCards = Array.from(grid.children);
            const maxPos = allCards.length;
            let selectedPosition = null;

            const { value: position } = await Swal.fire({
                title: `Mover Predio #${id}`,
                html: `<div class="d-grid gap-2 mt-3" style="grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));">
                        ${Array.from({ length: maxPos }, (_, i) => `<button class="btn btn-outline-primary num-btn py-3 fs-5">${i + 1}</button>`).join('')}
                       </div>`,
                showCancelButton: true,
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancelar',
                didOpen: () => {
                    const buttons = Swal.getHtmlContainer().querySelectorAll(".num-btn");
                    buttons.forEach(btn => {
                        btn.addEventListener("click", () => {
                            buttons.forEach(b => b.classList.remove("btn-primary", "text-white"));
                            btn.classList.add("btn-primary", "text-white");
                            selectedPosition = parseInt(btn.textContent);
                        });
                    });
                },
                preConfirm: () => {
                    if (!selectedPosition) Swal.showValidationMessage('Selecciona un número');
                    return selectedPosition;
                }
            });

            if (!position) return;

            card.classList.add('fade-out');
            $timeout(() => {
                grid.removeChild(card);
                const insertIndex = Math.min(position - 1, grid.children.length);
                if (insertIndex >= grid.children.length) grid.appendChild(card);
                else grid.insertBefore(card, grid.children[insertIndex]);
                card.classList.remove('fade-out');
                card.classList.add('fade-in');
                $timeout(() => card.classList.remove('fade-in'), 300);
            }, 300);
        }

        function modificarEstadoNotificacion(id) {
            Swal.fire({
                title: '¿Cancelar pedido?',
                text: 'Esta acción marcará el pedido como cancelado.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, cancelar',
                cancelButtonText: 'No',
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    const popup = Swal.getPopup();
                    if (popup) {
                        popup.style.fontSize = '1.2rem';
                        popup.style.padding = '2rem';
                        popup.style.width = '400px';
                    }

                    const confirmBtn = Swal.getConfirmButton();
                    const cancelBtn = Swal.getCancelButton();

                    if (confirmBtn) {
                        confirmBtn.style.fontSize = '1.5rem';
                        confirmBtn.style.padding = '0.75rem 2rem';
                    }
                    if (cancelBtn) {
                        cancelBtn.style.fontSize = '1.5rem';
                        cancelBtn.style.padding = '0.75rem 2rem';
                    }
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    const inventario_json = { estado: 4 };
                    $http({
                        method: 'PATCH',
                        data: inventario_json,
                        url: "/api/v1/notificacionZona/" + id + "/"
                    }).then(
                        function (response) {
                            removeCardWithFade(id);
                            Swal.fire({
                                icon: 'success',
                                title: 'Cancelada',
                                text: 'El pedido fue cancelado correctamente.',
                                timer: 2000,
                                showConfirmButton: false
                            });
                        },
                        function (response) {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'No se pudo cancelar el pedido.'
                            });
                        }
                    );
                }
            });
        }
        function modificarEstado(id, estado) {
            const inventario_json = { estado: estado };
            $http({
                method: 'PATCH',
                data: inventario_json,
                url: "/api/v1/notificacionZona/" + id + "/"
            }).then(
                function (response) {
                    getComandasPendientes();
                },
                function (response) {

                }
            );
        }


        // ========================
        // Eliminar tarjeta con fade
        // ========================
        function removeCardWithFade(id) {
            // modificarEstadoNotificacion(id);
            const card = grid.querySelector(`div[data-id='${id}']`) || carousel.querySelector(`div[data-id='${id}']`);
            if (!card) return;

            card.classList.add('fade-out');
            $timeout(() => {
                if (grid.contains(card)) grid.removeChild(card);
                else if (carousel.contains(card)) carousel.removeChild(card);

                // Mover tarjeta del carrusel al grid si hay espacio
                if (grid.children.length < MAX_CARDS && carousel.children.length) {
                    const nextMiniCard = carousel.children[0];
                    const comandaId = parseInt(nextMiniCard.dataset.id);
                    const comanda = arrayComandas.find(c => c.id === comandaId);
                    if (comanda) {
                        const cardGrande = createCard(comanda, false);
                        carousel.removeChild(nextMiniCard);
                        cardGrande.classList.add('fade-in');
                        grid.appendChild(cardGrande);
                        $timeout(() => cardGrande.classList.remove('fade-in'), 300);
                    }
                }
            }, 300);
        }

        // ========================
        // Cargar inicial tarjetas
        // ========================
        function cargarPrediosIniciales() {
            arrayComandas.forEach(predio => {
                alertCount = Math.max(alertCount, predio.id);
                const mini = grid.children.length >= MAX_CARDS;
                const card = createCard(predio, mini);
                if (!mini) grid.appendChild(card);
                else carousel.appendChild(card);
            });
        }

        // ========================
        // Firebase: escuchar cambios
        // ========================
        // let lastValorMensaje = null;
        //  nodo.child('mensaje').on('value', snapshot => {
        //    const nuevoValor = snapshot.val();
        //  if (nuevoValor !== null && nuevoValor !== lastValorMensaje) {
        //    lastValorMensaje = nuevoValor;
        //  getComandasPendientes();
        // }
        //});
        let lastValorMensaje = null;
        const nodo = db.ref('alertas/' + vm.empresaId + '/');
        nodo.child('mensaje').on('value', snapshot => {
            const nuevoValor = snapshot.val();
            if (nuevoValor !== null && nuevoValor !== lastValorMensaje) {
                lastValorMensaje = nuevoValor;

                // 👇 Cambio aquí:
                if (zonaSeleccionada) {
                    getComandasPendientes(zonaSeleccionada);
                }
            }
        });
        // ========================
        // Actualizar segundos y colores
        // ========================
        setInterval(() => {
            document.querySelectorAll(".tarjeta").forEach(card => {
                let segundos = parseInt(card.dataset.segundos) || 0;
                segundos++;
                card.dataset.segundos = segundos;
                const segEl = card.querySelector(".segundos");
                if (segEl) segEl.textContent = formatTime(segundos);

                card.classList.remove('alerta-baja', 'alerta-media', 'alerta-alta');
                if (segundos >= 45) card.classList.add('alerta-alta');
                else if (segundos >= 30) card.classList.add('alerta-media');
                else card.classList.add('alerta-baja');
            });
        }, 1000);

        // ========================
        // Inicializar
        // ========================
        // ========================
        // SweetAlert para seleccionar zona
        // ========================
        function seleccionarZona() {
            $http.get('/api/v1/zonaNotificacion/activos/')  // endpoint que devuelve las zonas
                .then(function (response) {
                    if (response.data && response.data.length) {
                        // Mapear a objeto {id: nombre} para SweetAlert
                        const inputOptions = {};
                        response.data.forEach(z => {
                            inputOptions[z.id] = z.nombre;
                        });

                        // Mostrar SweetAlert select
                        Swal.fire({
                            title: 'Selecciona la zona',
                            input: 'select',
                            inputOptions: inputOptions,
                            inputPlaceholder: 'Elige una zona',
                            confirmButtonText: 'Aceptar',
                            showCancelButton: false,
                            allowOutsideClick: false,
                            allowEscapeKey: false,
                            inputValidator: (value) => {
                                if (!value) {
                                    return 'Debes seleccionar al menos una zona';
                                }
                            }
                        }).then(result => {
                            if (result.value) {
                                zonaSeleccionada = result.value;
                                getComandasPendientes();
                            }
                        });

                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'No se encontraron zonas disponibles.'
                        });
                    }
                }, function (error) {
                    console.error("Error al cargar zonas", error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'No se pudieron cargar las zonas.'
                    });
                });
        }


        seleccionarZona();
        //  getComandasPendientes();
    }
})();
