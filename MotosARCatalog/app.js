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
    id:          'tvs-raider',
    nombre:      'TVS Raider 125',
    marca:       'TVS',
    modelo:      'Raider 125',
    cilindraje:  '124.8 cc',
    potencia:    '11.4 HP @ 7.500 rpm',
    torque:      '11.2 Nm @ 6.000 rpm',
    transmision: '5 velocidades',
    peso:        '123 kg',
    tanque:      '10 L',
    precio:      6290000,
    financiado:  'Desde $118.000/mes',
    cleanGlb:    '/models/android/tvs-raider.glb',
    arGlb:       '/models/android/tvs-raider_ar.glb',
    cleanUsdz:   '/models/ios/tvs-raider.usdz',
    arUsdz:      '/models/ios/tvs-raider_ar.usdz',
    glb:         '/models/android/tvs-raider_ar.glb',
    usdz:        '/models/ios/tvs-raider_ar.usdz',
    poster:      '/posters/tvs-raider.png',
    acento:      '#38bdf8',   /* cyan-400 */
    tags:        ['Sport', 'Premium', '125cc', 'Doble Disco'],
    descripcion: 'Tecnología Racing DNA de TVS. Diseño deportivo premium con panel LCD, faros LED y freno de disco delantero. Modelo 3D optimizado para Realidad Aumentada.',
    disponible:  true,
    scale:       '1 1 1',
  },
  {
    id:          'akt-nkd',
    nombre:      'AKT NKD 125',
    marca:       'AKT',
    modelo:      'NKD 125',
    cilindraje:  '125 cc',
    potencia:    '11 HP @ 8.000 rpm',
    torque:      '8.8 Nm @ 6.000 rpm',
    transmision: '5 velocidades',
    peso:        '118 kg',
    tanque:      '13.5 L',
    precio:      5990000,
    financiado:  'Desde $112.000/mes',
    cleanGlb:    '/models/android/akt-nkd.glb',
    arGlb:       '/models/android/akt-nkd_ar.glb',
    cleanUsdz:   '/models/ios/akt-nkd.usdz',
    arUsdz:      '/models/ios/akt-nkd_ar.usdz',
    glb:         '/models/android/akt-nkd_ar.glb',
    usdz:        '/models/ios/akt-nkd_ar.usdz',
    poster:      '/posters/akt-nkd.png',
    acento:      '#a3e635',   /* lime-400 */
    tags:        ['Ciudad', 'Café Racer', '125cc', 'Freno Disco'],
    descripcion: 'Estilo café racer moderno con motor 4T de alto rendimiento. Ligera, ágil y económica. Modelo 3D optimizado para Realidad Aumentada.',
    disponible:  true,
    scale:       '1 1 1',
  },
  {
    id:          'pulsar-ns200',
    nombre:      'Pulsar NS 200',
    marca:       'Bajaj',
    modelo:      'Pulsar NS 200',
    cilindraje:  '199.5 cc',
    potencia:    '24.5 HP @ 9.750 rpm',
    torque:      '18.74 Nm @ 8.000 rpm',
    transmision: '6 velocidades',
    peso:        '156 kg',
    tanque:      '12 L',
    precio:      12490000,
    financiado:  'Desde $234.000/mes',
    cleanGlb:    '/models/android/pulsar-ns200.glb',
    arGlb:       '/models/android/pulsar-ns200_ar.glb',
    cleanUsdz:   '/models/ios/pulsar-ns200.usdz',
    arUsdz:      '/models/ios/pulsar-ns200_ar.usdz',
    glb:         '/models/android/pulsar-ns200_ar.glb',
    usdz:        '/models/ios/pulsar-ns200_ar.usdz',
    poster:      '/posters/pulsar-ns200.png',
    acento:      '#f43f5e',   /* rose-500 */
    tags:        ['Sport', 'Performance', '200cc', 'Triple Chispa'],
    descripcion: 'Naked sport con motor DTS-Fi de triple chispa y refrigeración líquida. Máxima potencia y aceleración. Modelo 3D optimizado para Realidad Aumentada.',
    disponible:  true,
    scale:       '1 1 1',
  },
  {
    id:          'bajaj-boxer',
    nombre:      'Bajaj Boxer 100',
    marca:       'Bajaj',
    modelo:      'Boxer 100',
    cilindraje:  '100 cc',
    potencia:    '8.2 HP @ 7.500 rpm',
    torque:      '8.05 Nm @ 5.000 rpm',
    transmision: '4 velocidades',
    peso:        '113 kg',
    tanque:      '15 L',
    precio:      4490000,
    financiado:  'Desde $84.000/mes',
    cleanGlb:    '/models/android/bajaj-boxer.glb',
    arGlb:       '/models/android/bajaj-boxer_ar.glb',
    cleanUsdz:   '/models/ios/bajaj-boxer.usdz',
    arUsdz:      '/models/ios/bajaj-boxer_ar.usdz',
    glb:         '/models/android/bajaj-boxer_ar.glb',
    usdz:        '/models/ios/bajaj-boxer_ar.usdz',
    poster:      '/posters/bajaj-boxer.png',
    acento:      '#eab308',   /* amber-500 */
    tags:        ['Trabajo', 'Campo', '100cc', 'Ultra Rendimiento'],
    descripcion: 'La moto más robusta y guerrera del país. Durabilidad comprobada y mínimo consumo de combustible. Modelo 3D optimizado para Realidad Aumentada.',
    disponible:  true,
    scale:       '1 1 1',
  },
  {
    id:          'hero-eco',
    nombre:      'Hero Eco Deluxe',
    marca:       'Hero',
    modelo:      'Eco Deluxe',
    cilindraje:  '97.2 cc',
    potencia:    '7.9 HP @ 8.000 rpm',
    torque:      '7.55 Nm @ 5.000 rpm',
    transmision: '4 velocidades',
    peso:        '112 kg',
    tanque:      '10.5 L',
    precio:      4190000,
    financiado:  'Desde $79.000/mes',
    cleanGlb:    '/models/android/hero-eco.glb',
    arGlb:       '/models/android/hero-eco_ar.glb',
    cleanUsdz:   '/models/ios/hero-eco.usdz',
    arUsdz:      '/models/ios/hero-eco_ar.usdz',
    glb:         '/models/android/hero-eco_ar.glb',
    usdz:        '/models/ios/hero-eco_ar.usdz',
    poster:      '/posters/hero-eco.png',
    acento:      '#10b981',   /* emerald-500 */
    tags:        ['Ahorro', 'Ciudad', '100cc', 'i3S Ahorro'],
    descripcion: 'La campeona de la economía con tecnología i3S de ahorro de combustible. Confortable y confiable. Modelo 3D optimizado para Realidad Aumentada.',
    disponible:  true,
    scale:       '1 1 1',
  },
];

