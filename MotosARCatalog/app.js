/**
 * app.js — MotosAR Catalog
 * WebAR SPA para catálogo de motocicletas en Colombia
 *
 * Características:
 *  - Routing por URL params (?moto=id&ar=true)
 *  - Visor 3D con model-viewer y AR nativo
 *  - Panel ficha técnica expandible
 *  - Generador de QR con qrcode.js
 *  - Botón de WhatsApp dinámico por moto
 *  - Soporte teclado (←→ para navegar)
 */

'use strict';

/* ══════════════════════════════════════════════
   CONFIGURACIÓN  —  EDITAR SEGÚN EL NEGOCIO
══════════════════════════════════════════════ */
const CONFIG = {
  /** Número WhatsApp sin +, ni espacios: código país + número */
  whatsapp: '573001234567',

  /** Nombre del sitio en el QR sticker */
  siteName: 'MotosAR Colombia',

  /** Si true, intenta auto-activar AR cuando ?ar=true en URL */
  autoArPrompt: true,
};

/* ══════════════════════════════════════════════
   CATÁLOGO DE MOTOS
   glb:    ruta relativa desde MotosARCatalog/
   poster: imagen mientras carga el GLB
══════════════════════════════════════════════ */
const MOTOS = [
  {
    id:         'akt-nkd',
    nombre:     'AKT NKD 125',
    marca:      'AKT',
    modelo:     'NKD 125',
    cilindraje: '125 cc',
    potencia:   '11 HP @ 8.000 rpm',
    torque:     '8.8 Nm @ 6.000 rpm',
    transmision:'5 velocidades',
    peso:       '118 kg',
    tanque:     '13.5 L',
    precio:     5990000,
    financiado: 'Desde $112.000/mes',
    glb:        '../Akt%20Nkd/nkd.glb',
    poster:     '../Akt%20Nkd/3_dark.png',
    acento:     '#a3e635',   /* lime-400  */
    tags:       ['Ciudad', 'Café Racer', 'Sport'],
    descripcion: 'Estilo café racer moderno con motor 4T de alto rendimiento. Suspensión delantera telescópica y freno de disco para un manejo dinámico y seguro en ciudad.',
  },
  {
    id:         'bajaj-boxer',
    nombre:     'Bajaj Boxer 100',
    marca:      'Bajaj',
    modelo:     'Boxer 100',
    cilindraje: '100 cc',
    potencia:   '8.2 HP @ 7.500 rpm',
    torque:     '8.05 Nm @ 5.000 rpm',
    transmision:'4 velocidades',
    peso:       '113 kg',
    tanque:     '15 L',
    precio:     4490000,
    financiado: 'Desde $84.000/mes',
    glb:        '../Bajaj%20Boxer/boxer.glb',
    poster:     '../Bajaj%20Boxer/3_dark.png',
    acento:     '#fb923c',   /* orange-400 */
    tags:       ['Trabajo', 'Campo', 'Economía'],
    descripcion: 'La moto más robusta del segmento. Reconocida por su durabilidad extrema y bajo costo de mantenimiento, ideal para trabajo en ciudad y zonas rurales.',
  },
  {
    id:         'hero-eco',
    nombre:     'Hero Eco Deluxe',
    marca:      'Hero',
    modelo:     'Eco Deluxe',
    cilindraje: '97.2 cc',
    potencia:   '7.9 HP @ 8.000 rpm',
    torque:     '7.55 Nm @ 5.000 rpm',
    transmision:'4 velocidades',
    peso:       '112 kg',
    tanque:     '10.5 L',
    precio:     4190000,
    financiado: 'Desde $79.000/mes',
    glb:        '../Hero%20eco%20deluxe/hero.glb',
    poster:     '../Hero%20eco%20deluxe/3_dark.png',
    acento:     '#38bdf8',   /* sky-400 */
    tags:       ['Trabajo', 'Ahorro', 'Ciudad'],
    descripcion: 'La moto de trabajo más vendida en Colombia. Consumo de combustible excepcional (60+ km/L) y costo de mantenimiento mínimo. Confiable, día a día.',
  },
  {
    id:         'pulsar-ns200',
    nombre:     'Pulsar NS 200',
    marca:      'Bajaj',
    modelo:     'Pulsar NS 200',
    cilindraje: '199.5 cc',
    potencia:   '24.5 HP @ 9.750 rpm',
    torque:     '18.74 Nm @ 8.000 rpm',
    transmision:'6 velocidades',
    peso:       '156 kg',
    tanque:     '12 L',
    precio:     12490000,
    financiado: 'Desde $234.000/mes',
    glb:        '../Pulsar%20ns%20200/ns200.glb',
    poster:     '../Pulsar%20ns%20200/3_dark.png',
    acento:     '#f43f5e',   /* rose-500 */
    tags:       ['Sport', 'Performance', '200cc'],
    descripcion: 'Naked sport con motor DTS-Fi de triple chispa e inyección electrónica. La experiencia de conducción más emocionante del segmento 200cc en Colombia.',
  },
  {
    id:         'tvs-raider',
    nombre:     'TVS Raider 125',
    marca:      'TVS',
    modelo:     'Raider 125',
    cilindraje: '124.8 cc',
    potencia:   '11.4 HP @ 7.500 rpm',
    torque:     '11.2 Nm @ 6.000 rpm',
    transmision:'5 velocidades',
    peso:       '123 kg',
    tanque:     '10 L',
    precio:     6290000,
    financiado: 'Desde $118.000/mes',
    glb:        '../Tvs%20raider/Raider.glb',
    poster:     '../Tvs%20raider/3_dark.png',
    acento:     '#a78bfa',   /* violet-400 */
    tags:       ['Sport', 'Premium', '125cc'],
    descripcion: 'Tecnología Racing DNA de TVS. Diseño deportivo premium con panel de instrumentos LCD, faros LED y freno de disco delantero. La más avanzada del segmento.',
  },
];

