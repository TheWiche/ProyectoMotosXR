/**
 * app.js — MotosAR Catalog
 * WebAR SPA para catálogo de motocicletas en Colombia
 * Incluye Modo Cámara AR Universal (compatible con todos los teléfonos Android e iOS)
 * y soporte nativo para Scene Viewer / Quick Look.
 */

'use strict';

/* ══════════════════════════════════════════════
   CONFIGURACIÓN
══════════════════════════════════════════════ */
const CONFIG = {
  /** Número WhatsApp para cotizaciones (código país + número sin + ni espacios) */
  whatsapp: '573145813171',

  /** Nombre del sitio en el QR sticker */
  siteName: 'MotosAR Colombia',

  /** Si true, muestra prompt para activar AR al entrar con ?ar=true */
  autoArPrompt: true,
};

/* ══════════════════════════════════════════════
   CATÁLOGO DE MOTOS (5 modelos)
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
    acento:     '#a3e635',   /* lime-400 */
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
    descripcion: 'La moto de trabajo más vendida en Colombia. Consumo de combustible excepcional (60+ km/L) y costo de mantenimiento mínimo. Confiable día a día.',
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
  motoIdx:        0,
  fichaAbierta:   false,
  arPrompt:       false,
  qrListo:        false,
  loadTimer:      null,
  cameraStream:   null,
  cameraScale:    1.0,
  cameraTimerSec: 0,
  isCameraActive: false,
  isCapturing:    false,
  lastPhotoBlob:  null,
  lastPhotoUrl:   null,
};

/* ══════════════════════════════════════════════
   REFERENCIAS DOM
══════════════════════════════════════════════ */
let el = {};

