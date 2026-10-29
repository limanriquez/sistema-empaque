document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#persona_form");

    if (!form) {
        return;
    }

    // =====================================================
    // 1. DESACTIVAR AUTOCOMPLETADO
    // =====================================================

    form.setAttribute("autocomplete", "off");

    function desactivarAutocompletado(contenedor) {
        if (
            !contenedor ||
            contenedor.nodeType !== Node.ELEMENT_NODE
        ) {
            return;
        }

        const selector = "input, textarea, select";
        const campos = [];

        if (contenedor.matches(selector)) {
            campos.push(contenedor);
        }

        campos.push(
            ...contenedor.querySelectorAll(selector)
        );

        campos.forEach(function (campo) {
            campo.setAttribute("autocomplete", "off");

            if (
                campo.tagName === "INPUT" ||
                campo.tagName === "TEXTAREA"
            ) {
                campo.setAttribute("autocorrect", "off");
                campo.setAttribute("autocapitalize", "off");
                campo.setAttribute("spellcheck", "false");
            }
        });
    }

    desactivarAutocompletado(form);

    // Aplicar también a direcciones y teléfonos nuevos.
    const observador = new MutationObserver(function (mutaciones) {
        mutaciones.forEach(function (mutacion) {
            mutacion.addedNodes.forEach(function (nodo) {
                desactivarAutocompletado(nodo);
            });
        });
    });

    observador.observe(form, {
        childList: true,
        subtree: true,
    });

    // =====================================================
    // 2. LOCALIZAR LAS SECCIONES
    // =====================================================

    // Primer fieldset que no pertenece a un inline: son los
    // datos de la persona.
    const personaFieldset = Array.from(
        form.querySelectorAll("fieldset")
    ).find(function (fieldset) {
        return !fieldset.closest(".inline-group");
    });

    const direcciones =
        form.querySelector("#direcciones-group");

    const telefonos =
        form.querySelector("#telefonos-group");

    if (!personaFieldset || !direcciones || !telefonos) {
        console.error(
            "No se encontraron todos los paneles. " +
            "Verifica los IDs HTML de los inlines de Django.",
            {
                personaFieldset,
                direcciones,
                telefonos,
            }
        );

        return;
    }

    // =====================================================
    // 3. TÍTULO DE LA PESTAÑA DE PERSONA
    // =====================================================

    // Se toma del encabezado del fieldset, que ya define el
    // admin ("Datos de persona física" o "Datos de persona moral")
    // tanto en alta como en edición.
    const encabezado = personaFieldset.querySelector("h2, legend");
    const esAltaMoral = window.location.pathname.includes("/add/moral/");

    const tituloPersona =
        (encabezado && encabezado.textContent.trim()) ||
        (esAltaMoral
            ? "Datos de persona moral"
            : "Datos de persona física");

    // =====================================================
    // 4. CONFIGURAR LAS TRES PESTAÑAS
    // =====================================================

    const panels = [
        {
            title: tituloPersona,
            element: personaFieldset,
            id: personaFieldset.id || "persona-datos-panel",
        },
        {
            title: "Direcciones",
            element: direcciones,
            id: direcciones.id,
        },
        {
            title: "Teléfonos",
            element: telefonos,
            id: telefonos.id,
        },
    ];

    const tabs = document.createElement("div");

    tabs.className = "persona-tabs";
    tabs.setAttribute("role", "tablist");
    tabs.setAttribute("aria-label", "Secciones de persona");

    // =====================================================
    // 5. ACTIVAR PESTAÑA
    // =====================================================

    function activarPestana(indice, enfocar) {
        panels.forEach(function (panel, i) {
            const activa = i === indice;

            panel.button.classList.toggle("active", activa);

            panel.button.setAttribute(
                "aria-selected",
                String(activa)
            );

            panel.button.tabIndex = activa ? 0 : -1;

            panel.element.hidden = !activa;
        });

        if (enfocar) {
            panels[indice].button.focus();
        }
    }

    // =====================================================
    // 6. CREAR BOTONES DE LAS PESTAÑAS
    // =====================================================

    panels.forEach(function (panel, indice) {
        const button = document.createElement("button");

        button.type = "button";
        button.id = "persona-tab-" + indice;
        button.className = "persona-tab-button";
        button.textContent = panel.title;

        button.setAttribute("role", "tab");
        button.setAttribute("aria-selected", "false");
        button.setAttribute("aria-controls", panel.id);

        button.addEventListener("click", function () {
            activarPestana(indice, false);
        });

        // Navegación con el teclado: flechas, Inicio y Fin.
        button.addEventListener("keydown", function (evento) {
            let destino = null;

            if (evento.key === "ArrowRight") {
                destino = (indice + 1) % panels.length;
            } else if (evento.key === "ArrowLeft") {
                destino = (indice - 1 + panels.length) % panels.length;
            } else if (evento.key === "Home") {
                destino = 0;
            } else if (evento.key === "End") {
                destino = panels.length - 1;
            }

            if (destino !== null) {
                evento.preventDefault();
                activarPestana(destino, true);
            }
        });

        panel.button = button;

        panel.element.id = panel.id;
        panel.element.setAttribute("role", "tabpanel");
        panel.element.setAttribute("aria-labelledby", button.id);

        tabs.appendChild(button);
    });

    // =====================================================
    // 7. INSERTAR PESTAÑAS Y MOSTRAR LA INICIAL
    // =====================================================

    form.insertBefore(tabs, form.firstChild);

    // Si el servidor devolvió errores de validación, abrir la
    // primera pestaña que los contenga para que no queden ocultos.
    const indiceConError = panels.findIndex(function (panel) {
        return panel.element.querySelector(".errorlist, .errors");
    });

    activarPestana(indiceConError >= 0 ? indiceConError : 0, false);

    // =====================================================
    // 8. VALIDACIÓN NATIVA DEL NAVEGADOR
    // =====================================================

    // Si un campo obligatorio está vacío en una pestaña oculta, el
    // navegador no puede enfocarlo. Se abre la pestaña del primer
    // campo inválido antes de que intente hacerlo.
    let invalidoManejado = false;

    form.addEventListener(
        "invalid",
        function (evento) {
            if (invalidoManejado) {
                return;
            }

            invalidoManejado = true;

            setTimeout(function () {
                invalidoManejado = false;
            }, 0);

            const indice = panels.findIndex(function (panel) {
                return panel.element.contains(evento.target);
            });

            if (indice >= 0) {
                activarPestana(indice, false);
            }
        },
        true
    );
});