/* ══════════════════════════════════════════════
   ESTADO DE LA APP
══════════════════════════════════════════════ */
const state = {
  motoIdx:      0,
  fichaAbierta: false,
  arPrompt:     false,
  qrListo:      false,
  loadTimer:    null,
};

/* ══════════════════════════════════════════════
   REFERENCIAS DOM
══════════════════════════════════════════════ */
let el = {};

function bindEls() {
  el = {
    mv:           document.getElementById('mv'),
    selector:     document.getElementById('selector'),
    accentBar:    document.getElementById('accentBar'),
    loadOverlay:  document.getElementById('loadOverlay'),
    loadBar:      document.getElementById('loadBar'),
    arPrompt:     document.getElementById('arPrompt'),
    arPromptMoto: document.getElementById('arPromptMoto'),
    arPromptBtn:  document.getElementById('arPromptBtn'),
    arPromptSkip: document.getElementById('arPromptSkip'),
    motoMarca:    document.getElementById('motoMarca'),
    motoNombre:   document.getElementById('motoNombre'),
    motoPrecio:   document.getElementById('motoPrecio'),
    motoFinanc:   document.getElementById('motoFinanc'),
    motoDesc:     document.getElementById('motoDesc'),
    motoTags:     document.getElementById('motoTags'),
    motoSpecs:    document.getElementById('motoSpecs'),
    fichaPanel:   document.getElementById('fichaPanel'),
    fichaToggle:  document.getElementById('fichaToggle'),
    fichaExpanded:document.getElementById('fichaExpanded'),
    arFloatBtn:   document.getElementById('arFloatBtn'),
    waBtn:        document.getElementById('waBtn'),
    qrBtn:        document.getElementById('qrBtn'),
    qrModal:      document.getElementById('qrModal'),
    qrModalClose: document.getElementById('qrModalClose'),
    qrContainer:  document.getElementById('qrContainer'),
    stickerNombre:document.getElementById('stickerNombre'),
    stickerPrecio:document.getElementById('stickerPrecio'),
    qrUrlDisplay: document.getElementById('qrUrlDisplay'),
    printBtn:     document.getElementById('printBtn'),
    arToast:      document.getElementById('arToast'),
    arToastMsg:   document.getElementById('arToastMsg'),
  };
}