/* ══════════════════════════════════════════════
   ESTADO DE LA APP
══════════════════════════════════════════════ */
const state = {
  motoIdx:        0,
  arMode:         'ar',       /* 'ar' (con anotaciones 3D) o 'clean' (moto limpia) */
  fichaAbierta:   false,
  fichaAbierta:   false,
  arPrompt:       false,
  qrListo:        false,
  loadTimer:      null,
  cameraStream:   null,
  cameraScale:    1.0,
  cameraTimerSec: 0,
  isCameraActive: false,
  isCapturing:    false,
  isModelReady:   false,
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
    modelStatusPill:        document.getElementById('modelStatusPill'),
    modelStatusText:        document.getElementById('modelStatusText'),
    modelStatusDot:         document.getElementById('modelStatusDot'),
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
    downloadCardBtn:    document.getElementById('downloadCardBtn'),
    copyUrlBtn:         document.getElementById('copyUrlBtn'),
    modeBtnAr:          document.getElementById('modeBtnAr'),
    modeBtnClean:       document.getElementById('modeBtnClean'),
    viewerControlsBar:  document.getElementById('viewerControlsBar'),
    btnToggleRotate:    document.getElementById('btnToggleRotate'),
    btnRotateIconPause: document.getElementById('btnRotateIconPause'),
    btnRotateIconPlay:  document.getElementById('btnRotateIconPlay'),
    btnRotateLabel:     document.getElementById('btnRotateLabel'),
    btnResetView:       document.getElementById('btnResetView'),
    btnToggleLabels:    document.getElementById('btnToggleLabels'),
    labelToggleText:    document.getElementById('labelToggleText'),
    btnFullscreen:      document.getElementById('btnFullscreen'),
    fsIconEnter:        document.getElementById('fsIconEnter'),
    fsIconExit:         document.getElementById('fsIconExit'),
    fsLabel:            document.getElementById('fsLabel'),
    arToast:            document.getElementById('arToast'),
    arToastMsg:         document.getElementById('arToastMsg'),
    arToastTitle:       document.getElementById('arToastTitle'),
    arToastIcon:        document.getElementById('arToastIcon'),

    /* Modal Selector AR */
    arChoiceModal:          document.getElementById('arChoiceModal'),
    arChoiceClose:          document.getElementById('arChoiceClose'),
    btnLaunchNativeAR:      document.getElementById('btnLaunchNativeAR'),
    btnLaunchNativeARThumb: document.getElementById('btnLaunchNativeARThumb'),
    arChoiceIosTip:         document.getElementById('arChoiceIosTip'),
    btnLaunchCameraAR:      document.getElementById('btnLaunchCameraAR'),


    /* Vista Cámara AR Universal con Anclaje Espacial */
    arCameraView:           document.getElementById('arCameraView'),
    arCameraFeed:           document.getElementById('arCameraFeed'),
    arCaptureCanvas:        document.getElementById('arCaptureCanvas'),
    cameraFlash:            document.getElementById('cameraFlash'),
    cameraCountdownOverlay: document.getElementById('cameraCountdownOverlay'),
    cameraCountdownNumber:  document.getElementById('cameraCountdownNumber'),
    arSpatialStage:         document.getElementById('arSpatialStage'),
    arGroundReticle:        document.getElementById('arGroundReticle'),
    arCameraModelWrap:      document.getElementById('arCameraModelWrap'),
    arFloorShadow:          document.getElementById('arFloorShadow'),
    cameraMv:               document.getElementById('cameraMv'),
    arCamClose:             document.getElementById('arCamClose'),
    arCamMotoNombre:        document.getElementById('arCamMotoNombre'),
    arCamTimerBtn:          document.getElementById('arCamTimerBtn'),
    arCamTimerBadge:        document.getElementById('arCamTimerBadge'),
    arCamRotate180:         document.getElementById('arCamRotate180'),
    arCamTip:               document.getElementById('arCamTip'),
    arCamTipText:           document.getElementById('arCamTipText'),
    arOrbitBar:             document.getElementById('arOrbitBar'),
    arCamPrev:              document.getElementById('arCamPrev'),
    arCamNext:              document.getElementById('arCamNext'),
    arCamCapture:           document.getElementById('arCamCapture'),
    arShutterInner:         document.getElementById('arShutterInner'),
    arShutterSpinner:       document.getElementById('arShutterSpinner'),
    arShutterLabel:         document.getElementById('arShutterLabel'),

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
   ESTADO DINÁMICO DEL BOTÓN AR
══════════════════════════════════════════════ */
function setArButtonReady(isReady) {
  state.isModelReady = isReady;
  if (!el.arFloatBtn) return;
  const textSpan = el.arFloatBtn.querySelector('.ar-float-text');
  const ring = el.arFloatBtn.querySelector('.ar-float-ring');

  const m = MOTOS[state.motoIdx];
  if (m && !m.disponible) {
    el.arFloatBtn.setAttribute('disabled', 'true');
    el.arFloatBtn.classList.remove('is-loading');
    if (textSpan) textSpan.textContent = 'Próximamente en AR';
    if (ring) ring.style.display = 'none';
    return;
  }

  if (isReady) {
    el.arFloatBtn.removeAttribute('disabled');
    el.arFloatBtn.classList.remove('is-loading');
    if (textSpan) textSpan.textContent = 'Ver en mi espacio (AR)';
    if (ring) ring.style.display = '';
  } else {
    el.arFloatBtn.setAttribute('disabled', 'true');
    el.arFloatBtn.classList.add('is-loading');
    if (textSpan) textSpan.textContent = 'Cargando modelo 3D…';
    if (ring) ring.style.display = 'none';
  }
}

/* ══════════════════════════════════════════════
   CARGAR MOTO
══════════════════════════════════════════════ */
function loadMoto(idx) {
  state.motoIdx = idx;
  state.qrListo = false;
  const m = MOTOS[idx];

  /* Color de acento dinámico */
  if (el.accentBar) el.accentBar.style.background = m.acento;
  document.documentElement.style.setProperty('--accent-ar', m.acento);

  /* Carga del modelo 3D principal */
  setArButtonReady(false);
  clearTimeout(state.loadTimer);
  el.loadOverlay.classList.remove('hidden', 'fade-out');
  el.loadBar.style.width = '0%';

  const currentMode = state.arMode || 'ar';
  const targetGlb = (currentMode === 'ar' ? m.arGlb : m.cleanGlb) || m.glb;
  const targetUsdz = (currentMode === 'ar' ? m.arUsdz : m.cleanUsdz) || m.usdz;

  // Actualizar estado visual de los botones de modo
  if (el.modeBtnAr && el.modeBtnClean) {
    el.modeBtnAr.classList.toggle('active', currentMode === 'ar');
    el.modeBtnClean.classList.toggle('active', currentMode === 'clean');
  }
  if (el.btnToggleLabels && el.labelToggleText) {
    const isAr = (currentMode === 'ar');
    el.btnToggleLabels.classList.toggle('active-gold', isAr);
    el.labelToggleText.textContent = isAr ? 'Ocultar etiquetas' : 'Mostrar etiquetas';
    el.btnToggleLabels.title = isAr ? 'Ocultar etiquetas y ver moto limpia' : 'Mostrar fichas técnicas 3D';
  }

  el.mv.setAttribute('poster', m.poster);
  if (targetUsdz) {
    el.mv.setAttribute('ios-src', targetUsdz);
  } else {
    el.mv.removeAttribute('ios-src');
  }

  // Asignar directamente src si cambia
  if (el.mv.getAttribute('src') !== targetGlb) {
    el.mv.setAttribute('src', targetGlb);
  } else {
    hideLoadOverlay();
  }
  el.mv.scale = m.scale || '1 1 1';

  /* Configurar enlace nativo para Apple Quick Look (iOS) */
  if (el.btnLaunchNativeAR) {
    if (targetUsdz) {
      const fullUsdz = window.location.origin + targetUsdz + '#allowsContentScaling=0';
      el.btnLaunchNativeAR.setAttribute('href', fullUsdz);
      el.btnLaunchNativeAR.setAttribute('rel', 'ar');
    } else {
      el.btnLaunchNativeAR.removeAttribute('href');
    }
    if (el.btnLaunchNativeARThumb) {
      el.btnLaunchNativeARThumb.src = window.location.origin + m.poster;
    }
  }

  /* Si la cámara AR está activa, sincronizar también el modelo de la cámara */
  if (state.isCameraActive && el.cameraMv) {
    el.arCamMotoNombre.textContent = m.nombre;
    el.cameraMv.setAttribute('src', targetGlb);
    if (targetUsdz) el.cameraMv.setAttribute('ios-src', targetUsdz);
  }

  /* Ficha técnica */
  if (el.motoMarca)  el.motoMarca.textContent  = m.marca;
  if (el.motoNombre) el.motoNombre.textContent = m.nombre;
  if (el.motoPrecio) el.motoPrecio.textContent = formatCOP(m.precio);
  if (el.motoFinanc) el.motoFinanc.textContent = m.financiado;
  if (el.motoDesc)   el.motoDesc.textContent   = m.descripcion;
  if (el.motoTags)   el.motoTags.innerHTML     = m.tags.map(t => `<span class="tag">${t}</span>`).join('');
  if (el.motoSpecs)  el.motoSpecs.innerHTML    = buildSpecs(m);

  /* WhatsApp URLs */
  refreshWhatsApp(m);

  /* Actualizar y centrar pills del selector en móvil y escritorio */
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

  /* Timeout de seguridad rápido para evitar cuelgues (8 segundos) */
  state.loadTimer = setTimeout(() => hideLoadOverlay(), 8000);
}

function setViewModelMode(mode) {
  state.arMode = mode;
  const m = MOTOS[state.motoIdx];
  const targetGlb = (mode === 'ar' ? m.arGlb : m.cleanGlb) || m.glb;
  const targetUsdz = (mode === 'ar' ? m.arUsdz : m.cleanUsdz) || m.usdz;

  if (el.modeBtnAr && el.modeBtnClean) {
    el.modeBtnAr.classList.toggle('active', mode === 'ar');
    el.modeBtnClean.classList.toggle('active', mode === 'clean');
  }
  if (el.btnToggleLabels && el.labelToggleText) {
    const isAr = (mode === 'ar');
    el.btnToggleLabels.classList.toggle('active-gold', isAr);
    el.labelToggleText.textContent = isAr ? 'Ocultar etiquetas' : 'Mostrar etiquetas';
    el.btnToggleLabels.title = isAr ? 'Ocultar etiquetas y ver moto limpia' : 'Mostrar fichas técnicas 3D';
  }

  // Breve micro-loader de feedback
  el.loadOverlay.classList.remove('hidden', 'fade-out');
  el.loadBar.style.width = '40%';
  clearTimeout(state.loadTimer);
  state.loadTimer = setTimeout(() => hideLoadOverlay(), 6000);

  el.mv.setAttribute('src', targetGlb);
  if (targetUsdz) {
    el.mv.setAttribute('ios-src', targetUsdz);
  } else {
    el.mv.removeAttribute('ios-src');
  }

  if (el.btnLaunchNativeAR) {
    if (targetUsdz) {
      el.btnLaunchNativeAR.setAttribute('href', window.location.origin + targetUsdz + '#allowsContentScaling=0');
      el.btnLaunchNativeAR.setAttribute('rel', 'ar');
    } else {
      el.btnLaunchNativeAR.removeAttribute('href');
    }
  }

  if (state.isCameraActive && el.cameraMv) {
    el.cameraMv.setAttribute('src', targetGlb);
    if (targetUsdz) el.cameraMv.setAttribute('ios-src', targetUsdz);
  }

  // Actualizar modal QR si está abierto
  if (el.qrModal && !el.qrModal.classList.contains('hidden')) {
    openQRModal();
  }

  showARToast(mode === 'ar' ? '⚡ Modo Fichas Técnicas 3D activado' : '✨ Modo Moto Limpia activado');
}

function buildSpecs(m) {
  const specs = [
    {
      label: 'Potencia',
      val: m.potencia,
      icon: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'
    },
    {
      label: 'Torque',
      val: m.torque,
      icon: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
    },
    {
      label: 'Cilindraje',
      val: m.cilindraje,
      icon: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>'
    },
    {
      label: 'Tanque',
      val: m.tanque,
      icon: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>'
    },
    {
      label: 'Peso neto',
      val: m.peso,
      icon: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>'
    },
    {
      label: 'Transmisión',
      val: m.transmision,
      icon: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20v-6M6 20V10M18 20V4"/></svg>'
    },
  ];

  return `
    <div class="specs-grid">
      ${specs.map(s => `
        <div class="spec-card">
          <div class="spec-card-header">
            <span class="spec-card-icon">${s.icon}</span>
            <span class="spec-card-label">${s.label}</span>
          </div>
          <span class="spec-card-value">${s.val}</span>
        </div>
      `).join('')}
    </div>
  `;
}

function hideLoadOverlay() {
  clearTimeout(state.loadTimer);
  setArButtonReady(true);
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
       class="moto-pill${i === state.motoIdx ? ' active' : ''}${!m.disponible ? ' pill-disabled' : ''}"
       data-idx="${i}"
       style="--acento:${m.acento}"
       aria-label="${m.nombre}${!m.disponible ? ' (Próximamente)' : ''}"
     >
       <div class="pill-thumb-wrap">
         <img src="${m.poster}" alt="${m.nombre}" class="pill-thumb" loading="lazy" />
       </div>
       <div class="pill-info">
         <span class="pill-marca">${m.marca}</span>
         <span class="pill-modelo">${m.modelo}</span>
       </div>
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
   ESTADO Y ROTACIÓN SUAVE 360° (Botones sin giroscopio)
   Giro suave orgánico por interpolación lerp
══════════════════════════════════════════════ */
const orbitState = {
  currentDeg: 0,
  targetDeg: 0,
  animId: null,
  tipTimer: null,
};

function showArCamTip(text) {
  if (!el.arCamTip || !el.arCamTipText) return;
  el.arCamTipText.textContent = text;
  el.arCamTip.style.opacity = '1';
  clearTimeout(orbitState.tipTimer);
  orbitState.tipTimer = setTimeout(() => {
    if (el.arCamTip) el.arCamTip.style.opacity = '0';
  }, 3500);
}

function updateOrbitChipsUI(deg) {
  const norm = ((deg % 360) + 360) % 360;
  document.querySelectorAll('.ar-orbit-chip').forEach(btn => {
    const chipAngle = parseFloat(btn.dataset.angle);
    let diff = Math.abs(norm - chipAngle);
    if (diff > 180) diff = 360 - diff;
    btn.classList.toggle('active', diff < 45);
  });
}

function smoothRotateTo(targetDeg) {
  orbitState.targetDeg = ((targetDeg % 360) + 360) % 360;
  updateOrbitChipsUI(orbitState.targetDeg);
  try { if (navigator.vibrate) navigator.vibrate(25); } catch (_) {}

  if (orbitState.animId) cancelAnimationFrame(orbitState.animId);

  function animate() {
    if (!state.isCameraActive || !el.cameraMv) return;
    let diff = orbitState.targetDeg - orbitState.currentDeg;
    // Camino angular más corto [-180, 180]
    diff = ((diff + 180) % 360 + 360) % 360 - 180;

    if (Math.abs(diff) < 0.25) {
      orbitState.currentDeg = orbitState.targetDeg;
      el.cameraMv.cameraOrbit = `${orbitState.currentDeg.toFixed(1)}deg 78deg 2.6m`;
      orbitState.animId = null;
      return;
    }

    // Lerp suave del 13% para animación fluida y orgánica
    orbitState.currentDeg += diff * 0.13;
    orbitState.currentDeg = ((orbitState.currentDeg % 360) + 360) % 360;
    el.cameraMv.cameraOrbit = `${orbitState.currentDeg.toFixed(1)}deg 78deg 2.6m`;
    orbitState.animId = requestAnimationFrame(animate);
  }
  orbitState.animId = requestAnimationFrame(animate);
}

/* ══════════════════════════════════════════════
   SELECTOR DE MODO AR (Nativo 360° vs Cámara Web)
══════════════════════════════════════════════ */
function requestAR() {
  const m = MOTOS[state.motoIdx];
  if (m && !m.disponible) {
    showARToast('Este modelo estará disponible próximamente en 3D y AR.');
    return;
  }
  if (!state.isModelReady) return;
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

function launchNativeAR(e) {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const isInApp = /FBAN|FBAV|Instagram|WhatsApp|Line/i.test(navigator.userAgent);

  if (isIOS) {
    closeArChoiceModal();

    if (isInApp) {
      showARToast(
        'Si Quick Look no se abre en WhatsApp, toca (···) arriba y elige "Abrir en Safari", o usa el Modo Cámara.',
        'Consejo para iPhone',
        'info'
      );
    } else {
      showARToast('Iniciando Apple Quick Look (360° en piso real)...', 'Realidad Aumentada', 'info');
    }

    // En iOS dejamos que el evento de clic nativo sobre <a rel="ar" href="..."> proceda para que WebKit lance Quick Look
    return;
  }

  // En Android u otros navegadores:
  if (e && e.preventDefault) e.preventDefault();
  closeArChoiceModal();

  const m = MOTOS[state.motoIdx];
  const isAndroid = /Android/.test(navigator.userAgent);
  if (isAndroid && m && (m.arGlb || m.glb)) {
    showARToast('Iniciando Scene Viewer con infografía 3D...', 'Realidad Aumentada', 'info');
    const fullGlbUrl = new URL(m.arGlb || m.glb, window.location.origin).href;
    const intentUrl = `intent://arvr.google.com/scene-viewer/1.0?file=${encodeURIComponent(fullGlbUrl)}&mode=ar_only&resizable=false#Intent;scheme=https;package=com.google.ar.core;action=android.intent.action.VIEW;end;`;
    window.location.href = intentUrl;
    return;
  }

  if (el.mv) {
    try {
      showARToast('Iniciando Realidad Aumentada en tu espacio...', 'Realidad Aumentada', 'info');
      el.mv.activateAR();
    } catch (err) {
      console.warn('activateAR no disponible:', err);
      showARToast('El visor nativo no está disponible. Puedes usar el Modo Cámara Web.', 'Aviso', 'warning');
    }
  } else {
    showARToast('Visor 3D no inicializado.', 'Aviso', 'warning');
  }
}

function showARToast(msg, title = 'Realidad Aumentada', type = 'info') {
  if (el.arToastTitle) el.arToastTitle.textContent = title;
  if (el.arToastMsg) el.arToastMsg.textContent = msg || 'Iniciando Realidad Aumentada…';

  if (el.arToastIcon) {
    if (type === 'warning') {
      el.arToastIcon.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="color:#fbbf24;">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>
        </svg>
      `;
    } else if (type === 'success') {
      el.arToastIcon.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="color:#4ade80;">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      `;
    } else {
      el.arToastIcon.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="color:#38bdf8;">
          <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"/>
        </svg>
      `;
    }
  }

  if (el.arToast) {
    el.arToast.classList.remove('hidden', 'toast-info', 'toast-warning', 'toast-success');
    el.arToast.classList.add(`toast-${type}`);
    clearTimeout(state.toastTimer);
    el.arToast.classList.remove('hidden');
    state.toastTimer = setTimeout(() => {
      el.arToast.classList.add('hidden');
    }, type === 'warning' ? 5000 : 4000);
  }
}

/* ══════════════════════════════════════════════
   CÁMARA AR UNIVERSAL (WebAR Passthrough)
   Funciona en el 100% de iPhones y Androids con cámara web
══════════════════════════════════════════════ */
function unlockAudioOnIOS() {
  try {
    const ctx = getAudioContext();
    if (ctx && ctx.state === 'suspended') {
      ctx.resume();
    }
  } catch (_) {}
}

async function startCameraAR() {
  closeArChoiceModal();
  const m = MOTOS[state.motoIdx];

  // Desbloquear audio en iOS Safari mediante el toque directo del usuario
  unlockAudioOnIOS();

  // Pausar el visor 3D principal para liberar VRAM y GPU en iOS Safari
  if (el.mv) {
    try { el.mv.pause(); } catch (_) {}
  }

  try {
    let stream = null;
    const constraintsList = [
      { video: { facingMode: { ideal: 'environment' }, width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: false },
      { video: { facingMode: { ideal: 'environment' } }, audio: false },
      { video: true, audio: false }
    ];

    for (const constraints of constraintsList) {
      try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        if (stream) break;
      } catch (e) {
        console.warn('Constraint no soportado, probando siguiente opción:', constraints, e);
      }
    }

    if (!stream) {
      throw new Error('No se pudo acceder a la cámara trasera.');
    }

    state.cameraStream = stream;

    // Configurar video para iOS Safari y Android
    el.arCameraFeed.setAttribute('playsinline', '');
    el.arCameraFeed.setAttribute('webkit-playsinline', '');
    el.arCameraFeed.muted = true;
    el.arCameraFeed.playsInline = true;
    el.arCameraFeed.srcObject = stream;
    await el.arCameraFeed.play();

    state.isCameraActive = true;
    el.arCameraView.classList.remove('hidden');
    el.arCamMotoNombre.textContent = m.nombre;

    // Cargar modelo 3D en el visor de cámara transparente adaptado al piso
    el.cameraMv.setAttribute('src', m.glb);
    if (m.usdz) el.cameraMv.setAttribute('ios-src', m.usdz);
    el.cameraMv.scale = m.scale || '1 1 1';
    el.cameraMv.cameraTarget = '0m 0.45m 0m';
    el.cameraMv.cameraOrbit = '0deg 78deg 2.6m';
    el.cameraMv.fieldOfView = '35deg';
    setCameraScale(1.0);

    // Iniciar rotación orbital en 0° (vista frontal)
    orbitState.currentDeg = 0;
    orbitState.targetDeg = 0;
    if (orbitState.animId) {
      cancelAnimationFrame(orbitState.animId);
      orbitState.animId = null;
    }
    updateOrbitChipsUI(0);

    showArCamTip('Gira la moto suavemente con los botones o con el dedo');

  } catch (err) {
    console.warn('Error accediendo a la cámara:', err);
    if (el.mv) {
      try { el.mv.play(); } catch (_) {}
    }
    alert('Para ver la moto en tu espacio real, permite el acceso a la cámara en el navegador.');
  }
}

function stopCameraAR() {
  if (state.cameraStream) {
    state.cameraStream.getTracks().forEach(track => track.stop());
    state.cameraStream = null;
  }

  if (orbitState.animId) {
    cancelAnimationFrame(orbitState.animId);
    orbitState.animId = null;
  }

  state.isCameraActive = false;
  el.arCameraView.classList.add('hidden');
  el.arCameraFeed.srcObject = null;

  // Reanudar el visor 3D principal del fondo
  if (el.mv) {
    try { el.mv.play(); } catch (_) {}
  }
}

function setCameraScale(scale) {
  state.cameraScale = scale;
  if (el.cameraMv) {
    el.cameraMv.scale = `${scale} ${scale} ${scale}`;
  }
  document.querySelectorAll('.ar-scale-btn').forEach(b => {
    b.classList.toggle('active', parseFloat(b.dataset.scale) === scale);
  });
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

function toggleCameraTimer() {
  // Alterna entre 0s y 3s
  state.cameraTimerSec = (state.cameraTimerSec === 0) ? 3 : 0;
  if (el.arCamTimerBadge) {
    el.arCamTimerBadge.textContent = state.cameraTimerSec + 's';
  }
  if (el.arCamTimerBtn) {
    el.arCamTimerBtn.style.color = (state.cameraTimerSec > 0) ? 'var(--accent-ar)' : '#fff';
    el.arCamTimerBtn.style.borderColor = (state.cameraTimerSec > 0) ? 'var(--accent-ar)' : 'rgba(255,255,255,0.15)';
  }

  showArCamTip(state.cameraTimerSec > 0 ? '⏱️ Temporizador de 3s activado (prepárate para la foto)' : '⏱️ Temporizador desactivado');
  try { if (navigator.vibrate) navigator.vibrate(30); } catch (_) {}
}

/* ══════════════════════════════════════════════
   FLUJO DE CAPTURA FOTOGRÁFICA
══════════════════════════════════════════════ */
function triggerPhotoCapture() {
  if (state.isCapturing) return;

  if (state.cameraTimerSec > 0) {
    // Cuenta regresiva 3, 2, 1
    state.isCapturing = true;
    let count = state.cameraTimerSec;

    el.cameraCountdownOverlay.classList.remove('hidden');
    el.cameraCountdownNumber.textContent = count;
    playCountdownBeep(false);
    try { if (navigator.vibrate) navigator.vibrate(40); } catch (_) {}

    const interval = setInterval(() => {
      count--;
      if (count > 0) {
        el.cameraCountdownNumber.textContent = count;
        // Reiniciar animación css de pulso
        el.cameraCountdownNumber.style.animation = 'none';
        void el.cameraCountdownNumber.offsetWidth;
        el.cameraCountdownNumber.style.animation = '';
        playCountdownBeep(false);
        try { if (navigator.vibrate) navigator.vibrate(40); } catch (_) {}
      } else {
        clearInterval(interval);
        el.cameraCountdownOverlay.classList.add('hidden');
        playCountdownBeep(true);
        executePhotoSnap();
      }
    }, 1000);
  } else {
    executePhotoSnap();
  }
}

async function executePhotoSnap() {
  state.isCapturing = true;

  // Estado UI en el botón obturador
  if (el.arCamCapture) el.arCamCapture.classList.add('capturing');
  if (el.arShutterSpinner) el.arShutterSpinner.classList.remove('hidden');
  if (el.arShutterInner) el.arShutterInner.style.opacity = '0.2';
  if (el.arShutterLabel) el.arShutterLabel.textContent = '...';

  // Sonido de obturador y hápticos duales
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
      const shadowRx = canvas.width * 0.35 * state.cameraScale;
      const shadowRy = 35 * state.cameraScale;

      const grad = ctx.createRadialGradient(shadowX, shadowY, 0, shadowX, shadowY, shadowRx);
      grad.addColorStop(0, 'rgba(0, 0, 0, 0.68)');
      grad.addColorStop(0.5, 'rgba(0, 0, 0, 0.3)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.ellipse(shadowX, shadowY, shadowRx, shadowRy, 0, 0, Math.PI * 2);
      ctx.fill();

      // Dibujar modelo 3D sobre la cámara
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
      ctx.fillText(`WebAR 1:1 · ${dateStr}`, canvas.width - padX, canvas.height - Math.round(barHeight * 0.2));

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
  if (el.arShutterSpinner) el.arShutterSpinner.classList.add('hidden');
  if (el.arShutterInner) el.arShutterInner.style.opacity = '1';
  if (el.arShutterLabel) el.arShutterLabel.textContent = 'FOTO';
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
  try { if (navigator.vibrate) navigator.vibrate(15); } catch (_) {}
}



/* ══════════════════════════════════════════════
   QR MODAL & TARJETA DE VITRINA
══════════════════════════════════════════════ */
function openQRModal() {
  const m   = MOTOS[state.motoIdx];
  const mode = state.arMode || 'ar';
  const url = window.location.origin + '/ar.html?moto=' + m.id + '&mode=' + mode;

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

function copyARUrl() {
  const m = MOTOS[state.motoIdx];
  const mode = state.arMode || 'ar';
  const url = window.location.origin + '/ar.html?moto=' + m.id + '&mode=' + mode;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => {
      showARToast('📋 ¡Enlace copiado al portapapeles!');
    }).catch(() => {
      prompt('Copia este enlace para compartir:', url);
    });
  } else {
    prompt('Copia este enlace para compartir:', url);
  }
}

function downloadCardPNG() {
  if (!state.qrListo) {
    showARToast('Generando código QR, intenta en un momento...');
    return;
  }
  const m = MOTOS[state.motoIdx];
  const qrCanvas = el.qrContainer.querySelector('canvas') || el.qrContainer.querySelector('img');
  if (!qrCanvas) {
    showARToast('Esperando QR...');
    return;
  }

  const canvas = document.createElement('canvas');
  canvas.width = 1000;
  canvas.height = 1350;
  const ctx = canvas.getContext('2d');

  // Fondo oscuro elegante
  ctx.fillStyle = '#0b1326';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Borde temático neón con acento de la moto
  ctx.strokeStyle = m.acento || '#38bdf8';
  ctx.lineWidth = 10;
  ctx.strokeRect(20, 20, canvas.width - 40, canvas.height - 40);

  // Línea sutil interna
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
  ctx.lineWidth = 2;
  ctx.strokeRect(34, 34, canvas.width - 68, canvas.height - 68);

  // Logo MotosXR
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 50px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('MotosXR', canvas.width / 2, 105);

  ctx.fillStyle = m.acento || '#38bdf8';
  ctx.font = 'bold 20px monospace';
  ctx.fillText('REALIDAD AUMENTADA 1:1 · COLOMBIA', canvas.width / 2, 148);

  // Nombre de la moto
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 54px sans-serif';
  ctx.fillText(m.nombre.toUpperCase(), canvas.width / 2, 240);

  // Precio
  ctx.fillStyle = m.acento || '#38bdf8';
  ctx.font = 'bold 44px monospace';
  ctx.fillText(formatCOP(m.precio), canvas.width / 2, 305);

  // Pills de especificaciones técnicas
  ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.fillRect(140, 350, canvas.width - 280, 58);
  ctx.fillStyle = '#dae2fd';
  ctx.font = '22px sans-serif';
  ctx.fillText(`${m.cilindraje}  ·  ${m.potencia}  ·  ${m.peso}  ·  Tanque ${m.tanque}`, canvas.width / 2, 388);

  // Cuadro blanco para el código QR
  const qrBoxSize = 480;
  const qrBoxX = (canvas.width - qrBoxSize) / 2;
  const qrBoxY = 445;
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(qrBoxX, qrBoxY, qrBoxSize, qrBoxSize);

  // Dibujar QR dentro del cuadro blanco
  ctx.drawImage(qrCanvas, qrBoxX + 25, qrBoxY + 25, qrBoxSize - 50, qrBoxSize - 50);

  // Texto de llamado a la acción
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 30px sans-serif';
  ctx.fillText('ESCANEA CON LA CÁMARA DE TU CELULAR', canvas.width / 2, 990);

  ctx.fillStyle = '#94a3b8';
  ctx.font = '20px sans-serif';
  ctx.fillText('Apunta a una superficie plana en tu sala o garaje', canvas.width / 2, 1035);
  ctx.fillText('Sin descargar aplicaciones · Compatible con iPhone y Android', canvas.width / 2, 1070);

  // Modo actual indicado
  const isArMode = (state.arMode || 'ar') === 'ar';
  ctx.fillStyle = isArMode ? 'rgba(56, 189, 248, 0.2)' : 'rgba(163, 230, 53, 0.2)';
  ctx.fillRect(200, 1120, canvas.width - 400, 50);
  ctx.fillStyle = isArMode ? '#38bdf8' : '#a3e635';
  ctx.font = 'bold 18px monospace';
  ctx.fillText(isArMode ? '⚡ INCLUYE FICHAS TÉCNICAS HOLOGRÁFICAS 3D' : '✨ SHOWROOM REALISTA LIMPIO 1:1', canvas.width / 2, 1152);

  // Footer
  ctx.fillStyle = '#64748b';
  ctx.font = '16px monospace';
  ctx.fillText(`motosxr.vercel.app · Catálogo Oficial`, canvas.width / 2, 1270);

  // Descargar archivo PNG
  const link = document.createElement('a');
  link.download = `MotosXR_${m.id}_Tarjeta_AR.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
  showARToast('✅ Tarjeta AR descargada con éxito');
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

  // Notificar estado de Scene Viewer sin forzar apertura automática de cámara
  el.mv.addEventListener('ar-status', e => {
    if (e.detail.status === 'failed') {
      showARToast('Google Scene Viewer no compatible. Puedes usar el modo de Cámara Web.');
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

  /* Controles de Cámara AR Universal */
  el.arCamClose.addEventListener('click', stopCameraAR);
  el.arCamCapture.addEventListener('click', triggerPhotoCapture);
  if (el.arCamTimerBtn) {
    el.arCamTimerBtn.addEventListener('click', toggleCameraTimer);
  }
  el.arCamPrev.addEventListener('click', () => {
    loadMoto((state.motoIdx - 1 + MOTOS.length) % MOTOS.length);
  });
  el.arCamNext.addEventListener('click', () => {
    loadMoto((state.motoIdx + 1) % MOTOS.length);
  });

  /* Botón girar 180 grados suave */
  if (el.arCamRotate180) {
    el.arCamRotate180.addEventListener('click', () => {
      smoothRotateTo(orbitState.targetDeg + 180);
    });
  }

  /* Chips de ángulos 360° en cámara (0° Frente, 90° Lado, 180° Atrás, 270° Lado) */
  document.querySelectorAll('.ar-orbit-chip').forEach(btn => {
    btn.addEventListener('click', e => {
      const deg = parseFloat(e.currentTarget.dataset.angle) || 0;
      smoothRotateTo(deg);
    });
  });

  /* Sincronizar estado y chips si el usuario gira la moto arrastrando con el dedo */
  if (el.cameraMv) {
    el.cameraMv.addEventListener('camera-change', () => {
      if (!orbitState.animId && typeof el.cameraMv.getCameraOrbit === 'function') {
        const o = el.cameraMv.getCameraOrbit();
        if (o && typeof o.theta === 'number') {
          const deg = (o.theta * 180 / Math.PI) % 360;
          orbitState.currentDeg = ((deg % 360) + 360) % 360;
          orbitState.targetDeg = orbitState.currentDeg;
          updateOrbitChipsUI(orbitState.currentDeg);
        }
      }
    });
  }

  /* Botones de Escala en Cámara */
  document.querySelectorAll('.ar-scale-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      setCameraScale(parseFloat(e.target.dataset.scale));
    });
  });

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

  /* QR modal & Tarjeta */
  el.qrBtn.addEventListener('click', openQRModal);
  el.qrModalClose.addEventListener('click', closeQRModal);
  el.qrModal.addEventListener('click', e => {
    if (e.target === el.qrModal) closeQRModal();
  });
  if (el.downloadCardBtn) el.downloadCardBtn.addEventListener('click', downloadCardPNG);
  if (el.copyUrlBtn) el.copyUrlBtn.addEventListener('click', copyARUrl);

  /* Switch Dual de Modo AR / 3D */
  if (el.modeBtnAr) el.modeBtnAr.addEventListener('click', () => setViewModelMode('ar'));
  if (el.modeBtnClean) el.modeBtnClean.addEventListener('click', () => setViewModelMode('clean'));

  /* ── Barra HUD de controles dentro del visor 3D ── */
  if (el.btnToggleRotate) {
    el.btnToggleRotate.addEventListener('click', () => {
      const isAuto = el.mv.hasAttribute('auto-rotate');
      if (isAuto) {
        el.mv.removeAttribute('auto-rotate');
        if (el.btnRotateIconPause) el.btnRotateIconPause.classList.add('hidden');
        if (el.btnRotateIconPlay) el.btnRotateIconPlay.classList.remove('hidden');
        if (el.btnRotateLabel) el.btnRotateLabel.textContent = 'Reanudar rotación';
        el.btnToggleRotate.title = 'Reanudar rotación automática';
        showARToast('⏸ Rotación pausada');
      } else {
        el.mv.setAttribute('auto-rotate', '');
        if (el.btnRotateIconPause) el.btnRotateIconPause.classList.remove('hidden');
        if (el.btnRotateIconPlay) el.btnRotateIconPlay.classList.add('hidden');
        if (el.btnRotateLabel) el.btnRotateLabel.textContent = 'Pausar rotación';
        el.btnToggleRotate.title = 'Pausar rotación automática';
        showARToast('▶ Rotación automática activada');
      }
    });
  }

  if (el.btnResetView) {
    el.btnResetView.addEventListener('click', () => {
      el.mv.cameraOrbit = 'auto auto auto';
      el.mv.cameraTarget = 'auto auto auto';
      el.mv.fieldOfView = 'auto';
      try {
        if (typeof el.mv.resetTurntableRotation === 'function') {
          el.mv.resetTurntableRotation(0);
        }
      } catch (_) {}
      showARToast('↺ Posición inicial restablecida');
    });
  }

  if (el.btnToggleLabels) {
    el.btnToggleLabels.addEventListener('click', () => {
      const nextMode = state.arMode === 'ar' ? 'clean' : 'ar';
      setViewModelMode(nextMode);
    });
  }

  if (el.btnFullscreen) {
    el.btnFullscreen.addEventListener('click', () => {
      const targetArea = document.getElementById('viewerArea') || el.mv;
      if (!document.fullscreenElement && !document.webkitFullscreenElement) {
        if (targetArea.requestFullscreen) {
          targetArea.requestFullscreen();
        } else if (targetArea.webkitRequestFullscreen) {
          targetArea.webkitRequestFullscreen();
        }
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        }
      }
    });

    const updateFullscreenState = () => {
      const isFullscreen = Boolean(document.fullscreenElement || document.webkitFullscreenElement);
      if (el.fsIconEnter) el.fsIconEnter.classList.toggle('hidden', isFullscreen);
      if (el.fsIconExit) el.fsIconExit.classList.toggle('hidden', !isFullscreen);
      if (el.fsLabel) el.fsLabel.textContent = isFullscreen ? 'Salir' : 'Pantalla completa';
    };
    document.addEventListener('fullscreenchange', updateFullscreenState);
    document.addEventListener('webkitfullscreenchange', updateFullscreenState);
  }

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
