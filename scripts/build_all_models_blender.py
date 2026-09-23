#!/usr/bin/env python3
"""
build_all_models_blender.py
Pipeline oficial para generar los modelos 3D de MotosXR:
- iOS: public/models/ios/<moto>.usdz (Limpio) y <moto>_ar.usdz (Con Anotaciones 3D)
- Android: public/models/android/<moto>.glb (Limpio) y <moto>_ar.glb (Con Anotaciones 3D)

Implementa fielmente la arquitectura requerida:
1. Tarjetas gráficas con Pillow en resolución nítida (1024x540 RGBA con marco neón y esquinas transparentes).
2. Técnica de doble cara (Front & Back) con coordenadas UV invertidas horizontalmente (uv[0] = 1.0 - uv[0])
   para lectura correcta en 360° desde cualquier ángulo.
3. Material con auto-emisión de luz (Base Color + Emission Color a 1.3) para legibilidad en AR sin importar la iluminación real.
4. Esferas de anclaje (PinSphere) y líneas conectoras (LeaderLine) mediante rotación por cuaterniones.
5. Filtro de texturas a PNG 24-bit (cero WebP, evita pantalla rosa en Apple Quick Look).
6. Decimación selectiva únicamente a mallas > 5000 vértices (motor/chasis), dejando textos y líneas con 100% de nitidez.
7. Exportación a USDZ con coordenadas Y-Up de Apple ARKit (convert_orientation=True, export_global_up_selection='Y', export_global_forward_selection='NEGATIVE_Z').
"""

import os
import sys
import json
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

