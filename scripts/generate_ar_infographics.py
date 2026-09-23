#!/usr/bin/env python3
"""
generate_ar_infographics.py
Pipeline automatizado con Blender 5.2 + Python (Pillow) para generar:
1. Tarjetas de infografía 2D en alta resolución (Pillow).
2. Construcción 3D en Blender:
   - Planos de doble cara con sombreador Emissivo (Emission = 1.0) para máxima legibilidad en AR.
   - Varillas cilíndricas neón y pines esféricos anclados a piezas mecánicas.
   - Optimización de malla (Decimate inteligente) para cumplir la regla estricta de Safari (< 30 MB).
3. Exportación dual:
   - `<id>_ar.glb` (con compresión Draco para Android Scene Viewer).
   - `<id>_ar.usdz` (Y-Up, cero texturas WebP, empaquetado nativo para Apple ARKit Quick Look).
"""

import os
import sys
import subprocess
from PIL import Image, ImageDraw, ImageFont

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

MOTOS_DATA = {
    'tvs-raider': {
        'nombre': 'TVS Raider 125',
        'glb': 'public/models/tvs-raider.glb',
        'accent': '#38bdf8',  # Neon Cyan
        'cards': [
            {
                'category': 'MOTOR & POTENCIA',
                'title': '124.8 cc · 11.4 HP',
                'specs': ['Torque: 11.2 Nm @ 6.000 rpm', 'Transmisión: 5 velocidades', 'Racing DNA monocilíndrico 4T'],
                'pos': (0.10, 0.48, 0.65),
                'target': (0.05, 0.15, 0.38)
            },
            {
                'category': 'FRENOS & SEGURIDAD',
                'title': 'Disco Lobulado 240mm',
                'specs': ['Caliper delantero doble pistón', 'Tambor trasero 130mm síncrono', 'Frenado de respuesta inmediata'],
                'pos': (0.70, -0.45, 0.50),
                'target': (0.72, -0.12, 0.30)
            },
            {
                'category': 'TANQUE & AUTONOMÍA',
                'title': 'Capacidad: 10 Litros',
                'specs': ['Rendimiento: ~45 km/L', 'Autonomía estimada: ~450 km', 'Tapa deportiva con panel LCD'],
                'pos': (0.15, 0.42, 1.05),
                'target': (0.15, 0.00, 0.85)
            },
            {
                'category': 'SUSPENSIÓN & CHASIS',
                'title': 'Monoshock de 5 Pasos',
                'specs': ['Horquilla delantera telescópica 30mm', 'Chasis tubular cuna simple', 'Estabilidad en curvas a alta velocidad'],
                'pos': (-0.50, 0.48, 0.70),
                'target': (-0.35, 0.08, 0.48)
            },
            {
                'category': 'ESCAPE & RENDIMIENTO',
                'title': 'Escape Deportivo Racing',
                'specs': ['Protector térmico de aluminio', 'Sonido característico TVS Racing', 'Cumple normativa ambiental'],
                'pos': (-0.45, -0.52, 0.55),
                'target': (-0.45, -0.22, 0.30)
            }
        ]
    },
    'akt-nkd': {
        'nombre': 'AKT NKD 125',
        'glb': 'public/models/akt-nkd.glb',
        'accent': '#a3e635',  # Lime Neon
        'cards': [
            {
                'category': 'MOTOR & POTENCIA',
                'title': '125 cc 4T · 11 HP',
                'specs': ['Torque: 8.8 Nm @ 6.000 rpm', 'Transmisión: 5 velocidades', 'Motor CGR de bajo consumo'],
                'pos': (0.10, 0.48, 0.65),
                'target': (0.05, 0.15, 0.38)
            },
            {
                'category': 'FRENOS & SEGURIDAD',
                'title': 'Freno de Disco Delantero',
                'specs': ['Caliper de doble pistón', 'Líneas reforzadas', 'Respuesta firme y progresiva'],
                'pos': (0.70, -0.45, 0.50),
                'target': (0.72, -0.12, 0.30)
            },
            {
                'category': 'TANQUE & AUTONOMÍA',
                'title': 'Capacidad: 13.5 Litros',
                'specs': ['3.5 galones de capacidad', 'Excelente autonomía urbana', 'Estilo clásico Café Racer'],
                'pos': (0.15, 0.42, 1.05),
                'target': (0.15, 0.00, 0.85)
            },
            {
                'category': 'SUSPENSIÓN & CHASIS',
                'title': 'Doble Amortiguador',
                'specs': ['Telescópica delantera hidráulica', 'Doble shock trasero ajustable', 'Chasis ligero de solo 118 kg'],
                'pos': (-0.50, 0.48, 0.70),
                'target': (-0.35, 0.08, 0.48)
            },
            {
                'category': 'ESCAPE & ESTILO',
                'title': 'Escape Café Racer',
                'specs': ['Silenciador negro mate deportivo', 'Tono grave característico', 'Protector antiquemaduras'],
                'pos': (-0.45, -0.52, 0.55),
                'target': (-0.45, -0.22, 0.30)
            }
        ]
    },
    'pulsar-ns200': {
        'nombre': 'Pulsar NS 200',
        'glb': 'public/models/pulsar-ns200.glb',
        'accent': '#f43f5e',  # Rose/Red Neon
        'cards': [
            {
                'category': 'MOTOR & POTENCIA',
                'title': '199.5 cc · 24.5 HP',
                'specs': ['Triple Chispa DTS-i 4 Válvulas', 'Refrigeración líquida por radiador', 'Torque: 18.7 Nm @ 8.000 rpm'],
                'pos': (0.10, 0.50, 0.68),
                'target': (0.05, 0.15, 0.40)
            },
            {
                'category': 'FRENOS & ABS',
                'title': 'Disco 300mm con ABS',
                'specs': ['Sistema de frenos ByBre (Brembo)', 'Disco trasero 230mm', 'Máximo control antibloqueo'],
                'pos': (0.72, -0.48, 0.52),
                'target': (0.75, -0.12, 0.32)
            },
            {
                'category': 'TANQUE & ERGONOMÍA',
                'title': 'Capacidad: 12 Litros',
                'specs': ['Diseño muscular Naked Sport', 'Aletas aerodinámicas integradas', 'Consumo optimizado EFI'],
                'pos': (0.15, 0.44, 1.10),
                'target': (0.15, 0.00, 0.88)
            },
            {
                'category': 'SUSPENSIÓN & CHASIS',
                'title': 'Chasis Perimetral',
                'specs': ['Nitrox Monoshock trasero', 'Horquilla delantera 37mm', 'Gran rigidez torsional'],
                'pos': (-0.52, 0.50, 0.72),
                'target': (-0.35, 0.08, 0.50)
            },
            {
                'category': 'ESCAPE & TECNOLOGÍA',
                'title': 'ExhausTEC Bajo Vientre',
                'specs': ['Centro de gravedad rebajado', 'Distribución de masas 50:50', 'Sonido nítido de alta gama'],
                'pos': (-0.15, -0.52, 0.42),
                'target': (-0.10, -0.15, 0.22)
            }
        ]
    },
    'bajaj-boxer': {
        'nombre': 'Bajaj Boxer 100',
        'glb': 'public/models/bajaj-boxer.glb',
        'accent': '#eab308',  # Amber Neon
        'cards': [
            {
                'category': 'MOTOR & EFICIENCIA',
                'title': '100 cc · 8.2 HP',
                'specs': ['Torque: 8.2 Nm @ 4.500 rpm', 'Motor de trabajo pesado 4T', 'Bajísimo consumo de combustible'],
                'pos': (0.10, 0.48, 0.65),
                'target': (0.05, 0.15, 0.38)
            },
            {
                'category': 'FRENOS & DURABILIDAD',
                'title': 'Tambores Reforzados',
                'specs': ['Zapatas de alta duración 130mm', 'Bajo costo de mantenimiento', 'Frenado constante en carga'],
                'pos': (0.70, -0.45, 0.50),
                'target': (0.72, -0.12, 0.30)
            },
            {
                'category': 'TANQUE & RENDIMIENTO',
                'title': 'Capacidad: 11 Litros',
                'specs': ['Hasta 70 km por galón', 'Autonomía de más de 500 km', 'Tanque metálico resistente'],
                'pos': (0.15, 0.42, 1.05),
                'target': (0.15, 0.00, 0.85)
            },
            {
                'category': 'SUSPENSIÓN DE CARGA',
                'title': 'Suspensión SNS',
                'specs': ['Spring-in-Spring (Doble resorte)', 'Capacidad de carga superior', 'Comodidad en vías rurales'],
                'pos': (-0.50, 0.48, 0.70),
                'target': (-0.35, 0.08, 0.48)
            },
            {
                'category': 'ESCAPE & CHASIS',
                'title': 'Silenciador Cromado',
                'specs': ['Escape alargado cromado', 'Parrilla de carga integrada', 'Chasis de acero tubular reforzado'],
                'pos': (-0.45, -0.52, 0.55),
                'target': (-0.45, -0.22, 0.30)
            }
        ]
    },
    'hero-eco': {
        'nombre': 'Hero Eco Deluxe',
        'glb': 'public/models/hero-eco.glb',
        'accent': '#10b981',  # Emerald Neon
        'cards': [
            {
                'category': 'MOTOR & TECNOLOGÍA',
                'title': '97.2 cc OHC · 8.2 HP',
                'specs': ['Sistema i3S (Start-Stop inteligente)', 'Torque: 8.05 Nm @ 5.000 rpm', 'Máximo ahorro de gasolina'],
                'pos': (0.10, 0.48, 0.65),
                'target': (0.05, 0.15, 0.38)
            },
            {
                'category': 'FRENOS INTEGRADOS',
                'title': 'Frenos IBS',
                'specs': ['Integrated Braking System', 'Distribución inteligente del frenado', 'Menor distancia de parada'],
                'pos': (0.70, -0.45, 0.50),
                'target': (0.72, -0.12, 0.30)
            },
            {
                'category': 'TANQUE & AHORRO',
                'title': 'Capacidad: 10.5 Litros',
                'specs': ['Autonomía de larga distancia', 'Tapa con llave de seguridad', 'Ideal para trabajo y transporte diario'],
                'pos': (0.15, 0.42, 1.05),
                'target': (0.15, 0.00, 0.85)
            },
            {
                'category': 'SUSPENSIÓN',
                'title': 'Suspensión Ajustable',
                'specs': ['Telescópica delantera hidráulica', 'Amortiguadores traseros de 2 pasos', 'Manejo suave en ciudad'],
                'pos': (-0.50, 0.48, 0.70),
                'target': (-0.35, 0.08, 0.48)
            },
            {
                'category': 'ESCAPE & ACABADOS',
                'title': 'Escape Eco Protegido',
                'specs': ['Protector cromado antiquemaduras', 'Bajas emisiones contaminantes', 'Estructura ligera de 112 kg'],
                'pos': (-0.45, -0.52, 0.55),
                'target': (-0.45, -0.22, 0.30)
            }
        ]
    }
}

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generate_card_image(category, title, specs, accent_hex, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    W, H = 512, 280
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    accent_rgb = hex_to_rgb(accent_hex)
    bg_rgba = (15, 23, 42, 245)
    border_rgba = (*accent_rgb, 255)

    # Rectángulo redondeado principal
    draw.rounded_rectangle([4, 4, W-5, H-5], radius=24, fill=bg_rgba, outline=border_rgba, width=3)

    # Fuentes
    font_badge = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 20)
    font_title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 30)
    font_spec  = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
    font_sub   = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 18)

    # Badge con categoría
    badge_w = int(draw.textlength(category, font=font_badge)) + 24
    draw.rounded_rectangle([24, 20, 24 + badge_w, 52], radius=10, fill=(*accent_rgb, 40), outline=(*accent_rgb, 200), width=1)
    draw.text((36, 24), category, font=font_badge, fill=border_rgba)

    # Título principal
    draw.text((24, 68), title, font=font_title, fill=(255, 255, 255, 255))

    # Líneas de especificaciones
    y = 118
    for i, line in enumerate(specs):
        color = (226, 232, 240, 255) if i == 0 else (148, 163, 184, 255)
        if i == len(specs) - 1 and len(specs) > 2:
            color = (*accent_rgb, 230)
        draw.text((24, y), line, font=font_spec if i < 2 else font_sub, fill=color)
        y += 36 if i < 2 else 32

    img.save(out_path, format='PNG')
    return out_path


