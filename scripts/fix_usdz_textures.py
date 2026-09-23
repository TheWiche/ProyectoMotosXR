#!/usr/bin/env python3
"""
fix_usdz_textures.py
Corrige las rutas de texturas dentro de los archivos USDZ para que sean relativas ('./extracted_image_*.jpg/png')
en lugar de rutas absolutas de Windows ('C:/Users/.../AppData/Local/Temp/...').
Esto permite que Apple ARKit Quick Look en iPhone resuelva y renderice las texturas 3D en alta definición.
"""

import os
import glob
import tempfile
import zipfile
import struct
import binascii
from pxr import Sdf, Usd, UsdUtils

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


def fix_usdz_textures(usdz_path):
    print(f"\nCorrigiendo texturas en: {os.path.basename(usdz_path)}...")
    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(usdz_path, 'r') as z_in:
            z_in.extractall(tmpdir)
            
        usdc_files = [f for f in os.listdir(tmpdir) if f.endswith('.usdc')]
        if not usdc_files:
            print("  [ERROR] No se encontro archivo USDC")
            return False
            
        usdc_name = usdc_files[0]
        usdc_path = os.path.join(tmpdir, usdc_name)
        
        # Modificar rutas de texturas a relativas
        layer = Sdf.Layer.FindOrOpen(usdc_path)
        if not layer:
            print("  [ERROR] No se pudo abrir la capa USDC")
            return False
            
        def make_relative(path):
            base = os.path.basename(path)
            new_path = f'./{base}'
            print(f"    Ruta corregida: {path} -> {new_path}")
            return new_path
            
        UsdUtils.ModifyAssetPaths(layer, make_relative)
        layer.Save()
        del layer
        
        # Empaquetar de nuevo con alineacion de 64 bytes
        temp_out = os.path.join(tmpdir, 'fixed_' + os.path.basename(usdz_path))
        writer = AlignedUSDZWriter(temp_out)
        
        with open(usdc_path, 'rb') as f:
            writer.add_file(usdc_name, f.read())
            
        for fname in sorted(os.listdir(tmpdir)):
            if fname != usdc_name and not fname.startswith('fixed_'):
                fpath = os.path.join(tmpdir, fname)
                with open(fpath, 'rb') as f:
                    writer.add_file(fname, f.read())
                    
        writer.close()
        
        # Validar resolucion de texturas
        val_stage = Usd.Stage.Open(temp_out)
        resolved_count = 0
        for p in val_stage.Traverse():
            for a in p.GetAttributes():
                if a.GetTypeName() == Sdf.ValueTypeNames.Asset:
                    val = a.Get()
                    if val and val.resolvedPath:
                        resolved_count += 1
                        print(f"    [OK] Resuelto: {val.path} -> {val.resolvedPath}")
                    else:
                        print(f"    [WARN] No resuelto: {val}")
        del val_stage
        
        # Reemplazar archivo original
        with open(temp_out, 'rb') as src, open(usdz_path, 'wb') as dst:
            dst.write(src.read())
            
        print(f"  [EXITO] {os.path.basename(usdz_path)} actualizado con {resolved_count} texturas resueltas!")
        return True
    finally:
        # Limpieza silenciosa de tmpdir
        try:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass


def main():
    target_dir = os.path.join('public', 'models')
    usdz_files = sorted(glob.glob(os.path.join(target_dir, '*.usdz')))
    for f in usdz_files:
        fix_usdz_textures(f)
    print("\nTODOS LOS MODELOS USDZ FUERON ACTUALIZADOS CON TEXTURAS RELATIVAS.")

if __name__ == '__main__':
    main()

