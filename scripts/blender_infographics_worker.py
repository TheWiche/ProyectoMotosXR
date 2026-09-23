import bpy
import os
import sys
import json
import mathutils

def hex_to_rgba(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)) + (1.0,)

def main():
    # Read arguments after '--'
    args = sys.argv
    if '--' not in args:
        print("[ERROR] No se encontraron argumentos despues de '--'")
        sys.exit(1)
        
    config_path = args[args.index('--') + 1]
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
        
    glb_in = cfg['glb_in']
    out_glb = cfg['out_glb']
    out_usdz = cfg['out_usdz']
    accent_hex = cfg['accent_hex']
    cards_data = cfg['cards_data']
    accent_rgba = hex_to_rgba(accent_hex)
    
    print(f"Iniciando construccion Blender para {glb_in}...")
    
    # 1. Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # 2. Import clean GLB
    bpy.ops.import_scene.gltf(filepath=glb_in)
    
    # 3. Decimate body mesh to ensure USDZ < 30 MB for Safari
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and len(obj.data.vertices) > 5000:
            mod = obj.modifiers.new(name='Decimate_Body', type='DECIMATE')
            mod.ratio = 0.45
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier='Decimate_Body')
            print(f"Decimated {obj.name} to {len(obj.data.vertices)} vertices")
            
    # 4. Create Emissive Material for pointer lines and pins
    pin_mat = bpy.data.materials.new(name='Infographic_Neon')
    pin_mat.use_nodes = True
    pin_bsdf = pin_mat.node_tree.nodes.get('Principled BSDF')
    pin_bsdf.inputs['Base Color'].default_value = accent_rgba
    pin_bsdf.inputs['Emission Color'].default_value = accent_rgba
    pin_bsdf.inputs['Emission Strength'].default_value = 2.0
    
    # 5. Build Cards, Lines and Pins
    for idx, c in enumerate(cards_data):
        card_name = f"Card_{idx}_{c['category']}"
        pos = c['pos']
        target = c['target']
        img_path = c['img_path']
        
        # --- Thin Box for Double-Sided Card (readable from both sides) ---
        width, height, thickness = 0.38, 0.21, 0.004
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
        card_obj = bpy.context.active_object
        card_obj.name = card_name
        card_obj.scale = (width, thickness, height)
        bpy.ops.object.transform_apply(scale=True)
        
        # UV Mapping: map front (+Y) and back (-Y) faces
        mesh = card_obj.data
        uv_layer = mesh.uv_layers.active or mesh.uv_layers.new(name='UVMap')
        for poly in mesh.polygons:
            normal = poly.normal
            if abs(normal.y) > 0.8:
                for loop_idx in poly.loop_indices:
                    v_idx = mesh.loops[loop_idx].vertex_index
                    v = mesh.vertices[v_idx].co
                    u = (v.x / width) + 0.5
                    v_uv = (v.z / height) + 0.5
                    if normal.y < 0:
                        u = 1.0 - u  # Mirror back face so text reads left to right
                    uv_layer.data[loop_idx].uv = (u, v_uv)
                    
        # Card Emissive Material
        mat = bpy.data.materials.new(name=f"Mat_{card_name}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get('Principled BSDF')
        
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.image = bpy.data.images.load(img_path)
        
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.0
        links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])
        
        card_obj.data.materials.append(mat)
        
        # --- Pointer Pin Sphere at Mechanical Target ---
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.016, location=target)
        pin_obj = bpy.context.active_object
        pin_obj.name = f"{card_name}_Pin"
        pin_obj.data.materials.append(pin_mat)
        
        # --- Pointer Line (Cylinder) from Card Bottom to Pin ---
        line_start = (pos[0], pos[1], pos[2] - height/2)
        v_start = mathutils.Vector(line_start)
        v_end = mathutils.Vector(target)
        direction = v_end - v_start
        length = direction.length
        center = (v_start + v_end) / 2.0
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.003, depth=length, location=center)
        line_obj = bpy.context.active_object
        line_obj.name = f"{card_name}_Line"
        line_obj.rotation_mode = 'QUATERNION'
        line_obj.rotation_quaternion = mathutils.Vector((0, 0, 1)).rotation_difference(direction)
        line_obj.data.materials.append(pin_mat)
        
    # 6. Regla de Oro 1: Cero texturas WebP en Apple Quick Look (convertir todo a PNG/JPEG)
    for img in list(bpy.data.images):
        if img.file_format not in ('PNG', 'JPEG') or img.name.endswith('.webp') or (img.filepath and '.webp' in img.filepath):
            clean_name = os.path.splitext(img.name)[0]
            png_path = os.path.abspath(f"temp_cards/{clean_name}.png")
            os.makedirs(os.path.dirname(png_path), exist_ok=True)
            img.file_format = 'PNG'
            img.filepath_raw = png_path
            try:
                img.save()
                new_img = bpy.data.images.load(png_path)
                img.user_remap(new_img)
                bpy.data.images.remove(img)
            except Exception as e:
                print(f"Warning converting image {img.name}: {e}")
                
    # 7. Export GLB with Draco Compression for Android Scene Viewer
    os.makedirs(os.path.dirname(out_glb), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        export_draco_mesh_compression_enable=True,
        export_materials='EXPORT',
        export_image_format='AUTO'
    )
    print(f"GLB Exported: {out_glb} (Size: {os.path.getsize(out_glb)/1024/1024:.2f} MB)")
    
    # 8. Export USDZ for Apple ARKit Quick Look (Y-Up, < 30 MB)
    os.makedirs(os.path.dirname(out_usdz), exist_ok=True)
    bpy.ops.wm.usd_export(
        filepath=out_usdz,
        convert_orientation=True,
        export_global_up_selection='Y',
        export_global_forward_selection='NEGATIVE_Z',
        generate_preview_surface=True,
        export_materials=True,
        relative_paths=True
    )
    print(f"USDZ Exported: {out_usdz} (Size: {os.path.getsize(out_usdz)/1024/1024:.2f} MB)")
    print("EXITO_BLENDER")

if __name__ == '__main__':
    main()
