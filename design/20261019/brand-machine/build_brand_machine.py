"""Identity press / NEPROSTO. Original editable Blender concept, 19 October 2026.
Source of truth: VPS. Local directory is temporary GPU-render space only.
blender -b --factory-startup -P build_brand_machine.py -- --out DIR [--draft]
"""
import bpy, math, sys, argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('--out',required=True)
p.add_argument('--draft',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=Path(a.out);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
def lin(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def material(n,h,metal=0,rough=.4,grain=0):
 m=bpy.data.materials.new(n);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*(lin(int(h[i:i+2],16)/255) for i in (0,2,4)),1)
 bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if grain:
  noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=165
  noise.inputs['Detail'].default_value=2
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.2;bump.inputs['Distance'].default_value=grain
  m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 return m
M={
 'ivory':material('Warm enamel','E8EAE1',.18,.31,.006),
 'ink':material('Graphite powder coat','20231F',.25,.34,.004),
 'lime':material('Acid lime enamel','C9DF36',.16,.3,.002),
 'silver':material('Satin machined aluminium','BCC3BD',.86,.25,.003),
 'darkmetal':material('Dark steel','4D544C',.85,.3),
 'paper':material('Uncoated ivory paper','F2F1E7',0,.69,.005),
 'blackprint':material('Letterpress ink','111810',0,.7),
 'rubber':material('Graphite roller rubber','171B17',0,.66,.009),
 'floor':material('Seamless warm background','F6F6F1',0,.8),
 'greenprint':material('Printed lime','BBCF26',0,.69),
}
glass=material('Smoked inspection acrylic','8EADA1',0,.12)
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.82
glass.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.45
M['glass']=glass
def finish(o,n,mat,bevel=0):
 o.name=n;o.data.materials.append(M[mat])
 if bevel:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=3
  mod=o.modifiers.new('Face normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def box(n,loc,dims,mat='ivory',bevel=.035,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if rot:o.rotation_euler=rot
 return finish(o,n,mat,bevel)
def rod(n,pt1,pt2,r,mat='silver',bevel=.012):
 u,v=Vector(pt1),Vector(pt2)
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=(v-u).length,location=(u+v)/2)
 o=bpy.context.object;o.rotation_euler=(v-u).to_track_quat('Z','Y').to_euler()
 return finish(o,n,mat,bevel)
def ring(n,loc,r,t,mat='silver',rot=(math.pi/2,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=72,minor_segments=12,location=loc,rotation=rot)
 return finish(bpy.context.object,n,mat)
def path(n,pts,r,mat):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3
 sp=c.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for b,co in zip(sp.bezier_points,pts):b.co=co;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(M[mat]);return o
def extrude(n,pts,depth,loc,mat='ink',bevel=.05):
 N=len(pts);verts=[(x,y,z) for y in [-depth/2,depth/2] for x,z in pts]
 faces=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]
 faces.extend((i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N))
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(n,mesh);bpy.context.collection.objects.link(o);o.location=loc
 return finish(o,n,mat,bevel)
font=None
for f in ['C:/Windows/Fonts/arialbd.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
 if Path(f).exists():font=bpy.data.fonts.load(f);break
def text(n,body,loc,size,mat='blackprint',rot=(math.pi/2,0,0),align='LEFT',depth=.0007):
 c=bpy.data.curves.new(n,'FONT');c.body=body;c.size=size;c.extrude=depth;c.align_x=align
 if font:c.font=font
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=rot;c.materials.append(M[mat]);return o
def bolt(n,x,y,z,r=.035):
 rod(n,(x,y+.02,z),(x,y-.02,z),r,'silver',.006)
 box(n+' screwdriver slot',(x,y-.027,z),(r*1.13,.012,r*.18),'darkmetal',.002)
def top_print(n,body,x,y,z,size=.2,mat='blackprint',angle=0):
 return text(n,body,(x,y,z),size,mat,(0,0,angle))
def bar_code(x,y,z,width=.34,height=.12,top=False):
 for i,w in enumerate([.013,.027,.009,.02,.034,.012,.023,.009,.026,.014]):
  t=sum([.013,.027,.009,.02,.034,.012,.023,.009,.026,.014][:i])+i*.01
  if top:box('Barcode ink',(x+t,y,z),(w,height,.002),'blackprint',0)
  else:box('Barcode ink',(x+t,y,z),(w,.002,height),'blackprint',0)

# Slender chassis with real feet and inset equipment rail.
box('Machined shared chassis',(-.05,.28,.28),(7.5,2.25,.22),'silver',.11)
box('Ivory top deck',(-.05,.28,.425),(7.22,2.05,.09),'ivory',.065)
for x in [-3.2,3.1]:
 for y in [-.55,1.08]:
  rod('Vibration isolator',(x,y,.06),(x,y,.19),.16,'rubber')
  rod('Adjustable foot',(x,y,.17),(x,y,.23),.11)
for x in [-3.1,-.3,2.5]:
 box('Front chassis vent',(x,-.856,.3),(.28,.012,.035),'darkmetal',.014)

# Asymmetric large open gantry: main visual identity.
arch=[(-1.22,0),(-1.22,3.25),(-.95,3.50),(.92,3.50),(1.19,3.25),(1.19,0),(.73,0),(.73,2.73),(-.71,2.73),(-.71,0)]
extrude('Graphite open press frame',arch,1.12,(-1.55,.35,.48),'ink',.085)
box('Enamel crown panel',(-1.55,-.225,3.59),(1.93,.045,.5),'ivory',.045)
text('NP model badge','NP—01',(-2.37,-.253,3.59),.25)
text('Studio signature','НЕПРОСТО',(-2.37,-.254,3.42),.095)
text('Equipment serial','IDENTITY / PRESS',(-1.30,-.254,3.70),.06)
text('Equipment serial line','EDITION  01',(-1.30,-.254,3.60),.052)
text('Gantry side calibration','01',(-2.64,-.23,2.75),.16,'ivory')
for i in range(7):box('Crown ventilation slot',(-.347,-.02+i*.12,3.52),(.012,.032,.24),'rubber',.009)
for x in [-2.54,-.55]:
 for z in [.77,3.05,3.86]:bolt('Gantry fastener',x,-.229,z)

# Platen, lead screw and columns, all connected to overhead mechanism.
for x in [-2.07,-1.02]:
 rod('Polished platen guide',(x,.23,1.1),(x,.23,3.20),.06)
 rod('Guide bushing',(x,.23,1.95),(x,.23,2.21),.105,'silver')
rod('Threaded actuator',(-1.55,.35,2.02),(-1.55,.35,3.25),.095,'darkmetal')
for i in range(26):
 ring('Lead screw thread',(-1.55,.35,2.03+i*.044),.1,.014,'silver',(0,0,0))
box('Moving lime platen',(-1.55,.30,2.02),(1.55,1.38,.25),'lime',.065)
box('Printing die',(-1.55,.3,1.86),(1.19,1.18,.075),'silver',.02)
box('Heated type bed',(-1.55,.30,1.10),(1.6,1.5,.18),'darkmetal',.035)
for x in [-2.17,-.93]:bolt('Platen fixing',x,-.411,2.03,.04)
path('Actuator cable',[(-1.0,.94,3.4),(-.65,1.15,3),(-.7,1.18,1.9),(-.12,1.14,.54)],.038,'rubber')

# Supply reel at the left: paper wound around a visible graphite spindle.
rod('Input spindle',(-3.14,-.62,1.05),(-3.14,1.12,1.05),.13,'darkmetal')
rod('Paper supply reel',(-3.14,-.41,1.05),(-3.14,.96,1.05),.55,'paper')
for y in [-.44,.99]:
 ring('Paper reel edge',(-3.14,y,1.05),.46,.009,'ivory')
 ring('Paper reel core',(-3.14,y,1.05),.14,.016,'darkmetal')
box('Reel support front',(-3.14,-.61,.68),(.22,.19,.47),'ivory',.05)
box('Reel support rear',(-3.14,1.13,.68),(.22,.19,.47),'ivory',.05)
rod('Reel end cap',(-3.14,-.73,1.05),(-3.14,-.65,1.05),.18,'silver')
# Continuous ribbon with a smooth leading curve onto the flat platen.
sections=[(-3.14,1.61),(-2.90,1.60),(-2.66,1.48),(-2.40,1.27),(-2.18,1.22),(-1.7,1.22),(-.7,1.22),(.3,1.22),(1.0,1.22),(1.55,1.15),(2.06,.91),(2.57,.82),(2.85,.82)]
verts=[(x,y,z) for x,z in sections for y in [-.34,.94]]
faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(sections)-1)]
mesh=bpy.data.meshes.new('Continuous printed web');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('Paper passing through machine',mesh);bpy.context.collection.objects.link(o);finish(o,o.name,'paper')
sol=o.modifiers.new('Paper thickness','SOLIDIFY');sol.thickness=.012
sub=o.modifiers.new('Gently bending paper','SUBSURF');sub.levels=2
# Bold graphic tiles on flat web, sitting clearly under the pressing plate.
for xx in [-1.9,-1.24,-.58,.08]:
 box('Printed registration bar',(xx,.31,1.231),(.19,1.16,.003),'greenprint',0)
