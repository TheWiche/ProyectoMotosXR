
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
    print(f"\n--- Generando Modelos Limpios para {moto_id} ---")
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
    print(f"\n--- Generando Modelos AR Holográficos para {moto_id} ---")
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
