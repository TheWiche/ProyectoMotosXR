#!/usr/bin/env python3
"""
process_user_usdz.py
Procesa los modelos USDZ originales descargados por el usuario:
1. 'Hero eco deluxe/hero.usdz' -> 'public/models/hero-eco.usdz' & 'hero-eco_ar.usdz'
2. 'Akt Nkd/nkd.usdz'         -> 'public/models/akt-nkd.usdz'  & 'akt-nkd_ar.usdz'
3. 'Bajaj Boxer/boxer.usdz'   -> 'public/models/bajaj-boxer.usdz' & 'bajaj-boxer_ar.usdz'
4. 'Pulsar ns 200/ns200.usdz' -> 'public/models/pulsar-ns200.usdz' & 'pulsar-ns200_ar.usdz'
5. 'Tvs raider/raider.usdz'   -> 'public/models/tvs-raider.usdz' & 'tvs-raider_ar.usdz'

Optimizaciones SIN decimation ni distorsión de malla:
- Malla 100% original intacta (vértices y normales preservados).
- Eliminación de la primvar redundante 'primvars:tangents' (ahorro de 20-30 MB).
- Texturas redimensionadas de 8K a resolución Retina 2K (2048x2048 JPEG/PNG).
- Empaquetado oficial con alineación estricta de 64 bytes para Apple ARKit Quick Look.
- Generación e inserción nativa de las 5 anotaciones técnicas 3D (HUD Retina 1024x540) en '_ar.usdz'.
- Generación de los modelos '_ar.glb' para Android sin decimate.
"""

import os
import sys
import glob
import json
import shutil
import zipfile
import tempfile
import struct
import binascii
import subprocess
from PIL import Image, ImageDraw, ImageFont
from pxr import Usd, UsdGeom, UsdShade, UsdUtils, Sdf, Gf

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

class AlignedUSDZWriter:
    """Escribe archivos .usdz con compresión STORED y alineación exacta de 64 bytes."""
    def __init__(self, filepath):
        self.filepath = filepath
        self.f = open(filepath, 'wb')
        self.records = []
        
    def add_file(self, arcname, data):
        header_offset = self.f.tell()
        filename_bytes = arcname.encode('utf-8')
        prefix_len = header_offset + 30 + len(filename_bytes)
        padding = (64 - (prefix_len % 64)) % 64
        extra = b'\x00' * padding
        
        crc = binascii.crc32(data) & 0xffffffff
        size = len(data)
        
        header = struct.pack(
            '<IHHHHHIIIHH',
            0x04034b50, 20, 0, 0, 0, 0,
            crc, size, size, len(filename_bytes), len(extra)
        )
        self.f.write(header)
        self.f.write(filename_bytes)
        self.f.write(extra)
        
        assert self.f.tell() % 64 == 0, f"Offset {self.f.tell()} no está alineado a 64 bytes"
        self.f.write(data)
        
        self.records.append({
            'arcname': filename_bytes,
            'header_offset': header_offset,
            'crc': crc,
            'size': size,
        })
        
    def close(self):
        cd_offset = self.f.tell()
        for r in self.records:
            cd_hdr = struct.pack(
                '<IHHHHHHIIIHHHHHII',
                0x02014b50, 20, 20, 0, 0, 0, 0,
                r['crc'], r['size'], r['size'],
                len(r['arcname']), 0, 0, 0, 0, 0,
                r['header_offset']
            )
            self.f.write(cd_hdr)
            self.f.write(r['arcname'])
            
        cd_size = self.f.tell() - cd_offset
        eocd = struct.pack(
            '<IHHHHIIH',
            0x06054b50, 0, 0,
            len(self.records), len(self.records),
            cd_size, cd_offset, 0
        )
        self.f.write(eocd)
        self.f.close()


