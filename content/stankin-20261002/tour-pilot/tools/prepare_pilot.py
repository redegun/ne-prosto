import bpy, pathlib, json, collections
from mathutils import Vector

root=pathlib.Path(__file__).parent
collection=bpy.data.collections['vagon3']
objects=[o for o in collection.all_objects if o.type in {'MESH','CURVE','SURFACE','FONT'} and not o.hide_render]
keep=set(objects)
for o in list(objects):
    p=o.parent
    while p:
        keep.add(p);p=p.parent
bpy.data.batch_remove(ids=[o for o in bpy.data.objects if o not in keep])
print('REMOVED_OTHER_CARS',flush=True)
bpy.context.view_layer.update()
missing=[]
materials={s.material for o in objects for s in o.material_slots if s.material}
for mat in materials:
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                im=node.image
                if im.source=='FILE' and not(im.packed_file or im.packed_files) and not pathlib.Path(bpy.path.abspath(im.filepath,library=im.library)).is_file():
                    missing.append({'material':mat.name,'image':im.name,'objects':[o.name for o in objects if mat in [s.material for s in o.material_slots]]})
report={'collection':'vagon3','geometry_objects':len(objects),'types':dict(collections.Counter(o.type for o in objects)),'materials':len(materials),'missing_textures':missing}
(root/'pilot-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

# Technical geometry proof; final branding is intentionally blocked by missing source images.
# Solid material colors preserve the source palette where it is available.
for mat in materials:
    color=list(mat.diffuse_color)
    if mat.use_nodes:
        p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if p:color=list(p.inputs['Base Color'].default_value)
    name=mat.name.lower()
    if 'glass' in name:color=[0.20,0.28,0.32,0.34]
    elif any(k in name for k in ['silver','steel','holdbar']):color=[0.56,0.60,0.63,1]
    elif 'seatcushion' in name or 'fabric' in name:color=[0.045,0.14,0.22,1]
    elif any(x['material']==mat.name for x in missing):color=[0.72,0.74,0.77,1]
    mat.use_nodes=True
    mat.node_tree.nodes.clear()
    output=mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    shader=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value=color
    shader.inputs['Roughness'].default_value=0.65
    if any(k in name for k in ['silver','steel','holdbar']):shader.inputs['Metallic'].default_value=0.65
    if 'glass' in name:
        shader.inputs['Alpha'].default_value=0.34
        mat.surface_render_method='DITHERED'
    mat.node_tree.links.new(shader.outputs['BSDF'],output.inputs['Surface'])
    mat.diffuse_color=color
for o in bpy.context.view_layer.objects:
    o.hide_set(False);o.hide_viewport=False;o.select_set(o in objects)
    if o.type=='MESH':
        for mod in list(o.modifiers):
            if mod.type=='SUBSURF':mod.levels=min(mod.levels,1);mod.render_levels=min(mod.render_levels,1)
bpy.ops.export_scene.gltf(filepath=str(root/'pilot-geometry.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=False)
print('PILOT_EXPORTED',len(objects),'objects',len(missing),'missing texture material links')
