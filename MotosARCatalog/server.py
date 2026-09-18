"""
server.py — MotosARCatalog
Servidor local para desarrollo. La app corre en http://localhost:8081

Uso:
    python server.py          → puerto 8081
    python server.py 3001     → puerto personalizado
"""
import sys, os, webbrowser, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8081


class ARHandler(SimpleHTTPRequestHandler):
    TYPES = {'.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json',
             '.webp': 'image/webp', '.wasm': 'application/wasm'}

    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        return self.TYPES.get(ext) or super().guess_type(path)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, fmt, *args):
        # Silenciar assets de imágenes/fuentes para no saturar la consola
        skip = ('.png', '.webp', '.woff2', '.woff', '.ttf', '.js', '.css')
        path = (args[0].split()[1] if args else '')
        if not any(path.endswith(e) for e in skip):
            super().log_message(fmt, *args)


def main():
    # Servir desde la raíz de ProyectoMotosXR (padre de esta carpeta)
    # así los paths ../Akt Nkd/ resuelven correctamente
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    url = 'http://localhost:{}/MotosARCatalog/'.format(PORT)
    print('=' * 55)
    print('  MotosAR dev server')
    print('  URL:  {}'.format(url))
    print('  Root: {}'.format(root))
    print('  Ctrl+C para detener')
    print('=' * 55)

    threading.Thread(
        target=lambda: (__import__('time').sleep(1), webbrowser.open(url)),
        daemon=True
    ).start()

    srv = HTTPServer(('', PORT), ARHandler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n[STOP] Servidor detenido.')
        srv.server_close()


if __name__ == '__main__':
    main()

