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

    const personaFieldset = Array.from(form.children).find(
        function (elemento) {
            return elemento.tagName === "FIELDSET";
        }
    );

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
    // 3. DETERMINAR EL TIPO DE PERSONA
    // =====================================================

    const rutaActual = window.location.pathname;

    const esPersonaMoral =
        rutaActual.includes("/add/moral/");

    const tituloPersona = esPersonaMoral
        ? "Datos de persona moral"
        : "Datos de persona física";

    // =====================================================
    // 4. CONFIGURAR LAS TRES PESTAÑAS
    // =====================================================

    const panels = [
        {
            title: tituloPersona,
            element: personaFieldset,
        },
        {
            title: "Direcciones",
            element: direcciones,
        },
        {
            title: "Teléfonos",
            element: telefonos,
        },
    ];

    const tabs = document.createElement("div");

    tabs.className = "persona-tabs";
    tabs.setAttribute("role", "tablist");
    tabs.setAttribute("aria-label", "Secciones de persona");

    // =====================================================
    // 5. ACTIVAR PESTAÑA
    // =====================================================

    function activarPestana(indice) {
        panels.forEach(function (panel, i) {
            const activa = i === indice;

            panel.button.classList.toggle("active", activa);

            panel.button.setAttribute(
                "aria-selected",
                String(activa)
            );

            panel.element.hidden = !activa;
        });
    }

    // =====================================================
    // 6. CREAR BOTONES DE LAS PESTAÑAS
    // =====================================================

    panels.forEach(function (panel, indice) {
        const button = document.createElement("button");

        button.type = "button";
        button.className = "persona-tab-button";
        button.textContent = panel.title;

        button.setAttribute("role", "tab");
        button.setAttribute("aria-selected", "false");

        button.addEventListener("click", function () {
            activarPestana(indice);
        });

        panel.button = button;

        tabs.appendChild(button);
    });

    // =====================================================
    // 7. INSERTAR PESTAÑAS Y MOSTRAR LA PRIMERA
    // =====================================================

    form.insertBefore(tabs, form.firstChild);

    activarPestana(0);
});