MOTOS_CONFIG = {
    'tvs-raider': {
        'nombre': 'TVS Raider 125',
        'src_usdz': 'Tvs raider/raider.usdz',
        'clean_glb': 'public/models/android/tvs-raider.glb',
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
                'pos_usd': (0.85, 0.45, -0.80),
                'target_usd': (0.72, 0.30, -0.12),
                'pos_blender': (0.85, -0.80, 0.45),
                'target_blender': (0.72, -0.12, 0.30),
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
                'pos_usd': (0.00, 0.70, -0.85),
                'target_usd': (0.05, 0.38, -0.15),
                'pos_blender': (0.00, -0.85, 0.70),
                'target_blender': (0.05, -0.15, 0.38),
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
                'pos_usd': (-0.75, 0.38, -0.80),
                'target_usd': (-0.45, 0.28, -0.22),
                'pos_blender': (-0.75, -0.80, 0.38),
                'target_blender': (-0.45, -0.22, 0.28),
                'side': 'right'
            },
            {
                'category': 'TANQUE & AUTONOMÍA',
                'title': 'Capacidad: 10 Litros · ~450 km',
                'specs': [
                    ('CONSUMO', 'Rendimiento sobresaliente ~45 km/L'),
                    ('PANEL', 'Tablero digital LCD a color con tacómetro'),
                    ('DISEÑO', 'Aletas aerodinámicas y puerto USB')
                ],
                'pos_usd': (0.15, 1.15, 0.80),
                'target_usd': (0.15, 0.88, 0.00),
                'pos_blender': (0.15, 0.80, 1.15),
                'target_blender': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN & CHASIS',
                'title': 'Monoshock Trasero a Gas',
                'specs': [
                    ('AJUSTE', 'Amortiguador monoshock de 5 pasos'),
                    ('DELANTERA', 'Horquilla telescópica de 30mm de diámetro'),
                    ('CHASIS', 'Bastidor tubular simple de gran rigidez')
                ],
                'pos_usd': (-0.55, 0.65, 0.80),
                'target_usd': (-0.35, 0.48, 0.08),
                'pos_blender': (-0.55, 0.80, 0.65),
                'target_blender': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'akt-nkd': {
        'nombre': 'AKT NKD 125',
        'src_usdz': 'Akt Nkd/nkd.usdz',
        'clean_glb': 'public/models/android/akt-nkd.glb',
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
                'pos_usd': (0.85, 0.45, -0.80),
                'target_usd': (0.72, 0.30, -0.12),
                'pos_blender': (0.85, -0.80, 0.45),
                'target_blender': (0.72, -0.12, 0.30),
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
                'pos_usd': (0.00, 0.70, -0.85),
                'target_usd': (0.05, 0.38, -0.15),
                'pos_blender': (0.00, -0.85, 0.70),
                'target_blender': (0.05, -0.15, 0.38),
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
                'pos_usd': (-0.75, 0.38, -0.80),
                'target_usd': (-0.45, 0.28, -0.22),
                'pos_blender': (-0.75, -0.80, 0.38),
                'target_blender': (-0.45, -0.22, 0.28),
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
                'pos_usd': (0.15, 1.15, 0.80),
                'target_usd': (0.15, 0.88, 0.00),
                'pos_blender': (0.15, 0.80, 1.15),
                'target_blender': (0.15, 0.00, 0.88),
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
                'pos_usd': (-0.55, 0.65, 0.80),
                'target_usd': (-0.35, 0.48, 0.08),
                'pos_blender': (-0.55, 0.80, 0.65),
                'target_blender': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'pulsar-ns200': {
        'nombre': 'Pulsar NS 200',
        'src_usdz': 'Pulsar ns 200/ns200.usdz',
        'clean_glb': 'public/models/android/pulsar-ns200.glb',
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
                'pos_usd': (0.85, 0.45, -0.80),
                'target_usd': (0.75, 0.32, -0.12),
                'pos_blender': (0.85, -0.80, 0.45),
                'target_blender': (0.75, -0.12, 0.32),
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
                'pos_usd': (0.00, 0.70, -0.85),
                'target_usd': (0.05, 0.40, -0.15),
                'pos_blender': (0.00, -0.85, 0.70),
                'target_blender': (0.05, -0.15, 0.40),
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
                'pos_usd': (-0.45, 0.35, -0.80),
                'target_usd': (-0.15, 0.22, -0.15),
                'pos_blender': (-0.45, -0.80, 0.35),
                'target_blender': (-0.15, -0.15, 0.22),
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
                'pos_usd': (0.15, 1.15, 0.80),
                'target_usd': (0.15, 0.88, 0.00),
                'pos_blender': (0.15, 0.80, 1.15),
                'target_blender': (0.15, 0.00, 0.88),
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
                'pos_usd': (-0.55, 0.65, 0.80),
                'target_usd': (-0.35, 0.50, 0.08),
                'pos_blender': (-0.55, 0.80, 0.65),
                'target_blender': (-0.35, 0.08, 0.50),
                'side': 'left'
            }
        ]
    },
    'bajaj-boxer': {
        'nombre': 'Bajaj Boxer 100',
        'src_usdz': 'Bajaj Boxer/boxer.usdz',
        'clean_glb': 'public/models/android/bajaj-boxer.glb',
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
                'pos_usd': (0.85, 0.45, -0.80),
                'target_usd': (0.72, 0.30, -0.12),
                'pos_blender': (0.85, -0.80, 0.45),
                'target_blender': (0.72, -0.12, 0.30),
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
                'pos_usd': (0.00, 0.70, -0.85),
                'target_usd': (0.05, 0.38, -0.15),
                'pos_blender': (0.00, -0.85, 0.70),
                'target_blender': (0.05, -0.15, 0.38),
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
                'pos_usd': (-0.75, 0.38, -0.80),
                'target_usd': (-0.45, 0.28, -0.22),
                'pos_blender': (-0.75, -0.80, 0.38),
                'target_blender': (-0.45, -0.22, 0.28),
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
                'pos_usd': (0.15, 1.15, 0.80),
                'target_usd': (0.15, 0.88, 0.00),
                'pos_blender': (0.15, 0.80, 1.15),
                'target_blender': (0.15, 0.00, 0.88),
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
                'pos_usd': (-0.55, 0.65, 0.80),
                'target_usd': (-0.35, 0.48, 0.08),
                'pos_blender': (-0.55, 0.80, 0.65),
                'target_blender': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    },
    'hero-eco': {
        'nombre': 'Hero Eco Deluxe',
        'src_usdz': 'Hero eco deluxe/hero.usdz',
        'clean_glb': 'public/models/android/hero-eco.glb',
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
                'pos_usd': (0.85, 0.45, -0.80),
                'target_usd': (0.72, 0.30, -0.12),
                'pos_blender': (0.85, -0.80, 0.45),
                'target_blender': (0.72, -0.12, 0.30),
                'side': 'right'
            },
            {
                'category': 'MOTOR & TECNOLOGÍA',
                'title': '97.2 cc OHC · 7.9 HP @ 8.000 rpm',
                'specs': [
                    ('SISTEMA i3S', 'Start-Stop automático de parada en semáforos'),
                    ('TORQUE', '7.55 Nm @ 5.000 rpm con gran elasticidad'),
                    ('EFICIENCIA', 'Mínimas emisiones y altísimo rendimiento')
                ],
                'pos_usd': (0.00, 0.70, -0.85),
                'target_usd': (0.05, 0.38, -0.15),
                'pos_blender': (0.00, -0.85, 0.70),
                'target_blender': (0.05, -0.15, 0.38),
                'side': 'right'
            },
            {
                'category': 'ESCAPE & ACABADOS',
                'title': 'Escape Ecológico con Protector',
                'specs': [
                    ('PROTECCIÓN', 'Escudo cromado protector antiquemaduras'),
                    ('CATALIZADOR', 'Filtro de emisiones ecológico amigable'),
                    ('PESO', 'Conjunto ultra ligero de tan solo 112 kg')
                ],
                'pos_usd': (-0.75, 0.38, -0.80),
                'target_usd': (-0.45, 0.28, -0.22),
                'pos_blender': (-0.75, -0.80, 0.38),
                'target_blender': (-0.45, -0.22, 0.28),
                'side': 'right'
            },
            {
                'category': 'TANQUE & AUTONOMÍA',
                'title': 'Capacidad: 10.5 Litros · Eco Drive',
                'specs': [
                    ('INDICADOR', 'Tablero con velocímetro e indicador i3S'),
                    ('AUTONOMÍA', 'Diseñado para semanas enteras en ciudad'),
                    ('COMODIDAD', 'Asiento amplio y ergonómico para dos')
                ],
                'pos_usd': (0.15, 1.15, 0.80),
                'target_usd': (0.15, 0.88, 0.00),
                'pos_blender': (0.15, 0.80, 1.15),
                'target_blender': (0.15, 0.00, 0.88),
                'side': 'left'
            },
            {
                'category': 'SUSPENSIÓN AJUSTABLE',
                'title': 'Doble Amortiguador de 2 Pasos',
                'specs': [
                    ('TRASERA', 'Amortiguadores hidráulicos regulables'),
                    ('DELANTERA', 'Horquilla telescópica suave para asfalto'),
                    ('CONFORT', 'Absorción superior de resaltos y huecos')
                ],
                'pos_usd': (-0.55, 0.65, 0.80),
                'target_usd': (-0.35, 0.48, 0.08),
                'pos_blender': (-0.55, 0.80, 0.65),
                'target_blender': (-0.35, 0.08, 0.48),
                'side': 'left'
            }
        ]
    }
}