/* ══════════════════════════════════════════════
   ROUTING — leer ?moto=id&ar=true desde la URL
══════════════════════════════════════════════ */
function parseURL() {
  const p = new URLSearchParams(window.location.search);
  const id = p.get('moto');
  if (id) {
    const i = MOTOS.findIndex(m => m.id === id);
    if (i !== -1) state.motoIdx = i;
  }
  if (p.get('ar') === 'true' && CONFIG.autoArPrompt) {
    state.arPrompt = true;
  }
}

/* ══════════════════════════════════════════════
   UTILIDADES
══════════════════════════════════════════════ */
function formatCOP(n) {
  return '$ ' + n.toLocaleString('es-CO') + ' COP';
}

function motoBaseURL() {
  /* URL canónica para el QR: origin + ruta de la carpeta del catálogo */
  const path = window.location.pathname.replace(/\/?[^/]*$/, '/');
  return window.location.origin + path;
}

/* ══════════════════════════════════════════════
   CARGAR MOTO
══════════════════════════════════════════════ */
function loadMoto(idx) {
  state.motoIdx   = idx;
  state.qrListo   = false;
  const m = MOTOS[idx];

  /* Acento visual */
  el.accentBar.style.background = m.acento;
  document.documentElement.style.setProperty('--cur-accent', m.acento);

  /* model-viewer */
  clearTimeout(state.loadTimer);
  el.loadOverlay.classList.remove('hidden', 'fade-out');
  el.loadBar.style.width = '0%';

  el.mv.setAttribute('poster', m.poster);
  /* Reset src para forzar re-load del evento 'load' */
  el.mv.removeAttribute('src');
  requestAnimationFrame(() => { el.mv.setAttribute('src', m.glb); });

  /* Timeout de seguridad: ocultar overlay si load no dispara en 25s */
  state.loadTimer = setTimeout(() => hideLoadOverlay(), 25000);

  /* Ficha */
  el.motoMarca.textContent  = m.marca;
  el.motoNombre.textContent = m.nombre;
  el.motoPrecio.textContent = formatCOP(m.precio);
  el.motoFinanc.textContent = m.financiado;
  el.motoDesc.textContent   = m.descripcion;
  el.motoTags.innerHTML     = m.tags.map(t => `<span class="tag">${t}</span>`).join('');
  el.motoSpecs.innerHTML    = buildSpecs(m);

  /* WhatsApp */
  refreshWhatsApp(m);

  /* Selector pills */
  document.querySelectorAll('.moto-pill').forEach((btn, i) => {
    btn.classList.toggle('active', i === idx);
    btn.style.setProperty('--acento', MOTOS[i].acento);
  });

  /* Cerrar ficha si está expandida */
  if (state.fichaAbierta) toggleFicha(false);
}

function buildSpecs(m) {
  const rows = [
    ['Cilindraje',   m.cilindraje],
    ['Potencia',     m.potencia],
    ['Torque',       m.torque],
    ['Transmisión',  m.transmision],
    ['Peso neto',    m.peso],
    ['Tanque',       m.tanque],
  ];
  return rows.map(([k, v]) =>
    `<div class="spec-row">
       <span class="spec-label">${k}</span>
       <span class="spec-value">${v}</span>
     </div>`
  ).join('');
}

function hideLoadOverlay() {
  clearTimeout(state.loadTimer);
  el.loadOverlay.classList.add('fade-out');
  setTimeout(() => el.loadOverlay.classList.add('hidden'), 320);
}

