"""
server.py - ProyectoMotosXR
Servidor HTTP local para servir la aplicacion sin errores CORS.
Permite cargar archivos .glb con model-viewer correctamente.

Uso:
    python server.py         -> http://localhost:8080
    python server.py 3000    -> http://localhost:3000
"""
import sys
import os
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class MotosXRHandler(SimpleHTTPRequestHandler):
    """Handler con CORS permisivo y MIME types correctos para GLB/WEBP."""

    # MIME types adicionales que SimpleHTTPRequestHandler no cubre bien
    EXTRA_TYPES = {
        '.glb':  'model/gltf-binary',
        '.gltf': 'model/gltf+json',
        '.webp': 'image/webp',
        '.wasm': 'application/wasm',
    }

    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in self.EXTRA_TYPES:
            return self.EXTRA_TYPES[ext]
        return super().guess_type(path)

    def end_headers(self):
        # CORS abierto para model-viewer y recursos externos
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        # Necesario para SharedArrayBuffer (usado por model-viewer AR)
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Mostrar solo requests que no sean assets (reduce spam)
        path = args[0].split()[1] if args else ''
        skip_exts = ('.png', '.webp', '.woff', '.woff2', '.ttf')
        if any(path.endswith(e) for e in skip_exts):
            return
        super().log_message(format, *args)


def open_browser(url):
    import time
    time.sleep(0.8)
    webbrowser.open(url)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    url = 'http://localhost:{}/'.format(PORT)

    print('=' * 50)
    print('  MotosXR Server')
    print('  URL: {}'.format(url))
    print('  Ctrl+C para detener')
    print('=' * 50)

    # Abrir browser automaticamente
    t = threading.Thread(target=open_browser, args=(url,), daemon=True)
    t.start()

    server = HTTPServer(('', PORT), MotosXRHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[STOPPED] Servidor detenido.')
        server.server_close()


if __name__ == '__main__':
    main()

