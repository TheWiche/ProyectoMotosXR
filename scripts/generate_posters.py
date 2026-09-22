import os
from PIL import Image
from rembg import remove

MOTOS = [
  {"id": "tvs-raider", "src": "Tvs raider/3_dark.png"},
  {"id": "akt-nkd", "src": "Akt Nkd/3_dark.png"},
  {"id": "pulsar-ns200", "src": "Pulsar ns 200/3_dark.png"},
  {"id": "bajaj-boxer", "src": "Bajaj Boxer/3_dark.png"},
  {"id": "hero-eco", "src": "Hero eco deluxe/3_dark.png"},
]

out_dir = os.path.abspath("public/posters")
os.makedirs(out_dir, exist_ok=True)

print("Procesando pósteres con IA (rembg U2Net con alpha matting)...")

for m in MOTOS:
  src_path = os.path.abspath(m["src"])
  dest_path = os.path.join(out_dir, f"{m['id']}.png")
  
  if not os.path.exists(src_path):
    print(f"! Archivo origen no encontrado: {src_path}")
    continue

  print(f"Extrayendo silueta transparente para {m['id']}...")
  try:
    with Image.open(src_path) as input_img:
      # Procesar con rembg
      output_img = remove(
        input_img,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=5
      )
      
      # Redimensionar suavemente a máximo 1024px para optimizar tamaño web
      output_img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
      output_img.save(dest_path, format="PNG", optimize=True)
      
      kb_size = os.path.getsize(dest_path) / 1024
      print(f"[OK] {m['id']}.png generado ({kb_size:.1f} KB)")
  except Exception as e:
    print(f"Error procesando {m['id']}: {e}")

print("Todos los pósteres transparentes fueron generados exitosamente.")
