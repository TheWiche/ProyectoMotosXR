# Proyecto MotosXR — Visualizador 3D & Realidad Aumentada (WebAR)

Catálogo interactivo web de motocicletas con soporte nativo de **Realidad Aumentada (WebAR)** para iPhone (Apple Quick Look / USDZ) y Android (Google Scene Viewer / Cámara Web / GLB), con visualización dual de modelos limpios 1:1 e infografías 3D flotantes.

---

## 🚀 Cómo Iniciar el Proyecto Localmente

Tienes dos formas sencillas de ejecutar el proyecto en tu computadora:

### Opción A: Con Node.js y Vite (Recomendada para Desarrollo)
1. Abre una terminal en esta carpeta.
2. Instala las dependencias:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo:
   ```bash
   npm run dev
   ```
   Abre en tu navegador la URL que indique la consola (generalmente `http://localhost:5173`).

4. Para compilar la versión optimizada de producción:
   ```bash
   npm run build
   ```

---

### Opción B: Con Python (Sin necesidad de instalar Node.js)
Si solo deseas visualizar y probar la página inmediatamente:
1. Ejecuta el archivo servidor incluido:
   ```bash
   python server.py
   ```
2. Abre en tu navegador:
   `http://localhost:8000/MotosARCatalog/`

---

## 📂 Estructura del Proyecto

- **`MotosARCatalog/`**: Aplicación web principal del catálogo interactivo.
  - `index.html`: Estructura del visor 3D, panel de especificaciones y modales.
  - `app.js`: Lógica interactiva, selector con miniaturas, controles HUD y sincronización.
  - `styles.css`: Estilos visuales con interfaz modo oscuro y diseño responsive sin solapamientos.
- **`index.html`**: Comparador 360° con control deslizante (scrubber).
- **`ar.html`**: Lanzador directo de Realidad Aumentada para móviles y stickers QR.
- **`reporte.html`**: Documento técnico de arquitectura, pipeline 3D y justificaciones de diseño.
- **`public/`**: Assets estáticos y modelos 3D optimizados:
  - `models/android/`: Modelos `.glb` optimizados para Android y navegadores WebGL.
  - `models/ios/`: Modelos `.usdz` para Apple Quick Look (iPhone / iPad).
  - `posters/`: Renders en alta resolución para previews inmediatas.
  - `frames/`: Secuencias fotográficas 360° para el comparador.
- **`scripts/`**: Scripts de Python y Blender con los que se procesaron y exportaron los modelos 3D e infografías.
- **`vercel.json`**: Configuración de encabezados CORS y tipos MIME para despliegue en la nube.

---

## 📱 Tecnologías y Compatibilidad
- **Android**: Compatible con Google Scene Viewer y modo Cámara Web Universal.
- **iOS (iPhone/iPad)**: Compatible nativamente mediante Apple Quick Look (USDZ con texturas PNG 24-bit y materiales Apple Preview Surface).
- **Formatos 3D**: GLB / USDZ (< 18.5 MB por modelo para carga rápida en redes móviles).
