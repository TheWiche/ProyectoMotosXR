import bpy
import os
import sys
import json
import math
import mathutils

def hex_to_rgba(hex_str):
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)) + (1.0,)

def main():
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
    backplate_path = cfg['backplate_path']
    accent_rgba = hex_to_rgba(accent_hex)
    
    print(f"Iniciando construccion Blender 3D HUD para {glb_in}...")
    
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
    pin_bsdf.inputs['Emission Strength'].default_value = 2.5
    
    # Material for Backplate (reusable across all cards)
    back_mat = bpy.data.materials.new(name='Mat_Backplate')
    back_mat.use_nodes = True
    back_nodes = back_mat.node_tree.nodes
    back_links = back_mat.node_tree.links
    back_bsdf = back_nodes.get('Principled BSDF')
    
    back_tex = back_nodes.new('ShaderNodeTexImage')
    back_tex.image = bpy.data.images.load(backplate_path)
    back_links.new(back_tex.outputs['Color'], back_bsdf.inputs['Base Color'])
    back_links.new(back_tex.outputs['Color'], back_bsdf.inputs['Emission Color'])
    back_bsdf.inputs['Emission Strength'].default_value = 0.8
    back_links.new(back_tex.outputs['Alpha'], back_bsdf.inputs['Alpha'])

    # 5. Build Cards, Lines and Pins
    card_width, card_height = 0.38, 0.20

    for idx, c in enumerate(cards_data):
        card_name = f"Card_{idx}_{c['category']}"
        pos = c['pos']
        target = c['target']
        img_path = c['img_path']
        side = c.get('side', 'right')
        
        # --- FRONT FACE PLANE ---
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
        front_obj = bpy.context.active_object
        front_obj.scale = (card_width, card_height, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        
        if side == 'right':
            front_obj.rotation_euler = (math.radians(90), 0, 0) # Normal -> -Y (outward)
        else:
            front_obj.rotation_euler = (math.radians(90), 0, math.radians(180)) # Normal -> +Y (outward)
        bpy.ops.object.transform_apply(rotation=True)
        
        # Front Material (Technical Specs)
        front_mat = bpy.data.materials.new(name=f"Mat_{card_name}_Front")
        front_mat.use_nodes = True
        fnodes = front_mat.node_tree.nodes
        flinks = front_mat.node_tree.links
        fbsdf = fnodes.get('Principled BSDF')
        
        ftex = fnodes.new('ShaderNodeTexImage')
        ftex.image = bpy.data.images.load(img_path)
        flinks.new(ftex.outputs['Color'], fbsdf.inputs['Base Color'])
        flinks.new(ftex.outputs['Color'], fbsdf.inputs['Emission Color'])
        fbsdf.inputs['Emission Strength'].default_value = 1.0
        flinks.new(ftex.outputs['Alpha'], fbsdf.inputs['Alpha'])
        
        front_obj.data.materials.append(front_mat)
        
        # --- BACK FACE PLANE (Dark branded backplate) ---
        bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
        back_obj = bpy.context.active_object
        back_obj.scale = (card_width, card_height, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        
        if side == 'right':
            back_obj.rotation_euler = (math.radians(90), 0, math.radians(180)) # Normal -> +Y (inward)
            back_obj.location = (0, 0.003, 0)
        else:
            back_obj.rotation_euler = (math.radians(90), 0, 0) # Normal -> -Y (inward)
            back_obj.location = (0, -0.003, 0)
        bpy.ops.object.transform_apply(rotation=True, location=True)
        
        back_obj.data.materials.append(back_mat)
        
        # --- JOIN FRONT AND BACK INTO SINGLE CARD OBJECT ---
        front_obj.select_set(True)
        back_obj.select_set(True)
        bpy.context.view_layer.objects.active = front_obj
        bpy.ops.object.join()
        
        card_obj = bpy.context.active_object
        card_obj.name = card_name
        card_obj.location = pos
        
        # --- POINTER PIN SPHERE AT MECHANICAL TARGET ---
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018, location=target)
        pin_obj = bpy.context.active_object
        pin_obj.name = f"{card_name}_Pin"
        pin_obj.data.materials.append(pin_mat)
        
        # --- POINTER LINE (CYLINDER) FROM CARD BOTTOM TO PIN ---
        line_start = (pos[0], pos[1], pos[2] - card_height/2)
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
