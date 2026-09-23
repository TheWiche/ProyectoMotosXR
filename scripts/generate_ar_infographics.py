#!/usr/bin/env python3
"""
generate_ar_infographics.py
Pipeline automatizado con Blender 5.2 + Python (Pillow) para generar:
1. Tarjetas de infografía 2D en alta resolución Retina (1024x540 px) con Pillow:
   - Front Face: Ficha técnica legible, espaciada, alto contraste, badge neón.
   - Back Face: Placa oscura metalizada con logotipo de MotosXR (sin texto invertido).
2. Construcción 3D en Blender:
   - Posicionamiento radial espacioso (Y = ±0.80m a ±0.85m), alejadas del chasis para evitar colisiones.
   - Planos orientados hacia afuera (Normal -Y para lado derecho, Normal +Y para lado izquierdo).
   - Lectura de izquierda a derecha natural y upright desde cualquier lado del vehículo.
   - Mapeo UV exacto [0..1] sin tiling ni repeticiones.
   - Varillas cilíndricas neón y pines esféricos anclados a piezas mecánicas.
   - Decimate inteligente para cumplir la regla estricta de Safari (< 30 MB).
3. Exportación dual:
   - `<id>_ar.glb` (compresión Draco para Android Scene Viewer).
   - `<id>_ar.usdz` (Y-Up, cero WebP, empaquetado nativo para Apple ARKit Quick Look).
"""

