"""Isolated procedural 3D/render pilot. No engine or existing artwork edits."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'weapon_pipeline_v3'
assert version in {'weapon_pipeline_v1','weapon_pipeline_v2','weapon_pipeline_v3'}
OUT = ROOT / 'design/models/sora/experiments' / version
if OUT.exists():
    raise RuntimeError('Preserve existing pilot; choose a new version')
assert bpy.app.version[:2] == (5,2), bpy.app.version_string
OUT.mkdir(parents=True)
scene = bpy.context.scene
# Work only in the fresh factory scene passed by the launcher.
for obj in tuple(scene.objects):
    bpy.data.objects.remove(obj,do_unlink=True)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.render.resolution_x = scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.render.fps = 30
scene.world.color = (.5,.5,.5)
# Avoid thumbnail-cache writes when saving the isolated scene.
preview_property=bpy.context.preferences.filepaths.bl_rna.properties.get('file_preview_type')
if preview_property and 'NONE' in {item.identifier for item in preview_property.enum_items}:
    bpy.context.preferences.filepaths.file_preview_type='NONE'

def toon(name,color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    normal = nodes.new('ShaderNodeNewGeometry')
    dot = nodes.new('ShaderNodeVectorMath');dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = Vector((-.5,-.8,.65)).normalized()
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    base = ramp.color_ramp.elements[0];base.position = 0
    base.color = (*(x*.28 for x in color),1)
    for position,scale in [(.18,.60),(.55,1.0),(.82,1.15)]:
        item = ramp.color_ramp.elements.new(position)
        item.color = (*(min(1,x*scale) for x in color),1)
    links = mat.node_tree.links
    links.new(normal.outputs['Normal'],dot.inputs[0])
    links.new(dot.outputs['Value'],ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'],emission.inputs['Color'])
    links.new(emission.outputs[0],output.inputs['Surface'])
    return mat

gold = toon('gold_cel',(.93,.53,.035))
silver = toon('silver_cel',(.66,.73,.81))
black = toon('grip_cel',(.038,.048,.062))
blue = toon('collar_blue_cel',(.045,.13,.28))
root = bpy.data.objects.new('KingdomKey_Rigid_Root',None)
scene.collection.objects.link(root)
root['role'] = 'Procedural rigid weapon geometry pilot; not an extracted game asset or approved production model'
root['axis'] = 'Handle, collars and shaft share local +Z'

def finish(obj,name,mat,bevel=0):
    obj.name = name;obj.parent = root
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('small_edge_bevel','BEVEL');mod.width = bevel;mod.segments = 2
    return obj

def cylinder(name,radius,depth,z,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=(0,0,z))
    return finish(bpy.context.object,name,mat,.003)

def extrude(name,polygon,thickness,mat):
    # Flat silhouette in X/Z, with real thickness along Y.
    count = len(polygon)
    vertices = [(x,y,z) for y in (-thickness/2,thickness/2) for x,z in polygon]
    faces = [tuple(reversed(range(count))),tuple(range(count,count*2))]
    faces += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh = bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj = bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    return finish(obj,name,mat,.002)

# Single frame mesh with an actual opening, rather than four disconnected bars.
outer=[(-.15,-.40),(-.18,-.36),(-.18,.015),(-.145,.06),(.145,.06),(.18,.015),(.18,-.36),(.15,-.40)]
inner=[(-.10,-.33),(-.115,-.31),(-.115,-.035),(-.095,-.01),(.095,-.01),(.115,-.035),(.115,-.31),(.10,-.33)]
verts=[(x,y,z) for y in (-.035,.035) for ring in (outer,inner) for x,z in ring]
faces=[]
for i in range(8):
    j=(i+1)%8
    faces += [(i,j,8+j,8+i),(16+i,24+i,24+j,16+j),(i,16+i,16+j,j),(8+i,8+j,24+j,24+i)]
mesh=bpy.data.meshes.new('guard_frame_mesh');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('guard_frame',mesh);scene.collection.objects.link(obj);finish(obj,'guard_frame',gold,.005)
cylinder('central_black_handle',.031,.32,-.17,black)
cylinder('gold_pommel',.047,.055,-.355,gold)
cylinder('gold_collar',.052,.07,.035,gold)
cylinder('blue_collar',.037,.09,.115,blue)
cylinder('silver_shaft',.026,1.22,.77,silver)
cylinder('silver_end_cap',.030,.05,1.40,silver)
# Preserve previous constructions and trace the newest user-supplied crown reference.
reference_points=None
if version=='weapon_pipeline_v1':
    teeth_polygon=[(0,1.43),(.22,1.43),(.22,1.27),(.18,1.32),(.145,1.25),(.11,1.32),(.075,1.25),(.035,1.32),(0,1.31)]
elif version=='weapon_pipeline_v2':
    teeth_polygon=[(0,1.43),(.22,1.43),(.22,1.24),(.17,1.24),(.17,1.32),(.14,1.32),(.14,1.25),(.09,1.25),(.09,1.32),(.06,1.32),(.06,1.26),(0,1.26)]
else:
    # Approximate visible silhouette landmarks in the attached640x640 diagonal weapon image.
    # Outer prongs have slanted flat ends; two inner projections have rounded ends.
    reference_points=[(511,199),(474,127),(484,117),(505,148),(510,128),
                      (504,126),(501,121),(502,116),(506,112),(511,111),(516,114),(519,119),(518,124),(516,127),
                      (546,134),(538,110),(532,108),(528,103),(529,97),(533,93),(539,92),(544,96),(546,101),(544,106),(542,108),
                      (567,107),(540,79),(549,64),(600,109)]
    shaft_axis=Vector((.733,-.680));shaft_axis.normalize()
    across=Vector((shaft_axis.y,-shaft_axis.x))
    tip=Vector((609,126));scale=.00239
    teeth_polygon=[(round((Vector(point)-tip).dot(across)*scale,6),round(1.40+(Vector(point)-tip).dot(shaft_axis)*scale,6)) for point in reference_points]
    # The photo shows the visible cylinder edge; extend the hidden root into the shaft.
    teeth_polygon[0]=(-.005,teeth_polygon[0][1]);teeth_polygon[-1]=(-.005,teeth_polygon[-1][1])
    (OUT/'crown_reference_trace.json').write_text(json.dumps(dict(source='User-attached640x640 Kingdom Key reference image, October19; image only, no mesh file supplied',method='Approximate hand-traced visible silhouette; not a recovered original mesh',imageLandmarks=reference_points,shaftAxisImageXY=list(shaft_axis),acrossImageXY=list(across),localSilhouetteXZ=teeth_polygon),indent=2)+'\n',encoding='utf-8')
extrude('crown_teeth',teeth_polygon,.045,silver)
for number,z in enumerate([-.29,-.23,-.17,-.11,-.05]):
    cylinder('grip_ridge_%02d'%number,.0325,.007,z,black)

# Chain and pendant belong to this rigid prop test; secondary chain dynamics are a later step.
for i in range(8):
    bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=6,location=(-.012*i,-.006,-.409-.032*i),major_radius=.022,minor_radius=.005)
    link=bpy.context.object
    link.rotation_euler=(math.pi/2,0,(i%2)*math.pi/2)
    link.scale=(.7,1,1);finish(link,'chain_link_%02d'%i,silver)
for name,center,radius in [('pendant_center',(-.10,-.006,-.72),.042),('pendant_ear_left',(-.137,-.006,-.69),.025),('pendant_ear_right',(-.067,-.006,-.68),.025)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=radius,location=center)
    pendant=bpy.context.object;pendant.scale.y=.28;finish(pendant,name,silver)

bpy.ops.object.camera_add(location=(2.9,-5.8,2.15))
camera=bpy.context.object;camera.name='Sprite_Orthographic_Camera';camera.data.type='ORTHO';camera.data.ortho_scale=2.65
camera.rotation_euler=(Vector((0,0,.36))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
scene.render.use_freestyle=True
lines=scene.view_layers[0].freestyle_settings.linesets[0].linestyle
lines.color=(.025,.022,.020);lines.thickness=1.4
for obj in scene.objects:
    obj.select_set(obj.type=='MESH' or obj==root)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(OUT/'kingdom_key_rigid_pilot.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
renders=[]
for name,degrees in [('front_three_quarter',0),('foreground_tip',32),('opposite_three_quarter',-32)]:
    root.rotation_euler=(0,0,math.radians(degrees))
    scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    renders.append(dict(file=name+'.png',rootRotationZDegrees=degrees))
root.rotation_euler=(0,0,0)
scene.render.filepath=str(OUT/'sprite_')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'weapon_pipeline_pilot.blend'))
report=dict(status='Procedural 3D prop and transparent-render test; not a Sora character model',blenderVersion=bpy.app.version_string,
            renderEngine=scene.render.engine,device=scene.cycles.device,canvas=[512,512],transparentFilm=True,orthographicCamera=True,
            meshObjects=sum(obj.type=='MESH' for obj in scene.objects),rigidRoot=root.name,handleAndShaftAxis='local +Z',
            renders=renders,model='kingdom_key_rigid_pilot.glb',scene='weapon_pipeline_pilot.blend',teethSilhouetteXZ=teeth_polygon,
            userApprovedArtwork=False,soraCharacterMeshReady=False,rigOrAnimationReady=False,gameplayIntegrated=False,
            limitations=['Geometry is a procedural interpretation for a render-pipeline test.','Chain is rigid in this pilot.','No Sora character, skinning, run animation or cel-style match has been completed.'])
(OUT/'pilot_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
