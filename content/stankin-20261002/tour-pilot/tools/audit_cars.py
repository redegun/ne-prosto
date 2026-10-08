import bpy, json, pathlib
from mathutils import Vector
root=pathlib.Path(__file__).parent
result=[]
for i in range(1,9):
    coll=bpy.data.collections['vagon'+str(i)]
    objects=[o for o in coll.all_objects if o.type=='MESH' and not o.hide_render]
    obs=[]
    mats=set()
    for o in objects:
        points=[o.matrix_world@Vector(p) for p in o.bound_box]
        obs.append({'name':o.name,'min':[min(p[k] for p in points) for k in range(3)],'max':[max(p[k] for p in points) for k in range(3)],'polys':len(o.data.polygons)})
        mats.update(s.material for s in o.material_slots if s.material)
    active=[]
    for m in mats:
        if not m.use_nodes:continue
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image and any(s.is_linked for s in n.outputs):
                active.append({'material':m.name,'image':n.image.name,'packed':bool(n.image.packed_file or n.image.packed_files),'links':[[l.from_socket.name,l.to_node.name,l.to_socket.name] for l in m.node_tree.links if l.from_node==n]})
    result.append({'car':i,'objects':obs,'active_images':active})
(root/'cars-audit.json').write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
print('AUDIT_COMPLETE')
