"""Export a color-preserving sibling GLB; keep the procedural toon .blend intact."""
import json
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[4]
assert str(ROOT).lower()==r'D:\KH Fighting Game'.lower()
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'weapon_pipeline_v1'
assert version in {'weapon_pipeline_v1','weapon_pipeline_v2','weapon_pipeline_v3'}
OUT=ROOT/'design/models/sora/experiments'/version
target=OUT/'kingdom_key_flat_colors_v3.glb'
if target.exists():raise RuntimeError('Preserve existing model export')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'weapon_pipeline_pilot.blend'),load_ui=False)
palette={}
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type=='MESH' or obj.name=='KingdomKey_Rigid_Root')
    if obj.type=='MESH':
        for slot in obj.material_slots:
            # The original procedural normal/ramp nodes cannot be exported as glTF materials.
            original=slot.material
            if original.name not in palette:
                mat=bpy.data.materials.new(original.name+'_flat_export')
                mat.diffuse_color=original.diffuse_color;mat.use_nodes=True
                mat.node_tree.nodes.clear()
                output=mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
                surface=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
                surface.inputs['Base Color'].default_value=original.diffuse_color
                surface.inputs['Roughness'].default_value=.9
                surface.inputs['Metallic'].default_value=0
                mat.node_tree.links.new(surface.outputs['BSDF'],output.inputs['Surface'])
                palette[original.name]=mat
            slot.material=palette[original.name]
bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
print(json.dumps(dict(file=target.name,purpose='Flat palette for model exchange; use the original blend for actual toon sprite renders',originalBlendSaved=False)))