function bindEls() {
  el = {
    mv:                     document.getElementById('mv'),
    selector:               document.getElementById('selector'),
    accentBar:              document.getElementById('accentBar'),
    loadOverlay:            document.getElementById('loadOverlay'),
    loadBar:                document.getElementById('loadBar'),
    viewerTip:              document.getElementById('viewerTip'),
    navPrev:                document.getElementById('navPrev'),
    navNext:                document.getElementById('navNext'),
    arPrompt:               document.getElementById('arPrompt'),
    arPromptMoto:           document.getElementById('arPromptMoto'),
    arPromptBtn:            document.getElementById('arPromptBtn'),
    arPromptSkip:           document.getElementById('arPromptSkip'),
    motoMarca:              document.getElementById('motoMarca'),
    motoNombre:             document.getElementById('motoNombre'),
    motoPrecio:             document.getElementById('motoPrecio'),
    motoFinanc:             document.getElementById('motoFinanc'),
    motoDesc:               document.getElementById('motoDesc'),
    motoTags:               document.getElementById('motoTags'),
    motoSpecs:              document.getElementById('motoSpecs'),
    fichaPanel:             document.getElementById('fichaPanel'),
    fichaToggle:            document.getElementById('fichaToggle'),
    fichaCompact:           document.getElementById('fichaCompact'),
    fichaExpanded:          document.getElementById('fichaExpanded'),
    panelArBtn:             document.getElementById('panelArBtn'),
    panelWaBtn:             document.getElementById('panelWaBtn'),
    arFloatBtn:             document.getElementById('arFloatBtn'),
    waBtn:              document.getElementById('waBtn'),
    qrBtn:              document.getElementById('qrBtn'),
    qrModal:            document.getElementById('qrModal'),
    qrModalClose:       document.getElementById('qrModalClose'),
    qrContainer:        document.getElementById('qrContainer'),
    stickerNombre:      document.getElementById('stickerNombre'),
    stickerPrecio:      document.getElementById('stickerPrecio'),
    qrUrlDisplay:       document.getElementById('qrUrlDisplay'),
    printBtn:           document.getElementById('printBtn'),
    arToast:            document.getElementById('arToast'),
    arToastMsg:         document.getElementById('arToastMsg'),

    /* Modal Selector AR */
    arChoiceModal:      document.getElementById('arChoiceModal'),
    arChoiceClose:      document.getElementById('arChoiceClose'),
    btnLaunchNativeAR:  document.getElementById('btnLaunchNativeAR'),
    btnLaunchCameraAR:  document.getElementById('btnLaunchCameraAR'),

    /* Vista Cámara & Foto Simplificada */
    arCameraView:           document.getElementById('arCameraView'),
    arCameraFeed:           document.getElementById('arCameraFeed'),
    arCaptureCanvas:        document.getElementById('arCaptureCanvas'),
    cameraFlash:            document.getElementById('cameraFlash'),
    arSpatialStage:         document.getElementById('arSpatialStage'),
    arCameraModelWrap:      document.getElementById('arCameraModelWrap'),
    arFloorShadow:          document.getElementById('arFloorShadow'),
    cameraMv:               document.getElementById('cameraMv'),
    arCamClose:             document.getElementById('arCamClose'),
    arCamMotoNombre:        document.getElementById('arCamMotoNombre'),
    arCamRotate180:         document.getElementById('arCamRotate180'),
    arCamTip:               document.getElementById('arCamTip'),
    arCamTipText:           document.getElementById('arCamTipText'),
    arCamPrev:              document.getElementById('arCamPrev'),
    arCamNext:              document.getElementById('arCamNext'),
    arCamCapture:           document.getElementById('arCamCapture'),
    arShutterInner:         document.getElementById('arShutterInner'),

    /* Vista Previa de Foto Capturada */
    photoModal:             document.getElementById('photoModal'),
    photoModalClose:        document.getElementById('photoModalClose'),
    photoMotoBadge:         document.getElementById('photoMotoBadge'),
    photoNativeShareBtn:    document.getElementById('photoNativeShareBtn'),
    photoPreviewImg:        document.getElementById('photoPreviewImg'),
    photoDownloadBtn:       document.getElementById('photoDownloadBtn'),
    photoWaBtn:             document.getElementById('photoWaBtn'),
    photoRetakeBtn:         document.getElementById('photoRetakeBtn'),
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
  const path = window.location.pathname.replace(/\/?[^/]*$/, '/');
  return window.location.origin + path;
}

/* ══════════════════════════════════════════════
   CARGAR MOTO
══════════════════════════════════════════════ */
function loadMoto(idx) {
  state.motoIdx = idx;
  state.qrListo = false;
  const m = MOTOS[idx];

  /* Color de acento dinámico */
  el.accentBar.style.background = m.acento;
  document.documentElement.style.setProperty('--accent-ar', m.acento);

  /* Carga del modelo 3D principal */
  clearTimeout(state.loadTimer);
  el.loadOverlay.classList.remove('hidden', 'fade-out');
  el.loadBar.style.width = '0%';

  el.mv.setAttribute('poster', m.poster);
  el.mv.removeAttribute('src');
  requestAnimationFrame(() => {
    el.mv.setAttribute('src', m.glb);
  });

  /* Si la cámara AR está activa, sincronizar también el modelo de la cámara */
  if (state.isCameraActive && el.cameraMv) {
    el.arCamMotoNombre.textContent = m.nombre;
    el.cameraMv.setAttribute('src', m.glb);
  }

  /* Timeout de seguridad en caso de redes móviles lentas */
  state.loadTimer = setTimeout(() => hideLoadOverlay(), 25000);

  /* Ficha técnica */
  el.motoMarca.textContent  = m.marca;
  el.motoNombre.textContent = m.nombre;
  el.motoPrecio.textContent = formatCOP(m.precio);
  el.motoFinanc.textContent = m.financiado;
  el.motoDesc.textContent   = m.descripcion;
  el.motoTags.innerHTML     = m.tags.map(t => `<span class="tag">${t}</span>`).join('');
  el.motoSpecs.innerHTML    = buildSpecs(m);

  /* WhatsApp URLs */
  refreshWhatsApp(m);

  /* Actualizar y centrar pills del selector en móvil */
  document.querySelectorAll('.moto-pill').forEach((btn, i) => {
    const isActive = (i === idx);
    btn.classList.toggle('active', isActive);
    btn.style.setProperty('--acento', MOTOS[i].acento);
    if (isActive) {
      btn.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }
  });

  /* Actualizar URL en historial sin recargar */
  const url = new URL(window.location);
  url.searchParams.set('moto', m.id);
  window.history.replaceState({}, '', url);
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
    `¿Puedes darme más información sobre disponibilidad y financiación? 🏍️`
  );
  const waUrl = `https://wa.me/${CONFIG.whatsapp}?text=${txt}`;
  if (el.waBtn) el.waBtn.href = waUrl;
  if (el.panelWaBtn) el.panelWaBtn.href = waUrl;
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
    if (btn && +btn.dataset.idx !== state.motoIdx) {
      loadMoto(+btn.dataset.idx);
    }
  });
}

