"""Add equally lit reference-angle comparisons without overwriting diagnostics."""
import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
OUT = ROOT / 'design/models/sora/experiments/weapon_pipeline_v4'
SOURCE = ROOT / 'design/models/sora/experiments/weapon_pipeline_v3/kingdom_key_reference_crown.blend'
files = ['previous_crown_lit.png', 'revised_crown_lit.png', 'revised_weapon_lit.png',
         'kingdom_key_crown_v4_review.blend', 'Lit_Review_QA.json']
assert all(not (OUT / filename).exists() for filename in files)


def prepare(source):
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    scene = bpy.context.scene
    scene.cycles.samples = 16
    scene.render.resolution_x = scene.render.resolution_y = 768
    # Move the existing procedural key light to the reference-facing side.
    # Old and new use the same light; no mesh or palette change is made here.
    for material in bpy.data.materials:
        if not material.node_tree:
            continue
        for node in material.node_tree.nodes:
            if node.type == 'VECT_MATH' and node.operation == 'DOT_PRODUCT':
                node.inputs[1].default_value = Vector((-.5, .8, .65)).normalized()
    return scene


def render(scene, filename, center, scale):
    camera = scene.camera
    center = Vector(center)
    camera.location = center + Vector((.6, 6, .48))
    rotation = (center - camera.location).to_track_quat('-Z', 'Y')
    camera.rotation_euler = (rotation @ Quaternion((0, 0, 1), math.atan2(.733, .680))).to_euler()
    camera.data.ortho_scale = scale
    scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)


scene = prepare(SOURCE)
render(scene, 'previous_crown_lit.png', (.107, 0, 1.265), .43)
scene = prepare(OUT / 'kingdom_key_crown_v4.blend')
render(scene, 'revised_crown_lit.png', (.107, 0, 1.265), .43)
render(scene, 'revised_weapon_lit.png', (.015, 0, .35), 2.55)
scene.render.filepath = str(OUT / 'sprite_')
target = OUT / 'kingdom_key_crown_v4_review.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
bpy.ops.wm.open_mainfile(filepath=str(target), load_ui=False)
assert len(bpy.data.objects['crown_teeth'].data.vertices) == 2 * 107
assert abs(bpy.data.objects['crown_teeth'].dimensions.y - .018) < .001
assert bpy.context.scene.camera.data.type == 'ORTHO'
records = []
for filename in files[:3]:
    image = bpy.data.images.load(str(OUT / filename), check_existing=False)
    assert tuple(image.size) == (768, 768) and image.channels == 4
    pixels = list(image.pixels)
    assert min(pixels[3::4]) == 0 and max(pixels[3::4]) > .99
    records.append(dict(file=filename, sha256=hashlib.sha256((OUT / filename).read_bytes()).hexdigest()))
report = dict(passed=True, savedSceneReopened=True, geometry='Same v4 crown; lighting and camera review only',
              scene=target.name, sceneSha256=hashlib.sha256(target.read_bytes()).hexdigest(), renders=records,
              matchingOldNewCameraAndLight=True, calibratedReferenceMatch=False,
              sourceReference='Inline image only; not embedded or available as a source mesh')
(OUT / 'Lit_Review_QA.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
