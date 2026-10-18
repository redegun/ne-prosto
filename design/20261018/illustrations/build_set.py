"""NE PROSTO: seven editable service still lifes. Blender 5 / Cycles.
Run: blender -b --factory-startup -P build_set.py -- --out <dir> [--only web] [--draft]
Canonical source lives on VPS; local directory is temporary GPU rendering space.
"""
import bpy, math, sys, argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--only');p.add_argument('--draft',action='store_true')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=Path(args.out);OUT.mkdir(parents=True,exist_ok=True)
def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def mat(name,h,metal=0,rough=.35):
    m=bpy.data.materials.new(name);m.use_nodes=True
    rgb=[linear(int(h[i:i+2],16)/255) for i in (0,2,4)]
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    return m
M={}
def finish(o,name,material,bevel=0):
    o.name=name;o.data.materials.append(M[material])
    if bevel:
        b=o.modifiers.new('Soft machined edges','BEVEL');b.width=bevel;b.segments=5
        n=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');n.keep_sharp=True
    if o.type=='MESH':
        for face in o.data.polygons:face.use_smooth=True
    return o
def box(name,loc,dims,m='ivory',bevel=.08,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    finish(o,name,m,bevel)
    if rot:o.rotation_euler=rot
    return o
def ball(name,loc,r,m='lime'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=r,location=loc)
    return finish(bpy.context.object,name,m)
def rod(name,a,b,r,m='silver',r2=None):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=r,radius2=r if r2 is None else r2,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return finish(o,name,m,.025)
def ring(name,loc,r,t,m='silver',rot=(math.pi/2,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=96,minor_segments=20,location=loc,rotation=rot)
    return finish(bpy.context.object,name,m)
def poly(name,coords,depth,loc,m='lime',bevel=.04):
    n=len(coords);verts=[(x,y,z) for y in (-depth/2,depth/2) for x,z in coords]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.location=loc
    return finish(o,name,m,bevel)
def path(name,coords,r,m):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=20;c.bevel_depth=r;c.bevel_resolution=5
    s=c.splines.new('POLY');s.points.add(len(coords)-1)
    for p,co in zip(s.points,coords):p.co=(*co,1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(M[m]);return o
def text(name,body,loc,size,m='ink',rotation=(math.pi/2,0,0)):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.extrude=.004;c.align_x='CENTER';c.align_y='CENTER'
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation;c.materials.append(M[m]);return o
def plate(name,loc,dims,m='ivory',angle=0):
    return box(name,loc,dims,m,.12,(0,0,angle))
def star(name,loc,r=1,m='lime'):
    pts=[]
    for i in range(48):
        a=i*math.tau/48;r0=r if i%6 in (1,2,3) else r*.45
        pts.append((math.cos(a)*r0,math.sin(a)*r0))
    return poly(name,pts,.28,loc,m,.055)
def scene_setup(slug):
    scene=bpy.data.scenes.new(slug);bpy.context.window.scene=scene
    scene.render.engine='CYCLES';scene.cycles.device='GPU';scene.cycles.samples=48 if args.draft else 160
    scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.025
    scene.render.resolution_x=900 if args.draft else 1440;scene.render.resolution_y=675 if args.draft else 1080;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=-.05
    world=bpy.data.worlds.new(slug+' studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.8,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35;scene.world=world
    box('Infinite warm paper',(0,0,-.17),(200,200,.2),'paper',0)
    def light(name,loc,power,size,color):
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
    light('Large softbox / left',(-3,-4,7),700,5.0,(1,.97,.91))
    light('White reflector / right',(5,-1,4),480,4,(.91,.95,1))
    light('Edge light',(1,4,6),850,3.5,(1,1,.94))
    d=bpy.data.cameras.new('Orthographic product camera');o=bpy.data.objects.new('Orthographic product camera',d);scene.collection.objects.link(o)
    o.location=(6,-10,7);target=Vector((0,0,1.25));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=6.5;scene.camera=o
    return scene
def web():
    plate('Browser / graphite chassis',(-.25,.25,1.55),(3.25,.28,2.25),'ink')
    plate('Browser / porcelain canvas',(-.25,.085,1.5),(2.94,.08,1.81),'ivory')
    for x in [-1.52,-1.35,-1.18]:ball('Browser control',(x,.07,2.53),.045,'lime')
    box('Editorial hero block',(-.82,.02,1.67),(1.42,.045,.8),'lime',.04)
    for i in range(3):box('Text lines',(.55,.018,1.94-i*.21),(.77,.04,.06),'ink',.022)
    for x in [-1.25,-.27,.71]:box('Layout modules',(x,.01,.98),(.77,.045,.28),'stone',.035)
    coords=[(-.43,.7),(-.4,-.5),(-.1,-.29),(.16,-.76),(.48,-.57),(.19,-.11),(.57,-.04)]
    poly('Sculpted cursor',coords,.23,(1.26,-.72,1.22),'lime',.055)
    box('Floating tab',(-1.30,-.6,.45),(1.26,.55,.16),'silver',.07)
    for i in range(3):ball('Tab details',(-1.66+i*.28,-.67,.55),.045,'ink')
def branding():
    plate('Identity card',(-.35,.18,1.25),(2.5,.23,2.18),'ink')
    star('Custom asterisk',(-.45,-.015,1.4),.78,'lime')
    text('Studio mark','N / P',(-.45,-.16,.51),.14,'ivory')
    for i,(x,y,m) in enumerate([(1.0,-.30,'stone'),(1.12,-.52,'ivory'),(1.24,-.74,'lime')]):
        box('Colour sample '+str(i),(x,y,.22+i*.07),(.9,1.45,.10),m,.035,(0,0,.15-i*.22))
    ring('Metallic brand seal',(-1.35,-.75,.23),.41,.09,'silver',(0,0,0))
def advertising():
    # A hollow acoustic cone, pointed diagonally toward the viewer.
    a=Vector((-.55,.05,1.30));b=Vector((.95,-.35,1.75));axis=(b-a).normalized()
    q=axis.to_track_quat('Z','Y');N=96;verts=[]
    for z,r in [(0,.30),(1.62,.83),(1.62,.70),(.14,.23)]:
        for i in range(N):verts.append(tuple(a+q@Vector((r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z))))
    faces=[]
    for j,k in [(0,1),(1,2),(2,3),(3,0)]:
        faces += [(j*N+i,j*N+(i+1)%N,k*N+(i+1)%N,k*N+i) for i in range(N)]
    mesh=bpy.data.meshes.new('Megaphone shell');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('Megaphone / lime shell',mesh);bpy.context.collection.objects.link(o);finish(o,o.name,'lime',.025)
    rod('Rear graphite housing',a-axis*.43,a+axis*.08,.29,'ink')
    rod('Handle',(-.33,.02,1.29),(-.57,.05,.28),.16,'ink')
    rod('Interior driver',a+axis*.3,a+axis*.48,.22,'ink')
    for i in range(2):
        centre=b+axis*(.48+i*.37)
        # short curved sound strips, intentionally not a full surrounding ring
        basis=q
        coords=[tuple(centre+basis@Vector((math.cos(t)*(.62+i*.19),math.sin(t)*(.62+i*.19),0))) for t in [j*math.pi/32-math.pi*.35 for j in range(24)]]
        path('Sound arc',coords,.045,'silver')
    box('Campaign tile',(-1.18,-.42,.16),(1.12,1.15,.18),'ivory',.08,(0,0,-.20))
    ball('Attention point',(-1.37,-.34,.39),.20,'lime')
def packaging():
    box('Carton',(-.3,.22,1.12),(1.9,1.45,2.22),'ivory',.09)
    box('Lime sleeve',(-.3,-.525,1.12),(1.92,.10,1.05),'lime',.035)
    box('Sleeve / side',(.685,.22,1.12),(.065,1.45,1.05),'lime',.025)
    text('Packaging monogram','N / P',(-.3,-.59,1.18),.29,'ink')
    box('Top fold',(-.3,.22,2.245),(1.65,.012,.018),'stone',.005)
    box('Product label',(1.15,-.5,.19),(1.00,1.10,.13),'ink',.055,(0,0,-.16))
    ring('Label seal',(1.15,-.5,.27),.23,.04,'lime',(0,0,0))
    rod('Paper tube',(-1.48,-.45,.22),(-1.48,-.45,1.40),.25,'stone')
    rod('Tube cap',(-1.48,-.45,1.39),(-1.48,-.45,1.51),.265,'silver')
def promotion():
    for x,h,m in [(-1.25,.64,'stone'),(-.45,1.05,'ivory'),(.35,1.55,'lime')]:
        box('Search growth',(x,.25,h/2),(.60,.72,h),m,.07)
    # Large magnifying glass in front of the rising columns.
    ring('Search ring',(.38,-.5,1.72),.73,.12,'silver')
    rod('Search handle',(.94,-.5,1.14),(1.53,-.5,.42),.16,'ink')
    pts=[(-.72,-.30),(-.72,-.08),(.1,.64),(-.14,.64),(-.14,.91),(.62,.91),(.62,.18),(.35,.18),(.35,.44),(-.50,-.30)]
    poly('Upward direction',pts,.14,(-.78,-.6,1.84),'lime',.025)
def gear(loc):
    N=96;verts=[]
    for y in [-.18,.18]:
        for typ in ['outer','inner']:
            for i in range(N):
                a=i*math.tau/N;r=(1.05 if i%8 in [2,3,4,5] else .87) if typ=='outer' else .44
                verts.append((math.cos(a)*r,y,math.sin(a)*r))
    faces=[]
    for i in range(N):
        j=(i+1)%N
        faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
    mesh=bpy.data.meshes.new('Gear');mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new('Support / machined gear',mesh);bpy.context.collection.objects.link(o);o.location=loc;finish(o,o.name,'ink',.045)
def support():
    gear((-.55,.12,1.2))
    ring('Bearing',(-.55,-.09,1.2),.47,.065,'silver')
    plate('Status tile',(.95,-.47,.86),(1.40,.25,1.42),'lime')
    poly('Check mark',[(-.43,.02),(-.24,-.24),(.43,.39),(.56,.25),(-.25,-.48),(-.58,-.13)],.06,(.97,-.63,.96),'ink',.035)
    ball('Spare bearing',(-1.42,-.65,.23),.23,'silver')
    rod('Spare pin',(-.5,-.75,.13),(.2,-.75,.13),.11,'ivory')
def social():
    plate('Conversation / back',(-.55,.28,1.67),(2.35,.28,1.55),'ink')
    poly('Speech tail',[(-.2,.1),(.25,.1),(-.22,-.35)],.23,(-1.15,.28,.97),'ink',.035)
    for x in [-1.08,-.59,-.1]:ball('Typing dots',(x,.10,1.67),.105,'ivory')
    plate('Conversation / front',(.8,-.49,.99),(1.65,.26,1.39),'lime')
    poly('Speech tail',[(-.2,.1),(.25,.1),(.22,-.30)],.23,(1.18,-.49,.38),'lime',.035)
    heart=[]
    for i in range(80):
        t=i*math.tau/80
        heart.append((16*math.sin(t)**3/40,(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/40))
    poly('Heart',heart,.10,(.8,-.67,1.02),'ink',.025)
    ring('Shared connection',(-1.1,-.70,.23),.4,.08,'silver',(0,0,0))
    ball('Conversation accent',(1.1,.15,2.35),.19,'silver')
bpy.ops.wm.read_factory_settings(use_empty=True)
M={'paper':mat('Paper / warm neutral','F6F6F1',0,.7),'ivory':mat('Porcelain / warm white','ECEEE5',.05,.29),'ink':mat('Graphite / satin','191B18',.10,.42),'lime':mat('Lime / glazed polymer','C9DF36',.08,.33),'silver':mat('Aluminium / brushed','C5CBC3',.8,.24),'stone':mat('Warm grey / matte','A2AA9A',.05,.42)}
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
builders={'web':web,'branding':branding,'advertising':advertising,'packaging':packaging,'promotion':promotion,'support':support,'social':social}
scenes=[]
for slug,build in builders.items():
    if args.only and slug!=args.only:continue
    s=scene_setup(slug);build();s.render.filepath=str(OUT/(slug+'.png'));scenes.append(s)
bpy.context.window.scene=scenes[0]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('ne-prosto-services'+('-'+args.only if args.only else '')+'.blend')),compress=True)
for s in scenes:
    bpy.context.window.scene=s;bpy.ops.render.render(write_still=True)
print('RENDER COMPLETE',str(OUT))