def hex_to_rgb(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def make_front_card(category, title, specs, accent_hex, brand_name, out_path):
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

def make_backplate(accent_hex, brand_name, out_path):
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

def create_texture_material(stage, mat_path, tex_file):
    existing = stage.GetPrimAtPath(mat_path)
    if existing:
        return UsdShade.Material(existing)
        
    material = UsdShade.Material.Define(stage, mat_path)
    pbr = UsdShade.Shader.Define(stage, f'{mat_path}/PBRShader')
    pbr.CreateIdAttr('UsdPreviewSurface')
    
    reader = UsdShade.Shader.Define(stage, f'{mat_path}/stReader')
    reader.CreateIdAttr('UsdPrimvarReader_float2')
    reader.CreateInput('varname', Sdf.ValueTypeNames.Token).Set('st')
    
    tex = UsdShade.Shader.Define(stage, f'{mat_path}/texSampler')
    tex.CreateIdAttr('UsdUVTexture')
    tex.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath(os.path.basename(tex_file)))
    tex.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(reader.CreateOutput('result', Sdf.ValueTypeNames.Float2))
    
    pbr.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.CreateOutput('rgb', Sdf.ValueTypeNames.Color3f))
    pbr.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.CreateOutput('rgb', Sdf.ValueTypeNames.Color3f))
    pbr.CreateInput('opacity', Sdf.ValueTypeNames.Float).ConnectToSource(tex.CreateOutput('a', Sdf.ValueTypeNames.Float))
    
    material.CreateSurfaceOutput().ConnectToSource(pbr.CreateOutput('surface', Sdf.ValueTypeNames.Token))
    return material