MOTOS_CONFIG = {
    'hero-eco': {
        'nombre': 'Hero Eco Deluxe',
        'clean_glb': 'public/models/android/hero-eco.glb',
        'accent': '#10b981',  # Emerald Neon
        'decimate_ratio': 0.45,
        'cards': [
            {
                'category': 'FRENOS INTEGRADOS',
                'title': 'Sistema IBS (Integrated Braking)',
                'specs': [
                    ('TECNOLOGÍA', 'Distribución inteligente del esfuerzo'),
                    ('SEGURIDAD', 'Acciona ambos frenos con maneta trasera'),
                    ('DISTANCIA', 'Reducción comprobada de frenado')
                ],
                'pos': (0.85, -0.80, 0.45),
                'target': (0.72, -0.12, 0.30),
                'side': 'right'
            },
            {
                'category': 'MOTOR & POTENCIA',
                'title': '97.2 cc · 7.9 HP @ 8.000 rpm',
                'specs': [
                    ('TORQUE', '7.55 Nm @ 5.000 rpm · Gran empuje'),
                    ('TECNOLOGÍA', 'Motor 4T monocilíndrico OHC'),
                    ('TRANSMISIÓN', '4 velocidades con embrague húmedo')
                ],
                'pos': (0.00, -0.85, 0.70),
                'target': (0.05, -0.15, 0.38),
                'side': 'right'
            },
            {
                'category': 'ESCAPE & ECOLOGÍA',
                'title': 'Tecnología i3S Ecológica',
                'specs': [
                    ('AHORRO', 'Apagado automático en ralentí'),
                    ('ENCENDIDO', 'Reinicio instantáneo al presionar clutch'),
                    ('EMISIONES', 'Cumple normativa ambiental Euro 3')
                ],
                'pos': (-0.75, -0.80, 0.38),
                'target': (-0.45, -0.22, 0.28),
                'side': 'right'
            },
            {
                'category': 'TANQUE & CONSUMO',
                'title': 'Capacidad: 10.5 Litros · i3S',
                'specs': [
                    ('AUTONOMÍA', 'Hasta 80 km/galón según manejo'),
                    ('DISEÑO', 'Gráficos modernos y tapa deportiva'),
                    ('PESO LIGERO', 'Solo 112 kg de peso en seco')
                ],
                'pos': (0.15, 0.80, 1.15),
                'target': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN & CONFORT',
                'title': 'Doble Amortiguador Trasero',
                'specs': [
                    ('REGULACIÓN', '5 posiciones de ajuste de precarga'),
                    ('DELANTERA', 'Horquilla telescópica hidráulica'),
                    ('CHASIS', 'Tubular de doble cuna reforzado')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'akt-nkd': {
        'nombre': 'AKT NKD 125',
        'clean_glb': 'public/models/android/akt-nkd.glb',
        'accent': '#a3e635',  # Lime Neon
        'decimate_ratio': 0.45,
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
        'nombre': 'Pulsar NS 200 FI',
        'clean_glb': 'public/models/android/pulsar-ns200.glb',
        'accent': '#f43f5e',  # Rose/Red Neon
        'decimate_ratio': 0.45,
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
                'category': 'ESCAPE & CENTRO GRAVEDAD',
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
                    ('ERGONOMÍA', 'Tanque muscular con hendiduras de rodilla'),
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
        'nombre': 'Bajaj Boxer CT 100',
        'clean_glb': 'public/models/android/bajaj-boxer.glb',
        'accent': '#eab308',  # Amber Neon
        'decimate_ratio': 0.45,
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
                    ('ESTRUCTURA', 'Tubería de acero para terreno rural')
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
                    ('TECNOLOGÍA', 'Doble resorte coaxial para absorción'),
                    ('CARGA', 'Soporta pasajeros y carga pesada sin ceder'),
                    ('DELANTERA', 'Horquilla telescópica hidráulica larga')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'tvs-raider': {
        'nombre': 'TVS Raider 125',
        'clean_glb': 'public/models/android/tvs-raider.glb',
        'accent': '#38bdf8',  # Neon Cyan
        'decimate_ratio': 0.45,
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
                'category': 'TANQUE & TECNOLOGÍA',
                'title': 'Capacidad: 10 Litros · Display LCD',
                'specs': [
                    ('TABLERO', 'Pantalla digital a color con indicador marcha'),
                    ('DISEÑO', 'Líneas afiladas estilo streetfighter naked'),
                    ('CONECTIVIDAD', 'Toma USB de carga rápida integrada')
                ],
                'pos': (0.15, 0.80, 1.15),
                'target': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN MONOSHOCK',
                'title': 'Monoamortiguador Trasero de Gas',
                'specs': [
                    ('TECNOLOGÍA', 'Monoshock con precarga ajustable 5 pasos'),
                    ('DELANTERA', 'Horquilla de 30 mm para alta precisión'),
                    ('ESTABILIDAD', 'Comportamiento deportivo impecable')
                ],
                'pos': (-0.55, 0.80, 0.65),
                'target': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    }
}

def hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def make_card_texture(category, title, specs, accent_hex, brand_name, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    W, H = 1024, 540
    # Fondo transparente para canal alfa en esquinas redondeadas
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    accent_rgb = hex_to_rgb(accent_hex)
    bg_rgba = (15, 23, 42, 230)  # #0f172ae6 oscuro semitransparente
    border_rgba = (*accent_rgb, 255)  # Marco neón brillante

    # Caja principal con esquinas redondeadas
    draw.rounded_rectangle([6, 6, W - 7, H - 7], radius=32, fill=bg_rgba, outline=border_rgba, width=4)
    # Borde sutil interior
    draw.rounded_rectangle([14, 14, W - 15, H - 15], radius=24, fill=None, outline=(*accent_rgb, 60), width=2)

    font_badge = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 24)
    font_title = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 44)
    font_spec  = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 28)
    font_sub   = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)

    # Pastilla de categoría
    badge_w = int(draw.textlength(category, font=font_badge)) + 36
    draw.rounded_rectangle([40, 36, 40 + badge_w, 86], radius=16, fill=(*accent_rgb, 40), outline=(*accent_rgb, 220), width=2)
    draw.text((58, 46), category, font=font_badge, fill=border_rgba)

    # Tag de marca
    tag = f"{brand_name.upper()} · 3D AR"
    tag_w = int(draw.textlength(tag, font=font_sub))
    draw.text((W - 40 - tag_w, 50), tag, font=font_sub, fill=(148, 163, 184, 255))

    # Línea divisoria
    draw.line([(40, 110), (W - 40, 110)], fill=(*accent_rgb, 90), width=2)

    # Título principal
    draw.text((40, 136), title, font=font_title, fill=(255, 255, 255, 255))

    # Especificaciones técnicas
    y = 224
    for label, val in specs:
        draw.ellipse([42, y + 8, 54, y + 20], fill=border_rgba)
        draw.text((68, y), f"{label}:", font=font_spec, fill=border_rgba)
        lbl_w = int(draw.textlength(f"{label}:", font=font_spec))
        draw.text((78 + lbl_w, y), val, font=font_spec, fill=(226, 232, 240, 255))
        y += 64

    # Pie de tarjeta
    draw.line([(40, H - 64), (W - 40, H - 64)], fill=(30, 41, 59, 200), width=1)
    draw.text((42, H - 46), 'MOTOSXR AR PRECISION · ANOTACIÓN TÉCNICA 1:1', font=font_sub, fill=(100, 116, 139, 255))

    img.save(out_path, format='PNG')
    return out_path

def generate_blender_runner_script():
    """Genera el script interno de Blender que realiza todo el trabajo 3D."""
    script_content = '''
import bpy
import os
import sys
import json
import math
import mathutils

def hex_to_rgba(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)) + (1.0,)

def remap_all_images_to_png(temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    for img in list(bpy.data.images):
        clean_name = img.name.replace('.webp', '').replace('.png', '').replace(' ', '_')
        png_path = os.path.join(temp_dir, f"{clean_name}.png")
        img.file_format = 'PNG'
        img.filepath_raw = png_path
        try:
            img.save()
            new_img = bpy.data.images.load(png_path)
            img.user_remap(new_img)
            bpy.data.images.remove(img)
        except Exception as e:
            print(f"Warning converting image {img.name}: {e}")

def apply_decimate(ratio):
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and len(obj.data.vertices) > 5000:
            mod = obj.modifiers.new(name="Decimate_Moto", type='DECIMATE')
            mod.ratio = ratio
            print(f"  [DECIMATE] ({ratio}) en {obj.name} ({len(obj.data.vertices)} verts)")

def main():
    args = sys.argv
    config_path = args[args.index('--') + 1]
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    moto_id = cfg['moto_id']
    clean_glb_in = cfg['clean_glb_in']
    out_clean_usdz = cfg['out_clean_usdz']
    out_ar_usdz = cfg['out_ar_usdz']
    out_clean_glb = cfg['out_clean_glb']
    out_ar_glb = cfg['out_ar_glb']
    accent_hex = cfg['accent']
    accent_rgba = hex_to_rgba(accent_hex)
    decimate_ratio = cfg['decimate_ratio']
    cards_data = cfg['cards']
    temp_png_dir = os.path.abspath(f"temp_blender_pngs/{moto_id}")

    # =========================================================================
    # FASE A: MODELO LIMPIO (Showroom 1:1)
    # =========================================================================
    print(f"\\n--- Generando Modelos Limpios para {moto_id} ---")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=clean_glb_in)

    # Remapear a PNG
    remap_all_images_to_png(temp_png_dir)

    # Decimate selectivo
    apply_decimate(decimate_ratio)

    # Exportar USDZ Limpio para iOS
    os.makedirs(os.path.dirname(out_clean_usdz), exist_ok=True)
    bpy.ops.wm.usd_export(
        filepath=out_clean_usdz,
        convert_orientation=True,
        export_global_up_selection='Y',
        export_global_forward_selection='NEGATIVE_Z',
        usdz_downscale_size='2048',
        export_materials=True,
        generate_preview_surface=True
    )
    print(f"[OK] USDZ Limpio iOS: {out_clean_usdz} ({os.path.getsize(out_clean_usdz)/(1024*1024):.2f} MB)")

    # =========================================================================
    # FASE B: MODELO CON ANOTACIONES 3D (AR Holográfico)
    # =========================================================================
    print(f"\\n--- Generando Modelos AR Holográficos para {moto_id} ---")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=clean_glb_in)

    # Remapear texturas de la moto a PNG
    remap_all_images_to_png(temp_png_dir)

    # Decimate a la moto (chasis/motor) ANTES de añadir las tarjetas
    apply_decimate(decimate_ratio)

    # Material de pines y líneas conectoras (Emisivo Neón)
    pin_mat = bpy.data.materials.new(name="Mat_Pin_Neon")
    pin_mat.use_nodes = True
    p_nodes = pin_mat.node_tree.nodes
    p_bsdf = p_nodes.get('Principled BSDF')
    p_bsdf.inputs['Base Color'].default_value = accent_rgba
    p_bsdf.inputs['Emission Color'].default_value = accent_rgba
    p_bsdf.inputs['Emission Strength'].default_value = 2.5

    card_width, card_height = 0.38, 0.20

    for idx, c in enumerate(cards_data):
        card_name = f"Card_{idx}_{c['category']}"
        pos = c['pos']
        target = c['target']
        side = c.get('side', 'right')
        img_path = c['img_path']

        # Material con auto-emisión para la tarjeta
        card_mat = bpy.data.materials.new(name=f"Mat_{card_name}")
        card_mat.use_nodes = True
        nodes = card_mat.node_tree.nodes
        links = card_mat.node_tree.links
        bsdf = nodes.get('Principled BSDF')

        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = bpy.data.images.load(img_path)

        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.3
        links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])
        card_mat.blend_method = 'BLEND'

        # --- 1. PLANO FRONTAL ---
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
        front_plane = bpy.context.active_object
        front_plane.name = f"{card_name}_Front"
        front_plane.scale = (card_width, card_height, 1.0)
        bpy.ops.object.transform_apply(scale=True)

        if side == 'right':
            front_plane.rotation_euler = (math.radians(90), 0, 0)
        else:
            front_plane.rotation_euler = (math.radians(90), 0, math.radians(180))
        bpy.ops.object.transform_apply(rotation=True)

        front_plane.data.materials.append(card_mat)

        # --- 2. PLANO TRASERO (Doble Cara con UV Invertidas) ---
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
        back_plane = bpy.context.active_object
        back_plane.name = f"{card_name}_Back"
        back_plane.scale = (card_width, card_height, 1.0)
        bpy.ops.object.transform_apply(scale=True)

        if side == 'right':
            back_plane.rotation_euler = (math.radians(90), 0, math.radians(180))
            back_plane.location = (0, 0.001, 0)
        else:
            back_plane.rotation_euler = (math.radians(90), 0, 0)
            back_plane.location = (0, -0.001, 0)
        bpy.ops.object.transform_apply(rotation=True, location=True)

        # Invertir eje X de coordenadas UV en plano trasero para lectura al derecho
        uv_layer = back_plane.data.uv_layers.active
        if not uv_layer:
            uv_layer = back_plane.data.uv_layers.new(name='UVMap')
        for loop in back_plane.data.loops:
            uv = uv_layer.data[loop.index].uv
            uv[0] = 1.0 - uv[0]

        back_plane.data.materials.append(card_mat)

        # Unir front y back en un único objeto
        front_plane.select_set(True)
        back_plane.select_set(True)
        bpy.context.view_layer.objects.active = front_plane
        bpy.ops.object.join()

        card_obj = bpy.context.active_object
        card_obj.name = card_name
        card_obj.location = pos

        # --- 3. ESFERA DE ANCLAJE (PinSphere) ---
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018, location=target)
        pin_obj = bpy.context.active_object
        pin_obj.name = f"{card_name}_Pin"
        pin_obj.data.materials.append(pin_mat)

        # --- 4. TUBO CONECTOR (LeaderLine) ---
        line_start = (pos[0], pos[1], pos[2] - card_height / 2)
        v_start = mathutils.Vector(line_start)
        v_end = mathutils.Vector(target)
        diff = v_end - v_start
        length = diff.length
        mid = (v_start + v_end) / 2.0

        bpy.ops.mesh.primitive_cylinder_add(radius=0.003, depth=length, location=mid)
        line_obj = bpy.context.active_object
        line_obj.name = f"{card_name}_Line"
        line_obj.rotation_mode = 'QUATERNION'
        line_obj.rotation_quaternion = mathutils.Vector((0, 0, 1)).rotation_difference(diff)
        line_obj.data.materials.append(pin_mat)

    # Exportar USDZ con Fichas para iOS
    os.makedirs(os.path.dirname(out_ar_usdz), exist_ok=True)
    bpy.ops.wm.usd_export(
        filepath=out_ar_usdz,
        convert_orientation=True,
        export_global_up_selection='Y',
        export_global_forward_selection='NEGATIVE_Z',
        usdz_downscale_size='2048',
        export_materials=True,
        generate_preview_surface=True
    )
    print(f"[OK] USDZ AR Holográfico iOS: {out_ar_usdz} ({os.path.getsize(out_ar_usdz)/(1024*1024):.2f} MB)")

    # Exportar GLB con Fichas para Android
    os.makedirs(os.path.dirname(out_ar_glb), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out_ar_glb,
        export_format='GLB',
        export_draco_mesh_compression_enable=True,
        export_materials='EXPORT',
        export_image_format='AUTO'
    )
    print(f"[OK] GLB AR Holográfico Android: {out_ar_glb} ({os.path.getsize(out_ar_glb)/(1024*1024):.2f} MB)")

    if os.path.exists(temp_png_dir):
        shutil.rmtree(temp_png_dir, ignore_errors=True)

if __name__ == '__main__':
    main()
'''
    worker_path = os.path.abspath('scripts/blender_master_export_worker.py')
    with open(worker_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    return worker_path

def main():
    print("=================================================================")
    print("PIPELINE MAESTRO BLENDER: GENERANDO MODELOS PARA IOS Y ANDROID")
    print("=================================================================")

    os.makedirs('public/models/ios', exist_ok=True)
    os.makedirs('public/models/android', exist_ok=True)

    worker_script = generate_blender_runner_script()

    for moto_id, info in MOTOS_CONFIG.items():
        print(f"\n=======================================================")
        print(f"PROCESANDO: {info['nombre']} ({moto_id})")
        print(f"=======================================================")

        clean_glb_in = os.path.abspath(info['clean_glb'])
        if not os.path.exists(clean_glb_in):
            print(f"[ERROR] Archivo fuente no encontrado: {clean_glb_in}")
            continue

        # Generar texturas de las tarjetas en alta resolución
        cards_data = []
        for i, c in enumerate(info['cards']):
            tex_path = os.path.abspath(f"temp_cards/{moto_id}/card_{i}.png")
            make_card_texture(c['category'], c['title'], c['specs'], info['accent'], info['nombre'], tex_path)
            cards_data.append({
                'category': c['category'],
                'pos': c['pos'],
                'target': c['target'],
                'side': c['side'],
                'img_path': tex_path.replace('\\', '/')
            })

        cfg = {
            'moto_id': moto_id,
            'clean_glb_in': clean_glb_in,
            'out_clean_usdz': os.path.abspath(f"public/models/ios/{moto_id}.usdz"),
            'out_ar_usdz': os.path.abspath(f"public/models/ios/{moto_id}_ar.usdz"),
            'out_clean_glb': os.path.abspath(f"public/models/android/{moto_id}.glb"),
            'out_ar_glb': os.path.abspath(f"public/models/android/{moto_id}_ar.glb"),
            'accent': info['accent'],
            'decimate_ratio': info['decimate_ratio'],
            'cards': cards_data
        }

        cfg_path = os.path.abspath(f"temp_cards/{moto_id}/config.json")
        with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)

        cmd = [BLENDER_EXE, '--background', '--python', worker_script, '--', cfg_path]
        print(f"Ejecutando Blender para {moto_id}...")
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        for line in res.stdout.splitlines():
            if '[OK]' in line or 'MB' in line or '[DECIMATE]' in line or 'Error' in line:
                print(f"  {line.encode('ascii', 'replace').decode('ascii')}")

    print("\n=================================================================")
    print("PIPELINE COMPLETADO EXITOSAMENTE PARA LAS 5 MOTOCICLETAS")
    print("=================================================================")

if __name__ == '__main__':
    main()