def process_moto(moto_id, moto_info):
    print(f"\n==========================================")
    print(f"PROCESANDO AR INFOGRAFÍA: {moto_info['nombre']} ({moto_id})")
    print(f"==========================================")

    # 1. Generar texturas de tarjetas
    cards_list = []
    cards_dir = os.path.abspath(os.path.join("temp_cards", moto_id))
    os.makedirs(cards_dir, exist_ok=True)

    for i, c in enumerate(moto_info['cards']):
        clean_tag = c['category'].replace(' ', '_').replace('&', '').lower()
        card_img_path = os.path.join(cards_dir, f"card_{clean_tag}.png")
        generate_card_image(c['category'], c['title'], c['specs'], moto_info['accent'], card_img_path)
        cards_list.append({
            'category': c['category'],
            'pos': c['pos'],
            'target': c['target'],
            'img_path': card_img_path.replace('\\', '/')
        })

    # 2. Guardar configuracion en JSON para el worker de Blender
    glb_in = os.path.abspath(moto_info['glb'])
    out_glb = os.path.abspath(os.path.join("public", "models", f"{moto_id}_ar.glb"))
    out_usdz = os.path.abspath(os.path.join("public", "models", f"{moto_id}_ar.usdz"))

    config = {
        'glb_in': glb_in,
        'out_glb': out_glb,
        'out_usdz': out_usdz,
        'accent_hex': moto_info['accent'],
        'cards_data': cards_list
    }

    config_path = os.path.join(cards_dir, f"config_{moto_id}.json")
    import json
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # 3. Ejecutar Blender en modo headless pasando el worker
    worker_script = os.path.abspath(os.path.join("scripts", "blender_infographics_worker.py"))
    cmd = [BLENDER_EXE, "--background", "--python", worker_script, "--", config_path]
    print(f"Ejecutando Blender 5.2 para {moto_id}...")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

    if res.returncode != 0:
        print(f"[ERROR BLENDER] Salida:\n{res.stderr}\n{res.stdout}")
        return False

    # 4. Validar resultados
    if not os.path.exists(out_glb) or not os.path.exists(out_usdz):
        print(f"[ERROR] No se encontraron los archivos generados en {out_glb} o {out_usdz}")
        return False

    glb_size = os.path.getsize(out_glb) / (1024 * 1024)
    usdz_size = os.path.getsize(out_usdz) / (1024 * 1024)
    print(f"[EXITO] {moto_id}_ar.glb:  {glb_size:.2f} MB")
    print(f"[EXITO] {moto_id}_ar.usdz: {usdz_size:.2f} MB")
    return True

def main():
    if not os.path.exists(BLENDER_EXE):
        print(f"Error: Blender no encontrado en {BLENDER_EXE}")
        sys.exit(1)

    os.makedirs("temp_cards", exist_ok=True)
    success_count = 0
    for moto_id, moto_info in MOTOS_DATA.items():
        if process_moto(moto_id, moto_info):
            success_count += 1

    print(f"\n==========================================")
    print(f"PROCESADOS EXITOSAMENTE {success_count}/{len(MOTOS_DATA)} MODELOS CON INFOGRAFÍA 3D")
    print(f"==========================================")

if __name__ == '__main__':
    main()