def process_single_moto(moto_id, moto_info):
    print(f"\n=======================================================")
    print(f"PROCESANDO MODELO USDZ: {moto_info['nombre']} ({moto_id})")
    print(f"=======================================================")
    
    src_usdz = moto_info['src_usdz']
    if not os.path.exists(src_usdz):
        print(f"[ERROR] Archivo fuente no encontrado: {src_usdz}")
        return False
        
    os.makedirs("public/models/ios", exist_ok=True)
    os.makedirs("public/models/android", exist_ok=True)
    out_clean_usdz = os.path.abspath(f"public/models/ios/{moto_id}.usdz")
    out_ar_usdz = os.path.abspath(f"public/models/ios/{moto_id}_ar.usdz")
    out_ar_glb = os.path.abspath(f"public/models/android/{moto_id}_ar.glb")
    
    # 1. Extraer USDZ del usuario
    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(src_usdz, 'r') as z:
            z.extractall(tmpdir)
            
        usdc_files = [f for f in os.listdir(tmpdir) if f.endswith('.usdc')]
        if not usdc_files:
            print("[ERROR] No se encontró archivo .usdc en el paquete USDZ")
            return False
            
        usdc_name = usdc_files[0]
        usdc_path = os.path.join(tmpdir, usdc_name)
        
        # 2. Optimizar Stage USD (Remover 'primvars:tangents')
        stage = Usd.Stage.Open(usdc_path)
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                if prim.HasProperty('primvars:tangents'):
                    prim.RemoveProperty('primvars:tangents')
                    
        # Asegurar rutas de texturas estrictamente relativas (sin rutas de temp ni absolutas)
        for prim in stage.Traverse():
            if prim.IsA(UsdShade.Shader):
                shader = UsdShade.Shader(prim)
                inp = shader.GetInput('file')
                if inp:
                    val = inp.Get()
                    if val and hasattr(val, 'path'):
                        base_name = os.path.basename(val.path)
                        inp.Set(Sdf.AssetPath(base_name))
        stage.GetRootLayer().Save()
            
        # 3. Optimizar texturas nativas a Retina 2K (2048x2048 max)
        for fname in os.listdir(tmpdir):
            fpath = os.path.join(tmpdir, fname)
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    with Image.open(fpath) as img:
                        if max(img.size) > 2048:
                            orig_sz = img.size
                            img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                            fmt = 'JPEG' if fname.lower().endswith(('.jpg', '.jpeg')) else 'PNG'
                            img.save(fpath, format=fmt, quality=88, optimize=True)
                            print(f"  [Textura Optimizada] {fname}: {orig_sz} -> {img.size}")
                except Exception as e:
                    print(f"  [WARN] No se pudo redimensionar {fname}: {e}")
                    
        # 4. Guardar archivo LIMPIO: public/models/<id>.usdz
        writer_clean = AlignedUSDZWriter(out_clean_usdz)
        with open(usdc_path, 'rb') as f:
            writer_clean.add_file(usdc_name, f.read())
        for fname in sorted(os.listdir(tmpdir)):
            if fname != usdc_name and not fname.endswith('.usdz'):
                fpath = os.path.join(tmpdir, fname)
                with open(fpath, 'rb') as f:
                    writer_clean.add_file(fname, f.read())
        writer_clean.close()
        clean_sz = os.path.getsize(out_clean_usdz) / (1024 * 1024)
        print(f"[EXITO LIMPIO] {moto_id}.usdz: {clean_sz:.2f} MB")
        
        # 5. Generar Tarjetas de Infografía en Pillow
        cards_dir = os.path.abspath(os.path.join("temp_cards", moto_id))
        os.makedirs(cards_dir, exist_ok=True)
        
        backplate_name = "card_backplate.png"
        backplate_path = os.path.join(tmpdir, backplate_name)
        make_backplate(moto_info['accent'], moto_info['nombre'], backplate_path)
        
        card_tex_files = []
        for i, c in enumerate(moto_info['cards']):
            tex_name = f"card_{i}.png"
            tex_path = os.path.join(tmpdir, tex_name)
            make_front_card(c['category'], c['title'], c['specs'], moto_info['accent'], moto_info['nombre'], tex_path)
            card_tex_files.append((tex_name, tex_path))
            
        # 6. Añadir Anotaciones 3D al Stage USD
        accent_rgb_tuple = hex_to_rgb(moto_info['accent'])
        accent_gf = Gf.Vec3f(accent_rgb_tuple[0]/255.0, accent_rgb_tuple[1]/255.0, accent_rgb_tuple[2]/255.0)
        
        pin_mat = UsdShade.Material.Define(stage, '/Root/Materials/Mat_NeonPin')
        pin_shader = UsdShade.Shader.Define(stage, '/Root/Materials/Mat_NeonPin/PBRShader')
        pin_shader.CreateIdAttr('UsdPreviewSurface')
        pin_shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(accent_gf)
        pin_shader.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f).Set(accent_gf * 2.5)
        pin_mat.CreateSurfaceOutput().ConnectToSource(pin_shader.CreateOutput('surface', Sdf.ValueTypeNames.Token))
        
        card_width, card_height = 0.38, 0.20
        back_mat = create_texture_material(stage, '/Root/Materials/Mat_Backplate', f'./{backplate_name}')
        
        for idx, c in enumerate(moto_info['cards']):
            pos = c['pos_usd']
            target = c['target_usd']
            side = c['side']
            front_tex_rel = f"./card_{idx}.png"
            card_root = f"/Root/Annotations/Card_{idx}"
            card_xform = UsdGeom.Xform.Define(stage, card_root)
            
            # --- Front Quad Mesh ---
            front_mesh = UsdGeom.Mesh.Define(stage, f"{card_root}/Front")
            if side == 'right':
                pts_front = [
                    Gf.Vec3f(-card_width/2, -card_height/2, 0.0),
                    Gf.Vec3f( card_width/2, -card_height/2, 0.0),
                    Gf.Vec3f( card_width/2,  card_height/2, 0.0),
                    Gf.Vec3f(-card_width/2,  card_height/2, 0.0)
                ]
            else:
                pts_front = [
                    Gf.Vec3f( card_width/2, -card_height/2, 0.0),
                    Gf.Vec3f(-card_width/2, -card_height/2, 0.0),
                    Gf.Vec3f(-card_width/2,  card_height/2, 0.0),
                    Gf.Vec3f( card_width/2,  card_height/2, 0.0)
                ]
            front_mesh.CreatePointsAttr(pts_front)
            front_mesh.CreateFaceVertexCountsAttr([4])
            front_mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
            uv_f = UsdGeom.PrimvarsAPI(front_mesh).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.varying)
            uv_f.Set([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
            
            front_mat = create_texture_material(stage, f"/Root/Materials/Mat_Card_{idx}_Front", front_tex_rel)
            UsdShade.MaterialBindingAPI(front_mesh).Bind(front_mat)
            
            # --- Back Quad Mesh (Backplate) ---
            back_mesh = UsdGeom.Mesh.Define(stage, f"{card_root}/Back")
            z_off = 0.003 if side == 'right' else -0.003
            if side == 'right':
                pts_back = [
                    Gf.Vec3f( card_width/2, -card_height/2, z_off),
                    Gf.Vec3f(-card_width/2, -card_height/2, z_off),
                    Gf.Vec3f(-card_width/2,  card_height/2, z_off),
                    Gf.Vec3f( card_width/2,  card_height/2, z_off)
                ]
            else:
                pts_back = [
                    Gf.Vec3f(-card_width/2, -card_height/2, z_off),
                    Gf.Vec3f( card_width/2, -card_height/2, z_off),
                    Gf.Vec3f( card_width/2,  card_height/2, z_off),
                    Gf.Vec3f(-card_width/2,  card_height/2, z_off)
                ]
            back_mesh.CreatePointsAttr(pts_back)
            back_mesh.CreateFaceVertexCountsAttr([4])
            back_mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
            uv_b = UsdGeom.PrimvarsAPI(back_mesh).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.varying)
            uv_b.Set([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
            UsdShade.MaterialBindingAPI(back_mesh).Bind(back_mat)
            
            # Position Card Xform
            UsdGeom.Xformable(card_xform).AddTranslateOp().Set(Gf.Vec3d(pos[0], pos[1], pos[2]))
            
            # --- Anchor Pin Sphere ---
            pin_sphere = UsdGeom.Sphere.Define(stage, f"{card_root}/Pin")
            pin_sphere.CreateRadiusAttr(0.018)
            UsdGeom.Xformable(pin_sphere).AddTranslateOp().Set(Gf.Vec3d(target[0], target[1], target[2]))
            UsdShade.MaterialBindingAPI(pin_sphere).Bind(pin_mat)
            
            # --- Pointer Line Cylinder ---
            line_start = Gf.Vec3d(pos[0], pos[1] - card_height/2, pos[2])
            line_end = Gf.Vec3d(target[0], target[1], target[2])
            diff = line_end - line_start
            length = diff.GetLength()
            mid = (line_start + line_end) / 2.0
            rot = Gf.Rotation(Gf.Vec3d(0, 1, 0), diff.GetNormalized())
            
            cyl = UsdGeom.Cylinder.Define(stage, f"{card_root}/PointerLine")
            cyl.CreateAxisAttr('Y')
            cyl.CreateHeightAttr(length)
            cyl.CreateRadiusAttr(0.003)
            cyl_xf = UsdGeom.Xformable(cyl)
            cyl_xf.AddTranslateOp().Set(mid)
            cyl_xf.AddOrientOp().Set(Gf.Quatf(rot.GetQuat()))
            UsdShade.MaterialBindingAPI(cyl).Bind(pin_mat)
            
        # Asegurar rutas de texturas estrictamente relativas también para el modelo enriquecido
        for prim in stage.Traverse():
            if prim.IsA(UsdShade.Shader):
                shader = UsdShade.Shader(prim)
                inp = shader.GetInput('file')
                if inp:
                    val = inp.Get()
                    if val and hasattr(val, 'path'):
                        base_name = os.path.basename(val.path)
                        inp.Set(Sdf.AssetPath(base_name))
        stage.GetRootLayer().Save()
        del stage
        
        # 7. Empaquetar modelo enriquecido: public/models/<id>_ar.usdz
        writer_ar = AlignedUSDZWriter(out_ar_usdz)
        with open(usdc_path, 'rb') as f:
            writer_ar.add_file(usdc_name, f.read())
        for fname in sorted(os.listdir(tmpdir)):
            if fname != usdc_name and not fname.endswith('.usdz'):
                fpath = os.path.join(tmpdir, fname)
                with open(fpath, 'rb') as f:
                    writer_ar.add_file(fname, f.read())
        writer_ar.close()
        ar_sz = os.path.getsize(out_ar_usdz) / (1024 * 1024)
        print(f"[EXITO ENRIQUECIDO AR] {moto_id}_ar.usdz: {ar_sz:.2f} MB")
        
        # 8. Generar modelo Android GLB con anotaciones y SIN DECIMATION en Blender
        print(f"Exportando GLB AR Android (sin decimate) para {moto_id}...")
        blender_cards_list = []
        for i, c in enumerate(moto_info['cards']):
            tex_path = os.path.join(tmpdir, f"card_{i}.png")
            blender_cards_list.append({
                'category': c['category'],
                'pos': c['pos_blender'],
                'target': c['target_blender'],
                'side': c['side'],
                'img_path': tex_path.replace('\\', '/')
            })
            
        blender_cfg = {
            'glb_in': os.path.abspath(moto_info['clean_glb']),
            'out_glb': out_ar_glb,
            'out_usdz': os.path.abspath(f"temp_test/{moto_id}_discard.usdz"),
            'accent_hex': moto_info['accent'],
            'backplate_path': backplate_path.replace('\\', '/'),
            'cards_data': blender_cards_list
        }
        cfg_path = os.path.join(tmpdir, 'blender_cfg.json')
        with open(cfg_path, 'w', encoding='utf-8') as f_cfg:
            json.dump(blender_cfg, f_cfg, indent=2)
            
        worker_script = os.path.abspath('scripts/blender_infographics_worker.py')
        cmd = [BLENDER_EXE, '--background', '--python', worker_script, '--', cfg_path]
        subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if os.path.exists(out_ar_glb):
            glb_sz = os.path.getsize(out_ar_glb) / (1024 * 1024)
            print(f"[EXITO ANDROID GLB] {moto_id}_ar.glb: {glb_sz:.2f} MB")
            
        return True
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def main():
    print("=================================================================")
    print("PIPELINE MAESTRO USDZ: PROCESANDO MODELOS DESCARGADOS POR EL USUARIO")
    print("=================================================================")
    
    success = 0
    for moto_id, info in MOTOS_CONFIG.items():
        if process_single_moto(moto_id, info):
            success += 1
            
    print(f"\n=================================================================")
    print(f"PROCESAMIENTO COMPLETADO: {success}/{len(MOTOS_CONFIG)} MODELOS USDZ/GLB ACTUALIZADOS")
    print("=================================================================")

if __name__ == '__main__':
    main()
