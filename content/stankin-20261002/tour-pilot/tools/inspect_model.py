import bpy, json, pathlib, collections, math
from mathutils import Vector

root = pathlib.Path(__file__).parent
def bounds(objects):
    points = [o.matrix_world @ Vector(v) for o in objects if o.type == 'MESH' for v in o.bound_box]
    return [[round(min(v[i] for v in points),3) for i in range(3)], [round(max(v[i] for v in points),3) for i in range(3)]] if points else None

images = []
for im in bpy.data.images:
    packed = bool(im.packed_file or im.packed_files)
    path = bpy.path.abspath(im.filepath, library=im.library)
    images.append(dict(name=im.name, source=im.source, packed=packed, path=path, exists=pathlib.Path(path).is_file() if path else False, size=list(im.size), users=im.users))

report = dict(
    version=bpy.app.version_string,
    objects=len(bpy.data.objects), meshes=len(bpy.data.meshes), materials=len(bpy.data.materials),
    unique_vertices=sum(len(m.vertices) for m in bpy.data.meshes),
    unique_polygons=sum(len(m.polygons) for m in bpy.data.meshes),
    images=images,
    libraries=[dict(name=l.name, path=l.filepath, missing=l.is_missing) for l in bpy.data.libraries],
    collections=[dict(name=c.name, objects=len(c.objects), recursive_objects=len(c.all_objects), children=[x.name for x in c.children], hidden=c.hide_render, bounds=bounds(c.objects)) for c in bpy.data.collections],
    scenes=[dict(name=s.name, objects=len(s.objects), camera=s.camera.name if s.camera else None, units=s.unit_settings.scale_length) for s in bpy.data.scenes],
    cameras=[dict(name=o.name, position=list(o.matrix_world.translation), rotation=list(o.rotation_euler), lens=o.data.lens) for o in bpy.data.objects if o.type=='CAMERA'],
    objects_list=[dict(name=o.name, type=o.type, data=o.data.name if o.data else None, hidden=o.hide_render, hide_viewport=o.hide_viewport, collections=[c.name for c in o.users_collection], position=[round(x,3) for x in o.matrix_world.translation], bounds=bounds([o]), materials=[m.name for m in o.data.materials if m] if o.type=='MESH' else []) for o in bpy.data.objects]
)
(root/'inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
missing=[im for im in images if im['source']=='FILE' and not im['packed'] and not im['exists']]
summary={k:v for k,v in report.items() if k not in ['images','objects_list','cameras']}
summary['missing_images']=missing
summary['image_counts']={'total':len(images),'packed':sum(i['packed'] for i in images),'missing':len(missing)}
(root/'inspection-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print('INSPECTION_COMPLETE',len(missing),'missing images')
