"""Export where a limb's joints land in each rendered 512 px frame of a keyed loop.

Opens <version>/sora_idle_loop.blend read-only and writes <version>/Limb_Screen.json with the
shoulder, elbow and wrist pixel positions of the given side for every keyed frame.
Run: blender --background --python export_limb_screen.py -- walk_fwd_v12 R
"""
import json
import sys
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version, side = sys.argv[sys.argv.index('--')+1:][:2]
OUT = ROOT / 'design/models/sora' / version
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'sora_idle_loop.blend'))
scene = bpy.context.scene
arm = next(o for o in scene.objects if o.type == 'ARMATURE')
size = scene.render.resolution_x


def pixel(bone):
    world = (arm.matrix_world @ arm.pose.bones[bone].matrix).translation
    v = world_to_camera_view(scene, scene.camera, world)
    return [round(v.x*size, 1), round((1 - v.y)*size, 1)]


frames = []
for f in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(f)
    frames.append({k: pixel(f'{side}_{b}') for k, b in (('shoulder', 'ude1'), ('elbow', 'ude2'), ('wrist', 'te'))})
(OUT / 'Limb_Screen.json').write_text(json.dumps({'side': side, 'size': size, 'frames': frames}, indent=2) + '\n',
                                      encoding='utf-8')
print('LIMB_OK', len(frames), frames[0])
