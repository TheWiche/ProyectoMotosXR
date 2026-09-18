# -*- coding: utf-8 -*-
"""
normalize_backgrounds.py - ProyectoMotosXR
Estandariza fondos de las 5 carpetas de motos para Dark Mode.

Fondos BLANCOS (Akt Nkd, Bajaj Boxer, Pulsar ns 200):
  -> Remocion BFS flood-fill desde bordes + transparencia
  -> Guarda como N_dark.png (PNG con canal alpha)

Fondos ya procesados (Hero eco deluxe, Tvs raider _cleanup):
  -> Convierte fondo negro a transparente y guarda como N_dark.png

Requiere: Pillow (pip install Pillow)
Opcional: numpy  (pip install numpy)  -- mejora calidad
"""
from __future__ import print_function
import os
import sys
from pathlib import Path
from collections import deque

# --- Pillow ----------------------------------------------------------------
try:
    from PIL import Image
    print("[OK] Pillow disponible")
except ImportError:
    print("[ERR] Pillow no instalado. Ejecuta: pip install Pillow")
    sys.exit(1)

# --- NumPy (opcional) ------------------------------------------------------
try:
    import numpy as np
    USE_NUMPY = True
    print("[OK] NumPy disponible - remocion de fondo avanzada")
except ImportError:
    USE_NUMPY = False
    print("[WARN] NumPy no disponible - remocion basica (pip install numpy para mejor calidad)")

# --- CONFIGURACION ---------------------------------------------------------
BASE_DIR = Path(__file__).parent

BIKES = {
    "Akt Nkd": {
        "files":   ["{}.png".format(i)  for i in range(1, 9)],
        "bg":      "white",
        "out_pat": "{n}_dark.png",
    },
    "Bajaj Boxer": {
        "files":   ["{}.webp".format(i) for i in range(1, 9)],
        "bg":      "white",
        "out_pat": "{n}_dark.png",
    },
    "Hero eco deluxe": {
        "files":   ["{}_cleanup.png".format(i)  for i in range(1, 9)],
        "bg":      "black",
        "out_pat": "{n}_dark.png",
    },
    "Pulsar ns 200": {
        "files":   ["{}.webp".format(i) for i in range(1, 9)],
        "bg":      "white",
        "out_pat": "{n}_dark.png",
    },
    "Tvs raider": {
        "files":   ["{}_cleanup.webp".format(i) for i in range(1, 9)],
        "bg":      "black",
        "out_pat": "{n}_dark.png",
    },
}

WHITE_THRESHOLD = 235   # R+G+B > 3*threshold => fondo blanco
BLACK_THRESHOLD = 20    # R+G+B < 3*threshold => fondo negro


# --- FUNCIONES -------------------------------------------------------------

def bfs_flood(mask_2d):
    """BFS desde todos los bordes de la imagen. Devuelve mascara booleana del fondo."""
    h, w = mask_2d.shape
    visited = [[False] * w for _ in range(h)]
    queue = deque()

    # Semillas: borde superior/inferior
    for col in range(w):
        for row in [0, h - 1]:
            if mask_2d[row, col] and not visited[row][col]:
                visited[row][col] = True
                queue.append((row, col))
    # Semillas: borde izquierdo/derecho
    for row in range(h):
        for col in [0, w - 1]:
            if mask_2d[row, col] and not visited[row][col]:
                visited[row][col] = True
                queue.append((row, col))

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and mask_2d[nr, nc]:
                visited[nr][nc] = True
                queue.append((nr, nc))

    # Convertir a array numpy booleano
    import numpy as npp
    result = npp.zeros((h, w), dtype=bool)
    for r in range(h):
        for c in range(w):
            result[r, c] = visited[r][c]
    return result


def remove_white_bg(img):
    """Elimina fondo blanco -> transparencia."""
    img_rgba = img.convert("RGBA")

    if USE_NUMPY:
        data = np.array(img_rgba, dtype=np.uint8)
        h, w = data.shape[:2]
        r, g, b = data[:, :, 0].astype(int), data[:, :, 1].astype(int), data[:, :, 2].astype(int)
        white_mask = (r + g + b) > (WHITE_THRESHOLD * 3 - 30)

        # BFS rapido con numpy views
        visited = np.zeros((h, w), dtype=bool)
        queue = deque()
        rows_seeds = np.concatenate([np.where(white_mask[0])[0], np.where(white_mask[h-1])[0]])
        for c in rows_seeds:
            if not visited[0, c]:  visited[0, c] = True;  queue.append((0, c))
            if not visited[h-1,c]: visited[h-1,c]= True;  queue.append((h-1, c))
        col_seeds = np.concatenate([np.where(white_mask[:,0])[0], np.where(white_mask[:,w-1])[0]])
        for r_idx in col_seeds:
            if not visited[r_idx, 0]:   visited[r_idx,0]=True;   queue.append((r_idx,0))
            if not visited[r_idx,w-1]:  visited[r_idx,w-1]=True; queue.append((r_idx,w-1))

        while queue:
            row, col = queue.popleft()
            for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                nr, nc = row+dr, col+dc
                if 0 <= nr < h and 0 <= nc < w and not visited[nr,nc] and white_mask[nr,nc]:
                    visited[nr,nc] = True
                    queue.append((nr,nc))

        data[visited, 3] = 0
        return Image.fromarray(data, "RGBA")
    else:
        # Fallback: umbral global sin BFS
        datas = list(img_rgba.getdata())
        new_data = []
        for r, g, b, a in datas:
            if r > WHITE_THRESHOLD and g > WHITE_THRESHOLD and b > WHITE_THRESHOLD:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((r, g, b, a))
        img_rgba.putdata(new_data)
        return img_rgba