top_print('Print in progress','НЕ',-.50,-.28,1.238,.46)
for xx in [-2.18,-.18]:
 for yy in [-.27,.85]:
  box('Registration tick',(xx,yy,1.24),(.08,.009,.003),'blackprint',0)
  box('Registration tick',(xx,yy,1.24),(.009,.08,.003),'blackprint',0)

# Output roller mechanism; transparent protective cover is framed, not a vague cube.
for x in [.4,1.22]:
 for y in [-.59,1.19]:
  box('Roller bearing upright',(x,y,1.02),(.19,.18,1.06),'ivory',.065)
for z,r in [(.84,.33),(1.58,.35)]:
 rod('Rubber feed roller',(.8,-.40,z),(.8,1.02,z),r,'rubber')
 rod('Feed roller axle',(.8,-.81,z),(.8,1.31,z),.09,'silver')
 for y in [-.52,1.13]:
  rod('Bearing housing',(.8,y-.10,z),(.8,y+.10,z),.22,'silver')
  ring('Bearing seal',(.8,y-.11,z),.145,.023,'rubber')
box('Inspection window',(.8,1.22,1.53),(1.05,.055,.72),'glass',.03)
for z in [1.13,1.95]:box('Guard window rim',(.8,1.245,z),(1.18,.07,.06),'silver',.02)
for xx in [.235,1.365]:box('Guard window upright',(xx,1.245,1.54),(.05,.07,.87),'silver',.015)

