(function () {
    'use strict';

    angular
        .module('operaciones.operacion.controllers')
        .controller('ComandaPorZona', ComandaPorZonaController);

    ComandaPorZonaController.$inject = ['$scope', '$timeout'];

    function ComandaPorZonaController($scope, $timeout) {
        const vm = this;

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
        const nodo = db.ref('alertas/centro');

        const MAX_CARDS = 18;
        let alertCount = 0;
        const grid = document.getElementById("grid");
        const carousel = document.getElementById("carousel");

        const prediosIniciales = Array.from({ length: 25 }, (_, i) => ({
            id: i + 1,
            ubicacion: "Zona",
            cultivo: "Platillo",
            fecha: new Date().toLocaleDateString(),
            horaCreacion: new Date()
        }));

        const createCard = (predio, mini = false) => {
            const card = document.createElement("div");
            card.className = "tarjeta" + (mini ? " mini" : "");
            card.dataset.id = predio.id;
            card.dataset.segundos = 0;

            const hora = predio.horaCreacion.toLocaleTimeString();

            card.innerHTML = `
                <div class="fw-bold fs-5 mb-1">Predio #${predio.id}</div>
                <div class="text-secondary flex-grow-1">
                  📍 ${predio.ubicacion}<br>
                  🍽️ ${predio.cultivo}<br>
                  📅 ${predio.fecha}<br>
                  🕒 <span class="font-monospace hora">${hora}</span><br>
                  ⏱ <span class="font-monospace segundos">0</span> seg
                </div>
                <div class="mt-2 d-flex gap-1">
                  <button class="btn btn-primary" data-action="ver">Ver</button>
                  <button class="btn btn-success" data-action="mover">Mover</button>
                  <button class="btn btn-danger" data-action="eliminar">Eliminar</button>
                </div>
            `;

            card.querySelectorAll("button").forEach(btn => {
                btn.addEventListener("click", () => {
                    const action = btn.dataset.action;
                    if (action === "ver") showCardID(predio.id);
                    else if (action === "mover") moveCardWithFade(predio.id);
                    else if (action === "eliminar") removeCardWithFade(predio.id);
                });
            });

            return card;
        };

        function showCardID(id) {
            Swal.fire({ icon: 'info', title: `🆔 Predio #${id}`, text: `ID: ${id}`, confirmButtonText: 'Cerrar' });
        }

        function removeCardWithFade(id) {
            const card = grid.querySelector(`div[data-id='${id}']`) || carousel.querySelector(`div[data-id='${id}']`);
            if (!card) return;

            card.classList.add('fade-out');
            $timeout(() => {
                if (grid.contains(card)) grid.removeChild(card);
                else if (carousel.contains(card)) carousel.removeChild(card);

                if (grid.children.length < MAX_CARDS && carousel.children.length) {
                    const next = carousel.children[0];
                    carousel.removeChild(next);
                    next.classList.remove('mini');
                    next.classList.add('fade-in');
                    grid.appendChild(next);
                    $timeout(() => next.classList.remove('fade-in'), 300);
                }
            }, 300);
        }

        async function moveCardWithFade(id) {
            const card = grid.querySelector(`div[data-id='${id}']`);
            if (!card) return;

            const allCards = Array.from(grid.children);
            const maxPos = allCards.length;

            let selectedPosition = null;
            const { value: position } = await Swal.fire({
                title: `Mover Predio #${id}`,
                html: `<div class="d-grid gap-2 mt-3" style="grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));">
                         ${Array.from({ length: maxPos }, (_, i) => `<button class="btn btn-outline-primary num-btn py-3 fs-5">${i+1}</button>`).join('')}
                       </div>`,
                showCancelButton: true,
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancelar',
                didOpen: () => {
                    const buttons = Swal.getHtmlContainer().querySelectorAll(".num-btn");
                    buttons.forEach(btn => {
                        btn.addEventListener("click", () => {
                            buttons.forEach(b => b.classList.remove("btn-primary","text-white"));
                            btn.classList.add("btn-primary","text-white");
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

        function cargarPrediosIniciales() {
            prediosIniciales.forEach(predio => {
                alertCount = Math.max(alertCount, predio.id);
                const mini = grid.children.length >= MAX_CARDS;
                const card = createCard(predio, mini);
                if (!mini) grid.appendChild(card);
                else carousel.appendChild(card);
            });
        }

        nodo.on('value', snapshot => {
            if (!snapshot.val()) return;
            alertCount++;
            const predioNuevo = {
                id: alertCount,
                ubicacion: "Zona",
                cultivo: "Platillo",
                fecha: new Date().toLocaleDateString(),
                horaCreacion: new Date()
            };
            const mini = grid.children.length >= MAX_CARDS;
            const newCard = createCard(predioNuevo, mini);
            if (!mini) {
                grid.appendChild(newCard);
                newCard.classList.add('fade-in');
                $timeout(() => newCard.classList.remove('fade-in'), 300);
            } else {
                carousel.appendChild(newCard);
            }
        });

        cargarPrediosIniciales();

        setInterval(() => {
            document.querySelectorAll(".tarjeta").forEach(card => {
                let segundos = parseInt(card.dataset.segundos) || 0;
                segundos++;
                card.dataset.segundos = segundos;
                card.querySelector(".segundos").textContent = segundos;

                card.classList.remove('alerta-baja','alerta-media','alerta-alta');
                if (segundos >= 45) card.classList.add('alerta-alta');
                else if (segundos >= 30) card.classList.add('alerta-media');
                else card.classList.add('alerta-baja');
            });
        }, 1000);
    }
})();