/* ══════════════════════════════════════════════
   ESTADO Y CONTROL DE CÁMARA LIGERA (Ultra Rápida)
══════════════════════════════════════════════ */
const cameraState = {
  tipTimer: null,
};

function showArCamTip(text) {
  if (!el.arCamTip || !el.arCamTipText) return;
  el.arCamTipText.textContent = text;
  el.arCamTip.style.opacity = '1';
  clearTimeout(cameraState.tipTimer);
  cameraState.tipTimer = setTimeout(() => {
    if (el.arCamTip) el.arCamTip.style.opacity = '0';
  }, 3500);
}

/* ══════════════════════════════════════════════
   SELECTOR DE MODO AR (Nativo 360° vs Cámara Web)
══════════════════════════════════════════════ */
function requestAR() {
  openArChoiceModal();
}

function openArChoiceModal() {
  if (el.arChoiceModal) {
    el.arChoiceModal.classList.remove('hidden');
  }
}

function closeArChoiceModal() {
  if (el.arChoiceModal) {
    el.arChoiceModal.classList.add('hidden');
  }
}

function launchNativeAR() {
  closeArChoiceModal();

  // Activar AR nativo en el elemento principal <model-viewer>
  // En iPhone abre Apple ARKit Quick Look con detección de piso y órbita física 360°
  // En Android abre Google Scene Viewer con ARCore
  if (el.mv) {
    try {
      showARToast('Iniciando Realidad Aumentada nativa...');
      el.mv.activateAR();
    } catch (err) {
      console.warn('activateAR falló, usando cámara alternativa:', err);
      showARToast('Iniciando modo cámara alternativa...');
      setTimeout(startCameraAR, 800);
    }
  } else {
    startCameraAR();
  }
}

function showARToast(msg) {
  const m = MOTOS[state.motoIdx];
  if (el.arToastMsg) el.arToastMsg.textContent = msg || `Iniciando Cámara AR en Vivo...`;
  if (el.arToast) {
    el.arToast.classList.remove('hidden');
    setTimeout(() => el.arToast.classList.add('hidden'), 4000);
  }
}

/* ══════════════════════════════════════════════
   CÁMARA AR UNIVERSAL (WebAR Passthrough)
   Funciona en el 100% de iPhones y Androids con cámara web
══════════════════════════════════════════════ */
async function startCameraAR() {
  closeArChoiceModal();
  const m = MOTOS[state.motoIdx];

  try {
    // Solicitar cámara trasera (environment) de alta resolución
    const constraints = {
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1920 },
        height: { ideal: 1080 },
      },
      audio: false,
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    state.cameraStream = stream;

    // Configurar video para iOS Safari y Android
    el.arCameraFeed.setAttribute('playsinline', '');
    el.arCameraFeed.setAttribute('webkit-playsinline', '');
    el.arCameraFeed.srcObject = stream;
    await el.arCameraFeed.play();

    state.isCameraActive = true;
    el.arCameraView.classList.remove('hidden');
    el.arCamMotoNombre.textContent = m.nombre;

    // Cargar modelo 3D con controles táctiles nativos de alto rendimiento
    el.cameraMv.setAttribute('src', m.glb);
    el.cameraMv.cameraTarget = '0m 0.45m 0m';
    el.cameraMv.cameraOrbit = '0deg 78deg 2.6m';
    el.cameraMv.fieldOfView = '35deg';

    showArCamTip('Arrastra para girar · Pellizca para cambiar tamaño');

  } catch (err) {
    console.warn('Error accediendo a la cámara:', err);
    alert('Para ver la moto en tu espacio, permite el acceso a la cámara en el navegador.');
  }
}

function stopCameraAR() {
  if (state.cameraStream) {
    state.cameraStream.getTracks().forEach(track => track.stop());
    state.cameraStream = null;
  }

  state.isCameraActive = false;
  el.arCameraView.classList.add('hidden');
  el.arCameraFeed.srcObject = null;
}