/* ══════════════════════════════════════════════
   WHATSAPP
══════════════════════════════════════════════ */
function refreshWhatsApp(m) {
  const txt = encodeURIComponent(
    `Hola! Estoy interesado en la *${m.nombre}* que vi en el catálogo AR.\n` +
    `💰 Precio: ${formatCOP(m.precio)}\n\n` +
    `¿Puedes darme más información? 🏍️`
  );
  el.waBtn.href = `https://wa.me/${CONFIG.whatsapp}?text=${txt}`;
}

/* ══════════════════════════════════════════════
   BUILD SELECTOR PILLS
══════════════════════════════════════════════ */
function buildSelector() {
  el.selector.innerHTML = MOTOS.map((m, i) =>
    `<button
       class="moto-pill${i === state.motoIdx ? ' active' : ''}"
       data-idx="${i}"
       style="--acento:${m.acento}"
       aria-label="${m.nombre}"
     >
       <span class="pill-marca">${m.marca}</span>
       <span class="pill-modelo">${m.modelo}</span>
     </button>`
  ).join('');

  el.selector.addEventListener('click', e => {
    const btn = e.target.closest('.moto-pill');
    if (btn && +btn.dataset.idx !== state.motoIdx) loadMoto(+btn.dataset.idx);
  });
}

/* ══════════════════════════════════════════════
   ACTIVAR AR
══════════════════════════════════════════════ */
function activateAR() {
  if (el.mv.canActivateAR) {
    el.mv.activateAR();
  } else {
    showARToast();
  }
}

function showARToast() {
  const m = MOTOS[state.motoIdx];
  el.arToastMsg.textContent = `Usa Chrome en Android o Safari en iPhone para ver la ${m.marca} en AR`;
  el.arToast.classList.remove('hidden');
  setTimeout(() => el.arToast.classList.add('hidden'), 4500);
}

/* ══════════════════════════════════════════════
   AR PROMPT (para URLs con ?ar=true)
══════════════════════════════════════════════ */
function initARPrompt() {
  if (!state.arPrompt) {
    el.arPrompt.classList.add('hidden');
    return;
  }
  const m = MOTOS[state.motoIdx];
  el.arPromptMoto.textContent = m.nombre;
  el.arPrompt.classList.remove('hidden');

  el.arPromptBtn.addEventListener('click', () => {
    el.arPrompt.classList.add('hidden');
    /* Pequeño delay para que el modelo termine de cargar */
    setTimeout(activateAR, 600);
  }, { once: true });

  el.arPromptSkip.addEventListener('click', () => {
    el.arPrompt.classList.add('hidden');
  }, { once: true });
}

/* ══════════════════════════════════════════════
   FICHA PANEL TOGGLE
══════════════════════════════════════════════ */
function toggleFicha(force) {
  const open = force !== undefined ? force : !state.fichaAbierta;
  state.fichaAbierta = open;
  el.fichaPanel.classList.toggle('open', open);
  el.fichaExpanded.setAttribute('aria-hidden', String(!open));
}

/* ══════════════════════════════════════════════
   QR MODAL
══════════════════════════════════════════════ */
function openQRModal() {
  const m   = MOTOS[state.motoIdx];
  const url = motoBaseURL() + '?moto=' + m.id + '&ar=true';

  el.stickerNombre.textContent = m.nombre;
  el.stickerPrecio.textContent = formatCOP(m.precio);
  el.qrUrlDisplay.textContent  = url;

  /* Limpiar QR anterior */
  el.qrContainer.innerHTML = '';
  state.qrListo = false;

  el.qrModal.classList.remove('hidden');

  /* Generar QR en el próximo frame para que el modal ya esté visible */
  requestAnimationFrame(() => {
    try {
      new QRCode(el.qrContainer, {
        text:         url,
        width:        180,
        height:       180,
        colorDark:    '#000000',
        colorLight:   '#ffffff',
        correctLevel: QRCode.CorrectLevel.H,
      });
      state.qrListo = true;
    } catch (e) {
      el.qrContainer.innerHTML =
        '<p style="color:#ef4444;font-size:12px;padding:12px;">Error generando QR: ' + e.message + '</p>';
    }
  });
}

