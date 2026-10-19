"""Read the saved pilot and its PNG/GLB outputs; write QA only."""
import hashlib
import json
import struct
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[4]
assert str(ROOT).lower()==r'D:\KH Fighting Game'.lower()
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'weapon_pipeline_v1'
assert version in {'weapon_pipeline_v1','weapon_pipeline_v2','weapon_pipeline_v3'}
OUT=ROOT/'design/models/sora/experiments'/version
report=json.loads((OUT/'pilot_report.json').read_text(encoding='utf-8'))
if version=='weapon_pipeline_v3':
    report['scene']='kingdom_key_reference_crown.blend'
    report['model']='kingdom_key_reference_crown.glb'
    report['renders']=[dict(file='reference_crown_front.png')]
assert bpy.app.version[:2]==(5,2)
bpy.ops.wm.open_mainfile(filepath=str(OUT/report['scene']),load_ui=False)
scene=bpy.context.scene
root=bpy.data.objects['KingdomKey_Rigid_Root']
meshes=[obj for obj in scene.objects if obj.type=='MESH']
assert len(meshes)==24 and all(obj.parent==root for obj in meshes)
assert scene.camera.data.type=='ORTHO' and scene.render.film_transparent
assert scene.render.image_settings.color_mode=='RGBA' and scene.cycles.device=='CPU'
for name in ['central_black_handle','gold_pommel','gold_collar','blue_collar','silver_shaft','silver_end_cap']:
    obj=bpy.data.objects[name]
    assert abs(obj.location.x)<1e-6 and abs(obj.location.y)<1e-6
    assert max(abs(angle) for angle in obj.rotation_euler)<1e-6
mesh_counts={obj.name:dict(vertices=len(obj.data.vertices),polygons=len(obj.data.polygons)) for obj in meshes}
renders=[]
for item in report['renders']:
    file=OUT/item['file']
    image=bpy.data.images.load(str(file),check_existing=False)
    assert tuple(image.size)==(512,512) and image.channels==4
    pixels=list(image.pixels)
    alpha=pixels[3::4]
    visible=[(n%512,n//512) for n,a in enumerate(alpha) if a>.1]
    bounds=[min(x for x,y in visible),min(y for x,y in visible),max(x for x,y in visible),max(y for x,y in visible)]
    assert min(alpha)==0 and max(alpha)>.99 and min(bounds[:2])>10 and max(bounds[2:])<501
    renders.append(dict(file=item['file'],sha256=hashlib.sha256(file.read_bytes()).hexdigest(),alphaRange=[min(alpha),max(alpha)],boundsBottomOrigin=bounds))
glb=(OUT/report['model']).read_bytes()
magic,glb_version,length=struct.unpack_from('<4sII',glb)
assert magic==b'glTF' and glb_version==2 and length==len(glb)
json_length,json_type=struct.unpack_from('<II',glb,12)
assert json_type==0x4e4f534a
gltf=json.loads(glb[20:20+json_length])
assert gltf.get('meshes') and gltf.get('nodes') and gltf['buffers'][0]['byteLength']>0
qa=dict(passed=True,blenderVersion=bpy.app.version_string,savedSceneReopened=True,meshCount=len(meshes),allMeshesShareRigidRoot=True,
        gripCollarsShaftShareLocalAxis=True,orthographicCamera=True,renderEngine=scene.render.engine,device=scene.cycles.device,
        renders=renders,glbVersion=glb_version,glbMeshCount=len(gltf['meshes']),glbBytes=len(glb),meshCounts=mesh_counts,
        sceneSha256=hashlib.sha256((OUT/report['scene']).read_bytes()).hexdigest(),glbSha256=hashlib.sha256(glb).hexdigest(),
        blenderToonShaderPortableToGLB=False,fullSoraCharacterOrAnimationReady=False,gameplayIntegrated=False)
if version=='weapon_pipeline_v3':
    colors=[tuple(material.get('pbrMetallicRoughness',{}).get('baseColorFactor',[])) for material in gltf['materials']]
    assert len(set(colors))==4
    qa['paletteColorsVerified']=4
target=OUT/('Reference_Final_Scene_QA.json' if version=='weapon_pipeline_v3' else 'QA_Report.json')
if target.exists():
    raise RuntimeError('Preserve existing QA report')
target.write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
preview_setting=getattr(bpy.context.preferences.filepaths,'file_preview_type',None)
print(json.dumps(dict(passed=True,savedSceneReopened=True,meshCount=len(meshes),transparentRenders=len(renders),glbBytes=len(glb),filePreviewSetting=preview_setting),indent=2))
