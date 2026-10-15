import bpy,json,pathlib,sys
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
root=pathlib.Path(args[0]) if args else pathlib.Path(__file__).parent
root.mkdir(parents=True,exist_ok=True)
report=[];deps=bpy.context.evaluated_depsgraph_get()
for car in range(1,9):
    collection=bpy.data.collections['vagon'+str(car)];rows=[]
    for ob in collection.all_objects:
        if ob.type!='MESH' or ob.hide_render:continue
        ev=ob.evaluated_get(deps);mesh=ev.to_mesh();uv=mesh.uv_layers.active
        if not uv:ev.to_mesh_clear();continue
        for mi,mat in enumerate(mesh.materials):
            if not mat or not mat.name.lower().startswith('vagon'):continue
            polys=[p for p in mesh.polygons if p.material_index==mi]
            if not polys:continue
            points=[ev.matrix_world@mesh.vertices[v].co for p in polys for v in p.vertices]
            yy=[(1-uv.data[i].uv.y)%1 for p in polys for i in p.loop_indices]
            xx=[uv.data[i].uv.x%1 for p in polys for i in p.loop_indices]
            mixed=sum(min((1-uv.data[i].uv.y)%1 for i in p.loop_indices)<.42<max((1-uv.data[i].uv.y)%1 for i in p.loop_indices) for p in polys)
            rows.append({'object':ob.name,'material':mat.name,'faces':len(polys),'uv_x':[min(xx),max(xx)],'uv_y_top':[min(yy),max(yy)],'crosses_042':mixed,'bounds':[[min(v[k] for v in points),max(v[k] for v in points)] for k in range(3)]})
        ev.to_mesh_clear()
    report.append({'car':car,'surfaces':rows})
(root/'exterior-uv-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for row in report:
    print('UV',row['car'],[(s['object'],[round(v,4) for v in s['uv_y_top']],s['crosses_042']) for s in row['surfaces']],flush=True)
