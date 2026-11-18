# Blender script: measure a MoMask BVH swing in the terms build_sprite_pilot.py uses for attack keys.
# Per frame: hips height, torso pitch (forward lean), shoulder turn relative to the hips, right hand relative
# to the hips (forward / toward the body's right / height) and right forearm direction, all in the body frame
# fixed at the first frame (forward = facing, right = body's right). Writes <out>.json and prints a table.
# usage: blender -b --factory-startup --python analyze_swing.py -- <in.bvh> <out.json>
import json, math, sys
import bpy
from mathutils import Vector

src, out = sys.argv[sys.argv.index('--') + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_anim.bvh(filepath=src, update_scene_fps=True)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
scn = bpy.context.scene
f0, f1 = (int(x) for x in arm.animation_data.action.frame_range)
P = arm.pose.bones
W = lambda name, tail=False: arm.matrix_world @ (P[name].tail if tail else P[name].head)

def flat(v):
    v = Vector((v.x, v.y, 0)); return v.normalized()

rows = []
scn.frame_set(f0)
right0 = flat(W('RightUpLeg') - W('LeftUpLeg'))
fwd0 = Vector((0, 0, 1)).cross(right0).normalized()
for f in range(f0, f1 + 1):
    scn.frame_set(f)
    hips = W('Hips')
    hip_r = flat(W('RightUpLeg') - W('LeftUpLeg'))
    sh_r = flat(W('RightArm') - W('LeftArm'))
    yaw = lambda v: math.degrees(math.atan2(v.dot(fwd0), v.dot(right0)))  # 0 = square, + = right side swung forward
    spine = (W('Neck') - hips).normalized()
    hand = W('RightHand', tail=True) - hips
    fore = (W('RightHand', tail=True) - W('RightForeArm')).normalized()
    rows.append(dict(
        frame=f, hips_z=round(hips.z, 3),
        pitch=round(math.degrees(math.atan2(spine.dot(fwd0), spine.z)), 1),
        hip_turn=round(yaw(hip_r), 1), shoulder_twist=round(yaw(sh_r) - yaw(hip_r), 1),
        hand=[round(hand.dot(fwd0), 3), round(hand.dot(right0), 3), round(W('RightHand', tail=True).z, 3)],
        hand_rel_z=round(hand.z, 3),
        forearm=[round(fore.dot(fwd0), 2), round(fore.dot(right0), 2), round(fore.z, 2)]))
for i, r in enumerate(rows):
    r['hand_speed'] = 0.0 if i == 0 else round((Vector(r['hand']) - Vector(rows[i - 1]['hand'])).length * scn.render.fps, 2)
json.dump(dict(source=src, fps=scn.render.fps, frames=rows), open(out, 'w'), indent=1)
print('frame hips_z pitch hip_turn sh_twist  hand(fwd,right,z)   rel_z  forearm(fwd,right,z)  speed')
for r in rows:
    print('SW', r['frame'], r['hips_z'], r['pitch'], r['hip_turn'], r['shoulder_twist'], r['hand'], r['hand_rel_z'], r['forearm'], r['hand_speed'])