/* ══════════════════════════════════════════════
   EFECTOS DE AUDIO SINTETIZADOS (Web Audio API)
   Sin archivos externos: instantáneo en 3G/4G y compatible con iOS y Android
══════════════════════════════════════════════ */
let audioCtx = null;
function getAudioContext() {
  if (!audioCtx) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (AudioCtx) audioCtx = new AudioCtx();
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playCameraShutterSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;

    // Click 1: Apertura de cortinilla mecánica
    const osc1 = ctx.createOscillator();
    const gain1 = ctx.createGain();
    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(850, now);
    osc1.frequency.exponentialRampToValueAtTime(140, now + 0.07);

    gain1.gain.setValueAtTime(0.4, now);
    gain1.gain.exponentialRampToValueAtTime(0.01, now + 0.07);

    osc1.connect(gain1);
    gain1.connect(ctx.destination);
    osc1.start(now);
    osc1.stop(now + 0.07);

    // Click 2: Cierre de obturador tras 60ms
    setTimeout(() => {
      try {
        const now2 = ctx.currentTime;
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(450, now2);
        osc2.frequency.exponentialRampToValueAtTime(90, now2 + 0.09);

        gain2.gain.setValueAtTime(0.35, now2);
        gain2.gain.exponentialRampToValueAtTime(0.01, now2 + 0.09);

        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        osc2.start(now2);
        osc2.stop(now2 + 0.09);
      } catch (_) {}
    }, 60);
  } catch (_) {}
}

function playCountdownBeep(isFinal) {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(isFinal ? 1350 : 750, now);
    gain.gain.setValueAtTime(0.35, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + (isFinal ? 0.22 : 0.12));

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + (isFinal ? 0.22 : 0.12));
  } catch (_) {}
}

/* ══════════════════════════════════════════════
   FLUJO DE CAPTURA FOTOGRÁFICA INSTANTÁNEA
══════════════════════════════════════════════ */
function triggerPhotoCapture() {
  if (state.isCapturing) return;
  executePhotoSnap();
}

