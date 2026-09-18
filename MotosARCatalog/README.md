# MotosAR — WebAR Motorcycle Catalog

Catálogo interactivo con **Realidad Aumentada** para motos en Colombia. Sin instalar apps — funciona desde el navegador.

## Estructura del proyecto

```
ProyectoMotosXR/               ← raíz del deploy
│
├── Akt Nkd/                   ← activos moto 1
│   ├── nkd.glb
│   └── 3_dark.png
├── Bajaj Boxer/ ...
├── Hero eco deluxe/ ...
├── Pulsar ns 200/ ...
├── Tvs raider/ ...
│
└── MotosARCatalog/            ← ESTA APP
    ├── index.html
    ├── app.js
    ├── styles.css
    ├── server.py              ← dev local
    └── README.md
```

## Desarrollo local

```bash
# Desde la carpeta MotosARCatalog:
python server.py

# Abre automáticamente: http://localhost:8081/MotosARCatalog/
```

## Deploy en Vercel / Netlify / GitHub Pages

La **raíz del deploy** debe ser `ProyectoMotosXR/` (el directorio padre, no esta subcarpeta).

### Vercel (recomendado)
```bash
cd ProyectoMotosXR
vercel --prod
# Framework preset: Other
# Build command: (vacío)
# Output directory: .
```

### Netlify
1. Sube o conecta el repo apuntando a `ProyectoMotosXR/`
2. Build command: vacío
3. Publish directory: `.`

### GitHub Pages
```bash
cd ProyectoMotosXR
git init && git add . && git commit -m "init"
gh repo create motosAR --public --push --source=.
# Activar Pages desde rama main, directorio raíz
```

La app queda en: `https://<usuario>.github.io/motosAR/MotosARCatalog/`

---

## URLs con parámetros (para QR)

| Parámetro | Descripción |
|---|---|
| `?moto=tvs-raider` | Abre directo en TVS Raider |
| `?moto=pulsar-ns200&ar=true` | Abre NS200 y muestra prompt AR |

**IDs disponibles:** `akt-nkd`, `bajaj-boxer`, `hero-eco`, `pulsar-ns200`, `tvs-raider`

---

## Flujo AR por plataforma

| Plataforma | Motor AR | Requisito |
|---|---|---|
| Android Chrome | Google Scene Viewer | Android 8+ |
| iOS Safari | AR Quick Look | iOS 12+ |
| Escritorio | — | Muestra toast informativo |

---

## Personalización rápida

Edita `app.js`, sección `CONFIG`:

```javascript
const CONFIG = {
  whatsapp: '573145813171',  // ← Tu número real
  siteName: 'MotosAR Colombia',
  autoArPrompt: true,
};
```

Edita los precios y fichas en el array `MOTOS` del mismo archivo.

---

## Stack técnico

- HTML5 nativo + CSS custom properties
- JavaScript ES6 (sin bundler — corre directamente en el browser)
- [`model-viewer`](https://modelviewer.dev) v3.5.0 (Google) para 3D + AR
- [qrcode.js](https://github.com/davidshimjs/qrcodejs) para generación de QR en cliente
- Zero dependencias de backend para la webapp