# Large tactile handwheel, concentric rings, knurling, and real pointer.
rod('Handwheel core',(.8,-1.01,1.58),(.8,-.80,1.58),.43,'silver')
rod('Handwheel graphite inset',(.8,-1.045,1.58),(.8,-1.015,1.58),.335,'ink')
ring('Handwheel lime ring',(.8,-1.065,1.58),.28,.022,'lime')
rod('Adjustment centre',(.8,-1.13,1.58),(.8,-1.05,1.58),.16,'silver')
for i in range(56):
 ang=math.tau*i/56
 rod('Knurled grip',(.8+math.cos(ang)*.425,-1.005,1.58+math.sin(ang)*.425),(.8+math.cos(ang)*.425,-.82,1.58+math.sin(ang)*.425),.014,'darkmetal',.003)
box('Dial pointer',(.8,-1.137,1.67),(.023,.008,.10),'ink',.003)
for i in range(11):
 ang=math.radians(25+i*13)
 xx=.8+math.cos(ang)*.35;zz=1.58+math.sin(ang)*.35
 box('Wheel index',(xx,-1.071,zz),(.011,.005,.036),'ivory',.002,(0,ang-math.pi/2,0))

# Compact control box toward front, integrated with the machine.
box('Control console',(-.33,-.57,.76),(.62,.50,.53),'ivory',.065)
box('Status display',(-.33,-.831,.87),(.44,.012,.16),'ink',.013)
text('Display numerals','028',(-.50,-.841,.83),.10,'lime')
for xx,mat in [(-.48,'lime'),(-.19,'ink')]:
 rod('Tactile control',(xx,-.86,.63),(xx,-.81,.63),.075,mat)
text('Control engraving','FEED',(-.49,-.837,.49),.046,'blackprint')