function closeQRModal() {
  el.qrModal.classList.add('hidden');
}

function printSticker() {
  if (!state.qrListo) return;
  window.print();
}

/* ══════════════════════════════════════════════
   MODEL-VIEWER EVENTS
══════════════════════════════════════════════ */
function initModelViewerEvents() {
  el.mv.addEventListener('load', () => hideLoadOverlay());

  el.mv.addEventListener('progress', e => {
    const pct = ((e.detail.totalProgress || 0) * 100).toFixed(0);
    el.loadBar.style.width = pct + '%';
    if (+pct >= 100) hideLoadOverlay();
  });

  el.mv.addEventListener('error', () => {
    clearTimeout(state.loadTimer);
    el.loadOverlay.innerHTML =
      `<p style="color:#f87171;font-size:12px;font-family:var(--font-mono);padding:16px;text-align:center;">
        Error cargando modelo 3D.<br/>Verifica que el servidor esté activo.
      </p>`;
  });

  el.mv.addEventListener('ar-status', e => {
    if (e.detail.status === 'failed') showARToast();
  });
}

/* ══════════════════════════════════════════════
   EVENT LISTENERS
══════════════════════════════════════════════ */
function initEvents() {
  /* AR float button */
  el.arFloatBtn.addEventListener('click', activateAR);

  /* Ficha toggle */
  el.fichaToggle.addEventListener('click', () => toggleFicha());

  /* Expand ficha on click on compact block too */
  el.fichaPanel.addEventListener('click', e => {
    if (!state.fichaAbierta && !e.target.closest('#fichaExpanded') && !e.target.closest('#fichaToggle')) {
      toggleFicha(true);
    }
  });

  /* QR modal */
  el.qrBtn.addEventListener('click', openQRModal);
  el.qrModalClose.addEventListener('click', closeQRModal);
  el.qrModal.addEventListener('click', e => { if (e.target === el.qrModal) closeQRModal(); });
  el.printBtn.addEventListener('click', printSticker);

  /* Keyboard navigation */
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if (!el.qrModal.classList.contains('hidden')) { closeQRModal(); return; }
      if (state.fichaAbierta) { toggleFicha(false); return; }
    }
    if (document.activeElement.tagName === 'INPUT') return;
    if (e.key === 'ArrowRight') loadMoto((state.motoIdx + 1) % MOTOS.length);
    if (e.key === 'ArrowLeft')  loadMoto((state.motoIdx - 1 + MOTOS.length) % MOTOS.length);
    /* Teclas 1-5: selección rápida */
    const n = parseInt(e.key);
    if (n >= 1 && n <= MOTOS.length) loadMoto(n - 1);
  });

  /* Touch swipe en el header selector para teclado táctil */
  let touchStartX = 0;
  document.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
  document.addEventListener('touchend', e => {
    /* Solo fuera del modal y de la ficha */
    if (!el.qrModal.classList.contains('hidden')) return;
    if (e.target.closest('#fichaPanel') || e.target.closest('#selector')) return;
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) < 60) return;   /* mínimo 60px de swipe */
    if (dx < 0) loadMoto((state.motoIdx + 1) % MOTOS.length);  /* swipe ← → siguiente */
    else         loadMoto((state.motoIdx - 1 + MOTOS.length) % MOTOS.length);
  }, { passive: true });
}

/* ══════════════════════════════════════════════
   INIT
══════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  parseURL();
  bindEls();
  buildSelector();
  initModelViewerEvents();
  initEvents();
  loadMoto(state.motoIdx);
  initARPrompt();
});

