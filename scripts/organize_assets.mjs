import fs from 'fs';
import path from 'path';

const MAPPINGS = [
  {
    id: 'tvs-raider',
    folder: 'Tvs raider',
    glbSrc: 'Tvs raider/Raider2.glb',
    usdzSrc: 'Tvs raider/raider.usdz',
  },
  {
    id: 'akt-nkd',
    folder: 'Akt Nkd',
    glbSrc: 'Akt Nkd/nkd2.glb',
    usdzSrc: 'Akt Nkd/nkd.usdz',
  },
  {
    id: 'pulsar-ns200',
    folder: 'Pulsar ns 200',
    glbSrc: 'Pulsar ns 200/ns200_2.glb',
    usdzSrc: 'Pulsar ns 200/ns200.usdz',
  },
  {
    id: 'bajaj-boxer',
    folder: 'Bajaj Boxer',
    glbSrc: 'Bajaj Boxer/boxer2.glb',
    usdzSrc: 'Bajaj Boxer/boxer.usdz',
  },
  {
    id: 'hero-eco',
    folder: 'Hero eco deluxe',
    glbSrc: 'Hero eco deluxe/hero2.glb',
    usdzSrc: 'Hero eco deluxe/Hero.usdz',
  },
];

const publicModelsDir = path.resolve('public/models');
const publicPostersDir = path.resolve('public/posters');
const publicFramesDir = path.resolve('public/frames');

fs.mkdirSync(publicModelsDir, { recursive: true });
fs.mkdirSync(publicPostersDir, { recursive: true });
fs.mkdirSync(publicFramesDir, { recursive: true });

console.log('Organizando modelos 3D hacia public/models/...');

for (const m of MAPPINGS) {
  // 1. Copiar GLB
  const destGlb = path.join(publicModelsDir, `${m.id}.glb`);
  if (fs.existsSync(m.glbSrc)) {
    fs.copyFileSync(m.glbSrc, destGlb);
    const sizeMb = (fs.statSync(destGlb).size / (1024 * 1024)).toFixed(2);
    console.log(`✓ ${m.id}.glb copiado (${sizeMb} MB)`);
  } else {
    console.warn(`! Archivo no encontrado: ${m.glbSrc}`);
  }

  // 2. Copiar USDZ
  const destUsdz = path.join(publicModelsDir, `${m.id}.usdz`);
  if (fs.existsSync(m.usdzSrc)) {
    fs.copyFileSync(m.usdzSrc, destUsdz);
    const sizeMb = (fs.statSync(destUsdz).size / (1024 * 1024)).toFixed(2);
    console.log(`✓ ${m.id}.usdz copiado (${sizeMb} MB)`);
  } else {
    console.warn(`! Archivo no encontrado: ${m.usdzSrc}`);
  }

  // 3. Copiar fotogramas 360 hacia public/frames/<id>/
  const destFrameFolder = path.join(publicFramesDir, m.id);
  fs.mkdirSync(destFrameFolder, { recursive: true });
  for (let i = 1; i <= 8; i++) {
    const frameFile = `${i}_dark.png`;
    const srcFrame = path.join(m.folder, frameFile);
    const destFrame = path.join(destFrameFolder, frameFile);
    if (fs.existsSync(srcFrame)) {
      fs.copyFileSync(srcFrame, destFrame);
    }
  }
  console.log(`✓ Fotogramas 360 copiados hacia public/frames/${m.id}/`);
}

console.log('Estructura de public/ organizada exitosamente.');
