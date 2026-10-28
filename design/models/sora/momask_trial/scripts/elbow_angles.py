# Blender script: print the elbow bend of both arms for every drawing in a build's sora_idle_loop.blend.
# Bend = angle between upper arm (ude1) and forearm (ude2): 0 = straight arm, 90 = right angle.
# Also prints shoulder (kata tail) and fist (te head) positions so hand targets can be moved along the arm.
# usage: blender -b --factory-startup --python elbow_angles.py -- <path/to/sora_idle_loop.blend>
import sys, math
import bpy

bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index('--') + 1])
scn = bpy.context.scene
arm = next(o for o in scn.objects if o.type == 'ARMATURE')
P = arm.pose.bones
W = lambda b, tail=False: arm.matrix_world @ (P[b].tail if tail else P[b].head)
for f in range(scn.frame_start, scn.frame_end + 1):
    scn.frame_set(f)
    out = []
    for s in ('L', 'R'):
        up = W(f'{s}_ude1', True) - W(f'{s}_ude1')
        fo = W(f'{s}_ude2', True) - W(f'{s}_ude2')
        bend = math.degrees(up.angle(fo))
        out.append(f'{s} bend {bend:5.1f}  shoulder {tuple(round(c, 2) for c in W(f"{s}_ude1"))}  '
                   f'fist {tuple(round(c, 2) for c in W(f"{s}_te"))}')
    print('ELBOW', f, ' | '.join(out))