# Lightweight product output tray.
box('Receiving tray',(2.43,.28,.68),(1.9,1.65,.08),'silver',.055)
for yy in [-.55,1.10]:box('Folded tray edge',(2.43,yy,.77),(1.9,.035,.18),'silver',.018)
for xx in [1.8,3.0]:box('Tray leg',(xx,.3,.55),(.08,1.3,.23),'darkmetal',.018)

# Hero packaging, an authored print composition on physical paper.
box('Finished carton',(2.47,.54,1.36),(.95,.83,1.27),'paper',.025)
box('Carton top fold',(2.47,.54,2.002),(.016,.76,.008),'ivory',.001)
box('Lime carton side',(2.954,.54,1.36),(.014,.83,.98),'greenprint',.001)
box('Black carton field',(2.47,.116,1.52),(.80,.008,.82),'blackprint',.001)
text('Carton headline 1','НЕ',(2.10,.108,1.70),.31,'paper')
text('Carton headline 2','ПРО',(2.10,.108,1.43),.27,'lime')
text('Carton headline 3','СТО',(2.10,.108,1.17),.27,'paper')
text('Carton small signature','СТУДИЯ ДИЗАЙНА',(2.08,.107,.86),.053)
# Physical sticky label on the right side, correctly following the object.
text('Side serial','01',(2.965,.83,1.14),.42,'blackprint',(math.pi/2,0,math.pi/2))
# Sheet stack on front of tray, each sheet a real thin solid.
for j in range(6):
 box('Business card stack',(2.40,-.26,.85+j*.012),(.95,.48,.009),'paper',.006)
top_print('Cards wordmark','НЕПРОСТО',1.99,-.31,.927,.12)
box('Card lime stripe',(2.39,-.08,.927),(.84,.038,.002),'greenprint',0)
bar_code(2.56,-.35,.928,top=True)

# Sample board and sculpted Cyrillic type placed beside the input, not floating.
box('Type-block tray',(-2.32,-1.19,.10),(1.25,.65,.12),'silver',.04)
box('Type block foot',(-2.39,-1.21,.28),(.77,.35,.22),'ivory',.025)
text('Solid Cyrillic printing type','Н',(-2.73,-1.30,.37),.98,'lime',depth=.085)
# Small identity sheet leaning against the rear machine rail.
box('Printed sample board',(1.82,1.20,1.32),(.82,.06,1.2),'paper',.018)
text('Specimen typography','а',(1.45,1.16,1.20),.75,'blackprint')
text('Specimen caption','TYPO / 01',(1.50,1.16,.82),.075)
for xx in [-2.75,-.1,3.22]:
 for yy in [-.6,1.12]:
  rod('Deck bolt',(xx,yy,.47),(xx,yy,.48),.035,'darkmetal',.004)

# Studio lighting: warm background, rich blacks, controlled metal.
box('Studio ground',(0,0,-.09),(200,200,.1),'floor',0)
sc=bpy.context.scene;sc.name='NP01 Identity Machine'
sc.render.engine='CYCLES';sc.cycles.samples=48 if a.draft else 192
sc.cycles.use_denoising=True;sc.cycles.adaptive_threshold=.025
sc.cycles.max_bounces=8;sc.cycles.transmission_bounces=6
world=bpy.data.worlds.new('Neutral soft studio');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.80,.75,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.28;sc.world=world
def area(n,loc,power,size,color,target=(0,0,1.4)):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
 o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Large left key',(-5,-5,8),1550,5.2,(1,.97,.90))
area('Restrained front fill',(5,-4,5),650,4.2,(.92,.96,1))
area('Metal edge strip',(1,5,7),1850,4.0,(1,1,.94))
cam=bpy.data.cameras.new('Editorial product camera');co=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(co)
co.location=(8.8,-13.3,8.2);target=Vector((-.15,.22,1.75));co.rotation_euler=(target-co.location).to_track_quat('-Z','Y').to_euler()
cam.type='ORTHO';cam.ortho_scale=10.0;sc.camera=co
sc.render.resolution_x=1200 if a.draft else 1800
sc.render.resolution_y=900 if a.draft else 1350
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB'
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.12
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:sc.cycles.device='CPU'
sc.render.filepath=str(OUT/('brand-machine-draft.png' if a.draft else 'brand-machine.png'))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'neprosto-brand-machine.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('COMPLETED',sc.render.filepath,'objects',len(sc.objects))

