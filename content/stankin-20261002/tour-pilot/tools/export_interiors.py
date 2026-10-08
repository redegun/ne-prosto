"""Export one original carriage with the supplied interior atlas. Never saves the .blend."""
import bpy, pathlib, json, sys
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:]
car=int(args[0])
root=pathlib.Path(args[1]).resolve() if len(args)>1 else pathlib.Path(__file__).parent
names={1:'Вагон_1_внутри.jpg',2:'Вагон_2_внутри.jpg',3:'Вагон_3_внутри.jpg',4:'Вагон_4_внутри.jpg',5:'Внутри_5_2.jpg',6:'Вагон_6_внутри_Света.jpg',7:'Вагон_7_внутри.jpg',8:'Внутри_вагон_8.jpg'}
collection=bpy.data.collections['vagon'+str(car)]
objects=[];excluded=[]
for o in collection.all_objects:
    if o.type!='MESH' or o.hide_render:continue
    points=[o.matrix_world@Vector(p) for p in o.bound_box]
    if not len(o.data.polygons) or min(p.z for p in points)>10:
        excluded.append(o.name);continue
    objects.append(o)
keep=set(objects)
for o in objects:
    p=o.parent
    while p:keep.add(p);p=p.parent
bpy.data.batch_remove(ids=[o for o in bpy.data.objects if o not in keep])
bpy.context.view_layer.update()
materials={s.material for o in objects for s in o.material_slots if s.material}
branded=[];unused=[]
for mat in materials:
    color=list(mat.diffuse_color)
    active_missing=[]
    if mat.use_nodes:
        p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if p:color=list(p.inputs['Base Color'].default_value)
        for n in mat.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image:
                im=n.image
                if not(im.packed_file or im.packed_files) and not pathlib.Path(bpy.path.abspath(im.filepath)).is_file():
                    if any(s.is_linked for s in n.outputs):active_missing.append(im.name)
                    else:unused.append({'material':mat.name,'image':im.name})
    name=mat.name.lower()
    if 'glass' in name:color=[.20,.28,.32,.34]
    elif any(k in name for k in ['silver','steel','holdbar']):color=[.56,.60,.63,1]
    elif 'seatcushion' in name or 'fabric' in name:color=[.045,.14,.22,1]
    mat.use_nodes=True;mat.node_tree.nodes.clear()
    output=mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    shader=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value=color
    shader.inputs['Roughness'].default_value=.65
    if any(k in name for k in ['silver','steel','holdbar']):shader.inputs['Metallic'].default_value=.65
    if 'glass' in name:
        shader.inputs['Alpha'].default_value=.34;mat.surface_render_method='DITHERED'
    if active_missing:
        branded.append({'material':mat.name,'replaced_images':active_missing,'texture':names[car]})
        im=bpy.data.images.load(str(root/'textures-browser'/names[car]),check_existing=False)
        im.colorspace_settings.name='sRGB'
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
        shader.inputs['Base Color'].default_value=[1,1,1,1]
        shader.inputs['Metallic'].default_value=0;shader.inputs['Roughness'].default_value=.58
        mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    mat.node_tree.links.new(shader.outputs['BSDF'],output.inputs['Surface']);mat.diffuse_color=color
assert len(branded)==1,branded
for o in bpy.context.view_layer.objects:
    o.hide_set(False);o.hide_viewport=False;o.select_set(o in objects)
    if o.type=='MESH':
        for mod in o.modifiers:
            if mod.type=='SUBSURF':mod.levels=min(mod.levels,1);mod.render_levels=min(mod.render_levels,1)
out=root/'web'/'models';out.mkdir(exist_ok=True)
target=out/f'car-{car}.glb'
bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=16,export_draco_normal_quantization=12,export_draco_texcoord_quantization=14)
report={'car':car,'objects':len(objects),'excluded_helpers':excluded,'branding':branded,'disconnected_images_not_required':unused,'bytes':target.stat().st_size}
(root/f'car-{car}-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('CAR_EXPORTED',car,target.stat().st_size)
