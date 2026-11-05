
(function ($) {
    "use strict";

    $(document).ready(function () {

        // =========================================================
        // 1. ELEMENTOS DEL FORMULARIO
        // =========================================================

        const loteSelect = document.getElementById("id_lote_huerta");
        const variedadSelect = document.getElementById("id_variedad");

        const maximoContainer = document.querySelector(
            ".field-maximo_cajones .readonly"
        );

        if (!loteSelect || !variedadSelect || !$) {
            return;
        }

        const URL_VARIEDADES =
            "/admin/operaciones/loteempaque/variedades-disponibles/";

        let solicitudActual = 0;
        let controlador = null;

        let ultimoLoteDetectado = null;
        let ultimaVariedadDetectada = null;

        // =========================================================
        // 2. MENSAJES DEL FORMULARIO
        // =========================================================

        function mostrarMensaje(texto, error = false) {

            let elemento = document.getElementById(
                "mensaje-variedades-disponibles"
            );

            if (!elemento) {
                elemento = document.createElement("p");
                elemento.id = "mensaje-variedades-disponibles";
                elemento.style.marginTop = "6px";
                elemento.style.fontSize = "12px";

                variedadSelect.parentNode.appendChild(elemento);
            }

            elemento.textContent = texto;
            elemento.style.color = error ? "#ba2121" : "#666";
        }

        function limpiarMensaje() {

            const elemento = document.getElementById(
                "mensaje-variedades-disponibles"
            );

            if (elemento) {
                elemento.remove();
            }
        }

        // =========================================================
        // 3. ACTUALIZAR MÁXIMO DE CAJONES
        // =========================================================

        function actualizarMaximoCajones() {

            const opcion = variedadSelect.selectedOptions[0];

            if (!opcion || !opcion.value) {
                if (maximoContainer) {
                    maximoContainer.textContent = "0";
                }
                return;
            }

            const maximo = Number(opcion.dataset.maximo || 0);

            if (maximoContainer) {
                maximoContainer.textContent =
                    maximo.toLocaleString("es-MX");
            }
        }

        // =========================================================
        // 4. DETECTAR CAMBIOS DE VARIEDAD
        // =========================================================

        function procesarCambioVariedad() {

            const variedadId = String(
                variedadSelect.value || ""
            );

            if (variedadId === ultimaVariedadDetectada) {
                return;
            }

            ultimaVariedadDetectada = variedadId;

            actualizarMaximoCajones();
        }

        variedadSelect.addEventListener(
            "change",
            procesarCambioVariedad
        );

        $(variedadSelect).on(
            "select2:select.loteEmpaque",
            procesarCambioVariedad
        );

        $(variedadSelect).on(
            "select2:clear.loteEmpaque",
            procesarCambioVariedad
        );

        // =========================================================
        // 5. SINCRONIZAR SELECT2 CON EL SELECTOR NATIVO
        // =========================================================

        function sincronizarVariedad() {
            $(variedadSelect).trigger("change");
        }

        // =========================================================
        // 6. LIMPIAR VARIEDADES Y MÁXIMO
        // =========================================================

        function limpiarVariedades() {

            variedadSelect.replaceChildren();

            variedadSelect.add(
                new Option("---------", "")
            );

            variedadSelect.value = "";

            ultimaVariedadDetectada = "";

            sincronizarVariedad();
            actualizarMaximoCajones();
        }

        // =========================================================
        // 7. CANCELAR CONSULTAS ANTERIORES
        // =========================================================

        function cancelarConsulta() {

            solicitudActual++;

            if (controlador) {
                controlador.abort();
                controlador = null;
            }
        }

        // =========================================================
        // 8. DETECTAR CAMBIOS DE LOTE
        // =========================================================

        function procesarCambioLote(loteId) {

            loteId = String(loteId || "").trim();

            if (loteId === ultimoLoteDetectado) {
                return;
            }

            ultimoLoteDetectado = loteId;

            if (!loteId) {

                cancelarConsulta();
                limpiarVariedades();
                limpiarMensaje();

                return;
            }

            cargarVariedades(loteId);
        }

        // =========================================================
        // 9. CONSULTAR VARIEDADES DISPONIBLES
        // =========================================================

        async function cargarVariedades(loteId) {

            cancelarConsulta();

            const solicitud = solicitudActual;

            limpiarVariedades();
            limpiarMensaje();

            const nuevoControlador = new AbortController();
            controlador = nuevoControlador;

            variedadSelect.disabled = true;

            try {

                const url = new URL(
                    URL_VARIEDADES,
                    window.location.origin
                );

                url.searchParams.set("lote_id", loteId);

                const respuesta = await fetch(url.toString(), {
                    method: "GET",
                    credentials: "same-origin",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    signal: nuevoControlador.signal
                });

                if (!respuesta.ok) {
                    throw new Error(
                        "Error HTTP " + respuesta.status
                    );
                }

                const datos = await respuesta.json();

                // Ignorar respuestas de consultas anteriores.
                if (solicitud !== solicitudActual) {
                    return;
                }

                if (datos.error) {
                    throw new Error(datos.error);
                }

                if (!Array.isArray(datos.variedades)) {
                    throw new Error(
                        "La respuesta de variedades no es válida."
                    );
                }

                // Crear opciones del selector nativo.
                variedadSelect.replaceChildren();

                variedadSelect.add(
                    new Option("---------", "")
                );

                datos.variedades.forEach(function (item) {

                    const opcion = new Option(
                        String(item.nombre),
                        String(item.id)
                    );

                    // El máximo viaja en la opción.
                    // No se necesita otra consulta AJAX.
                    opcion.dataset.maximo = String(
                        item.maximo_cajones
                    );

                    variedadSelect.add(opcion);
                });

                variedadSelect.value = "";
                ultimaVariedadDetectada = "";

                sincronizarVariedad();
                actualizarMaximoCajones();

                if (datos.variedades.length) {

                    mostrarMensaje(
                        `${datos.variedades.length} variedad(es) disponible(s).`
                    );

                } else {

                    mostrarMensaje(
                        "No hay variedades disponibles para este lote.",
                        true
                    );
                }

            } catch (error) {

                if (
                    error.name !== "AbortError" &&
                    solicitud === solicitudActual
                ) {

                    ultimoLoteDetectado = null;

                    mostrarMensaje(error.message, true);
                }

            } finally {

                if (solicitud === solicitudActual) {

                    variedadSelect.disabled = false;

                    sincronizarVariedad();
                    actualizarMaximoCajones();

                    if (controlador === nuevoControlador) {
                        controlador = null;
                    }
                }
            }
        }

        // =========================================================
        // 10. EVENTOS DEL SELECTOR DE LOTE
        // =========================================================

        $(loteSelect).off(".loteEmpaque");

        $(loteSelect).on(
            "change.loteEmpaque",
            function () {
                procesarCambioLote(this.value);
            }
        );

        $(loteSelect).on(
            "select2:select.loteEmpaque",
            function (evento) {

                const id =
                    evento.params?.data?.id || this.value;

                procesarCambioLote(id);
            }
        );

        $(loteSelect).on(
            "select2:clear.loteEmpaque",
            function () {
                procesarCambioLote("");
            }
        );

        // =========================================================
        // 11. VIGILANCIA AUTOMÁTICA DE LOS SELECTORES
        // =========================================================

        function comprobarSeleccionLote() {

            const valor = String(
                loteSelect.value || ""
            ).trim();

            if (valor !== ultimoLoteDetectado) {
                procesarCambioLote(valor);
            }
        }

        function comprobarSeleccionVariedad() {

            const valor = String(
                variedadSelect.value || ""
            );

            if (valor !== ultimaVariedadDetectada) {
                procesarCambioVariedad();
            }
        }

        // =========================================================
        // 12. CORRECCIÓN DE FOCO EN SELECT2
        // =========================================================

        function corregirFocoSelect2(select) {

            if (!select) {
                return;
            }

            function retirarFocoSiEstaOculto() {

                const oculto =
                    select.getAttribute("aria-hidden") === "true";

                if (
                    oculto &&
                    document.activeElement === select
                ) {
                    select.blur();
                }
            }

            // Revisar después de la inicialización de Select2.
            requestAnimationFrame(function () {
                requestAnimationFrame(retirarFocoSiEstaOculto);
            });

            // Vigilar cambios de accesibilidad del selector.
            const observador = new MutationObserver(
                retirarFocoSiEstaOculto
            );

            observador.observe(select, {
                attributes: true,
                attributeFilter: [
                    "aria-hidden",
                    "class",
                    "tabindex"
                ]
            });

            // Evitar conservar el foco en el selector nativo oculto.
            select.addEventListener(
                "focus",
                retirarFocoSiEstaOculto
            );

            // Liberar el observador al abandonar la página.
            window.addEventListener(
                "pagehide",
                function () {
                    observador.disconnect();
                },
                { once: true }
            );
        }

        corregirFocoSelect2(loteSelect);
        corregirFocoSelect2(variedadSelect);

        // =========================================================
        // 13. INICIALIZACIÓN
        // =========================================================

        limpiarVariedades();
        limpiarMensaje();

        comprobarSeleccionLote();
        comprobarSeleccionVariedad();

        // Se conserva la vigilancia que resolvió el problema
        // de detección de cambios de Select2.
        const intervaloVigilancia = setInterval(function () {

            comprobarSeleccionLote();
            comprobarSeleccionVariedad();

        }, 250);

        // Liberar recursos.
        window.addEventListener(
            "pagehide",
            function () {

                clearInterval(intervaloVigilancia);
                cancelarConsulta();

            },
            { once: true }
        );

    });

})(
    window.django && window.django.jQuery
        ? window.django.jQuery
        : window.jQuery
);