def remove_black_bg(img):
    """Elimina fondo negro -> transparencia (para _cleanup con fondo negro puro)."""
    img_rgba = img.convert("RGBA")

    if USE_NUMPY:
        data = np.array(img_rgba, dtype=np.uint8)
        h, w = data.shape[:2]
        r, g, b = data[:, :, 0].astype(int), data[:, :, 1].astype(int), data[:, :, 2].astype(int)
        black_mask = (r + g + b) < (BLACK_THRESHOLD * 3)

        visited = np.zeros((h, w), dtype=bool)
        queue = deque()
        for col in range(w):
            for row in [0, h-1]:
                if black_mask[row, col] and not visited[row, col]:
                    visited[row, col] = True
                    queue.append((row, col))
        for row in range(h):
            for col in [0, w-1]:
                if black_mask[row, col] and not visited[row, col]:
                    visited[row, col] = True
                    queue.append((row, col))

        while queue:
            row, col = queue.popleft()
            for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                nr, nc = row+dr, col+dc
                if 0 <= nr < h and 0 <= nc < w and not visited[nr,nc] and black_mask[nr,nc]:
                    visited[nr,nc] = True
                    queue.append((nr,nc))

        data[visited, 3] = 0
        return Image.fromarray(data, "RGBA")
    else:
        datas = list(img_rgba.getdata())
        new_data = []
        for r, g, b, a in datas:
            if r < BLACK_THRESHOLD and g < BLACK_THRESHOLD and b < BLACK_THRESHOLD:
                new_data.append((0, 0, 0, 0))
            else:
                new_data.append((r, g, b, a))
        img_rgba.putdata(new_data)
        return img_rgba


def process_bike(folder_name, config, dry_run=False):
    folder = BASE_DIR / folder_name
    if not folder.exists():
        print("  [ERR] Carpeta no encontrada: {}".format(folder))
        return False

    print("\n[FOLDER] {}  [bg={}]".format(folder_name, config["bg"].upper()))
    ok_count = 0

    for i, filename in enumerate(config["files"], start=1):
        src  = folder / filename
        out_name = config["out_pat"].format(n=i)
        out  = folder / out_name

        if not src.exists():
            print("  [WARN] [{}/8] {} -- no encontrado".format(i, filename))
            continue

        if dry_run:
            status = "[EXISTS]" if out.exists() else "[PENDING]"
            print("  {} [{}/8] {} -> {}".format(status, i, filename, out_name))
            ok_count += 1
            continue

        try:
            img = Image.open(str(src))
            if config["bg"] == "white":
                result = remove_white_bg(img)
            else:
                result = remove_black_bg(img)

            result.save(str(out), "PNG", optimize=True)
            size_kb = out.stat().st_size // 1024
            print("  [OK]  [{}/8] {} -> {}  ({} KB)".format(i, filename, out_name, size_kb))
            ok_count += 1
        except Exception as exc:
            print("  [ERR] [{}/8] {} -- {}".format(i, filename, exc))

    return ok_count == len(config["files"])


# --- MAIN ------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv
    mode = "DRY RUN" if dry_run else "PROCESANDO"
    print("=" * 60)
    print("  ProyectoMotosXR -- Normalizacion de fondos  [{}]".format(mode))
    print("=" * 60)

    results = {}
    for folder_name, config in BIKES.items():
        results[folder_name] = process_bike(folder_name, config, dry_run=dry_run)

    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    all_ok = True
    for folder, ok in results.items():
        tag = "[OK]" if ok else "[ERR]"
        print("  {}  {}".format(tag, folder))
        if not ok:
            all_ok = False

    if all_ok:
        print("\n[DONE] Todos los frames procesados. Abre index.html con server.py activo.")
    else:
        print("\n[WARN] Algunos archivos no se procesaron. Revisa los errores.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

