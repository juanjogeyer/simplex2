// Estado global del tipo de modelo (maximización / minimización)
let tipoModelo = "max";

/* ============================================================
   EVENTOS PRINCIPALES
============================================================ */
document.addEventListener("DOMContentLoaded", () => {
    inicializarEventos();
    inicializarInterfaz();
    restaurarDatosPrevios();
});

/* ============================================================
   INICIALIZACIÓN
============================================================ */

/**
 * Configura todos los listeners iniciales de botones y entradas.
 */
function inicializarEventos() {
    const btnAgregar = document.getElementById("btnAgregar");
    const btnResolver = document.getElementById("btnResolver");
    const btnVerGrafico = document.getElementById("btnVerGrafico");
    const btnMax = document.getElementById("btnMax");
    const btnMin = document.getElementById("btnMin");
    const inputVariables = document.getElementById("numVariables");

    // Alternar tipo de modelo (Max / Min)
    btnMax.addEventListener("click", () => alternarModelo("max", btnMax, btnMin));
    btnMin.addEventListener("click", () => alternarModelo("min", btnMin, btnMax));

    // Agregar nueva restricción
    btnAgregar.addEventListener("click", agregarRestriccion);

    // Actualizar cuando cambia la cantidad de variables
    inputVariables.addEventListener("change", () => {
        renderFuncionObjetivo();
        actualizarRestricciones();
        ocultarResultado();
        // Ocultar botón gráfico hasta la próxima resolución
        const grafBtn = document.getElementById("btnVerGrafico");
        const extra = document.getElementById("accionesExtra");
        if (grafBtn && extra) {
            grafBtn.style.display = "none";
            extra.classList.add("hidden");
        }
    });

    // Resolver el problema
    btnResolver.addEventListener("click", solveProblem);

    // Ver gráfico
    if (btnVerGrafico) {
        btnVerGrafico.addEventListener("click", async () => {
            try {
                const data = prepareRequestData();
                if (data.C.length !== 2) return; // Seguridad
                const resp = await fetch("/simplex/generate-graph-html", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
                const html = await resp.text();
                if (!resp.ok) throw new Error(html || "No se pudo generar gráfico");
                const win = window.open("about:blank", "_blank");
                if (win) {
                    win.document.write(html);
                    win.document.close();
                }
            } catch (e) {
                console.error("Error mostrando gráfico:", e);
            }
        });
    }

    // Validación dinámica de entradas numéricas
    document.addEventListener("input", validarEntradaNumerica);
}

/**
 * Renderiza los elementos iniciales en la interfaz.
 */
function inicializarInterfaz() {
    renderFuncionObjetivo();
    actualizarRestricciones();
}

/* ============================================================
   FUNCIONES DE INTERFAZ
============================================================ */

/**
 * Alterna el tipo de modelo entre MAX y MIN, actualizando estilos.
 */
function alternarModelo(tipo, btnActivo, btnInactivo) {
    tipoModelo = tipo;
    btnActivo.classList.replace("btn-secondary", "btn-primary");
    btnInactivo.classList.replace("btn-primary", "btn-secondary");
    renderFuncionObjetivo();
}

/**
 * Renderiza la función objetivo según el número de variables y tipo de modelo.
 */
function renderFuncionObjetivo() {
    const contenedor = document.getElementById("funcionObjetivo");
    const numVariables = parseInt(document.getElementById("numVariables").value, 10);
    contenedor.innerHTML = "";

    const label = document.createElement("label");
    label.textContent = tipoModelo === "max" ? "Maximizar Z = " : "Minimizar Z = ";
    label.className = "input-label";
    contenedor.appendChild(label);

    for (let i = 1; i <= numVariables; i++) {
        contenedor.appendChild(crearInputVariable(`coef${i}`, 1));
        contenedor.insertAdjacentHTML("beforeend", ` x<sub>${i}</sub>${i < numVariables ? " + " : ""}`);
    }
}

/**
 * Crea un input numérico estandarizado.
 */
function crearInputVariable(id, valor = "") {
    const input = document.createElement("input");
    input.type = "number";
    input.value = valor;
    input.className = "input-field variable-input";
    input.id = id;
    return input;
}

/**
 * Agrega una nueva restricción al contenedor.
 */
function agregarRestriccion() {
    const contenedor = document.getElementById("restricciones");
    const numVars = parseInt(document.getElementById("numVariables").value, 10);

    if (isNaN(numVars) || numVars <= 0) {
        console.error("Número de variables inválido al agregar restricción.");
        return;
    }

    const restriccionDiv = document.createElement("div");
    restriccionDiv.className = "restriccion-row restriccion";

    restriccionDiv.innerHTML = generarContenidoRestriccion(numVars);
    contenedor.insertBefore(restriccionDiv, document.getElementById("btnAgregar"));

    restriccionDiv.querySelector(".btnEliminar").addEventListener("click", () => restriccionDiv.remove());
}

/**
 * Genera el contenido HTML de una restricción.
 */
function generarContenidoRestriccion(numVars) {
    let inputs = "";
    for (let i = 1; i <= numVars; i++) {
        inputs += `<input type="number" value="1" class="input-field variable-input a${i}"> x<sub>${i}</sub>${i < numVars ? " + " : ""}`;
    }

    return `
        ${inputs}
        <select class="input-field operador">
            <option value="<=" selected>≤</option>
            <option value="=">=</option>
            <option value=">=">≥</option>
        </select>
        <input type="number" value="10" class="input-field variable-input b">
        <button class="btn btn-delete btnEliminar" type="button" title="Eliminar restricción">&times;</button>
    `;
}

/**
 * Elimina todas las restricciones actuales y las regenera con el número correcto de variables.
 */
function actualizarRestricciones() {
    const contenedor = document.getElementById("restricciones");
    const numVars = parseInt(document.getElementById("numVariables").value, 10);

    if (isNaN(numVars) || numVars <= 0) {
        console.error("Número de variables inválido al actualizar restricciones.");
        return;
    }

    // Eliminar todas las restricciones existentes
    contenedor.querySelectorAll(".restriccion").forEach(r => r.remove());

    // Agregar una nueva restricción inicial con el número correcto de variables
    agregarRestriccion();
}

/* ============================================================
   VALIDACIÓN Y UTILIDADES
============================================================ */

/**
 * Muestra un mensaje de error en pantalla
 */
function mostrarError(mensaje) {
    const resultDiv = document.getElementById("resultado");
    if (!resultDiv) return;
    
    resultDiv.innerHTML = `
        <div class="alert alert-error">
            <strong>⚠️ Error de Validación</strong>
            <p>${mensaje}</p>
        </div>
    `;
    resultDiv.classList.remove("hidden");
    resultDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}

/**
 * Oculta el div de resultados
 */
function ocultarResultado() {
    const resultDiv = document.getElementById("resultado");
    if (resultDiv) {
        resultDiv.classList.add("hidden");
        resultDiv.innerHTML = "";
    }
}

/**
 * Valida en tiempo real los inputs numéricos y aplica estilos de error.
 */
function validarEntradaNumerica(e) {
    if (e.target.tagName !== "INPUT" || e.target.type !== "number") return;

    // 1. Guardar la posición del cursor y el valor original
    let cursorPos = e.target.selectionStart;
    let valorOriginal = e.target.value;

    // 2. Limpiar caracteres no válidos
    let valor = valorOriginal.replace(/[^\d.-]/g, "");

    // 3a. Lógica para el guion (solo uno y al principio)
    let primerChar = valor.startsWith('-') ? '-' : '';
    let resto = valor.startsWith('-') ? valor.substring(1) : valor;
    resto = resto.replace(/-/g, '');
    valor = primerChar + resto;

    // 3b. Corregir el problema de múltiples puntos
    const partes = valor.split('.');
    if (partes.length > 2) {
        valor = partes[0] + "." + partes.slice(1).join('');
    }

    // 4. Solo actualizar si el valor realmente cambió
    if (valor !== valorOriginal) {
        const diff = valorOriginal.length - valor.length;
        e.target.value = valor;
        e.target.selectionStart = e.target.selectionEnd = Math.max(0, cursorPos - diff);
    }

    // 6. Validación de CSS
    const esInvalido = !valor || isNaN(parseFloat(valor)) || valor.endsWith('.');
    e.target.classList.toggle("input-error", esInvalido);
}

/**
 * Valida que el número de variables sea correcto
 */
function validarNumeroVariables() {
    const numVariables = parseInt(document.getElementById("numVariables").value, 10);
    
    if (isNaN(numVariables) || numVariables <= 0) {
        mostrarError("El número de variables debe ser mayor o igual a 1.");
        return false;
    }
    
    return true;
}

/**
 * Valida que todos los inputs tengan valores numéricos válidos
 */
function validarInputsNumericos() {
    const inputs = document.querySelectorAll('input[type="number"]');
    const inputsInvalidos = [];
    
    inputs.forEach((input, index) => {
        const valor = input.value.trim();
        const numero = parseFloat(valor);
        
        if (!valor || isNaN(numero) || valor.endsWith('.')) {
            inputsInvalidos.push({
                input: input,
                id: input.id || `Input ${index + 1}`,
                valor: valor
            });
            input.classList.add("input-error");
        }
    });
    
    if (inputsInvalidos.length > 0) {
        const mensaje = `Se encontraron ${inputsInvalidos.length} campo(s) con valores inválidos. Por favor, revisá los campos marcados en rojo.`;
        mostrarError(mensaje);
        
        // Hacer scroll al primer input inválido
        if (inputsInvalidos[0].input) {
            inputsInvalidos[0].input.scrollIntoView({ behavior: "smooth", block: "center" });
            inputsInvalidos[0].input.focus();
        }
        
        return false;
    }
    
    return true;
}

/**
 * Valida que haya al menos una restricción
 */
function validarRestricciones() {
    const restricciones = document.querySelectorAll(".restriccion");
    
    if (restricciones.length === 0) {
        mostrarError("Debe agregar al menos una restricción al problema.");
        return false;
    }
    
    return true;
}

/* ============================================================
   PROCESAMIENTO DE DATOS
============================================================ */

/**
 * Obtiene los coeficientes de la función objetivo.
 */
function getFunctionObjective() {
    const numVariables = parseInt(document.getElementById("numVariables").value, 10);
    return Array.from({ length: numVariables }, (_, i) => {
        const valor = document.getElementById(`coef${i + 1}`).value.trim();
        const numero = parseFloat(valor);
        if (isNaN(numero)) throw new Error(`Coeficiente x${i + 1} inválido.`);
        return numero;
    });
}

/**
 * Obtiene todas las restricciones activas del formulario.
 */
function getRestrictions() {
    return Array.from(document.querySelectorAll(".restriccion")).map((r, index) => {
        // Seleccionar únicamente inputs de coeficientes a1..aN (evita tomar 'b')
        const coefInputs = Array.from(r.querySelectorAll('input.variable-input'))
            .filter(input => Array.from(input.classList).some(cls => /^a\d+$/.test(cls)));

        const coefs = coefInputs.map(input => {
            const valor = input.value.trim();
            const numero = parseFloat(valor);
            if (isNaN(numero)) {
                throw new Error(`Coeficiente inválido en restricción ${index + 1}: El valor '${valor}' no es un número válido.`);
            }
            return numero;
        });

        const operador = r.querySelector(".operador").value;
        const bInput = r.querySelector(".b");
        const bValor = bInput.value.trim();
        const b = parseFloat(bValor);
        
        if (isNaN(b)) {
            throw new Error(`Lado derecho inválido en restricción ${index + 1}: El valor '${bValor}' no es un número válido.`);
        }

        return [...coefs, operador, b];
    });
}

/**
 * Prepara los datos del problema para enviar al backend.
 */
function prepareRequestData() {
    const c = getFunctionObjective();
    const restricciones = getRestrictions();

    // Validar que todas las restricciones tengan el mismo número de variables que la función objetivo
    const numVariables = c.length;
    restricciones.forEach((restriccion, index) => {
        if (restriccion.length - 2 !== numVariables) {
            throw new Error(
                `La restricción ${index + 1} tiene un número de variables (${restriccion.length - 2}) diferente al de la función objetivo (${numVariables}).`
            );
        }
    });

    return {
        problem_type: tipoModelo === "max" ? "maximization" : "minimization",
        C: c,
        LI: restricciones.map(r => r.slice(0, -2)),
        O: restricciones.map(r => r.at(-2)),
        LD: restricciones.map(r => r.at(-1))
    };
}

/* ============================================================
   RESOLUCIÓN Y COMUNICACIÓN CON BACKEND
============================================================ */

/**
 * Envía el problema al backend y muestra el resultado.
 */
async function solveProblem() {
    const resultDiv = document.getElementById("resultado");
    if (!resultDiv) return console.error("No se encontró el div #resultado");

    // VALIDACIONES PREVIAS A LA EJECUCIÓN
    if (!validarNumeroVariables()) return;
    if (!validarInputsNumericos()) return;
    if (!validarRestricciones()) return;

    mostrarEstado(resultDiv, "⏳ Calculando...", "blue");
    localStorage.removeItem("simplex_result");

    try {
        const data = prepareRequestData();
        localStorage.setItem("simplex_inputs", JSON.stringify(data));

        const response = await fetch("/simplex/solve-tabular", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const body = await response.text();
        if (!response.ok) throw new Error(body || `Error ${response.status}`);
        const result = JSON.parse(body);

        manejarRespuestaExitosa(resultDiv, result, body);
    } catch (error) {
        manejarError(resultDiv, error);
    }
}

/**
 * Muestra un mensaje de estado en el contenedor de resultados.
 */
function mostrarEstado(div, mensaje, color = "") {
    div.classList.remove("hidden");
    div.textContent = mensaje;
    div.style.color = color;
}

/**
 * Maneja y muestra una respuesta exitosa del backend.
 */
function manejarRespuestaExitosa(div, result, rawBody) {
    const status = (result.status || "").toLowerCase();
    const solucion = result.solucion || {};
    const variables = solucion.variables || {};
    const valorOptimo = (solucion.valor_optimo ?? "N/A").toFixed?.(2) || "N/A";

    if (status === "optimo") localStorage.setItem("simplex_result", rawBody);

    const tablasBtn = status === "optimo" ? `<a href="/tablas" class="btn btn-tablas btn-full btn-large">Ver Tablas</a>` : "";

    div.innerHTML = `
        <h3 class="section-title">Resultado</h3>
        <div class="resultado-card">
            <p><strong>Estado:</strong> ${result.status}</p>
            <p><strong>Valor Óptimo:</strong> ${valorOptimo}</p>
            <p><strong>Variables:</strong></p>
            <ul class="resultado-list">
                ${Object.entries(variables)
                    .filter(([key]) => key.startsWith("x"))
                    .map(([key, value]) => `<li>${key}: ${(+value).toFixed(2)}</li>`)
                    .join("")}
            </ul>
            ${tablasBtn}
        </div>
    `;
    div.style.color = "";
    div.scrollIntoView({ behavior: "smooth", block: "start" });

    // Mostrar botón gráfico si el problema tiene exactamente 2 variables
    const grafBtn = document.getElementById("btnVerGrafico");
    const extra = document.getElementById("accionesExtra");
    let numVars = 0;
    try {
        const rawInputs = localStorage.getItem("simplex_inputs");
        if (rawInputs) {
            const inputs = JSON.parse(rawInputs);
            numVars = Array.isArray(inputs?.C) ? inputs.C.length : 0;
        } else {
            numVars = parseInt(document.getElementById("numVariables").value, 10) || 0;
        }
    } catch (_) {
        numVars = parseInt(document.getElementById("numVariables").value, 10) || 0;
    }

    if (grafBtn && extra) {
        if (numVars === 2) {
            grafBtn.style.display = "block";
            extra.classList.remove("hidden");
        } else {
            grafBtn.style.display = "none";
            extra.classList.add("hidden");
        }
    }
}

/**
 * Maneja los errores durante el proceso de resolución.
 */
function manejarError(div, error) {
    console.error("Error en solveProblem():", error);
    div.innerHTML = `
        <h3 class="section-title">Resultado</h3>
        <div class="resultado-card">
            <p class="resultado-error"><strong>Error:</strong> ${error.message || "No se pudo resolver el problema."}</p>
            <p class="resultado-error-sub">Revisá la consola (F12) para más detalles.</p>
        </div>
    `;
    div.classList.remove("hidden");
}

/* ============================================================
   RESTAURACIÓN DE DATOS
============================================================ */

/**
 * Restaura el estado del formulario desde localStorage si existe.
 */
function restaurarDatosPrevios() {
    try {
        const raw = localStorage.getItem("simplex_inputs");
        if (!raw) return;

        const data = JSON.parse(raw);
        tipoModelo = data.problem_type === "minimization" ? "min" : "max";
        alternarModelo(tipoModelo, 
            document.getElementById(tipoModelo === "min" ? "btnMin" : "btnMax"),
            document.getElementById(tipoModelo === "min" ? "btnMax" : "btnMin")
        );

        document.getElementById("numVariables").value = data.C.length;
        renderFuncionObjetivo();
        data.C.forEach((val, idx) => document.getElementById(`coef${idx + 1}`).value = val);

        const cont = document.getElementById("restricciones");
        cont.querySelectorAll(".restriccion").forEach(r => r.remove());
        data.LI.forEach((coef, i) => {
            agregarRestriccion();
            const restr = cont.querySelectorAll(".restriccion")[i];
            coef.forEach((val, j) => restr.querySelector(`.a${j + 1}`).value = val);
            restr.querySelector(".operador").value = data.O[i];
            restr.querySelector(".b").value = data.LD[i];
        });
    } catch (e) {
        console.warn("No se pudieron restaurar los datos previos:", e);
    }
}