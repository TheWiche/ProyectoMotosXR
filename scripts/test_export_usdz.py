import http.server
import threading
import os
import sys
from playwright.sync_api import sync_playwright

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

PORT = 8999
httpd = http.server.HTTPServer(('127.0.0.1', PORT), SilentHandler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()

print("Servidor local iniciado. Lanzando headless Chromium...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"http://127.0.0.1:{PORT}/MotosARCatalog/index.html")
    
    print("Esperando que model-viewer cargue el modelo 3D optimizado...")
    page.wait_for_function("() => document.getElementById('mv') && document.getElementById('mv').loaded", timeout=60000)
    
    print("Modelo cargado. Exportando USDZ oficial de model-viewer...")
    base64_data = page.evaluate("""async () => {
        const mv = document.getElementById('mv');
        const blob = await mv.exportScene({ format: 'usdz' });
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.readAsDataURL(blob);
        });
    }""")
    
    import base64
    raw_data = base64.b64decode(base64_data)
    out_path = "public/models/tvs-raider_optimized.usdz"
    with open(out_path, "wb") as f:
        f.write(raw_data)
        
    mb_size = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Éxito: USDZ generado en {out_path} con tamaño de {mb_size:.2f} MB!")
    browser.close()

httpd.shutdown()

