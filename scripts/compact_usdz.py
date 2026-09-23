#!/usr/bin/env python3
"""
compact_usdz.py
Optimiza los archivos USDZ para que pesen menos de 90 MB (cumpliendo con el limite estricto de Vercel de 100 MB
y optimizando el tiempo de descarga y uso de VRAM en Apple ARKit Quick Look para iOS).

1. Remueve la primvar redundante `primvars:tangents` del mesh (ahorro de 20-30 MB por modelo; Quick Look genera tangentes al vuelo).
2. Optimiza las texturas de 8K/4K a resolución 2K (2048x2048), formato estándar y recomendado por Apple para AR móvil.
3. Empaqueta el archivo USDZ con alineación de 64 bytes según la especificación oficial de Pixar/Apple USDZ.
"""

import os
import glob
import tempfile
import zipfile
import struct
import binascii
from PIL import Image
from pxr import Usd, UsdGeom, Sdf, UsdUtils

class AlignedUSDZWriter:
    """Escribe archivos .usdz con compresion STORED y alineacion exacta de 64 bytes."""
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
        
        assert self.f.tell() % 64 == 0, f"Offset {self.f.tell()} no esta alineado a 64 bytes"
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


def optimize_usdz(usdz_path):
    orig_size_mb = os.path.getsize(usdz_path) / (1024 * 1024)
    print(f"\nProcesando: {os.path.basename(usdz_path)} ({orig_size_mb:.2f} MB)...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Extraer contenido
        with zipfile.ZipFile(usdz_path, 'r') as z_in:
            z_in.extractall(tmpdir)
            
        usdc_files = [f for f in os.listdir(tmpdir) if f.endswith('.usdc')]
        if not usdc_files:
            print(f"  [!] No se encontro archivo .usdc en {usdz_path}")
            return False
            
        usdc_name = usdc_files[0]
        usdc_path = os.path.join(tmpdir, usdc_name)
        
        # 2. Abrir Stage y remover tangentes innecesarias
        stage = Usd.Stage.Open(usdc_path)
        modified = False
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                if prim.HasProperty('primvars:tangents'):
                    prim.RemoveProperty('primvars:tangents')
                    modified = True
                    print(f"  -> Removida primvar 'primvars:tangents' de {prim.GetPath()}")
                    
        compact_usdc_path = os.path.join(tmpdir, 'compacted_' + usdc_name)
        stage.Export(compact_usdc_path)
        del stage
        os.replace(compact_usdc_path, usdc_path)

        # 2b. Corregir rutas de texturas para que sean estrictamente relativas (./archivo.jpg)
        layer = Sdf.Layer.FindOrOpen(usdc_path)
        if layer:
            UsdUtils.ModifyAssetPaths(layer, lambda p: './' + os.path.basename(p))
            layer.Save()
            del layer

        
        # 3. Optimizar texturas (> 2048px se redimensionan a max 2048)
        for fname in os.listdir(tmpdir):
            fpath = os.path.join(tmpdir, fname)
            if fname.lower().endswith(('.jpg', '.jpeg')):
                try:
                    img = Image.open(fpath)
                    orig_res = img.size
                    if max(orig_res) > 2048:
                        img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                        img.save(fpath, format='JPEG', quality=85, optimize=True)
                        print(f"  -> Textura {fname} optimizada: {orig_res} -> {img.size}")
                except Exception as e:
                    print(f"  [!] Error optimizando {fname}: {e}")
            elif fname.lower().endswith('.png'):
                try:
                    img = Image.open(fpath)
                    orig_res = img.size
                    if max(orig_res) > 2048:
                        img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                        img.save(fpath, format='PNG', optimize=True)
                        print(f"  -> Textura {fname} optimizada: {orig_res} -> {img.size}")
                except Exception as e:
                    print(f"  [!] Error optimizando {fname}: {e}")
                    
        # 4. Empaquetar USDZ con alineacion de 64 bytes
        temp_out_usdz = os.path.join(tmpdir, 'output.usdz')
        writer = AlignedUSDZWriter(temp_out_usdz)
        
        # El archivo .usdc DEBE ser el primero
        with open(usdc_path, 'rb') as f:
            writer.add_file(usdc_name, f.read())
            
        # Agregar los demas archivos (texturas)
        for fname in sorted(os.listdir(tmpdir)):
            if fname != usdc_name and not fname.endswith('.usdz'):
                fpath = os.path.join(tmpdir, fname)
                with open(fpath, 'rb') as f:
                    writer.add_file(fname, f.read())
                    
        writer.close()
        
        # 5. Validar con Pixar USD Stage
        val_stage = Usd.Stage.Open(temp_out_usdz)
        if not val_stage:
            print(f"  [ERROR] Fallo la validacion de USD en {temp_out_usdz}")
            return False
            
        new_size_mb = os.path.getsize(temp_out_usdz) / (1024 * 1024)
        print(f"  [OK] Exito: {orig_size_mb:.2f} MB -> {new_size_mb:.2f} MB (Ahorro: {orig_size_mb - new_size_mb:.2f} MB, {((orig_size_mb-new_size_mb)/orig_size_mb)*100:.1f}%)")
        
        # Reemplazar archivo destino
        os.replace(temp_out_usdz, usdz_path)
        return True


def main():
    target_dir = os.path.join('public', 'models')
    usdz_files = sorted(glob.glob(os.path.join(target_dir, '*.usdz')))
    
    if not usdz_files:
        print(f"No se encontraron archivos .usdz en {target_dir}")
        return
        
    print(f"Iniciando optimizacion de {len(usdz_files)} archivos USDZ...")
    for f in usdz_files:
        optimize_usdz(f)
        
    print("\n--- RESUMEN FINAL ---")
    total_size = 0
    for f in sorted(glob.glob(os.path.join(target_dir, '*.usdz'))):
        sz = os.path.getsize(f) / (1024 * 1024)
        total_size += sz
        status = "OK (< 100 MB)" if sz < 100 else "EXCEDE 100 MB"
        print(f"  {os.path.basename(f)}: {sz:.2f} MB [{status}]")
    print(f"Tamano total USDZ: {total_size:.2f} MB")

if __name__ == '__main__':
    main()

