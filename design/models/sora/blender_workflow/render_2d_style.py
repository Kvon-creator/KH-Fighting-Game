"""Re-render an approved 3D loop with an illustration-style look for the 2D sprite attempt.

Opens <source>/sora_idle_loop.blend (keyed loop) read-only, strengthens the cel shadow with a
cool tint, thickens the Freestyle ink lines, and renders every keyed frame to
<output>/frames_512_raw. The source .blend is never saved over.
Run: blender --background --python render_2d_style.py -- battle_v12 sprite2d_v1
"""
import json
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[4]
assert (ROOT / 'KingdomArena/project.godot').is_file(), ROOT  # project root (any clone)
source, version = sys.argv[sys.argv.index('--')+1:][:2]
import os
# SORA_CHARACTER=limit_form: player 2's Limit Form renders (build_sprite_pilot.py / limit_form_model.py).
SORA = ROOT / ('design/models/sora_limit_form' if os.environ.get('SORA_CHARACTER') == 'limit_form' else 'design/models/sora')
SRC = SORA / source / 'sora_idle_loop.blend'
OUT = SORA / version
if OUT.exists():
    raise RuntimeError('Preserve existing render; choose a new version')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
OUT.mkdir(parents=True); (OUT / 'frames_512_raw').mkdir()
scene = bpy.context.scene

# Illustration shading: larger, cooler shadow band like the pose sheet's flat two-tone art.
for mat in bpy.data.materials:
    if not mat.node_tree:
        continue
    for node in mat.node_tree.nodes:
        if node.type == 'VALTORGB':
            node.color_ramp.elements[0].color = (.52, .54, .70, 1)
            node.color_ramp.elements[1].position = .42

# Heavier ink: thick outer contour, firmer interior lines, dark navy ink like the sheet.
for lineset in bpy.context.view_layer.freestyle_settings.linesets:
    style = lineset.linestyle
    # Freestyle colours are linear: v1's (.07, .06, .11) displayed as grey-lavender (~75, 69, 95).
    style.color = (.07, .06, .11) if version == 'sprite2d_v1' else (.007, .006, .014)
    if lineset.name == 'outer_contour':
        # v3+: v2's 3.0 contour plus the post rim read as a soft glow.
        style.thickness = 3.0 if version in ('sprite2d_v1', 'sprite2d_v2') else 2.2
    else:
        style.thickness, style.alpha = 1.1, .8

frames = []
for f in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(f)
    path = OUT / 'frames_512_raw' / f'sora_idle3d_{f-1:02d}.png'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    frames.append(path.name)
(OUT / 'Render_Report.json').write_text(json.dumps({
    'source': f'{source}/sora_idle_loop.blend', 'version': version, 'frames': frames,
    'style': 'cool two-tone cel (shadow .52/.54/.70 at .42), navy ink, outer 3.0 / inner 1.1',
}, indent=2) + '\n', encoding='utf-8')
print('RENDER2D_OK', len(frames))
