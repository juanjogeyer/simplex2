document.addEventListener('DOMContentLoaded', () => {
  const contenedorTablas = document.getElementById('contenedorTablas');
  const estadoDiv = document.getElementById('estado');
  const resumenDiv = document.getElementById('resumen');
  const btnLimpiar = document.getElementById('btnLimpiar');

  // --- Eventos ---
  btnLimpiar?.addEventListener('click', limpiarResultados);

  // --- Flujo principal ---
  const raw = leerLocalStorage('simplex_result');
  if (!raw) return mostrarMensajeError(estadoDiv, 'No hay datos para mostrar.', 'Resuelve un problema primero y luego vuelve a esta página.');

  const data = parseJsonSeguro(raw);
  if (!data) return mostrarMensajeError(estadoDiv, 'Error al leer datos.', 'El resultado almacenado no es válido.');

  renderEstado(estadoDiv, data.status);
  renderTablas(contenedorTablas, data.tablas);
  renderResumen(resumenDiv, data.solucion);
});

// =====================
//  Funciones principales
// =====================

function limpiarResultados() {
  try { localStorage.removeItem('simplex_result'); } catch (_) {}
  ['contenedorTablas', 'estado', 'resumen'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = '';
    if (id === 'resumen') el.classList.add('hidden');
  });
}

function leerLocalStorage(clave) {
  try {
    return localStorage.getItem(clave);
  } catch {
    return null;
  }
}

function parseJsonSeguro(texto) {
  try {
    return JSON.parse(texto);
  } catch {
    return null;
  }
}

// =====================
//  Renderizado de vistas
// =====================

function renderEstado(contenedor, estado) {
  const estadoText = estado || 'desconocido';
  contenedor.innerHTML = `
    <h2 class="section-title">Estado</h2>
    <div class="resultado-card">
      <p><strong>Resultado:</strong> ${escapeHtml(estadoText)}</p>
    </div>
  `;
}

function renderTablas(contenedor, tablas) {
  const lista = Array.isArray(tablas) ? tablas : [];
  contenedor.innerHTML = lista.length
    ? lista.map(renderTabla).join('')
    : "<p class='resultado-error-sub'>No se recibieron tablas del servidor.</p>";
}

function renderResumen(contenedor, solucion) {
  if (!solucion) return;

  const { variables = {}, valor_optimo } = solucion;
  const valor = typeof valor_optimo === 'number' ? valor_optimo.toFixed(2) : 'No disponible';

  const listaVariables = Object.entries(variables)
    .filter(([k]) => k)
    .map(([k, v]) => `<li>${escapeHtml(k)}: ${typeof v === 'number' ? v.toFixed(2) : escapeHtml(v)}</li>`)
    .join('');

  contenedor.innerHTML = `
    <h2 class="section-title">Solución</h2>
    <div class="resultado-card">
      <p><strong>Valor Óptimo:</strong> ${valor}</p>
      <p><strong>Variables:</strong></p>
      <ul class="resultado-list">${listaVariables}</ul>
    </div>
  `;
  contenedor.classList.remove('hidden');
}

// =====================
//  Render tabla simplex
// =====================

function renderTabla(tabla) {
  const headers = tabla.headers || [];
  const filas = tabla.filas || [];
  const filaObj = tabla.fila_obj || [];

  const thead = `
    <thead>
      <tr>${headers.map(h => `<th>${escapeHtml(h)}</th>`).join('')}</tr>
    </thead>`;

  const bodyRows = filas.map(row => `
    <tr>${row.map((cell, idx) => 
      idx === 0 
        ? `<th class="th-row">${escapeHtml(String(cell))}</th>` 
        : `<td>${formatNumber(cell)}</td>`).join('')}
    </tr>`).join('');

  const zRow = filaObj.length ? `
    <tr class="fila-obj">
      ${filaObj.map((cell, idx) => 
        idx === 0 
          ? `<th class="th-row">${escapeHtml(String(cell))}</th>` 
          : `<td>${formatNumber(cell)}</td>`).join('')}
    </tr>` : '';

  return `
    <details class="tabla-container" open>
      <summary class="tabla-summary">${escapeHtml(tabla.titulo || 'Tabla')}</summary>
      <div class="table-wrapper">
        <table class="simplex-table">
          ${thead}
          <tbody>${bodyRows}${zRow}</tbody>
        </table>
      </div>
    </details>`;
}

// =====================
//  Utilidades
// =====================

function escapeHtml(str = '') {
  return str.replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[c] || c));
}

function formatNumber(val) {
  if (typeof val === 'number') return Number(val.toFixed(6));
  const n = Number(val);
  return isNaN(n) ? escapeHtml(String(val)) : Number(n.toFixed(6));
}

function mostrarMensajeError(div, titulo, subtitulo) {
  div.innerHTML = `
    <p class="resultado-error"><strong>${escapeHtml(titulo)}</strong></p>
    <p class="resultado-error-sub">${escapeHtml(subtitulo)}</p>
  `;
}
