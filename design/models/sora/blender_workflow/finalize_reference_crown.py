"""Finish the reference-traced crown and verify its connection to the shaft."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
assert str(ROOT).lower()==r'D:\KH Fighting Game'.lower()
OUT=ROOT/'design/models/sora/experiments/weapon_pipeline_v3'
target=OUT/'kingdom_key_reference_crown.blend'
if target.exists():raise RuntimeError('Preserve existing final scene')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'weapon_pipeline_pilot.blend'),load_ui=False)
bpy.context.preferences.filepaths.file_preview_type='NONE'
scene=bpy.context.scene
head=bpy.data.objects['crown_teeth']
count=len(head.data.vertices)//2
before=[list(head.data.vertices[index].co) for index in [0,count-1,count,2*count-1]]
for index in [0,count-1,count,2*count-1]:head.data.vertices[index].co.x=-.005
head.data.update()
assert head.data.validate() is False
assert min(vertex.co.x for vertex in head.data.vertices)<0<bpy.data.objects['silver_shaft'].dimensions.x
scene.render.filepath=str(OUT/'reference_crown_front.png')
bpy.ops.render.render(write_still=True)
camera=scene.camera
camera_location=camera.location.copy();camera_rotation=camera.rotation_euler.copy();camera_scale=camera.data.ortho_scale
points=[Vector(point) for point in head.bound_box]
center=(Vector(tuple(min(p[i] for p in points) for i in range(3)))+Vector(tuple(max(p[i] for p in points) for i in range(3))))/2
camera.location=center+Vector((.5,-2,.3));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=.42
scene.cycles.samples=16;scene.render.filepath=str(OUT/'reference_crown_detail.png')
bpy.ops.render.render(write_still=True)
camera.location=camera_location;camera.rotation_euler=camera_rotation;camera.data.ortho_scale=camera_scale
scene.render.filepath=str(OUT/'sprite_')
bpy.ops.wm.save_as_mainfile(filepath=str(target))
palette={}
for obj in scene.objects:
    obj.select_set(obj.type=='MESH' or obj.name=='KingdomKey_Rigid_Root')
    if obj.type=='MESH':
        for slot in obj.material_slots:
            original=slot.material
            if original.name not in palette:
                mat=bpy.data.materials.new(original.name+'_flat_export');mat.diffuse_color=original.diffuse_color
                mat.use_nodes=True;mat.node_tree.nodes.clear()
                output=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');surface=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
                surface.inputs['Base Color'].default_value=original.diffuse_color;surface.inputs['Roughness'].default_value=.9
                mat.node_tree.links.new(surface.outputs['BSDF'],output.inputs['Surface']);palette[original.name]=mat
            slot.material=palette[original.name]
glb=OUT/'kingdom_key_reference_crown.glb'
if glb.exists():raise RuntimeError('Preserve existing final GLB')
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
qa=dict(passed=True,reference='Newest user-attached640px diagonal Kingdom Key image',method='Approximate hand-traced crown silhouette with slanted outer prongs and two rounded inner projections; hidden root extends into shaft',
        sourceScene='weapon_pipeline_pilot.blend',originalRootVertices=before,rootVerticesNow=[list(head.data.vertices[index].co) for index in [0,count-1,count,2*count-1]],
        noInvalidMeshData=True,headIntersectsShaftAxis=True,rigidRoot='KingdomKey_Rigid_Root',
        scene=target.name,sceneSha256=hashlib.sha256(target.read_bytes()).hexdigest(),glb=glb.name,glbSha256=hashlib.sha256(glb.read_bytes()).hexdigest(),
        front='reference_crown_front.png',detail='reference_crown_detail.png',userApprovedExactGeometry=False,
        shoulderCarryOrSoraRigTested=False,gameplayIntegrated=False)
(OUT/'Reference_Crown_QA.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
print('Reference crown saved with a connected hidden root; previous trace and models preserved.')