import os
import sys
import json
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
                'category': 'FRENOS & SEGURIDAD',
                'title': 'Disco Lobulado 240 mm',
                'specs': [
                    ('CALIPER', 'Doble pistón con pastillas sinterizadas'),
                    ('SISTEMA', 'SBT síncrono con tambor trasero 130mm'),
                    ('RESPUESTA', 'Frenado inmediato y progresivo en lluvia')
                ],
                'pos': (0.85, -0.80, 0.45),
                'target': (0.72, -0.12, 0.30),
                'side': 'right'
            },
            {
                'category': 'MOTOR & POTENCIA',
                'title': '124.8 cc · 11.4 HP @ 7.500 rpm',
                'specs': [
                    ('TORQUE', '11.2 Nm @ 6.000 rpm · Excelente salida'),
                    ('TECNOLOGÍA', 'Motor 3 Válvulas monocilíndrico 4T'),
                    ('MODOS', 'Eco / Power con acelerador electrónico')
                ],
                'pos': (0.00, -0.85, 0.70),
                'target': (0.05, -0.15, 0.38),
                'side': 'right'
            },
            {
                'category': 'ESCAPE & RENDIMIENTO',
                'title': 'Escape Deportivo Racing DNA',
                'specs': [
                    ('DISEÑO', 'Salida elevada con protector de aluminio'),
                    ('SONIDO', 'Tono grave y deportivo TVS Racing'),
                    ('NORMATIVA', 'Catalizador integrado de bajas emisiones')
                ],
                'pos': (-0.75, -0.80, 0.38),
                'target': (-0.45, -0.22, 0.28),
                'side': 'right'
            },
            {
                'category': 'TANQUE & AUTONOMÍA',
                'title': 'Capacidad: 10 Litros · ~450 km',
                'specs': [
                    ('CONSUMO', 'Rendimiento sobresaliente ~45 km/L'),
                    ('PANEL', 'Tablero digital LCD a color con tacómetro'),
                    ('DISEÑO', 'Aletas aerodinámicas y puerto USB integrado')
                ],
                'pos': (0.15, 0.80, 1.15),
                'target': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN & CHASIS',
                'title': 'Monoshock Trasero a Gas',
                'specs': [
                    ('AJUSTE', 'Amortiguador monoshock de 5 pasos'),
                    ('DELANTERA', 'Horquilla telescópica de 30mm de diámetro'),
                    ('CHASIS', 'Bastidor tubular simple con gran rigidez')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'akt-nkd': {
        'nombre': 'AKT NKD 125',
        'glb': 'public/models/akt-nkd.glb',
        'accent': '#a3e635',  # Lime Neon
        'cards': [
            {
                'category': 'FRENOS & CONTROL',
                'title': 'Disco Delantero 240 mm',
                'specs': [
                    ('CALIPER', 'Doble pistón hidráulico de acción rápida'),
                    ('LÍNEAS', 'Conductos reforzados para tacto firme'),
                    ('SEGURIDAD', 'Excelente poder de detención urbana')
                ],
                'pos': (0.85, -0.80, 0.45),
                'target': (0.72, -0.12, 0.30),
                'side': 'right'
            },
            {
                'category': 'MOTOR & POTENCIA',
                'title': '125 cc 4T CGR · 11 HP @ 8.000 rpm',
                'specs': [
                    ('TORQUE', '8.8 Nm @ 6.000 rpm · Respuesta ágil'),
                    ('SISTEMA', 'Cadena de distribución de bajo ruido'),
                    ('CAJA', 'Transmisión de 5 velocidades sincronizadas')
                ],
                'pos': (0.00, -0.85, 0.70),
                'target': (0.05, -0.15, 0.38),
                'side': 'right'
            },
            {
                'category': 'ESCAPE & ESTILO',
                'title': 'Escape Estilo Café Racer',
                'specs': [
                    ('ACABADO', 'Silenciador negro mate deportivo'),
                    ('PROTECCIÓN', 'Placa antiquemaduras integrada'),
                    ('ACÚSTICA', 'Sonido clásico limpio y controlado')
                ],
                'pos': (-0.75, -0.80, 0.38),
                'target': (-0.45, -0.22, 0.28),
                'side': 'right'
            },
            {
                'category': 'TANQUE & AUTONOMÍA',
                'title': 'Capacidad: 13.5 Litros (3.5 Gal)',
                'specs': [
                    ('AUTONOMÍA', 'Más de 500 km por tanque lleno'),
                    ('LÍNEA', 'Forma aerodinámica estilo retro clásico'),
                    ('PESO TOTAL', 'Chasis ultra ligero de solo 118 kg')
                ],
                'pos': (0.15, 0.80, 1.15),
                'target': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN & CHASIS',
                'title': 'Doble Amortiguador Trasero',
                'specs': [
                    ('TRASERA', 'Doble shock regulable con resorte reforzado'),
                    ('DELANTERA', 'Horquilla telescópica hidráulica con fuelles'),
                    ('MANEJO', 'Máxima maniobrabilidad en tráfico pesado')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'pulsar-ns200': {
        'nombre': 'Pulsar NS 200',
        'glb': 'public/models/pulsar-ns200.glb',
        'accent': '#f43f5e',  # Rose/Red Neon
        'cards': [
            {
                'category': 'FRENOS & ABS',
                'title': 'Disco 300 mm con ABS ByBre',
                'specs': [
                    ('PINZAS', 'Fabricadas por ByBre (Brembo calipers)'),
                    ('SISTEMA', 'ABS antibloqueo en rueda delantera'),
                    ('TRASERO', 'Disco ventilado 230 mm con monopistón')
                ],
                'pos': (0.85, -0.80, 0.45),
                'target': (0.75, -0.12, 0.32),
                'side': 'right'
            },
            {
                'category': 'MOTOR & POTENCIA',
                'title': '199.5 cc · 24.5 HP @ 9.750 rpm',
                'specs': [
                    ('TORQUE', '18.74 Nm @ 8.000 rpm · Empuje explosivo'),
                    ('TECNOLOGÍA', 'Triple Chispa DTS-i · 4 Válvulas · EFI'),
                    ('REFRIGERACIÓN', 'Líquida por Radiador de alto rendimiento')
                ],
                'pos': (0.00, -0.85, 0.70),
                'target': (0.05, -0.15, 0.40),
                'side': 'right'
            },
            {
                'category': 'ESCAPE & CENTRO DE GRAVEDAD',
                'title': 'ExhausTEC Bajo Vientre',
                'specs': [
                    ('UBICACIÓN', 'Silenciador inferior centralizado'),
                    ('DINÁMICA', 'Distribución de masas perfecta 50:50'),
                    ('ESTABILIDAD', 'Centro de gravedad ultrabajo en curvas')
                ],
                'pos': (-0.45, -0.80, 0.35),
                'target': (-0.15, -0.15, 0.22),
                'side': 'right'
            },
            {
                'category': 'TANQUE & ERGONOMÍA',
                'title': 'Capacidad: 12 Litros · Naked Sport',
                'specs': [
                    ('ERGONOMÍA', 'Tanque muscular con hendiduras para rodillas'),
                    ('TABLERO', 'Consola análoga-digital con testigo RPM'),
                    ('MANILLAR', 'Semimanillares deportivos tipo clip-on')
                ],
                'pos': (0.15, 0.80, 1.15),
                'target': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN & CHASIS',
                'title': 'Chasis Perimetral + Nitrox',
                'specs': [
                    ('BASTIDOR', 'Perimetral de acero prensado de alta rigidez'),
                    ('MONOSHOCK', 'Amortiguador trasero con reservorio Nitrox'),
                    ('DELANTERA', 'Horquilla telescópica deportiva de 37 mm')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.50),
                'side': 'left'
            }
        ]
    },
    'bajaj-boxer': {
        'nombre': 'Bajaj Boxer 100',
        'glb': 'public/models/bajaj-boxer.glb',
        'accent': '#eab308',  # Amber Neon
        'cards': [
            {
                'category': 'FRENOS & DURABILIDAD',
                'title': 'Frenos de Tambor Reforzados 130 mm',
                'specs': [
                    ('ZAPATAS', 'Compuesto de alta duración y bajo desgaste'),
                    ('MANTENIMIENTO', 'Costo de repuestos sumamente económico'),
                    ('EFECTIVIDAD', 'Frenado consistente bajo carga pesada')
                ],
                'pos': (0.85, -0.80, 0.45),
                'target': (0.72, -0.12, 0.30),
                'side': 'right'
            },
            {
                'category': 'MOTOR & EFICIENCIA',
                'title': '100 cc 4T · 8.2 HP @ 7.500 rpm',
                'specs': [
                    ('TORQUE', '8.05 Nm @ 4.500 rpm · Gran fuerza a bajas RPM'),
                    ('CONFIABILIDAD', 'Motor guerrero para trabajo continuo'),
                    ('CONSUMO', 'Líder nacional en economía de combustible')
                ],
                'pos': (0.00, -0.85, 0.70),
                'target': (0.05, -0.15, 0.38),
                'side': 'right'
            },
            {
                'category': 'ESCAPE & CHASIS',
                'title': 'Silenciador Cromado Reforzado',
                'specs': [
                    ('ACABADO', 'Cromo anticorrosivo de larga duración'),
                    ('PARRILLA', 'Chasis extendido con soporte para carga'),
                    ('ESTRUCTURA', 'Tubería de acero diseñada para terreno rural')
                ],
                'pos': (-0.75, -0.80, 0.38),
                'target': (-0.45, -0.22, 0.28),
                'side': 'right'
            },
            {
                'category': 'TANQUE & RENDIMIENTO',
                'title': 'Capacidad: 11 Litros · > 500 km',
                'specs': [
                    ('RENDIMIENTO', 'Hasta 70 km por galón según manejo'),
                    ('MATERIAL', 'Tanque de acero con recubrimiento interior'),
                    ('TAPA', 'Tapa de rosca con sello hermético seguro')
                ],
                'pos': (0.15, 0.80, 1.15),
                'target': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN DE CARGA',
                'title': 'Suspensión SNS Spring-in-Spring',
                'specs': [
                    ('TECNOLOGÍA', 'Doble resorte coaxial para máxima absorción'),
                    ('CARGA', 'Soporta pasajeros y paquetes pesados sin ceder'),
                    ('DELANTERA', 'Horquilla telescópica hidráulica larga')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'hero-eco': {
        'nombre': 'Hero Eco Deluxe',
        'glb': 'public/models/hero-eco.glb',
        'accent': '#10b981',  # Emerald Neon
        'cards': [
            {
                'category': 'FRENOS INTEGRADOS',
                'title': 'Sistema IBS (Integrated Braking)',
                'specs': [
                    ('TECNOLOGÍA', 'Distribución inteligente del esfuerzo de parada'),
                    ('SEGURIDAD', 'Acciona ambos frenos con la maneta trasera'),
                    ('DISTANCIA', 'Reducción comprobada en distancia de parada')
                ],
                'pos': (0.85, -0.80, 0.45),
                'target': (0.72, -0.12, 0.30),
                'side': 'right'
            },
            {
                'category': 'MOTOR & TECNOLOGÍA',
                'title': '97.2 cc OHC · 7.9 HP @ 8.000 rpm',
                'specs': [
                    ('SISTEMA i3S', 'Start-Stop automático de parada en semáforos'),
                    ('TORQUE', '7.55 Nm @ 5.000 rpm con excelente elasticidad'),
                    ('EFICIENCIA', 'Mínimas emisiones y altísimo rendimiento')
                ],
                'pos': (0.00, -0.85, 0.70),
                'target': (0.05, -0.15, 0.38),
                'side': 'right'
            },
            {
                'category': 'ESCAPE & ACABADOS',
                'title': 'Escape Ecológico con Protector',
                'specs': [
                    ('PROTECCIÓN', 'Escudo cromado protector contra altas temperaturas'),
                    ('CATALIZADOR', 'Filtro de emisiones amigable con el medio ambiente'),
                    ('PESO', 'Conjunto ultra ligero de tan solo 112 kg')
                ],
                'pos': (-0.75, -0.80, 0.38),
                'target': (-0.45, -0.22, 0.28),
                'side': 'right'
            },
            {
                'category': 'TANQUE & AUTONOMÍA',
                'title': 'Capacidad: 10.5 Litros · Eco Drive',
                'specs': [
                    ('INDICADOR', 'Tablero con velocímetro e indicador i3S'),
                    ('AUTONOMÍA', 'Diseñado para semanas enteras de movilidad urbana'),
                    ('COMODIDAD', 'Asiento amplio y ergonómico para dos personas')
                ],
                'pos': (0.15, 0.80, 1.15),
                'target': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN AJUSTABLE',
                'title': 'Doble Amortiguador de 2 Pasos',
                'specs': [
                    ('TRASERA', 'Amortiguadores hidráulicos regulables en precarga'),
                    ('DELANTERA', 'Horquilla telescópica suave para asfalto irregular'),
                    ('CONFORT', 'Absorción superior de resaltos y huecos urbanos')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    }
}

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def generate_card_image(category, title, specs, accent_hex, brand_name, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    W, H = 1024, 540
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    accent_rgb = hex_to_rgb(accent_hex)
    bg_rgba = (10, 15, 29, 250)
    border_rgba = (*accent_rgb, 255)

    # Main Card Box
    draw.rounded_rectangle([6, 6, W-7, H-7], radius=32, fill=bg_rgba, outline=border_rgba, width=4)
    # Inner subtle glow border
    draw.rounded_rectangle([14, 14, W-15, H-15], radius=24, fill=None, outline=(*accent_rgb, 60), width=2)

    font_badge = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 24)
    font_title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 44)
    font_spec  = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 28)
    font_sub   = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)

    # Badge Pill
    badge_w = int(draw.textlength(category, font=font_badge)) + 36
    draw.rounded_rectangle([40, 36, 40 + badge_w, 86], radius=16, fill=(*accent_rgb, 40), outline=(*accent_rgb, 220), width=2)
    draw.text((58, 46), category, font=font_badge, fill=border_rgba)

    # Brand Tag
    tag = f"{brand_name.upper()} · 3D AR"
    tag_w = int(draw.textlength(tag, font=font_sub))
    draw.text((W - 40 - tag_w, 50), tag, font=font_sub, fill=(148, 163, 184, 255))

    # Divider line
    draw.line([(40, 110), (W - 40, 110)], fill=(*accent_rgb, 90), width=2)

    # Main Title / Value
    draw.text((40, 136), title, font=font_title, fill=(255, 255, 255, 255))

    # Specs
    y = 224
    for label, val in specs:
        draw.ellipse([42, y + 8, 54, y + 20], fill=border_rgba)
        draw.text((68, y), f"{label}:", font=font_spec, fill=border_rgba)
        lbl_w = int(draw.textlength(f"{label}:", font=font_spec))
        draw.text((78 + lbl_w, y), val, font=font_spec, fill=(226, 232, 240, 255))
        y += 64

    # Footer
    draw.line([(40, H - 64), (W - 40, H - 64)], fill=(30, 41, 59, 200), width=1)
    draw.text((42, H - 46), 'MOTOSXR AR PRECISION · ANOTACIÓN TÉCNICA 1:1', font=font_sub, fill=(100, 116, 139, 255))

    img.save(out_path, format='PNG')
    return out_path

def generate_backplate_image(accent_hex, brand_name, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    W, H = 1024, 540
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    accent_rgb = hex_to_rgb(accent_hex)
    bg_rgba = (10, 15, 29, 250)
    border_rgba = (*accent_rgb, 255)

    draw.rounded_rectangle([6, 6, W-7, H-7], radius=32, fill=bg_rgba, outline=border_rgba, width=4)
    draw.rounded_rectangle([14, 14, W-15, H-15], radius=24, fill=None, outline=(*accent_rgb, 60), width=2)

    font_logo = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 54)
    font_sub  = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 24)
    font_sub2 = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 18)

    logo_text = "MotosXR"
    w1 = int(draw.textlength(logo_text, font=font_logo))
    draw.text(((W - w1) // 2, H // 2 - 55), logo_text, font=font_logo, fill=(255, 255, 255, 255))

    sub_text = f"{brand_name.upper()} · FICHA TÉCNICA HOLOGRÁFICA"
    w2 = int(draw.textlength(sub_text, font=font_sub))
    draw.text(((W - w2) // 2, H // 2 + 20), sub_text, font=font_sub, fill=border_rgba)

    sub2 = "VISOR DE REALIDAD AUMENTADA 1:1"
    w3 = int(draw.textlength(sub2, font=font_sub2))
    draw.text(((W - w3) // 2, H // 2 + 65), sub2, font=font_sub2, fill=(148, 163, 184, 255))

    img.save(out_path, format='PNG')
    return out_path

def process_moto(moto_id, moto_info):
    print(f"\n==========================================")
    print(f"PROCESANDO AR INFOGRAFÍA: {moto_info['nombre']} ({moto_id})")
    print(f"==========================================")

    cards_dir = os.path.abspath(os.path.join("temp_cards", moto_id))
    os.makedirs(cards_dir, exist_ok=True)

    # 1. Generar backplate compartido
    backplate_path = os.path.join(cards_dir, "card_backplate.png")
    generate_backplate_image(moto_info['accent'], moto_info['nombre'], backplate_path)

    # 2. Generar tarjetas de especificaciones
    cards_list = []
    for i, c in enumerate(moto_info['cards']):
        clean_tag = c['category'].replace(' ', '_').replace('&', '').replace('+', '').lower()
        card_img_path = os.path.join(cards_dir, f"card_{i}_{clean_tag}.png")
        generate_card_image(c['category'], c['title'], c['specs'], moto_info['accent'], moto_info['nombre'], card_img_path)
        cards_list.append({
            'category': c['category'],
            'pos': c['pos'],
            'target': c['target'],
            'side': c['side'],
            'img_path': card_img_path.replace('\\', '/')
        })

    # 3. Guardar configuracion JSON para el worker de Blender
    glb_in = os.path.abspath(moto_info['glb'])
    out_glb = os.path.abspath(os.path.join("public", "models", f"{moto_id}_ar.glb"))
    out_usdz = os.path.abspath(os.path.join("public", "models", f"{moto_id}_ar.usdz"))

    config = {
        'glb_in': glb_in,
        'out_glb': out_glb,
        'out_usdz': out_usdz,
        'accent_hex': moto_info['accent'],
        'backplate_path': backplate_path.replace('\\', '/'),
        'cards_data': cards_list
    }

    config_path = os.path.join(cards_dir, f"config_{moto_id}.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # 4. Ejecutar Blender headless
    worker_script = os.path.abspath(os.path.join("scripts", "blender_infographics_worker.py"))
    cmd = [BLENDER_EXE, "--background", "--python", worker_script, "--", config_path]
    print(f"Ejecutando Blender 5.2 para {moto_id}...")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

    if res.returncode != 0:
        print(f"[ERROR BLENDER] Salida:\n{res.stderr}\n{res.stdout}")
        return False

    # 5. Validar archivos resultantes
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