async function executePhotoSnap() {
  state.isCapturing = true;

  // Estado UI en el botón obturador
  if (el.arCamCapture) el.arCamCapture.classList.add('capturing');

  // Sonido de obturador y hápticos
  playCameraShutterSound();
  try { if (navigator.vibrate) navigator.vibrate([40, 30, 60]); } catch (_) {}

  // Flash blanco en pantalla
  if (el.cameraFlash) {
    el.cameraFlash.classList.remove('hidden', 'fade');
    setTimeout(() => {
      el.cameraFlash.classList.add('fade');
      setTimeout(() => el.cameraFlash.classList.add('hidden'), 350);
    }, 45);
  }

  const video = el.arCameraFeed;
  const canvas = el.arCaptureCanvas;
  if (!video || !video.videoWidth) {
    resetShutterButton();
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');

  // 1. Fotograma en vivo de la cámara en alta resolución
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // 2. Render 3D de model-viewer
  try {
    const dataUrl = await el.cameraMv.toDataURL('image/png');
    const motoImg = new Image();
    motoImg.crossOrigin = 'anonymous';
    motoImg.onload = () => {
      // Sombra elíptica realista en el suelo
      const shadowX = canvas.width * 0.5;
      const shadowY = canvas.height * 0.78;
      const shadowRx = canvas.width * 0.35;
      const shadowRy = 35;

      const grad = ctx.createRadialGradient(shadowX, shadowY, 0, shadowX, shadowY, shadowRx);
      grad.addColorStop(0, 'rgba(0, 0, 0, 0.65)');
      grad.addColorStop(0.5, 'rgba(0, 0, 0, 0.28)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.ellipse(shadowX, shadowY, shadowRx, shadowRy, 0, 0, Math.PI * 2);
      ctx.fill();

      // Dibujar modelo 3D
      ctx.drawImage(motoImg, 0, 0, canvas.width, canvas.height);

      // 3. Banner fotográfico inferior tipo editorial automotriz
      const m = MOTOS[state.motoIdx];
      const barHeight = Math.max(100, Math.round(canvas.height * 0.115));
      const barGrad = ctx.createLinearGradient(0, canvas.height - barHeight - 45, 0, canvas.height);
      barGrad.addColorStop(0, 'rgba(11, 15, 25, 0)');
      barGrad.addColorStop(0.35, 'rgba(11, 15, 25, 0.78)');
      barGrad.addColorStop(1, 'rgba(11, 15, 25, 0.96)');
      ctx.fillStyle = barGrad;
      ctx.fillRect(0, canvas.height - barHeight - 45, canvas.width, barHeight + 45);

      // Franja de acento inferior con el color de la marca
      ctx.fillStyle = m.acento || '#a3e635';
      ctx.fillRect(0, canvas.height - 7, canvas.width, 7);

      // Textos profesionales
      const padX = Math.round(canvas.width * 0.05);
      const baseFontSize = Math.max(22, Math.round(canvas.width * 0.034));

      // Nombre y marca
      ctx.font = `bold ${Math.round(baseFontSize * 1.3)}px 'Space Grotesk', system-ui, sans-serif`;
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'left';
      ctx.fillText(m.nombre, padX, canvas.height - Math.round(barHeight * 0.55));

      // Precio en acento
      ctx.font = `bold ${Math.round(baseFontSize * 1.05)}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = m.acento || '#a3e635';
      ctx.fillText(formatCOP(m.precio), padX, canvas.height - Math.round(barHeight * 0.2));

      // Sello derecho
      ctx.font = `700 ${Math.round(baseFontSize * 0.85)}px 'Space Grotesk', system-ui, sans-serif`;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.textAlign = 'right';
      ctx.fillText('MotosAR Colombia', canvas.width - padX, canvas.height - Math.round(barHeight * 0.55));

      const dateStr = new Date().toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
      ctx.font = `500 ${Math.round(baseFontSize * 0.7)}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = 'rgba(203, 213, 225, 0.8)';
      ctx.fillText(`Catálogo AR · ${dateStr}`, canvas.width - padX, canvas.height - Math.round(barHeight * 0.2));

      // 4. Exportar a Blob y URL
      canvas.toBlob(blob => {
        if (!blob) {
          fallbackExport(canvas, m);
          return;
        }

        if (state.lastPhotoUrl) URL.revokeObjectURL(state.lastPhotoUrl);
        state.lastPhotoBlob = blob;
        const photoUrl = URL.createObjectURL(blob);
        state.lastPhotoUrl = photoUrl;

        el.photoPreviewImg.src = photoUrl;
        el.photoDownloadBtn.href = photoUrl;
        el.photoDownloadBtn.download = `MotosAR-${m.id}.png`;
        el.photoMotoBadge.textContent = m.nombre;

        const waText = encodeURIComponent(
          `¡Hola! Probé la *${m.nombre}* en mi espacio en Realidad Aumentada (MotosAR) y quiero cotizarla. Precio: ${formatCOP(m.precio)}`
        );
        el.photoWaBtn.href = `https://wa.me/${CONFIG.whatsapp}?text=${waText}`;

        el.photoModal.classList.remove('hidden');
        resetShutterButton();
      }, 'image/png');
    };
    motoImg.src = dataUrl;
  } catch (err) {
    console.error('Error procesando foto:', err);
    fallbackExport(canvas, MOTOS[state.motoIdx]);
  }
}

function fallbackExport(canvas, m) {
  const finalPhoto = canvas.toDataURL('image/png');
  el.photoPreviewImg.src = finalPhoto;
  el.photoDownloadBtn.href = finalPhoto;
  el.photoDownloadBtn.download = `MotosAR-${m.id}.png`;
  el.photoMotoBadge.textContent = m.nombre;
  el.photoModal.classList.remove('hidden');
  resetShutterButton();
}

function resetShutterButton() {
  state.isCapturing = false;
  if (el.arCamCapture) el.arCamCapture.classList.remove('capturing');
}

async function shareARPhoto() {
  const m = MOTOS[state.motoIdx];

  // Intento 1: Web Share API nativo con archivo de imagen (iOS Safari y Android)
  if (state.lastPhotoBlob && navigator.canShare) {
    try {
      const file = new File([state.lastPhotoBlob], `motosar-${m.id}.png`, { type: 'image/png' });
      if (navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: `${m.nombre} — MotosAR`,
          text: `¡Mira cómo se ve la ${m.nombre} en mi casa en Realidad Aumentada! Precio: ${formatCOP(m.precio)}. Cotízala en: ${window.location.origin}${window.location.pathname}`,
          files: [file],
        });
        return;
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.warn('Web Share no disponible para archivos:', err);
      } else {
        return; // Usuario canceló el modal nativo
      }
    }
  }

  // Intento 2: Compartir texto/enlace si no soporta archivos
  if (navigator.share) {
    try {
      await navigator.share({
        title: `${m.nombre} — MotosAR`,
        text: `¡Mira cómo se ve la ${m.nombre} en mi casa en Realidad Aumentada! Cotízala en: ${window.location.origin}${window.location.pathname}`,
        url: window.location.href,
      });
      return;
    } catch (_) {}
  }

  // Intento 3: Abrir WhatsApp con cotización
  const waText = encodeURIComponent(
    `¡Hola! Probé la *${m.nombre}* en mi espacio en Realidad Aumentada (MotosAR) y quiero cotizarla. Precio: ${formatCOP(m.precio)}`
  );
  window.open(`https://wa.me/${CONFIG.whatsapp}?text=${waText}`, '_blank');
}

