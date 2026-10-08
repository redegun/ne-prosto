import bpy,json,pathlib
root=pathlib.Path(__file__).parent
result={}
for i in range(1,9):
    mats={slot.material for ob in bpy.data.collections['vagon'+str(i)].all_objects for slot in ob.material_slots if slot.material}
    rows=[]
    for mat in mats:
        if not mat.use_nodes: continue
        for node in mat.node_tree.nodes:
            if node.type!='BSDF_PRINCIPLED':continue
            color=list(node.inputs['Emission Color'].default_value)
            strength=node.inputs['Emission Strength'].default_value
            if strength>0 and sum(color[:3])>0.05:
                rows.append({'name':mat.name,'color':color,'strength':strength})
    result[str(i)]=rows
(root/'lights-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('LIGHT_AUDIT',json.dumps(result,ensure_ascii=False))
