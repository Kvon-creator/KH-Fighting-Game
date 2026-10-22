"""Export first-frame alignment points (head and front hand grip) for a keyed sprite loop.

Opens <version>/sora_idle_loop.blend read-only and prints, for frame 1, the 512 px render
coordinates of the head bone (atama head) and of the front hand grip: the centroid of the
visible right-hand mesh (te + finger vertices) and the R_buki weapon socket.
Run: blender --background --python export_alignment_points.py -- walk_fwd_v18t
"""
import json
import sys
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version = sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'design/models/sora' / version / 'sora_idle_loop.blend'))
scene = bpy.context.scene
scene.frame_set(scene.frame_start)
arm = next(o for o in scene.objects if o.type == 'ARMATURE')
body = [o for o in scene.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' for m in o.modifiers)]
size = scene.render.resolution_x


def px(world):
    v = world_to_camera_view(scene, scene.camera, world)
    return [round(v.x*size, 1), round((1 - v.y)*size, 1)]


def bone(name):
    return (arm.matrix_world @ arm.pose.bones[name].matrix).translation


dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in body:
    groups = {o.vertex_groups[n].index for n in ('R_te', 'R_yubiB') if n in o.vertex_groups}
    ev = o.evaluated_get(dg).data
    pts += [o.matrix_world @ ev.vertices[v.index].co for v in o.data.vertices
            if any(e.group in groups and e.weight > .3 for e in v.groups)]
print('ALIGN', json.dumps({'version': version, 'head_bone_atama': px(bone('atama')),
                           'grip_hand_centroid_R': px(sum(pts, Vector()) / len(pts)),
                           'grip_socket_R_buki': px(bone('R_buki'))}))