/* ══════════════════════════════════════════════
   AR PROMPT (para visitas por QR con ?ar=true)
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
    setTimeout(requestAR, 400);
  }, { once: true });

  el.arPromptSkip.addEventListener('click', () => {
    el.arPrompt.classList.add('hidden');
  }, { once: true });
}

/* ══════════════════════════════════════════════
   FICHA PANEL TOGGLE (Bottom Sheet en Mobile)
══════════════════════════════════════════════ */
function toggleFicha(force) {
  const open = (force !== undefined) ? force : !state.fichaAbierta;
  state.fichaAbierta = open;
  el.fichaPanel.classList.toggle('open', open);
  el.fichaExpanded.setAttribute('aria-hidden', String(!open));
  document.body.classList.toggle('ficha-is-open', open);
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

  el.qrContainer.innerHTML = '';
  state.qrListo = false;

  el.qrModal.classList.remove('hidden');

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
        '<p style="color:#ef4444;font-size:12px;padding:12px;">Error generando QR</p>';
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
        No se pudo cargar el modelo 3D.<br/>Verifica la conexión.
      </p>`;
  });

  // Si Scene Viewer falla al lanzar AR, sugerir automáticamente la Cámara AR
  el.mv.addEventListener('ar-status', e => {
    if (e.detail.status === 'failed') {
      showARToast('Google Scene Viewer no compatible en este móvil.');
      setTimeout(() => startCameraAR(), 1200);
    }
  });

  /* Desvanecer tip al primer contacto */
  el.mv.addEventListener('camera-change', () => {
    if (el.viewerTip) el.viewerTip.style.opacity = '0';
  }, { once: true });
}

/* ══════════════════════════════════════════════
   EVENT LISTENERS
══════════════════════════════════════════════ */
function initEvents() {
  /* Botón AR flotante principal */
  el.arFloatBtn.addEventListener('click', requestAR);

  /* Botón AR dentro de la ficha técnica */
  if (el.panelArBtn) {
    el.panelArBtn.addEventListener('click', requestAR);
  }

  /* Controles de Cámara Simplificada */
  if (el.arCamClose) el.arCamClose.addEventListener('click', stopCameraAR);
  if (el.arCamCapture) el.arCamCapture.addEventListener('click', triggerPhotoCapture);
  if (el.arCamPrev) {
    el.arCamPrev.addEventListener('click', () => {
      loadMoto((state.motoIdx - 1 + MOTOS.length) % MOTOS.length);
    });
  }
  if (el.arCamNext) {
    el.arCamNext.addEventListener('click', () => {
      loadMoto((state.motoIdx + 1) % MOTOS.length);
    });
  }
  if (el.arCamRotate180) {
    el.arCamRotate180.addEventListener('click', () => {
      if (!el.cameraMv) return;
      const curOrbit = el.cameraMv.getAttribute('camera-orbit') || '0deg 78deg 2.6m';
      const parts = curOrbit.trim().split(/\s+/);
      const currentDeg = parseFloat(parts[0]) || 0;
      const nextDeg = (currentDeg + 180) % 360;
      el.cameraMv.cameraOrbit = `${nextDeg}deg 78deg 2.6m`;
      try { if (navigator.vibrate) navigator.vibrate(30); } catch (_) {}
    });
  }

  /* Modal Selector AR */
  if (el.arChoiceClose) {
    el.arChoiceClose.addEventListener('click', closeArChoiceModal);
  }
  if (el.arChoiceModal) {
    el.arChoiceModal.addEventListener('click', e => {
      if (e.target === el.arChoiceModal) closeArChoiceModal();
    });
  }
  if (el.btnLaunchNativeAR) {
    el.btnLaunchNativeAR.addEventListener('click', launchNativeAR);
  }
  if (el.btnLaunchCameraAR) {
    el.btnLaunchCameraAR.addEventListener('click', () => {
      closeArChoiceModal();
      startCameraAR();
    });
  }

  /* Modal / Sheet de Foto Capturada */
  el.photoModalClose.addEventListener('click', () => el.photoModal.classList.add('hidden'));
  el.photoRetakeBtn.addEventListener('click', () => el.photoModal.classList.add('hidden'));
  if (el.photoNativeShareBtn) {
    el.photoNativeShareBtn.addEventListener('click', shareARPhoto);
  }

  /* Flechas de navegación táctil en catálogo */
  el.navPrev.addEventListener('click', () => {
    loadMoto((state.motoIdx - 1 + MOTOS.length) % MOTOS.length);
  });
  el.navNext.addEventListener('click', () => {
    loadMoto((state.motoIdx + 1) % MOTOS.length);
  });

  /* Ficha toggle */
  el.fichaToggle.addEventListener('click', () => toggleFicha());
  el.fichaCompact.addEventListener('click', () => {
    if (window.innerWidth < 1024) toggleFicha();
  });

  /* QR modal */
  el.qrBtn.addEventListener('click', openQRModal);
  el.qrModalClose.addEventListener('click', closeQRModal);
  el.qrModal.addEventListener('click', e => {
    if (e.target === el.qrModal) closeQRModal();
  });
  el.printBtn.addEventListener('click', printSticker);

  /* Navegación por teclado */
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if (el.arChoiceModal && !el.arChoiceModal.classList.contains('hidden')) { closeArChoiceModal(); return; }
      if (!el.arCameraView.classList.contains('hidden')) { stopCameraAR(); return; }
      if (!el.photoModal.classList.contains('hidden')) { el.photoModal.classList.add('hidden'); return; }
      if (!el.qrModal.classList.contains('hidden')) { closeQRModal(); return; }
      if (state.fichaAbierta) { toggleFicha(false); return; }
    }
    if (document.activeElement.tagName === 'INPUT') return;
    if (e.key === 'ArrowRight') loadMoto((state.motoIdx + 1) % MOTOS.length);
    if (e.key === 'ArrowLeft')  loadMoto((state.motoIdx - 1 + MOTOS.length) % MOTOS.length);
    const n = parseInt(e.key);
    if (n >= 1 && n <= MOTOS.length) loadMoto(n - 1);
  });

  /* Swipe táctil en la ficha técnica */
  let touchStartX = 0;
  let touchStartY = 0;
  el.fichaPanel.addEventListener('touchstart', e => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }, { passive: true });

  el.fichaPanel.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    const dy = e.changedTouches[0].clientY - touchStartY;

    if (Math.abs(dy) > 40 && Math.abs(dy) > Math.abs(dx)) {
      if (dy < -40 && !state.fichaAbierta) toggleFicha(true);
      else if (dy > 40 && state.fichaAbierta) toggleFicha(false);
      return;
    }

    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0) loadMoto((state.motoIdx + 1) % MOTOS.length);
      else        loadMoto((state.motoIdx - 1 + MOTOS.length) % MOTOS.length);
    }
  }, { passive: true });

  /* Ocultar viewerTip automáticamente a los 4s */
  setTimeout(() => {
    if (el.viewerTip) el.viewerTip.style.opacity = '0';
  }, 4500);
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
