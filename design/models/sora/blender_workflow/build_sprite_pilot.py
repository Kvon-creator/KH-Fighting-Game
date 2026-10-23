"""Sora 3D-to-sprite pilot from the downloaded KH2 model (p_ex150.fbx) and Kingdom Key.

Scales Sora to 1.6 m, cel-shades his original textures with Freestyle outlines, attaches the
Kingdom Key to his R_buki weapon bone, poses an approximate approved-idle stance with IK
targets, and renders one transparent frame from a fixed three-quarter orthographic sprite
camera framed like the approved idle (512px canvas, ground at y=470). Downloads are not modified.
Run: blender --background --factory-startup --python build_sprite_pilot.py -- sprite_pilot_v1
"""
import json
import math
import sys
from pathlib import Path
import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
ARGS = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['sprite_pilot_v1']
version = ARGS[0]  # pose recipe
# Optional output name. sheet_*: same recipe on the from-scratch rig (character_blockout_v8)
# instead of the downloaded PS2 model.
OUT_NAME = ARGS[1] if len(ARGS) > 1 else version
SHEET_MODEL = OUT_NAME.startswith('sheet_')
# walk_fwd_v* / walk_back_v*: in-place guard shuffle on the one-handed battle-ready stance
# (battle_v2), per Kvon's movement grip rule (right hand only, Keyblade low and behind).
GAIT = version if version.startswith(('walk_fwd_v', 'walk_back_v', 'shuffle_fwd_v', 'shuffle_back_v')) else None
# shuffle_*_v*: Kvon's "idle shuffle": the approved battle idle's upper body unchanged, only the feet
# slide (front foot out, back foot follows); drawing 1 is the idle stance, so no transitions are needed.
IDLE_SHUFFLE = bool(GAIT) and GAIT.startswith('shuffle_')
SH_DIP_V4 = float(ARGS[2]) if len(ARGS) > 2 else .11  # shuffle v4 hip dip (m); optional 3rd argument
if GAIT:
    # v1: one-handed battle_v2 stance. v2+ (Kvon): keep both hands on the Keyblade, so the walk
    # starts from the approved two-handed battle idle (battle_v12) with no grip change.
    version = 'battle_v2' if GAIT.endswith('_v1') and not IDLE_SHUFFLE else 'battle_v12'
# one_hand_v*: user's one-handed idle, right hand only, blade angled down toward his feet.
# battle_v*: battle-ready one-handed stance (staggered feet, body turned to the opponent, blade
# low and back, guard hand up, combat bounce), following design/references/Sora_battle_stance.gif.
BATTLE = version.startswith('battle_v')
# battle_v4+: the mirrored pose-sheet crouch is two-handed (both fists on the handle).
TWO_HAND_BATTLE = BATTLE and version not in ('battle_v1', 'battle_v2', 'battle_v3')
ONE_HAND = (version.startswith('one_hand_v') or BATTLE) and not TWO_HAND_BATTLE
LOOP = version.startswith('idle_loop_v') or ONE_HAND or BATTLE  # 10-frame loop; sprite_pilot_v* = single frame
GRIP_SIDES = ('R',) if ONE_HAND else ('R', 'L')
KEY_FACES_CAMERA = LOOP and version not in ('idle_loop_v2', 'idle_loop_v3')  # user grip correction
CURL_FINGERS = KEY_FACES_CAMERA and version != 'idle_loop_v4'  # close the rip's open hands on the handle
# v6+ (user request): twist each wrist so the palm faces the handle, and turn the teeth up.
WRIST_TWIST = CURL_FINGERS and version != 'idle_loop_v5'
KEY_TEETH_UP = WRIST_TWIST
# v7+: pose from Kvon's Smash idle reference image instead of the approved 2D idle.
REF_POSE = LOOP and version not in {f'idle_loop_v{n}' for n in range(1, 7)}
MESH_GRIP = LOOP and version not in {f'idle_loop_v{n}' for n in range(1, 12)}  # v12+: grip at visible hand
# v14+ (user note): front (right) palm up, left wrist turned the opposite way, hands slid up toward the hilt.
PALM_ORIENT = LOOP and version not in {f'idle_loop_v{n}' for n in range(1, 14)}
# v15+ (user-approved): roll the fingers and thumbs around the handle with a "fist_wrap" shape key.
FIST_WRAP = LOOP and version not in {f'idle_loop_v{n}' for n in range(1, 15)}
# v15's plain roll curled the short fingers only 60-100 degrees; v16+ curls harder.
WRAP_GAIN, WRAP_MAX_DEG = (1.0, 250) if version == 'idle_loop_v15' else (1.7, 270)
# v17+: bend each wrist so the fingers cross the handle; v16's palm-up right fingers lay along it.
SQUARE_WRISTS = FIST_WRAP and version not in ('idle_loop_v15', 'idle_loop_v16')
SORA = ROOT / 'design/models/sora'
OUT = SORA / OUT_NAME
if OUT.exists():
    raise RuntimeError('Preserve existing pilot; choose a new version')
assert bpy.app.version[:2] == (5, 2), bpy.app.version_string
IDLE = ROOT / 'design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png'
HEIGHT = 1.6          # meters, T-pose top of hair to sole
# Grip-to-tip length: approved idle's proportion; v8+ reference shows a longer Key (tip near head height).
KEY_REACH = 1.0 if REF_POSE and version != 'idle_loop_v7' else .92
CAM_YAW = -40         # sprite three-quarter view; Sora faces screen right
OUT.mkdir(parents=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = 512
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.render.use_freestyle = True
scene.render.line_thickness_mode = 'ABSOLUTE'
scene.render.line_thickness = 1.0
# Heavy outer contour plus faint interior silhouettes: dense interior lines on the low-poly rip
# darkened the whole figure in v1-v3.
freestyle = bpy.context.view_layer.freestyle_settings
for lineset in tuple(freestyle.linesets):
    freestyle.linesets.remove(lineset)
for name, contour, thickness, alpha in (('outer_contour', True, 1.6, 1.0), ('interior_lines', False, .6, .45)):
    lineset = freestyle.linesets.new(name)
    lineset.select_by_edge_types = True
    lineset.select_silhouette = not contour
    lineset.select_border = lineset.select_crease = False
    lineset.select_external_contour = contour
    lineset.linestyle = bpy.data.linestyles.new(name)
    lineset.linestyle.color = (.06, .04, .05)
    lineset.linestyle.thickness = thickness
    lineset.linestyle.alpha = alpha


def update():
    bpy.context.view_layer.update()


def world_bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


# 1. Sora: import and normalize height.
if SHEET_MODEL:
    sheet_rig = 'character_blockout_v8' if OUT_NAME in ('sheet_battle_v1', 'sheet_battle_v2') else 'character_blockout_v9'
    with bpy.data.libraries.load(str(SORA / sheet_rig / 'sora_character_blockout.blend')) as (src, dst):
        dst.objects = list(src.objects)
    for o in dst.objects:
        if o.type != 'CAMERA':
            scene.collection.objects.link(o)
    # Appended objects' matrix_world is stale until updated (sheet_battle_v1 measured 2.57 m).
    bpy.context.view_layer.update()
else:
    bpy.ops.import_scene.fbx(filepath=str(SORA / 'downloads/p_ex150.fbx'))
arm = next(o for o in scene.objects if o.type == 'ARMATURE')
body = [o for o in scene.objects if o.type == 'MESH']
if SHEET_MODEL:
    # Hand/finger maths reads evaluated vertices by original index; keep subdivision render-only.
    for o in body:
        for mod in o.modifiers:
            if mod.type == 'SUBSURF':
                mod.show_viewport = False
# The rip stores faces as separate strips; weld coincident vertices (UVs and weights are kept).
for o in ([] if SHEET_MODEL else body):
    bm = bmesh.new(); bm.from_mesh(o.data)
    size = max(o.dimensions) / max(max(o.matrix_world.to_scale()), 1e-12)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=size*1e-4)
    bm.to_mesh(o.data); bm.free()
lo, hi = world_bounds(body)
arm.scale *= HEIGHT / (hi.z - lo.z)
update()

# 2. Kingdom Key: re-center its mesh on the grip, local +Z toward the tip, +X toward the teeth.
before = set(scene.objects)
bpy.ops.wm.obj_import(filepath=str(SORA / 'downloads/Kingdom Key/Kingdom Key.obj'))
key_parts = [o for o in scene.objects if o not in before and o.type == 'MESH']
if len(key_parts) > 1:
    bpy.ops.object.select_all(action='DESELECT')
    for o in key_parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = key_parts[0]
    bpy.ops.object.join()
key = key_parts[0]; key.name = 'Kingdom_Key'
bpy.context.view_layer.objects.active = key
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
co = np.array([v.co[:] for v in key.data.vertices])
axis = int(np.argmax(co.max(0) - co.min(0)))           # length axis
side = 0 if axis != 0 else 1                             # guard/teeth width axis (largest other span)
others = [i for i in range(3) if i != axis]
side = max(others, key=lambda i: co[:, i].max() - co[:, i].min())
bins = np.linspace(co[:, axis].min(), co[:, axis].max(), 21)
idx = np.clip(np.digitize(co[:, axis], bins) - 1, 0, 19)
spans = [np.ptp(co[idx == b, side]) if np.any(idx == b) else 0 for b in range(20)]
guard_bin = int(np.argmax(spans))
grip = co[idx == guard_bin].mean(0)
tip_end = co[:, axis].max() if abs(co[:, axis].max() - grip[axis]) > abs(co[:, axis].min() - grip[axis]) else co[:, axis].min()
tip_sign = 1 if tip_end > grip[axis] else -1
tip_bins = [b for b in range(20) if np.any(idx == b) and (bins[b] - grip[axis])*tip_sign > .8*abs(tip_end - grip[axis])]
teeth_offset = np.mean([co[idx == b, side].mean() for b in tip_bins]) - grip[side]
local_z = Vector([tip_sign if i == axis else 0 for i in range(3)])
local_x = Vector([math.copysign(1, teeth_offset) if i == side else 0 for i in range(3)])
local_y = local_z.cross(local_x)
basis = Matrix((local_x, local_y, local_z))             # rows: new axes in old coordinates
reach = abs(tip_end - grip[axis])
recenter = Matrix.Diagonal((KEY_REACH/reach,)*3).to_4x4() @ basis.to_4x4() @ Matrix.Translation(-Vector(grip))
key.data.transform(recenter)
key.data.update()
# The rip lays the loose keychain links in a straight row past the pommel; drop those islands.
bm = bmesh.new(); bm.from_mesh(key.data)
islands, seen = [], set()
for v in bm.verts:
    if v.index in seen:
        continue
    stack, island = [v], []
    seen.add(v.index)
    while stack:
        cur = stack.pop(); island.append(cur)
        for e in cur.link_edges:
            other = e.other_vert(cur)
            if other.index not in seen:
                seen.add(other.index); stack.append(other)
    islands.append(island)
chain = [v for island in islands if sum(v.co.z for v in island)/len(island) < -.12*KEY_REACH for v in island]
bmesh.ops.delete(bm, geom=chain, context='VERTS')
bm.to_mesh(key.data); bm.free()

# 3. Cel materials from the original textures (two-tone ramp, light from upper screen-left).
t = math.radians(CAM_YAW)
to_cam = Vector((math.sin(t), -math.cos(t), 0))
screen_left = Vector((-math.cos(t), -math.sin(t), 0))
LIGHT = (to_cam*.8 + screen_left*.25 + Vector((0, 0, .55))).normalized()  # front-lit face like the idle art
for mat in {s.material for o in body + [key] for s in o.material_slots if s.material}:
    old = next((n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None) if mat.node_tree else None
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    emit = nodes.new('ShaderNodeEmission')
    normal = nodes.new('ShaderNodeNewGeometry')
    dot = nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = LIGHT
    ramp = nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].color = (.74, .72, .78, 1)
    ramp.color_ramp.elements[1].position = .3; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    shade = nodes.new('ShaderNodeMix'); shade.data_type = 'RGBA'; shade.blend_type = 'MULTIPLY'
    shade.inputs['Factor'].default_value = 1
    links.new(normal.outputs['Normal'], dot.inputs[0])
    links.new(dot.outputs['Value'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], shade.inputs['B'])
    if old:
        tex = nodes.new('ShaderNodeTexImage'); tex.image = old
        links.new(tex.outputs['Color'], shade.inputs['A'])
    else:
        shade.inputs['A'].default_value = (*mat.diffuse_color[:3], 1)
    links.new(shade.outputs['Result'], emit.inputs['Color'])
    if old and old.channels == 4:
        clear = nodes.new('ShaderNodeBsdfTransparent'); mix = nodes.new('ShaderNodeMixShader')
        links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
        links.new(clear.outputs[0], mix.inputs[1]); links.new(emit.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], out.inputs['Surface'])
    else:
        links.new(emit.outputs[0], out.inputs['Surface'])

# 4. Approximate approved-idle pose from hand/foot targets (world meters).
if BATTLE:
    # Targets are in the body frame turned 30 degrees toward the opponent (screen right).
    # Left foot leads, right foot back and turned out; deeper knees; Key low at the right hip
    # angled down and back (away from the opponent); left hand up as a guard.
    POSE = {
        'body_turn_deg': 30, 'drop': .17, 'lean_deg': 14, 'hunch_deg': 10, 'neck_counter_deg': -18,
        'look_deg': 12,
        'R_foot': (-.22, .24, None), 'L_foot': (.16, -.30, None), 'toe_deg': {'L': 10, 'R': 50},
        'R_hand': (-.24, .02, .74), 'blade_dir': (-.25, .75, -.62),
        'blade_toward': (-.30, .95), 'tip_height': .20, 'grip_shift': .05,
        'L_relaxed_wrist': (.06, -.30, .98), 'L_elbow_hint': (1, .3, -.6),
        'shoulder_reach': True, 'L_hand_along_handle': 0,
    }
    if version != 'battle_v1':
        # v2+: v1's guard arm reached out nearly straight; bend the elbow and hold it nearer the chest.
        POSE.update({'L_relaxed_wrist': (.10, -.20, 1.00), 'L_elbow_hint': (1, .2, -1)})
    if version not in ('battle_v1', 'battle_v2'):
        # v3+: Kvon's reference (design/references/sora_kh2_pose_sheet.png, top right): a low, wide
        # guard crouch facing nearly forward, hunched, Key in the right fist at the hip with the blade
        # swung out level to his right side (tip slightly up), left arm hanging by the thigh.
        POSE = {
            'body_turn_deg': 10, 'drop': .22, 'lean_deg': 16, 'hunch_deg': 12, 'neck_counter_deg': -22,
            'look_deg': 8,
            'R_foot': (-.46, .04, None), 'L_foot': (.46, .00, None), 'toe_deg': {'L': 30, 'R': 30},
            'R_hand': (-.14, -.20, .66), 'blade_dir': (-.95, .05, .25), 'grip_shift': .05,
            'L_relaxed_wrist': (.30, -.14, .62), 'L_elbow_hint': (1, .3, 0),
            'shoulder_reach': True, 'L_hand_along_handle': 0,
        }
    if TWO_HAND_BATTLE:
        # v4+: the same reference pose MIRRORED, copied closely. Both fists sit on the handle low
        # between the thighs, slightly to his left; the blade runs level out to his left (tip a
        # little up); very wide deep squat, toes out; hunched, head down and turned to his left.
        # The right fist is the pommel-side hand; the left fist sits beside it toward the guard.
        POSE = {
            'body_turn_deg': 0, 'drop': .26, 'lean_deg': 16, 'hunch_deg': 12, 'neck_counter_deg': -10,
            'look_deg': 18, 'head_tilt_deg': -4,
            'R_foot': (-.50, .02, None), 'L_foot': (.50, .00, None), 'toe_deg': {'L': 35, 'R': 35},
            'R_hand': (.03, -.22, .60), 'L_hand_along_handle': .075, 'grip_shift': 0,
            'blade_dir': (.95, -.05, .22), 'shoulder_reach': True,
        }
        if version != 'battle_v4':
            # v5+: side-by-side with the mirrored drawing: hips higher, feet a bit wider,
            # blade rising a little more.
            POSE.update({'drop': .19, 'R_foot': (-.56, .02, None), 'L_foot': (.56, .00, None),
                         'R_hand': (.03, -.22, .66), 'blade_dir': (.93, -.05, .30)})
        if version not in ('battle_v4', 'battle_v5'):
            # v6+ (user): stand at the drawing's angle in the sprite view. The camera sits at yaw -40;
            # turning the body -25 degrees faces him nearly at the camera, turned slightly toward
            # screen right, as drawn. The blade turns with the body.
            POSE.update({'body_turn_deg': -25, 'turn_blade': True})
        if version not in ('battle_v4', 'battle_v5', 'battle_v6'):
            # v7+ (user): match the drawing's Keyblade angle as seen by the sprite camera. Measured
            # from the drawing: blade rises ~20 degrees on screen and looks 0.57 of his height
            # (v6: 0.71), so it is foreshortened ~37 degrees toward the viewer.
            POSE.update({'turn_blade': False, 'screen_blade': (20, 37)})
        if version not in ('battle_v4', 'battle_v5', 'battle_v6', 'battle_v7'):
            # v8+ (user): legs a little closer together; left fist nearer the right one on the handle.
            POSE.update({'R_foot': (-.46, .02, None), 'L_foot': (.46, .00, None), 'L_hand_along_handle': .06})
        if version not in ('battle_v4', 'battle_v5', 'battle_v6', 'battle_v7', 'battle_v8'):
            # v9+ (user): both hands must grab the handle; shift the grip until the left fist reaches.
            POSE['auto_reach'] = True
        if version not in ('battle_v4', 'battle_v5', 'battle_v6', 'battle_v7', 'battle_v8', 'battle_v9'):
            # v10+ (user): turn the left wrist (the one not anchoring the Key) so its palm faces the screen.
            POSE['L_palm_to_camera'] = True
        if version not in ('battle_v4', 'battle_v5', 'battle_v6', 'battle_v7', 'battle_v8', 'battle_v9', 'battle_v10'):
            POSE['L_palm_back_deg'] = 25 if version == 'battle_v11' else 45  # v11: slightly back; v12+: a little more
elif ONE_HAND:
    # Right hand low at his side, blade down and slightly forward toward his right foot;
    # left arm relaxed. Stance and hunch carried over from idle_loop_v11+.
    POSE = {
        'drop': .12, 'lean_deg': 12, 'hunch_deg': 10, 'neck_counter_deg': -16,
        'R_hand': (-.24, -.12, .80), 'L_relaxed_wrist': (.24, -.06, .80),
        'R_foot': (-.40, .02, None), 'L_foot': (.40, .02, None),
        'blade_dir': (-.18, -.30, -.94), 'toe_out_deg': 25, 'head_tilt_deg': 5,
        'shoulder_reach': True, 'grip_shift': .05, 'L_hand_along_handle': 0,
    }
    if version != 'one_hand_v1':
        # v2+: hand at the hip; blade tilt solved from the real grip so the tip angles out toward
        # his right foot and stops just above the floor (v1 stood vertical and dipped below it).
        POSE.update({'R_hand': (-.24, -.10, .74), 'blade_toward': (-.6, -.8),
                     'tip_height': .05 if version == 'one_hand_v2' else .10})  # v3: teeth clear the floor
elif REF_POSE and version == 'idle_loop_v7':
    # v7: Kvon's Smash idle reference (design/references/sora_smash_idle_pose_reference.png).
    # Wide stance with mild knee bend and toes out, upright torso, both hands low in front of the
    # waist, blade sweeping up and out past his right shoulder at a flat angle.
    POSE = {
        'drop': .10, 'lean_deg': 4,
        'R_hand': (-.05, -.24, .74), 'L_hand_along_handle': -.075,
        'R_foot': (-.40, .02, None), 'L_foot': (.40, .02, None),
        'blade_dir': (-.80, .30, .52), 'toe_out_deg': 25, 'head_tilt_deg': 5,
    }
elif REF_POSE and version not in ('idle_loop_v7', 'idle_loop_v8', 'idle_loop_v9', 'idle_loop_v10'):
    # v11+ (user note): a little stronger hunch; shoulders reach forward so both hands hold the handle.
    POSE = {
        'drop': .12, 'lean_deg': 12, 'hunch_deg': 10, 'neck_counter_deg': -16,
        'R_hand': (-.11, -.20, .71), 'L_hand_along_handle': -.075,
        'R_foot': (-.40, .02, None), 'L_foot': (.40, .02, None),
        'blade_dir': (-.80, .30, .70), 'toe_out_deg': 25, 'head_tilt_deg': 5,
        'shoulder_reach': True,
    }
    if version not in ('idle_loop_v11', 'idle_loop_v12'):
        POSE['grip_shift'] = .11 if PALM_ORIENT else .05  # v13: .05; v14+ slides hands further up
elif REF_POSE and version == 'idle_loop_v10':
    # v10: v9's hunch and bent elbows, grip lowered back to waist height like the reference.
    POSE = {
        'drop': .11, 'lean_deg': 9, 'hunch_deg': 7, 'neck_counter_deg': -10,
        'R_hand': (-.11, -.18, .72), 'L_hand_along_handle': -.075,
        'R_foot': (-.40, .02, None), 'L_foot': (.40, .02, None),
        'blade_dir': (-.80, .30, .70), 'toe_out_deg': 25, 'head_tilt_deg': 5,
    }
elif REF_POSE and version == 'idle_loop_v9':
    # v9 (user note): hunch over a little and bend the elbows to hold the Keyblade.
    # Lower spine and chest lean forward, the neck counters so he still looks ahead, and the
    # grip comes in toward the body so the arms no longer reach straight.
    POSE = {
        'drop': .11, 'lean_deg': 9, 'hunch_deg': 7, 'neck_counter_deg': -10,
        'R_hand': (-.11, -.17, .78), 'L_hand_along_handle': -.075,
        'R_foot': (-.40, .02, None), 'L_foot': (.40, .02, None),
        'blade_dir': (-.80, .30, .70), 'toe_out_deg': 25, 'head_tilt_deg': 5,
    }
elif REF_POSE:
    # v8: grip shifted to his right side and the blade steepened to match the reference.
    POSE = {
        'drop': .10, 'lean_deg': 4,
        'R_hand': (-.12, -.24, .74), 'L_hand_along_handle': -.075,
        'R_foot': (-.40, .02, None), 'L_foot': (.40, .02, None),
        'blade_dir': (-.80, .30, .70), 'toe_out_deg': 25, 'head_tilt_deg': 5,
    }
elif LOOP:
    # Refined toward the approved idle: deeper, wider crouch; grip lower and further forward;
    # flatter blade; left hand placed on the handle by measuring its weapon socket.
    POSE = {
        'drop': .20, 'lean_deg': 10,
        'R_hand': (-.02, -.26, .70), 'L_hand_along_handle': -.07,
        'R_foot': (-.40, .10, None), 'L_foot': (.38, -.08, None),
        'blade_dir': (-.25, .75, .55),
    }
elif not LOOP:
    POSE = {
        'drop': .15, 'lean_deg': 8,
        'R_hand': (-.04, -.24, .74), 'L_hand_along_handle': -.08,
        'R_foot': (-.36, .10, None), 'L_foot': (.34, -.08, None),
        'blade_dir': (-.25, .70, .67),
    }
if LOOP:
    # Breathing: body sinks and leans slightly at the exhale peak; feet stay planted.
    BREATH = {'drop': .012, 'lean_deg': 1.5, 'hands_z': -.008, 'head_counter_deg': -.8}
    DURATIONS_MS = [150, 130, 130, 150, 180, 150, 130, 130, 150, 180]  # approved idle timing
    BREATH_LAG = 0 if version == 'idle_loop_v2' else .12  # fraction of a cycle
    if BATTLE:
        # Combat bounce: a quicker, deeper bob through the knees instead of a slow breath.
        BREATH = {'drop': .025, 'lean_deg': 1.0, 'hands_z': -.012, 'head_counter_deg': -.5}
        DURATIONS_MS = [100, 90, 90, 100, 120, 100, 90, 90, 100, 120]
    if GAIT:
        # Two steps per cycle: the body bobs twice (handled in the loop), 10 frames x 80 ms.
        BREATH = {'drop': .02, 'lean_deg': .8, 'hands_z': -.01, 'head_counter_deg': -.4}
        DURATIONS_MS = [80]*10 if GAIT.endswith('_v1') else [65]*10  # v2+: a little faster
        # v3+ (Kvon): shuffle step. The front foot steps out (feet spread to the idle width), then the
        # back foot closes up (feet come together); one shoulder bounce per cycle instead of per step.
        SHUFFLE = not GAIT.endswith(('_v1', '_v2'))
        if SHUFFLE:
            STEP_LEN, NARROW, LIFT = .34, .56, .06  # metres: step, closed spacing, foot lift
            DURATIONS_MS = [55]*10  # 0.34 m per 0.55 s = 0.62 m/s, about the v2 speed
        # v4+ (Kvon, "Do all suggestions"): keyed shimmy. Weight shifts over the front foot before
        # the back foot moves; back heel lifts and pushes off from the toes; back foot arcs high
        # and lands toe-first; uneven step/hold rhythm; per-frame root motion for the game; body
        # dips on the front-foot landing and rises as the back foot passes.
        STEPPED = SHUFFLE and not GAIT.endswith('_v3')
        if STEPPED:
            # Along the walk axis (m, world): lead, lead lift, back, back lift, back heel-up deg,
            # body (hips), bob (+ dips, - rises), frame ms.
            STEP_KEYS = [
                (.56, .00, .00, .00, 0, .280, .00, 70),   # settled
                (.64, .07, .00, .00, 0, .295, .15, 55),   # front foot lifts
                (.82, .08, .00, .00, 0, .315, .30, 55),   # front foot reaches
                (.90, .00, .00, .00, 0, .340, 1.0, 70),   # front foot lands, body absorbs
                (.90, .00, .00, .00, 20, .430, .60, 70),  # weight over front foot, back heel up
                (.90, .00, .05, .05, 35, .480, .20, 50),  # back foot pushes off the toes
                (.90, .00, .20, .12, 10, .530, -.40, 50), # back foot arcs high, body rises
                (.90, .00, .33, .02, 15, .590, .00, 60),  # back foot lands toe-first
                (.90, .00, .34, .00, 0, .620, .15, 70),   # settle (body = start + one step)
            ]
            DURATIONS_MS = [k[7] for k in STEP_KEYS]
            # v6+ (Kvon): the back knee moves in toward the middle of the torso as the foot swings,
            # peaking at the arc, then returns to its original outward position.
            BACK_KNEE_IN = ([0]*9 if GAIT.endswith(('_v4', '_v5'))
                            else [0, 0, 0, 0, .3, .7, 1.0, .5, 0])
            # v7+ (Kvon): the foot moves toward the torso with the knee: it is pulled in toward the
            # midline by the same profile, and tucks higher and further under him at the arc.
            FOOT_IN = 0 if GAIT.endswith(('_v4', '_v5', '_v6')) else .7
            if FOOT_IN and GAIT.endswith('_v7'):
                STEP_KEYS[6] = (.90, .00, .26, .16, 10, .530, -.40, 50)
            elif FOOT_IN:
                # v8+: on screen "toward the torso" means forward and up under his hips: the back foot
                # tucks under him at the arc, then reaches back out to its landing spot.
                STEP_KEYS[5] = (.90, .00, .14, .09, 35, .480, .20, 50)
                STEP_KEYS[6] = (.90, .00, .42, .18, 10, .530, -.40, 50)
                STEP_KEYS[7] = (.90, .00, .37, .04, 15, .590, .00, 60)
            LEAD_KNEE_IN = [0]*len(STEP_KEYS)
            if not GAIT.endswith(('_v4', '_v5', '_v6', '_v7', '_v8')):
                # v9+: from Kvon's walking video (design/references/walking/). Feet come nearly
                # together under the hips (knees almost touching, legs straighter, body up), the front
                # foot steps far out to a wide stance (knees bent, body down) and holds, then the back
                # foot skims in low beside it with the knee travelling inward; holds at both ends.
                NARROW, STEP_LEN, FOOT_IN = .30, .50, 0
                BREATH['drop'] = .04  # bob -1 = up (narrow), +1 = down (wide)
                STEP_KEYS = [
                    (.30, .00, .00, .00, 0, .150, -1.0, 70),  # narrow hold, body up
                    (.36, .02, .00, .00, 0, .180, -.60, 60),  # front foot starts out
                    (.52, .03, .00, .00, 0, .250, -.10, 60),
                    (.70, .02, .00, .00, 0, .330, .50, 60),
                    (.80, .00, .00, .00, 0, .380, 1.0, 70),   # front foot lands wide, body down
                    (.80, .00, .00, .00, 0, .420, 1.0, 80),   # wide hold
                    (.80, .00, .00, .00, 15, .470, .80, 60),  # back heel lifts
                    (.80, .00, .10, .02, 10, .520, .40, 60),  # back foot skims in, knee inward
                    (.80, .00, .28, .03, 5, .580, -.20, 60),
                    (.80, .00, .44, .02, 0, .620, -.70, 60),
                    (.80, .00, .50, .00, 0, .650, -1.0, 70),  # back foot lands beside it, body up
                    (.80, .00, .50, .00, 0, .650, -1.0, 60),  # narrow hold
                ]
                BACK_KNEE_IN = [0, 0, 0, 0, 0, 0, .3, .7, 1.0, .7, .3, .1]
                LEAD_KNEE_IN = [.3, .5, .4, .2, 0, 0, 0, 0, 0, 0, 0, .2]
                if not GAIT.endswith('_v9'):
                    # v10+ (Kvon): no pause between cycles: the duplicate closing hold is dropped and the
                    # body keeps moving through the feet-together pose. Frames are held for whole 60 fps
                    # game frames (last field), 46 per cycle.
                    STEP_KEYS = [
                        (.30, .00, .00, .00, 0, .155, -1.0, 4),
                        (.36, .02, .00, .00, 0, .190, -.60, 4),
                        (.52, .03, .00, .00, 0, .255, -.10, 4),
                        (.70, .02, .00, .00, 0, .330, .50, 4),
                        (.80, .00, .00, .00, 0, .380, 1.0, 5),
                        (.80, .00, .00, .00, 0, .425, 1.0, 5),
                        (.80, .00, .00, .00, 15, .470, .80, 4),
                        (.80, .00, .10, .02, 10, .520, .40, 4),
                        (.80, .00, .28, .03, 5, .575, -.20, 4),
                        (.80, .00, .44, .02, 0, .615, -.70, 4),
                        (.80, .00, .50, .00, 0, .640, -1.0, 4),
                    ]
                    if not GAIT.endswith('_v10'):
                        # v11+ (Kvon, option A): slightly faster: the travelling drawings drop to 3 game
                        # frames, holds stay at 4; 40 frames per cycle (0.67 s), ~135 px/s.
                        STEP_KEYS = [(*k[:7], n) for k, n in zip(STEP_KEYS, [4, 3, 3, 4, 4, 4, 4, 3, 3, 4, 4])]
                    GAME_FRAMES = [k[7] for k in STEP_KEYS]
                    STEP_KEYS = [(*k[:7], round(k[7]*1000/60, 3)) for k in STEP_KEYS]
                    BACK_KNEE_IN = BACK_KNEE_IN[:11]
                    LEAD_KNEE_IN = [.3, .5, .4, .2, 0, 0, 0, 0, 0, 0, .2]
                DURATIONS_MS = [k[7] for k in STEP_KEYS]
                V12 = not GAIT.endswith(('_v9', '_v10', '_v11'))
                # v18+ (Kvon's idle-to-walk + grounded walk spec, Goku reference): deeper and wider crouch,
                # splayed knees, low shuffle, 65 px per cycle, pitch/roll sway, weapon vertical lag.
                # 'walk_fwd_v18t' is the 4-frame idle-to-walk transition into it.
                V18 = V12 and not GAIT.endswith(tuple(f'_v{n_}' for n_ in range(12, 18)))
                # 'walk_fwd_v18b' is the matching 4-frame brake back into the idle (same blend, reversed).
                # 'walk_fwd_v18w' brakes from the wide-stance contact (walk drawing 5) instead.
                BRAKE_WIDE = V18 and GAIT.endswith('w')
                BRAKE = V18 and (GAIT.endswith('b') or BRAKE_WIDE)
                TRANSITION = V18 and (GAIT.endswith('t') or BRAKE)
                if V12:
                    # v12+ (Kvon's walk spec): constant root velocity, exactly 90 game px per 40-frame cycle
                    # (2.25 px per game frame, 135 px/s); step length matched so planted feet stay exact.
                    RENDER_PX_PER_M = 385 / HEIGHT            # 512 px render: ortho_scale = HEIGHT*512/385
                    GAME_PX_PER_M = RENDER_PX_PER_M*384/512
                    STEP_LEN = (65 if V18 else 90) / GAME_PX_PER_M
                    k_scale = STEP_LEN / .50
                    NARROW0 = .68 if V18 else .30      # v18: feet stay wide even when closest (legs still reach)
                    if V18 and GAIT.startswith('walk_back'):
                        NARROW0 = .62  # the backward-reaching planted leg ran out of reach at .68 (foot lifted 5 px)
                    if V18 and not GAIT.endswith(('_v18', '_v18t', '_v18b', '_v18w')):
                        NARROW0 = .58  # v19 (Goku style): the sideways weight shift locked the trailing leg at .68
                    # Retreat: the hips sat over the trailing foot and the leading leg locked straight; centre
                    # the stance under the hips by shifting both feet toward the travel direction.
                    STANCE_SHIFT = -.08 if V18 and GAIT.startswith('walk_back') else 0.0  # +.06 locked the leg further
                    LIFT_CAP = .01 if V18 else 1.0     # v18: stepping foot barely clears the floor
                    # Pelvis drops 6 render px on the passing poses (3, 9) and is at default on contacts.
                    PASSING = [0, .5, 1, .5, 0, 0, 0, .5, 1, .5, 0]
                    keys, cum = [], 0
                    for idx, (k, f) in enumerate(zip(STEP_KEYS, GAME_FRAMES)):
                        cum += f if idx else 0
                        keys.append((NARROW0 + (k[0] - .30)*k_scale, min(k[1], LIFT_CAP), k[2]*k_scale,
                                     min(k[3], LIFT_CAP), k[4], .155 + STEP_LEN*cum/40, PASSING[idx], k[7]))
                    STEP_KEYS = keys
                    NARROW = NARROW0
                    drop = 6 / RENDER_PX_PER_M
                    BREATH.update({'drop': drop, 'lean_deg': 0, 'hands_z': -drop, 'head_counter_deg': 0})
                    # Weapon drag: -8 deg about the vertical at the passing poses (grip follows the handle).
                    WEAPON_DRAG = [-8*w for w in PASSING]
                    # Front arm: abduct 12-15 deg about the shoulder-wrist line, keeping 10-12 px forearm gap.
                    FRONT_ARM_RANGE, FRONT_ARM_GAP = (12.0, 15.0), (10.0, 12.0)
                    if V18:
                        CROUCH_EXTRA, WIDTH_SCALE, KNEE_SPLAY = .12, 1.2, .8
                        CONTACT = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]
                        # 3.5 deg extra forward pitch on contacts, easing to 0 on passing frames.
                        PITCH = [3.5*(1 - p_) for p_ in PASSING]
                        # walk_back_v18*: Gemini's retreat spec (relayed by Kvon): defensive posture with a slight
                        # backward pitch, toe-first plants on the backward steps, Keyblade 2.5 cm nearer the chest.
                        BACK = GAIT.startswith('walk_back')
                        LEAD_TOE = [0]*len(PASSING)
                        GUARD_IN = 0.0
                        ROLL_DEG = 2.0
                        # walk_fwd_v19+ (Gemini's Goku comparison, relayed by Kvon): inverted bounce (high with feet
                        # together, 7 cm low at the wide contacts), 7 cm stomping arcs, deeper hunch with a spine twist
                        # toward the stepping leg, shrugged shoulders, head locked forward, tighter weapon carry.
                        if BACK:
                            PITCH = [-1.5]*len(PASSING)
                            # Stepping foot lands toe first and rolls to the heel (lead lands on 3-4, trail on 9-10).
                            LEAD_TOE = [0, 6, 12, 8, 0, 0, 0, 0, 0, 0, 0]
                            GUARD_IN = .025
                        # Weapon lags: +5 cm when the pelvis drops (passing), -3 cm when the body rises (contact).
                        HANDS_EXTRA = [.05*p_ - .03*c_ for p_, c_ in zip(PASSING, CONTACT)]
                        # Chest roll 2 deg toward the weight-bearing leg (F = trailing foot, L = leading foot).
                        ROLL = [('F', .3), ('F', 1), ('F', 1), ('F', .5), ('L', .5), ('L', .8), ('L', 1),
                                ('L', 1), ('L', 1), ('L', .5), ('F', .3)]
                        GOKU = not GAIT.endswith(('_v18', '_v18t', '_v18b', '_v18w'))
                        if GOKU:
                            GBOB = [0, .25, .6, .9, 1, 1, .9, .6, .3, .1, 0]       # 1 = lowest (wide contacts)
                            BREATH.update({'drop': .07, 'hands_z': -.07})
                            HANDS_EXTRA = [.06*b_ - .04*(1 - b_) for b_ in GBOB]
                            PITCH = [0]*len(GBOB)                                   # static hunch instead
                            ROLL_DEG = 6.0
                            # Twist weight: +1 = lead-side shoulder forward (lead foot planting), -1 = trail side.
                            TWIST_W = [-1, -.6, 0, .6, 1, 1, .6, 0, -.6, -1, -1]
                            TWIST_DEG, SHRUG_DEG, CENTER_SHIFT = 12.5, 8.0, .025
                            GUARD_IN = .045
                            # Stomp: 7 cm arcs that drop fast; lead swings on 1-3, trail on 7-9.
                            STOMP = {1: (.05, 0), 2: (.07, 0), 3: (.03, 0), 7: (0, .05), 8: (0, .07), 9: (0, .03)}
                            STEP_KEYS = [(k_[0], STOMP.get(ix, (k_[1], k_[3]))[0], k_[2], STOMP.get(ix, (k_[1], k_[3]))[1],
                                          k_[4], k_[5], GBOB[ix], k_[7]) for ix, k_ in enumerate(STEP_KEYS)]
                            G_HUNCH, G_LEAN, G_NECK = (3, 8, -10.0) if BACK else (5, 11, -13.5)
                            if BACK:
                                # Retreat (Gemini round 3): lighter hunch, softer 4 cm arcs, toe-first plants.
                                STEP_KEYS = [(k_[0], k_[1]*.6, k_[2], k_[3]*.6, *k_[4:]) for k_ in STEP_KEYS]
                                PITCH = [0]*len(GBOB)
                        if TRANSITION:
                            # 4 drawings x 3 game frames easing from the battle idle into walk drawing 1.
                            TRANS_T = [u_*u_*(3 - 2*u_) for u_ in (.2, .4, .6, .8)]
                            if BRAKE:
                                TRANS_T = TRANS_T[::-1]  # walk contact pose -> battle idle
                            GAME_FRAMES = [3, 3, 3, 3]
                            DURATIONS_MS = [50.0]*4
        STRIDE, LIFT, SWING = .12, .06, .4  # half step length (m), foot lift (m), swing share of cycle
        if IDLE_SHUFFLE:
            SHUFFLE = STEPPED = False
            # (lead fraction, lead lift m, back fraction, back lift m, game frames); 30 frames per cycle.
            # v1 used a 0.28 m step: from the already-wide idle stance both legs locked straight.
            SH_STEP, SH_DIP = (.28, 0) if GAIT.endswith('_v1') else (.22, .03)
            SH_KEYS = [(0, 0, 0, 0, 5), (.25, .012, 0, 0, 4), (.7, .018, 0, 0, 4), (1, 0, 0, 0, 5),
                       (1, 0, .3, .012, 4), (1, 0, .75, .018, 4), (1, 0, .95, .004, 4)]
            if not GAIT.endswith('_v1'):
                SH_KEYS = [(*k[:4], 4) for k in SH_KEYS]  # 28 frames per cycle
            if not GAIT.endswith(('_v1', '_v2')):
                # v3+ (Kvon: too slow, not enough distance): longer 0.30 m step with a deeper hip dip so
                # the legs still reach, and quicker 3-frame holds (4 on the landing): 22 frames per cycle.
                SH_STEP, SH_DIP = .30, .075  # .06 left both legs fully straight at the widest point
                SH_KEYS = [(*k[:4], f) for k, f in zip(SH_KEYS, [3, 3, 3, 4, 3, 3, 3])]
            if not GAIT.endswith(('_v1', '_v2', '_v3')):
                # v4+ (Gemini's speed suggestions only, per Kvon): ~75 px per step (75 / 180.5 px per m) in
                # 18 game frames; the hip dip grows only as far as the longer step needs to keep the knees bent.
                SH_STEP, SH_DIP = 75 / 180.5, SH_DIP_V4
                SH_KEYS = [(*k[:4], f) for k, f in zip(SH_KEYS, [3, 2, 2, 4, 2, 2, 3])]
            if not GAIT.endswith(('_v1', '_v2', '_v3', '_v4')):
                # v5+ (Kvon: a middle point between v3 and v4): ~64.5 px per step in 20 game frames.
                SH_STEP = 64.5 / 180.5
                SH_KEYS = [(*k[:4], f) for k, f in zip(SH_KEYS, [3, 3, 2, 4, 2, 3, 3])]
                # Same breathing settings as the battle idle, frozen at its first frame, so drawing 1
                # matches the idle exactly.
                BREATH = {'drop': .025, 'lean_deg': 1.0, 'hands_z': -.012, 'head_counter_deg': -.5}
            GAME_FRAMES = [k[4] for k in SH_KEYS]
            DURATIONS_MS = [round(f*1000/60, 3) for f in GAME_FRAMES]
V18 = globals().get('V18', False)
TRANSITION = globals().get('TRANSITION', False)
bones = arm.data.bones
for name in ('L_ashi1', 'R_ashi1'):
    bones[name].use_inherit_rotation = False   # feet stay flat while the legs bend


def pose_world(name):
    return arm.matrix_world @ arm.pose.bones[name].matrix


def set_pose_world(name, matrix):
    arm.pose.bones[name].matrix = arm.matrix_world.inverted() @ matrix
    update()


def rotate_world(name, axis, degrees):
    m = pose_world(name); pivot = m.translation.copy()
    r = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(degrees), 4, axis) @ Matrix.Translation(-pivot)
    set_pose_world(name, r @ m)


def aim(name, child, target):
    # Swing bone `name` about its head so the head of `child` points at `target`.
    m = pose_world(name); head = m.translation.copy()
    turn = (pose_world(child).translation - head).rotation_difference(Vector(target) - head)
    set_pose_world(name, Matrix.Translation(head) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-head) @ m)


def two_bone(upper, lower, end, target, bend_hint):
    # Analytic two-bone solve: the middle joint bends toward bend_hint (v1's IK poles twisted the legs).
    h = pose_world(upper).translation.copy()
    l1 = (pose_world(lower).translation - h).length
    l2 = (pose_world(end).translation - pose_world(lower).translation).length
    d = Vector(target) - h; dist = min(d.length, (l1 + l2)*.999); dn = d.normalized()
    along = (l1*l1 - l2*l2 + dist*dist) / (2*dist)
    hint = Vector(bend_hint); perp = (hint - dn*hint.dot(dn)).normalized()
    aim(upper, lower, h + dn*along + perp*math.sqrt(max(l1*l1 - along*along, 0)))
    aim(lower, end, h + dn*dist)


def reset_pose():
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
        pb.rotation_quaternion = (1, 0, 0, 0); pb.rotation_euler = (0, 0, 0)
    update()


def hand_on(side, grip, bend_hint):
    # Place the hand so its weapon socket (buki), or the palm from v4, lands on the grip point.
    def place_wrist(passes):
        wrist = Vector(grip)
        for _ in range(passes):
            two_bone(f'{side}_ude1', f'{side}_ude2', f'{side}_te', wrist, bend_hint)
            if not LOOP:
                return
            wrist += Vector(grip) - hand_point(side)

    place_wrist(3 if LOOP else 1)
    # v16+: the twisted front shoulder must not swing back toward the grip (it undid the twist).
    no_reach = POSE.get('no_reach_side') == side
    for _ in range(4 if POSE.get('shoulder_reach') and not no_reach else 0):
        miss = Vector(grip) - hand_point(side)
        if miss.length <= .01:
            break
        # Still out of the arm's reach: swing the shoulder (kata) toward the grip, max 20 deg a step.
        head = pose_world(f'{side}_kata').translation
        arm_root = pose_world(f'{side}_ude1').translation
        turn = (arm_root - head).rotation_difference(arm_root + miss - head)
        if turn.angle > math.radians(20):
            turn = Quaternion(turn.axis, math.radians(20))
        set_pose_world(f'{side}_kata', Matrix.Translation(head) @ turn.to_matrix().to_4x4()
                       @ Matrix.Translation(-head) @ pose_world(f'{side}_kata'))
        place_wrist(3)


HAND_VERTS = {}


HAND_LOCAL = {}  # v15+: hand centre frozen in te-bone space so curled fingers don't drag the grip


def hand_point(side):
    if side in HAND_LOCAL:
        return pose_world(f'{side}_te') @ HAND_LOCAL[side]
    if MESH_GRIP:
        # v12+: centre of the visible hand (vertices on te + finger bones). The te/buki midpoint
        # sat below the handle, leaving the fists under the guard.
        if side not in HAND_VERTS:
            HAND_VERTS[side] = []
            for o in body:
                groups = {o.vertex_groups[n].index for n in (f'{side}_te', f'{side}_yubiB') if n in o.vertex_groups}
                HAND_VERTS[side] += [(o, v.index) for v in o.data.vertices
                                     if any(e.group in groups and e.weight > .3 for e in v.groups)]
        dg = bpy.context.evaluated_depsgraph_get()
        meshes = {o: o.evaluated_get(dg).data for o, _ in HAND_VERTS[side]}
        pts = [o.matrix_world @ meshes[o].vertices[i].co for o, i in HAND_VERTS[side]]
        return sum(pts, Vector()) / len(pts)
    socket = pose_world(f'{side}_buki').translation
    return (pose_world(f'{side}_te').translation + socket) / 2 if KEY_FACES_CAMERA else socket


ankle_z = pose_world('L_ashi1').translation.z
blade = Vector(POSE['blade_dir']).normalized()
if POSE.get('turn_blade'):  # blade_dir given in the body frame (battle_v6+)
    blade = (Matrix.Rotation(math.radians(POSE['body_turn_deg']), 3, 'Z') @ blade).normalized()
if POSE.get('screen_blade'):
    # Blade from its screen-space rise and its tilt toward the sprite camera (battle_v7+).
    rise, toward_cam = (math.radians(a) for a in POSE['screen_blade'])
    cam_t = math.radians(CAM_YAW)
    screen_right = Vector((math.cos(cam_t), math.sin(cam_t), 0))
    toward = Vector((math.sin(cam_t), -math.cos(cam_t), 0))
    blade = (math.cos(toward_cam)*(math.cos(rise)*screen_right + math.sin(rise)*Vector((0, 0, 1)))
             + math.sin(toward_cam)*toward).normalized()
    POSE['blade_dir'] = tuple(round(c, 4) for c in blade)


def solve_pose(breath=0.0, lag=None):
    # `lag` is the breath phase for hands/Key/head follow-through (trails the body slightly).
    lag = breath if lag is None else lag
    reset_pose()
    b = BREATH if LOOP else {'drop': 0, 'lean_deg': 0, 'hands_z': 0, 'head_counter_deg': 0}
    # battle_v*: the whole body turns toward the opponent; POSE targets are in that turned frame.
    turn = POSE.get('body_turn_deg', 0)
    turn_m = Matrix.Rotation(math.radians(turn), 3, 'Z')
    ax_x, ax_y = (turn_m @ Vector((1, 0, 0)), turn_m @ Vector((0, 1, 0))) if turn else ('X', 'Y')
    if turn:
        rotate_world('Root', 'Z', turn)
    set_pose_world('center', Matrix.Translation((0, 0, -POSE['drop'] - POSE.get('crouch_extra', 0)
                                                 - b['drop']*breath)) @ pose_world('center'))
    if POSE.get('center_shift'):
        # v19+: shift the pelvis sideways over the weight-bearing foot.
        cs_side, cs_amt = POSE['center_shift']
        fwd_c = (turn_m @ Vector((0, -1, 0))).normalized(); lat_c = fwd_c.cross(Vector((0, 0, 1)))
        foot_c = turn_m @ Vector((POSE[f'{cs_side}_foot'][0], POSE[f'{cs_side}_foot'][1], 0))
        hip_c = pose_world('center').translation.copy(); hip_c.z = 0
        sgn = 1 if (foot_c - hip_c).dot(lat_c) > 0 else -1
        set_pose_world('center', Matrix.Translation(lat_c*cs_amt*sgn) @ pose_world('center'))
    if POSE.get('hunch_deg') or POSE.get('hunch_extra'):
        rotate_world('hara', ax_x, POSE.get('hunch_deg', 0) + POSE.get('hunch_extra', 0))
    rotate_world('mune', ax_x, POSE['lean_deg'] + b['lean_deg']*breath + POSE.get('pitch_extra', 0))
    if POSE.get('chest_roll'):
        # v18+: roll the chest about the body's forward axis toward the weight-bearing foot.
        roll_side, roll_deg = POSE['chest_roll']
        fwd_ = (turn_m @ Vector((0, -1, 0))).normalized()
        lat_ = fwd_.cross(Vector((0, 0, 1)))
        foot_ = turn_m @ Vector((POSE[f'{roll_side}_foot'][0], POSE[f'{roll_side}_foot'][1], 0))
        hip_ = pose_world('hara').translation.copy(); hip_.z = 0
        rotate_world('mune', fwd_, roll_deg if (foot_ - hip_).dot(lat_) > 0 else -roll_deg)
    if POSE.get('chest_twist_deg'):
        # v14+ (Kvon): twist the upper spine/chest on its local Z so the front shoulder turns back.
        cols = pose_world('mune').to_3x3().normalized().col
        if POSE.get('twist_axis') == 'spine':
            # v16+: on the KH2 rig mune's local Z points sideways (local Z rotation bends the chest
            # back, as v14/v15 did); twist about whichever local axis runs up the spine.
            axis_ = max((Vector(c_) for c_ in cols), key=lambda c_: abs(c_.z))
            axis_ = axis_ if axis_.z > 0 else -axis_
        else:
            axis_ = Vector(cols[2])
        rotate_world('mune', axis_.normalized(), POSE['chest_twist_deg'])
    if POSE.get('neck_counter_deg') or POSE.get('neck_extra'):
        rotate_world('kubi', ax_x, POSE.get('neck_counter_deg', 0) + POSE.get('neck_extra', 0))
    if b['head_counter_deg']:
        rotate_world('kubi', ax_x, b['head_counter_deg']*lag)
    if POSE.get('look_deg'):
        rotate_world('kubi', 'Z', POSE['look_deg'])  # eyes on the opponent
    r_hand = turn_m @ Vector(POSE['R_hand']) + Vector((0, 0, b['hands_z']*lag))
    r_hand += Vector(POSE.get('grip_offset_world', (0, 0, 0)))  # v14+: grip moved off the stomach
    # v18+: the grip sinks with the deeper crouch, plus the weapon's vertical lag.
    r_hand += Vector((0, 0, POSE.get('hands_extra_z', 0) - POSE.get('crouch_extra', 0)))
    l_hand = r_hand + blade*POSE['L_hand_along_handle']
    toe_out = POSE.get('toe_out_deg', 0)
    for s, foot in (('R', POSE['R_foot']), ('L', POSE['L_foot'])):
        sign = -1 if s == 'R' else 1
        toe = POSE.get('toe_deg', {}).get(s, toe_out)
        # Knees track over turned-out toes.
        knee_hint = Vector((sign*(.3 + toe/50), -1, 0))
        if POSE.get('knee_splay'):
            knee_hint = knee_hint.lerp(Vector((sign*1.5, -.6, 0)), POSE['knee_splay'])  # v18+: knees wide
        knee_in = POSE.get('knee_in', {}).get(s, 0)
        if knee_in:
            # Swing the knee in toward the middle of the torso (walk v6+), then back out.
            knee_hint = knee_hint.lerp(Vector((-sign*.6, -1, 0)), knee_in)
        knee = turn_m @ knee_hint
        lift = foot[2] or 0  # walk gait raises the swinging foot
        two_bone(f'{s}_momo', f'{s}_sune', f'{s}_ashi1', turn_m @ Vector((foot[0], foot[1], ankle_z + lift)), knee)
        if toe or turn:
            rotate_world(f'{s}_ashi1', 'Z', sign*toe + turn)  # feet don't inherit the body turn
    for side, deg in POSE.get('foot_pitch', {}).items():
        if deg:
            # Heel up about the ankle, toes down (the ankle target was raised to keep toes on the floor).
            ankle = pose_world(f'{side}_ashi1').translation
            fwd = pose_world(f'{side}_ashi2').translation - ankle; fwd.z = 0; fwd.normalize()
            rotate_world(f'{side}_ashi1', fwd.cross(Vector((0, 0, 1))).normalized(), -deg)
    if POSE.get('head_yaw_cancel') and POSE.get('chest_twist_deg'):
        rotate_world('kubi', 'Z', -POSE['chest_twist_deg'])  # v19+: face stays on the opponent
    if POSE.get('shrug_deg'):
        for sd_ in ('R', 'L'):
            kh = pose_world(f'{sd_}_kata').translation
            kd = pose_world(f'{sd_}_ude1').translation - kh
            rotate_world(f'{sd_}_kata', kd.cross(Vector((0, 0, 1))).normalized(), POSE['shrug_deg'])
    if POSE.get('head_tilt_deg'):
        rotate_world('atama', ax_y, POSE['head_tilt_deg'])  # top of head toward his left, as referenced
    if POSE.get('front_flare_deg'):
        # v17+ (Kvon, option 1): flare the front arm out in the screen plane by tilting the
        # collarbone about the camera's view axis, so the elbow angles away from the jacket.
        side_f = POSE['front_flare_side']
        rotate_world(f'{side_f}_kata', Vector(POSE['flare_axis']), POSE['front_flare_deg'])
    if POSE.get('front_kata'):
        # v13+ (Kvon, option 2): pull the front shoulder back and out before the arm is solved,
        # so the hands stay on the handle while the arm silhouette widens.
        side_k, (yaw_k, lift_k) = POSE['front_kata']
        rotate_world(f'{side_k}_kata', 'Z', yaw_k)
        head = pose_world(f'{side_k}_kata').translation
        kdir = pose_world(f'{side_k}_ude1').translation - head
        rotate_world(f'{side_k}_kata', kdir.cross(Vector((0, 0, 1))).normalized(), lift_k)
    hand_on('R', r_hand, (-1, .4, -.3))
    if ONE_HAND:
        guard_hint = turn_m @ Vector(POSE.get('L_elbow_hint', (1, .6, -.2)))
        two_bone('L_ude1', 'L_ude2', 'L_te', turn_m @ Vector(POSE['L_relaxed_wrist']), guard_hint)
    else:
        hand_on('L', l_hand, (1, .4, -.3))
    if POSE.get('front_arm_deg'):
        # Swing the front elbow outward about the shoulder-wrist line; the hand stays on the handle.
        side = POSE['front_arm_side']
        shoulder = pose_world(f'{side}_ude1').translation
        wrist = pose_world(f'{side}_te').translation
        rotate_world(f'{side}_ude1', (wrist - shoulder).normalized(), POSE['front_arm_deg'])
    for side, degrees in TWIST.items():
        forearm = (pose_world(f'{side}_te').translation - pose_world(f'{side}_ude2').translation).normalized()
        rotate_world(f'{side}_te', forearm, degrees)
    if SQUARE_WRISTS:
        # A palm turned to the camera (battle_v10+) must not be re-squared to the handle.
        for side in [s for s in GRIP_SIDES if not (s == 'L' and POSE.get('L_palm_to_camera'))]:
            m = pose_world(f'{side}_te'); head = m.translation.copy()
            f = (pose_world(f'{side}_yubiB').translation - head).normalized()
            across = f - blade*f.dot(blade)
            if across.length > 1e-3:
                turn = f.rotation_difference(across.normalized())
                set_pose_world(f'{side}_te', Matrix.Translation(head) @ turn.to_matrix().to_4x4()
                               @ Matrix.Translation(-head) @ m)
    for side, (curl_axis, curl_sign) in FINGERS.items():
        set_curl(side, curl_axis, curl_sign)
    update()


FINGERS = {}  # side -> (local axis, sign) chosen once, reapplied every frame
TWIST = {}    # side -> wrist twist about the forearm in degrees (v6+)


def set_curl(side, curl_axis, curl_sign):
    for bone, degrees in ((f'{side}_yubiB', 85), (f'{side}_yubiA', 40)):
        pb = arm.pose.bones[bone]; pb.rotation_mode = 'QUATERNION'
        e = Euler((0, 0, 0)); setattr(e, curl_axis, curl_sign*math.radians(degrees))
        pb.rotation_quaternion = e.to_quaternion()
    update()


def pick_curl(side):
    # Bone rolls differ per hand, so test each curl direction and keep the one that brings the
    # finger vertices closest to the handle line.
    grip = hand_point(side)
    weighted = []
    for o in body:
        groups = {o.vertex_groups[n].index for n in (f'{side}_yubiB', f'{side}_yubiA') if n in o.vertex_groups}
        weighted += [(o, v.index) for v in o.data.vertices if any(e.group in groups and e.weight > .3 for e in v.groups)]
    best = None
    for curl_axis in 'xz':
        for curl_sign in (1, -1):
            set_curl(side, curl_axis, curl_sign)
            dg = bpy.context.evaluated_depsgraph_get()
            meshes = {o: o.evaluated_get(dg).data for o in {o for o, _ in weighted}}
            total = 0
            for o, i in weighted:
                r = o.matrix_world @ meshes[o].vertices[i].co - grip
                total += (r - blade*r.dot(blade)).length
            if best is None or total < best[0]:
                best = (total / max(len(weighted), 1), curl_axis, curl_sign)
    FINGERS[side] = best[1:]
    return round(best[0], 4)


def finger_distance(side):
    # Mean distance of the side's finger/thumb vertices from the handle line through the right palm.
    grip = hand_point('R')
    dg = bpy.context.evaluated_depsgraph_get()
    total = count = 0
    for o in body:
        groups = {o.vertex_groups[n].index for n in (f'{side}_yubiB', f'{side}_yubiA') if n in o.vertex_groups}
        if not groups:
            continue
        evaluated = o.evaluated_get(dg).data
        for v in o.data.vertices:
            if any(e.group in groups and e.weight > .3 for e in v.groups):
                r = o.matrix_world @ evaluated.vertices[v.index].co - grip
                total += (r - blade*r.dot(blade)).length; count += 1
    return total / max(count, 1)


def pick_hand(side):
    # Search wrist twist (15-degree steps) together with the finger-curl direction.
    best = None
    for degrees in range(-180, 180, 15):
        for curl in (('x', 1), ('x', -1), ('z', 1), ('z', -1)):
            TWIST[side] = degrees; FINGERS[side] = curl
            solve_pose(0.0)
            d = finger_distance(side)
            if best is None or d < best[0]:
                best = (d, degrees, curl)
    TWIST[side], FINGERS[side] = best[1], best[2]
    return round(best[0], 4)


REST_PALM = Vector((0, 0, -1))  # T-pose palms face down (thumb bones point forward)
if SHEET_MODEL:
    # A-pose rig: arms 50 degrees from vertical, palms toward the body (down and inward).
    REST_PALM = {'L': Vector((-math.cos(math.radians(50)), 0, -math.sin(math.radians(50)))),
                 'R': Vector((math.cos(math.radians(50)), 0, -math.sin(math.radians(50))))}


def rest_palm(side):
    return REST_PALM[side] if isinstance(REST_PALM, dict) else REST_PALM


def palm_normal(side):
    pb = arm.pose.bones[f'{side}_te']
    posed = (arm.matrix_world @ pb.matrix).to_3x3().normalized()
    rest = (arm.matrix_world @ arm.data.bones[f'{side}_te'].matrix_local).to_3x3().normalized()
    return (posed @ rest.inverted() @ rest_palm(side)).normalized()


def pick_anatomical_curl(side):
    # In the rest pose, keep the curl that moves the fingertips toward the palm side.
    reset_pose()
    rest_tip = pose_world(f'{side}_yubiB').to_translation() + (
        pose_world(f'{side}_yubiB').to_3x3() @ Vector((0, arm.data.bones[f'{side}_yubiB'].length, 0)))
    best = None
    for curl in (('x', 1), ('x', -1), ('z', 1), ('z', -1)):
        set_curl(side, *curl)
        m = pose_world(f'{side}_yubiB')
        tip = m.to_translation() + m.to_3x3() @ Vector((0, arm.data.bones[f'{side}_yubiB'].length, 0))
        score = (tip - rest_tip).dot(rest_palm(side))
        if best is None or score > best[0]:
            best = (score, curl)
    FINGERS[side] = best[1]


def pick_palm(side, target):
    # Twist the wrist about the forearm (10-degree steps) until the palm faces `target`.
    best = None
    for degrees in range(-180, 180, 10):
        TWIST[side] = degrees
        solve_pose(0.0)
        score = palm_normal(side).dot(target)
        if best is None or score > best[0]:
            best = (score, degrees)
    TWIST[side] = best[1]
    return round(best[0], 3)


solve_pose(0.0)
REACH_REPORT = []
if POSE.get('auto_reach'):
    # Move the whole grip (right fist + Key) toward the left hand until the left fist lands on its
    # handle spot; the right fist always sets the Key, so both then hold the handle.
    turn_m = Matrix.Rotation(math.radians(POSE.get('body_turn_deg', 0)), 3, 'Z')
    for _ in range(8):
        target = turn_m @ Vector(POSE['R_hand']) + blade*POSE['L_hand_along_handle']
        miss = target - hand_point('L')
        REACH_REPORT.append(round(miss.length, 4))
        if miss.length < .012:
            break
        POSE['R_hand'] = tuple(Vector(POSE['R_hand']) - turn_m.inverted() @ miss*.6)
        solve_pose(0.0)
if POSE.get('blade_toward'):
    # Tilt the blade so its tip lands tip_height above the soles along the chosen ground direction.
    ground_z = world_bounds(body)[0].z
    length = KEY_REACH - POSE.get('grip_shift', 0)
    dz = max(-length*.98, ground_z + POSE['tip_height'] - hand_point('R').z)
    toward = Matrix.Rotation(math.radians(POSE.get('body_turn_deg', 0)), 3, 'Z') @ Vector((*POSE['blade_toward'], 0))
    flat = toward.normalized()*math.sqrt(length*length - dz*dz)
    blade = (flat + Vector((0, 0, dz))).normalized()
    POSE['blade_dir'] = tuple(round(c, 4) for c in blade)
    solve_pose(0.0)
if ONE_HAND or TWO_HAND_BATTLE:
    # Gripping hands curl toward the palm and wrap (squared wrists); no palm-up/down search.
    for side in GRIP_SIDES:
        pick_anatomical_curl(side)
    FINGER_REPORT = {'grip_sides': list(GRIP_SIDES)}
    if POSE.get('L_palm_to_camera'):
        FINGER_REPORT['L_palm_to_camera_dot'] = pick_palm('L', to_cam)
        if POSE.get('L_palm_back_deg'):
            # v11+ (user): turn that palm slightly back toward Sora: try the offset both ways and
            # keep the one that faces the palm more toward his body.
            base, best = TWIST['L'], None
            for offset in (POSE['L_palm_back_deg'], -POSE['L_palm_back_deg']):
                TWIST['L'] = base + offset
                solve_pose(0.0)
                to_body = (pose_world('hara').translation - hand_point('L')).normalized()
                score = palm_normal('L').dot(to_body)
                if best is None or score > best[0]:
                    best = (score, base + offset, palm_normal('L').dot(to_cam))
            TWIST['L'] = best[1]
            FINGER_REPORT.update({'L_palm_to_body_dot': round(best[0], 3), 'L_palm_to_camera_dot_after': round(best[2], 3)})
elif PALM_ORIENT:
    for side in ('R', 'L'):
        pick_anatomical_curl(side)
    FINGER_REPORT = {'R_palm_up_dot': pick_palm('R', Vector((0, 0, 1))),
                     'L_palm_down_dot': pick_palm('L', Vector((0, 0, -1)))}
elif WRIST_TWIST:
    FINGER_REPORT = {side: pick_hand(side) for side in ('R', 'L')}
else:
    FINGER_REPORT = {side: pick_curl(side) for side in ('R', 'L')} if CURL_FINGERS else {}
if CURL_FINGERS:
    solve_pose(0.0)

# Kingdom Key in the right hand: grip at R_buki, blade up and back, away from the opponent.
def place_key():
    if KEY_FACES_CAMERA:
        # v4+ (user correction): guard face toward the camera, teeth (local +X) pointing down,
        # grip in the palm between wrist and weapon socket so the fist sits inside the guard.
        # grip_shift slides the Key so the fist wraps the handle's middle rather than its pommel end.
        grip_world = hand_point('R') - blade*POSE.get('grip_shift', 0)
        facing = (to_cam - blade*to_cam.dot(blade)).normalized()
        x_axis = facing.cross(blade).normalized()
        if (x_axis.z > 0) != KEY_TEETH_UP:
            x_axis = -x_axis
    else:
        grip_world = pose_world('R_buki').translation
        x_axis = blade.cross(Vector((0, 0, 1))).normalized()
    y_axis = blade.cross(x_axis)
    key.matrix_world = Matrix.Translation(grip_world) @ Matrix((x_axis, y_axis, blade)).transposed().to_4x4()
    update()


place_key()
WRAP_REPORT = {}


def skin_matrix(o, v):
    # Linear-blend skinning matrix (world) for one vertex, as the Armature modifier applies it.
    total, acc = 0.0, Matrix.Diagonal((0, 0, 0, 0))
    for e in v.groups:
        name = o.vertex_groups[e.group].name
        if name in arm.pose.bones and e.weight > 0:
            pb = arm.pose.bones[name]
            m = arm.matrix_world @ pb.matrix @ arm.data.bones[name].matrix_local.inverted() @ arm.matrix_world.inverted()
            acc = acc + m*e.weight; total += e.weight
    return acc*(1/total) if total else Matrix.Identity(4)


def build_fist_wrap():
    # Roll every finger/thumb vertex onto a circle around the handle line, measured from its
    # knuckle: arc length past the knuckle becomes angle around the handle (palm stays behind).
    origin, d = key.matrix_world.translation.copy(), blade
    dg = bpy.context.evaluated_depsgraph_get()
    targets = {}
    for side in GRIP_SIDES:
        for bone, part in ((f'{side}_yubiB', 'fingers'), (f'{side}_yubiA', 'thumb')):
            m = pose_world(bone); knuckle = m.translation.copy()
            along = (knuckle - origin).dot(d); centre = origin + d*along
            u = knuckle - centre; r0 = u.length; u.normalize()
            f = (m.to_3x3() @ Vector((0, 1, 0))).normalized()
            t = f - d*f.dot(d) - u*f.dot(u)
            t = t.normalized() if t.length > 1e-4 else d.cross(u).normalized()
            WRAP_REPORT[f'{side}_{part}_radius_m'] = round(r0, 4)
            for o in body:
                g = o.vertex_groups.get(bone)
                if not g:
                    continue
                ev = o.evaluated_get(dg).data
                for v in o.data.vertices:
                    w = next((e.weight for e in v.groups if e.group == g.index), 0)
                    if w < .05:
                        continue
                    p = o.matrix_world @ ev.vertices[v.index].co
                    rel = p - knuckle
                    s, h, a = rel.dot(t), rel.dot(u), rel.dot(d)
                    if s <= 0:
                        continue
                    theta = min(WRAP_GAIN*s / max(r0, .012), math.radians(WRAP_MAX_DEG))
                    wrapped = centre + d*a + (u*math.cos(theta) + t*math.sin(theta))*(r0 + h)
                    targets.setdefault(o, {})[v.index] = p.lerp(wrapped, min(w, 1))
    moved = 0
    for o, verts in targets.items():
        if not o.data.shape_keys:
            o.shape_key_add(name='Basis', from_mix=False)
        sk = o.shape_key_add(name='fist_wrap', from_mix=False)
        for i, world in verts.items():
            rest_world = skin_matrix(o, o.data.vertices[i]).inverted() @ world
            sk.data[i].co = o.matrix_world.inverted() @ rest_world
            moved += 1
        sk.value = 1.0
    update()
    WRAP_REPORT['vertices_wrapped'] = moved


if FIST_WRAP:
    HAND_LOCAL.update({s: pose_world(f'{s}_te').inverted() @ hand_point(s) for s in GRIP_SIDES})
    build_fist_wrap()
if not LOOP:
    # Single frame: ride the weapon bone. The loop re-places the Key each frame instead, because
    # the re-solved hand twists slightly per frame and a bone-parented Key wobbled visibly.
    world = key.matrix_world.copy()
    key.parent = arm; key.parent_type = 'BONE'; key.parent_bone = 'R_buki'
    update()
    key.matrix_world = world
    update()

# 5. Fixed sprite camera framed like the approved idle: about 385px tall, soles at y=470 of 512.
lo, hi = world_bounds(body)
cam_data = bpy.data.cameras.new('sprite_camera'); cam_data.type = 'ORTHO'
cam_data.ortho_scale = HEIGHT * 512 / 385
cam = bpy.data.objects.new('sprite_camera', cam_data); scene.collection.objects.link(cam)
ground = lo.z
center_z = ground + (470 - 256) / 512 * cam_data.ortho_scale
cam.location = Vector((0, 0, center_z)) + to_cam*6
cam.rotation_euler = (math.radians(90), 0, t)
scene.camera = cam

if LOOP:
    # Breathing loop: re-solve every frame from the rest pose, key all bones, render 512 + 128.
    (OUT / 'frames_512').mkdir(); (OUT / 'frames_128').mkdir()
    n = len(DURATIONS_MS)
    frames = []
    if GAIT:
        # Walk direction on the floor: toward the opponent (screen right) or away, in the body frame.
        turn_m = Matrix.Rotation(math.radians(POSE.get('body_turn_deg', 0)), 3, 'Z')
        screen_right = Vector((math.cos(t), math.sin(t), 0))
        walk_dir = (turn_m.inverted() @ screen_right) * (1 if '_fwd' in GAIT else -1)
        STANCE = {s: Vector((POSE[f'{s}_foot'][0], POSE[f'{s}_foot'][1], 0)) for s in ('R', 'L')}
        # The foot nearer the travel direction steps first; the other follows half a cycle later.
        leader = max(('R', 'L'), key=lambda s: STANCE[s].dot(walk_dir))

        if SHUFFLE:
            along = {sd: STANCE[sd].dot(walk_dir) for sd in STANCE}
            perp = {sd: STANCE[sd] - walk_dir*along[sd] for sd in STANCE}
            centre = (along['R'] + along['L']) / 2

            def ease(u):
                return u*u*(3 - 2*u)

            def shuffle_at(phase):
                # World positions along the walk axis; the body advances STEP_LEN per cycle.
                if phase < .5:
                    u = phase / .5
                    lead, back, lift_lead, lift_back = STEP_LEN*ease(u), 0.0, LIFT*math.sin(math.pi*u), 0.0
                else:
                    u = (phase - .5) / .5
                    lead, back, lift_lead, lift_back = STEP_LEN, STEP_LEN*ease(u), 0.0, LIFT*math.sin(math.pi*u)
                body = STEP_LEN*phase + STEP_LEN/2  # constant speed; centres the feet over the cycle
                return ((NARROW/2 + lead - body, lift_lead), (-NARROW/2 + back - body, lift_back))

        ROOT_MOTION = []  # metres the body advances when each frame starts (stepped gait)
        TOE_DIST = (pose_world('L_ashi2').translation - pose_world('L_ashi1').translation).length
        if GAIT.endswith(('_v1', '_v2', '_v3', '_v4')):
            pass
        else:
            # v5+: the shoe tip reaches ~1.5x past the toe joint; v4's heel-up frame sank the toes 6 px.
            TOE_DIST *= 1.5

        def foot_at(side, phase):
            phase = (phase + (0 if side == leader else .5)) % 1
            if phase < SWING:  # swing: travel forward with a lift
                u = phase / SWING; u = u*u*(3 - 2*u)
                return -STRIDE + 2*STRIDE*u, LIFT*math.sin(math.pi*phase/SWING)
            return STRIDE - 2*STRIDE*(phase - SWING)/(1 - SWING), 0.0  # stance: planted, slides back
    V12 = GAIT and globals().get('V12')
    if V12:
        BASE_BLADE = blade.copy()
        if V18 and globals().get('GOKU'):
            lead_ = max(('R', 'L'), key=lambda s_: Vector((*POSE[f'{s_}_foot'][:2], 0)).dot(Vector((1, 0, 0))))
            POSE.update({'twist_axis': 'spine', 'chest_twist_deg': 0}); solve_pose(0.0)
            x0 = pose_world(f'{lead_}_kata').translation.dot(Vector((math.cos(t), math.sin(t), 0)))
            POSE['chest_twist_deg'] = 10; solve_pose(0.0)
            x1 = pose_world(f'{lead_}_kata').translation.dot(Vector((math.cos(t), math.sin(t), 0)))
            TWIST_SIGN_G = 1 if x1 > x0 else -1
            POSE['chest_twist_deg'] = 0
        if V18 and globals().get('GUARD_IN'):
            to_chest = pose_world('hara').translation - hand_point('R'); to_chest.z = 0; to_chest.normalize()
            POSE['grip_offset_world'] = tuple(to_chest*GUARD_IN)
            GUARD_VEC = tuple(to_chest*GUARD_IN)
        cam_right = Vector((math.cos(t), math.sin(t), 0))
        PX = 512 / cam_data.ortho_scale
        FRONT = max(('R', 'L'), key=lambda sd: pose_world(f'{sd}_ude2').translation.dot(to_cam))

        def arm_gap_px(side):
            # Screen-space gap between the elbow half of the front forearm and the torso (mune/hara)
            # points, sampled at vertices and along edges, in 512 px render pixels. The wrist half
            # crosses in front of the waist to reach the handle, so it always overlaps the jacket.
            dg = bpy.context.evaluated_depsgraph_get()
            elbow = pose_world(f'{side}_ude2').translation; wrist = pose_world(f'{side}_te').translation
            fore = wrist - elbow
            arm_pts, torso_pts = [], []
            for o in body:
                gi = {g.name: g.index for g in o.vertex_groups}
                fa, tor = gi.get(f'{side}_ude2'), [gi[nm] for nm in ('mune', 'hara') if nm in gi]
                if fa is None and not tor:
                    continue
                ev, mw = o.evaluated_get(dg).data, o.matrix_world
                kind = {}
                for v in o.data.vertices:
                    w = {e.group: e.weight for e in v.groups}
                    kind[v.index] = 'a' if fa is not None and w.get(fa, 0) > .5 else (
                        't' if any(w.get(g_, 0) > .5 for g_ in tor) else None)
                pt = lambda i_: mw @ ev.vertices[i_].co
                for e in o.data.edges:
                    a_, b_ = e.vertices
                    if kind[a_] and kind[a_] == kind[b_]:
                        pa, pb = pt(a_), pt(b_)
                        for u in (0, .25, .5, .75, 1):
                            q = pa.lerp(pb, u)
                            if kind[a_] == 'a' and (q - elbow).dot(fore) / fore.length_squared > .5:
                                continue
                            (arm_pts if kind[a_] == 'a' else torso_pts).append((q.dot(cam_right)*PX, q.z*PX))
            A, B = np.array(arm_pts), np.array(torso_pts)
            return float(np.sqrt(((A[:, None] - B[None]) ** 2).sum(2)).min())

        # Outward = the swing direction that carries the elbow away from his body on screen.
        def elbow_out(deg):
            POSE.update({'front_arm_side': FRONT, 'front_arm_deg': deg})
            solve_pose(0.0)
            e = pose_world(f'{FRONT}_ude2').translation - pose_world('hara').translation
            return abs(e.dot(cam_right))
        # With the hand fixed on the handle the elbow is already at its outermost screen point, so both
        # directions tie on elbow position; pick the one that actually opens the forearm gap.
        def gap_at(deg):
            POSE.update({'front_arm_side': FRONT, 'front_arm_deg': deg})
            solve_pose(0.0)
            return arm_gap_px(FRONT)
        GAP_TRIAL = {d_: round(gap_at(d_), 2) for d_ in (0.0, FRONT_ARM_RANGE[0], -FRONT_ARM_RANGE[0], 15.0, -15.0)}
        print("ARM_TRIAL", FRONT, GAP_TRIAL)
        ARM_SIGN = 1 if GAP_TRIAL[FRONT_ARM_RANGE[0]] > GAP_TRIAL[-FRONT_ARM_RANGE[0]] else -1
        KATA_LOG = TWIST_LOG = ALPHA_LOG = None
        FLARE = GAIT.endswith('_v17')
        if GAIT.endswith(('_v15', '_v16', '_v17')):
            # v15+ (Kvon's spec): chest twist 15-22 deg away from the camera on its local Z, no
            # collarbone change, no grip shift. Validated on rendered pixels: open background between
            # the front forearm and the jacket must be >= 10 px on every frame of the cycle.
            POSE.pop('grip_offset_world', None)
            POSE.pop('front_kata', None)
            if not GAIT.endswith('_v15'):
                POSE['twist_axis'] = 'spine'
                POSE['no_reach_side'] = FRONT
            if FLARE:
                POSE.pop('twist_axis', None)

            def frame_pose(i_):
                # The same per-frame foot, knee and weapon-drag setup as the main loop (stepped gait).
                lead_w, lead_h, back_w, back_h, heel, body_w, bob_, _ = STEP_KEYS[i_]
                follower_ = 'R' if leader == 'L' else 'L'
                POSE['foot_pitch'] = {follower_: heel}
                POSE['knee_in'] = {follower_: BACK_KNEE_IN[i_], leader: LEAD_KNEE_IN[i_]}
                for side_, a_, h_ in ((leader, lead_w, lead_h),
                                      (follower_, back_w, back_h + TOE_DIST*math.sin(math.radians(heel)))):
                    pos_ = perp[side_] + walk_dir*(centre + a_ - body_w - NARROW/2 + STEP_KEYS[0][0]/2)
                    POSE[f'{side_}_foot'] = (pos_.x, pos_.y, h_)
                return bob_, (Matrix.Rotation(math.radians(WEAPON_DRAG[i_]), 3, 'Z') @ BASE_BLADE).normalized()

            def to_img(p_):
                return (256 + (p_.dot(cam_right) - cam.location.dot(cam_right))*PX,
                        256 - (p_.z - cam.location.z)*PX)

            def silhouette():
                eng, fs = scene.render.engine, scene.render.use_freestyle
                scene.render.engine, scene.render.use_freestyle = 'BLENDER_WORKBENCH', False
                probe = OUT / '_gap_probe.png'; scene.render.filepath = str(probe)
                bpy.ops.render.render(write_still=True)
                scene.render.engine, scene.render.use_freestyle = eng, fs
                im_ = bpy.data.images.load(str(probe), check_existing=False); px_ = np.empty(512*512*4, np.float32)
                im_.pixels.foreach_get(px_); bpy.data.images.remove(im_)
                return px_.reshape(512, 512, 4)[::-1, :, 3] > .5

            def open_gap(alpha, ex, ey, hx):
                # Widest run of background bounded by figure pixels on both sides, in the rows around
                # the front elbow, starting right of the elbow and ending before the hips' centre.
                best_w = 0
                for y_ in range(max(0, int(ey) - 40), min(512, int(ey) + 40)):
                    xs_ = np.where(alpha[y_])[0]
                    if len(xs_) < 2:
                        continue
                    lo_, hi_ = int(xs_.min()), int(min(hx, xs_.max()))
                    seg = alpha[y_, lo_:hi_ + 1].astype(int)
                    d_ = np.diff(seg)
                    starts, ends = np.where(d_ == -1)[0] + 1, np.where(d_ == 1)[0] + 1
                    for st in starts:
                        en = ends[ends > st]
                        if len(en) and lo_ + en[0] > ex - 8:
                            best_w = max(best_w, int(en[0] - st))
                return best_w

            POSE.pop('chest_twist_deg', None); solve_pose(0.0)
            if FLARE:
                # Flare direction: the sign that moves the front shoulder joint away from the hips on screen.
                POSE.update({'front_flare_side': FRONT, 'flare_axis': tuple(to_cam.normalized())})  # JSON-safe
                hip_x = to_img(pose_world('hara').translation)[0]

                def shoulder_out(deg_):
                    POSE['front_flare_deg'] = deg_; solve_pose(0.0)
                    return abs(to_img(pose_world(f'{FRONT}_ude1').translation)[0] - hip_x)
                FLARE_SIGN = 1 if shoulder_out(15) > shoulder_out(-15) else -1
                TWIST_SIGN, trials = 1, [(0, d_) for d_ in range(0, 41, 5)]
            else:
                base_depth = pose_world(f'{FRONT}_ude1').translation.dot(to_cam)
                POSE['chest_twist_deg'] = 18; solve_pose(0.0)
                TWIST_SIGN = 1 if pose_world(f'{FRONT}_ude1').translation.dot(to_cam) < base_depth else -1
                trials = [(t_, 0) for t_ in range(15, 23)]
            results = []
            for twist, flare in trials:
                for sign in (1, -1):
                    POSE.update({'chest_twist_deg': TWIST_SIGN*twist, 'front_arm_side': FRONT,
                                 'front_arm_deg': sign*FRONT_ARM_RANGE[0]})
                    if FLARE:
                        POSE['front_flare_deg'] = FLARE_SIGN*flare
                    per = []
                    for i_ in range(n):
                        bob_, blade = frame_pose(i_)
                        solve_pose(bob_, bob_)
                        place_key()
                        ex, ey = to_img(pose_world(f'{FRONT}_ude2').translation)
                        hx = to_img(pose_world('hara').translation)[0]
                        grip_l = (hand_point('L') - (hand_point('R') + blade*POSE['L_hand_along_handle'])).length
                        per.append({'gap_px': open_gap(silhouette(), ex, ey, hx), 'grip_error_L_m': round(grip_l, 4),
                                    'elbow_img': [round(ex, 1), round(ey, 1)], 'hip_img_x': round(hx, 1)})
                    worst = min(f_['gap_px'] for f_ in per)
                    results.append((twist if not FLARE else flare, sign, worst, per))
                    print('ALPHA_TRY', twist, flare, sign, worst, [f_['gap_px'] for f_ in per],
                          'shoulder_img', [round(c_, 1) for c_ in to_img(pose_world(f'{FRONT}_ude1').translation)])
            (OUT / '_gap_probe.png').unlink(missing_ok=True)
            # Smallest twist whose worst frame clears 13 px (3 px margin for the ink outline added in
            # the 2D style); otherwise the best worst-case found.
            ok = [r_ for r_ in results if r_[2] >= 13]
            twist, sign, worst, per = ok[0] if ok else max(results, key=lambda r_: (r_[2], -r_[0]))
            if FLARE:
                POSE.update({'chest_twist_deg': 0, 'front_flare_deg': FLARE_SIGN*twist,
                             'front_arm_deg': sign*FRONT_ARM_RANGE[0]})
            else:
                POSE.update({'chest_twist_deg': TWIST_SIGN*twist, 'front_arm_deg': sign*FRONT_ARM_RANGE[0]})
            ARM_SIGN = sign
            ALPHA_LOG = {('front_flare_deg' if FLARE else 'chest_twist_deg'): twist, 'twist_sign': TWIST_SIGN,
                         'abduction_deg': FRONT_ARM_RANGE[0],
                         'worst_gap_px_probe': worst, 'frames': per, 'met_target': bool(ok)}
            print('ALPHA_BEST', twist, sign, worst, bool(ok))
        elif GAIT.endswith('_v14'):
            # v14 (Kvon): no collarbone change. Twist the chest 6-10 deg away from the camera and, if
            # the front elbow would hyper-extend, move the grip forward off the stomach by up to 3 cm.
            def front_shoulder_depth():
                return pose_world(f'{FRONT}_ude1').translation.dot(to_cam)

            def extension():
                sh_ = pose_world(f'{FRONT}_ude1').translation
                el_ = pose_world(f'{FRONT}_ude2').translation
                wr_ = pose_world(f'{FRONT}_te').translation
                return (wr_ - sh_).length / ((el_ - sh_).length + (wr_ - el_).length)

            POSE.pop('chest_twist_deg', None); solve_pose(0.0); base_depth = front_shoulder_depth()
            POSE['chest_twist_deg'] = 8; solve_pose(0.0)
            TWIST_SIGN = 1 if front_shoulder_depth() < base_depth else -1  # away from the camera
            stomach = pose_world('hara').translation
            fwd = hand_point('R') - stomach; fwd.z = 0; fwd.normalize()
            best_t = None
            for twist in range(6, 11):
                for shift_cm in (0, 1, 2, 3):
                    for sign in (1, -1):
                        POSE.update({'chest_twist_deg': TWIST_SIGN*twist,
                                     'grip_offset_world': tuple(fwd*shift_cm/100)})
                        g_ = gap_at(sign*FRONT_ARM_RANGE[0])
                        ext = extension()
                        lo, hi = FRONT_ARM_GAP
                        miss = (0 if lo <= g_ <= hi else min(abs(g_ - lo), abs(g_ - hi))) + (5 if ext > .985 else 0)
                        # Prefer the smallest twist and shift that reach the band.
                        score = (round(miss, 2), twist, shift_cm)
                        if best_t is None or score < best_t[0]:
                            best_t = (score, twist, shift_cm, sign, g_, ext)
            _, twist, shift_cm, ARM_SIGN, g_, ext = best_t
            POSE.update({'chest_twist_deg': TWIST_SIGN*twist, 'grip_offset_world': tuple(fwd*shift_cm/100)})
            TWIST_LOG = {'chest_twist_deg': twist, 'direction_sign': TWIST_SIGN, 'grip_forward_cm': shift_cm,
                         'gap_px_at_12deg': round(g_, 2), 'front_arm_extension': round(ext, 3)}
            print('TWIST_BEST', TWIST_LOG)
        elif GAIT.endswith('_v13'):
            # v13+: search the front collarbone angle (+-20 deg turn, +-15 deg lift) with the elbow at
            # 12 deg; keep the one whose forearm gap lands nearest the 10-12 px band.
            best_k = None
            for yaw_k in range(-20, 21, 5):
                for lift_k in range(-15, 16, 5):
                    POSE['front_kata'] = (FRONT, (yaw_k, lift_k))
                    for sign in (1, -1):
                        g_ = gap_at(sign*FRONT_ARM_RANGE[0])
                        lo, hi = FRONT_ARM_GAP
                        miss = 0 if lo <= g_ <= hi else min(abs(g_ - lo), abs(g_ - hi))
                        if best_k is None or miss < best_k[0]:
                            best_k = (miss, yaw_k, lift_k, sign, g_)
            POSE['front_kata'] = (FRONT, (best_k[1], best_k[2]))
            ARM_SIGN = best_k[3]
            KATA_LOG = {'yaw_deg': best_k[1], 'lift_deg': best_k[2], 'gap_px_at_12deg': round(best_k[4], 2)}
            print('KATA_BEST', KATA_LOG)
        ARM_LOG = []
    for i in range(n):
        breath = (1 - math.cos(2*math.pi*i/n)) / 2
        # v3+: follow-through lag; a symmetric breath alone made frames 1-4 repeat as 9-6.
        lag = (1 - math.cos(2*math.pi*(i/n - BREATH_LAG))) / 2
        if GAIT and IDLE_SHUFFLE:
            # Feet in world terms along the walk; the body sits midway between them, so planted feet stay put.
            lf, lh, bf, bh, _ = SH_KEYS[i]
            follower = 'R' if leader == 'L' else 'L'
            body_now = SH_STEP*(lf + bf)/2
            prev = SH_KEYS[i - 1]
            body_prev = SH_STEP*(prev[0] + prev[2])/2 - (SH_STEP if i == 0 else 0)
            ROOT_MOTION.append(round(body_now - body_prev, 4))
            for side, frac, lift_ in ((leader, lf, lh), (follower, bf, bh)):
                pos = STANCE[side] + walk_dir*(SH_STEP*frac - body_now)
                POSE[f'{side}_foot'] = (pos.x, pos.y, lift_)
            breath = 0.0
            lag = 0.0 if GAIT.endswith('_v1') else (1 - math.cos(2*math.pi*(0 - .12))) / 2  # idle frame 1
            # Hips sink a little while the feet are spread so the legs can reach (grip sinks with them).
            POSE['crouch_extra'] = SH_DIP*(lf - bf)
        elif GAIT:
            if V18:
                SRC = 4 if BRAKE_WIDE else 0  # walk drawing the transition blends to/from
                if i == 0:
                    WALK0 = STEP_KEYS[SRC]
                follower_ = 'R' if leader == 'L' else 'L'
                w_ = TRANS_T[i] if TRANSITION else 1.0
                j_ = SRC if TRANSITION else i
                POSE.update({'crouch_extra': CROUCH_EXTRA*w_, 'pitch_extra': PITCH[j_]*w_,
                             'knee_splay': KNEE_SPLAY*w_, 'hands_extra_z': HANDS_EXTRA[j_]*w_,
                             'chest_roll': (follower_ if ROLL[j_][0] == 'F' else leader, ROLL_DEG*ROLL[j_][1]*w_)})
                if globals().get('GOKU'):
                    POSE.update({'hunch_extra': G_HUNCH*w_, 'pitch_extra': PITCH[j_]*w_ + G_LEAN*w_,
                                 'neck_extra': G_NECK*w_, 'grip_offset_world': tuple(Vector(GUARD_VEC)*w_)})
                    weight_side = follower_ if ROLL[j_][0] == 'F' else leader
                    POSE.update({'twist_axis': 'spine', 'chest_twist_deg': TWIST_SIGN_G*TWIST_DEG*TWIST_W[j_]*w_,
                                 'head_yaw_cancel': True, 'shrug_deg': SHRUG_DEG*w_,
                                 'center_shift': (weight_side, CENTER_SHIFT*ROLL[j_][1]*w_),
                                 'knee_splay': (KNEE_SPLAY + .2*GBOB[j_])*w_})
            if STEPPED and TRANSITION:
                # Idle -> walk drawing 1: feet move from the idle stance to the wide walk stance.
                lead_w, lead_h, back_w, back_h, heel, body_w, bob, _ = WALK0
                breath = lag = bob*TRANS_T[i]
                sweep = POSE.get('chest_twist_deg', 0) if globals().get('GOKU') else 0
                blade = (Matrix.Rotation(math.radians(WEAPON_DRAG[SRC]*TRANS_T[i] + sweep), 3, 'Z') @ BASE_BLADE).normalized()
                follower = 'R' if leader == 'L' else 'L'
                POSE['foot_pitch'] = {}
                POSE['knee_in'] = {leader: LEAD_KNEE_IN[SRC]*TRANS_T[i], follower: BACK_KNEE_IN[SRC]*TRANS_T[i]}
                for side, a in ((leader, lead_w), (follower, back_w)):
                    walk_pos = perp[side]*WIDTH_SCALE + walk_dir*(centre + a - body_w - NARROW/2 + STEP_KEYS[0][0]/2
                                                                  + STANCE_SHIFT)
                    pos = STANCE[side].lerp(walk_pos, TRANS_T[i])
                    POSE[f'{side}_foot'] = (pos.x, pos.y, 0.0)
                ROOT_MOTION.append(0.0)
            elif STEPPED:
                lead_w, lead_h, back_w, back_h, heel, body_w, bob, _ = STEP_KEYS[i]
                breath, lag = bob, STEP_KEYS[i - 1][6]  # hands/head trail the body by one frame
                if V12:
                    lag = bob  # hands drop with the pelvis on the same frame (grip intact)
                    sweep = POSE.get('chest_twist_deg', 0) if globals().get('GOKU') else 0  # blade follows the twist
                    blade = (Matrix.Rotation(math.radians(WEAPON_DRAG[i] + sweep), 3, 'Z') @ BASE_BLADE).normalized()
                follower = 'R' if leader == 'L' else 'L'
                rad = math.radians(heel)
                lead_toe = LEAD_TOE[i] if V18 else 0
                trail_toe = (10 if i in (8, 9) else 0) if V18 and BACK else 0
                POSE['foot_pitch'] = {follower: heel + trail_toe, leader: lead_toe}
                POSE['knee_in'] = {follower: BACK_KNEE_IN[i], leader: LEAD_KNEE_IN[i]}
                for side, a, h in ((leader, lead_w, lead_h + TOE_DIST*math.sin(math.radians(lead_toe))),
                                   (follower, back_w, back_h + TOE_DIST*math.sin(math.radians(heel + trail_toe)))):
                    tuck = FOOT_IN*BACK_KNEE_IN[i] if side == follower else 0
                    width_ = WIDTH_SCALE if V18 else 1.0
                    pos = (perp[side]*width_*(1 - tuck)
                           + walk_dir*(centre + a - body_w - NARROW/2 + STEP_KEYS[0][0]/2 + globals().get('STANCE_SHIFT', 0)))
                    POSE[f'{side}_foot'] = (pos.x, pos.y, h)
                ROOT_MOTION.append(round(body_w - (STEP_KEYS[i - 1][5] - (STEP_LEN if i == 0 else 0)), 4))
            elif SHUFFLE:
                breath = (1 - math.cos(2*math.pi*i/n)) / 2  # one bounce per cycle
                lag = (1 - math.cos(2*math.pi*(i/n - BREATH_LAG))) / 2
                (lead_a, lead_h), (back_a, back_h) = shuffle_at(i/n)
                for side in ('R', 'L'):
                    a, h = (lead_a, lead_h) if side == leader else (back_a, back_h)
                    pos = perp[side] + walk_dir*(centre + a)
                    POSE[f'{side}_foot'] = (pos.x, pos.y, h)
            else:
                breath = (1 - math.cos(4*math.pi*i/n)) / 2  # one dip per step
                lag = (1 - math.cos(4*math.pi*(i/n - BREATH_LAG/2))) / 2
                for side in ('R', 'L'):
                    offset, lift = foot_at(side, i/n)
                    pos = STANCE[side] + walk_dir*offset
                    POSE[f'{side}_foot'] = (pos.x, pos.y, lift)
        if V12 and ALPHA_LOG is None:
            # Pick the abduction in 12-15 deg whose forearm gap lands closest to the 10-12 px band.
            best = None
            for step in range(7):
                deg = FRONT_ARM_RANGE[0] + step*.5
                POSE.update({'front_arm_side': FRONT, 'front_arm_deg': ARM_SIGN*deg})
                solve_pose(breath, lag)
                gap = arm_gap_px(FRONT)
                lo, hi = FRONT_ARM_GAP
                miss = 0 if lo <= gap <= hi else min(abs(gap - lo), abs(gap - hi))
                if best is None or miss < best[0]:
                    best = (miss, deg, gap)
            POSE['front_arm_deg'] = ARM_SIGN*best[1]
            ARM_LOG.append({'abduction_deg': best[1], 'forearm_gap_px': round(best[2], 1),
                            'weapon_drag_deg': WEAPON_DRAG[i], 'pelvis_drop_px': round(6*bob, 2)})
        solve_pose(breath, lag)
        place_key()
        for pb in arm.pose.bones:
            for path in ('location', 'rotation_quaternion', 'rotation_euler', 'scale'):
                pb.keyframe_insert(path, frame=i + 1)
        key.keyframe_insert('location', frame=i + 1); key.keyframe_insert('rotation_euler', frame=i + 1)
        scene.frame_set(i + 1)
        path512 = OUT / 'frames_512' / f'sora_idle3d_{i:02d}.png'
        scene.render.filepath = str(path512)
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(str(path512))
        small = img.copy(); small.scale(128, 128)
        small.filepath_raw = str(OUT / 'frames_128' / path512.name); small.file_format = 'PNG'; small.save()
        frames.append({'filename': path512.name, 'duration_ms': DURATIONS_MS[i], 'breath': round(breath, 4),
                       'lag': round(lag, 4),
                       'grip_error_L_m': round((hand_point('L')
                                                - (Matrix.Rotation(math.radians(POSE.get('body_turn_deg', 0)), 3, 'Z')
                                                   @ Vector(POSE['R_hand']) + Vector((0, 0, BREATH['hands_z']*lag))
                                                   + blade*POSE['L_hand_along_handle'])).length, 4)})
    scene.frame_start, scene.frame_end = 1, n
    if REF_POSE:
        # Pose check from roughly the reference screenshot's near-front angle (not a sprite view).
        scene.frame_set(1)
        ref_data = bpy.data.cameras.new('reference_angle_camera'); ref_data.type = 'ORTHO'
        ref_data.ortho_scale = cam_data.ortho_scale
        ref_cam = bpy.data.objects.new('reference_angle_camera', ref_data); scene.collection.objects.link(ref_cam)
        # Near-front view, then (v10+) a right-side profile to judge the hunch.
        views = [('reference_angle_frame00.png', -10)]
        if version not in {f'idle_loop_v{n}' for n in range(7, 10)}:
            views.append(('side_check_frame00.png', -90))
        for filename, yaw in views:
            ref_t = math.radians(yaw)
            ref_cam.location = Vector((0, 0, center_z)) + Vector((math.sin(ref_t), -math.cos(ref_t), 0))*6
            ref_cam.rotation_euler = (math.radians(90), 0, ref_t)
            scene.camera = ref_cam
            scene.render.filepath = str(OUT / filename)
            bpy.ops.render.render(write_still=True)
        scene.camera = cam
    blend = OUT / 'sora_idle_loop.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
    report = {
        'version': version, 'blender': bpy.app.version_string, 'animation': 'standing_breathing_idle',
        'source': 'downloads/p_ex150.fbx + downloads/Kingdom Key/Kingdom Key.obj', 'loop': True,
        'canvas_size': [512, 512], 'ground_baseline_y': 470, 'body_anchor': [256, 470],
        'total_duration_ms': sum(DURATIONS_MS), 'pose': POSE, 'breath': BREATH,
        'camera_yaw_deg': CAM_YAW, 'ortho_scale': round(cam_data.ortho_scale, 4), 'frames': frames,
        'root_motion_m': ROOT_MOTION if GAIT else None,
        'game_frames_60fps': globals().get('GAME_FRAMES'),
        'v12_spec': ({'front_arm_side': FRONT, 'per_frame': ARM_LOG, 'front_shoulder': KATA_LOG,
                      'chest_twist': TWIST_LOG, 'silhouette_gap': ALPHA_LOG,
                      'root_px_per_drawing_384': [round(m*GAME_PX_PER_M, 3) for m in ROOT_MOTION]}
                     if V12 else None),
        'key_faces_camera': KEY_FACES_CAMERA, 'key_teeth_up': KEY_TEETH_UP, 'wrist_twist_deg': TWIST,
        'hand_search': FINGER_REPORT, 'fist_wrap': WRAP_REPORT, 'reach_misses_m': REACH_REPORT,
        'finger_curl': {s: {'axis': a, 'sign': g, 'mean_dist_to_handle_m': FINGER_REPORT.get(s)}
                        for s, (a, g) in FINGERS.items()},
        'blend': blend.name,
    }
    (OUT / 'Idle_Loop_Report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('LOOP_OK', json.dumps({k: report[k] for k in ('version', 'total_duration_ms')}),
          'grip_errors', [f['grip_error_L_m'] for f in frames])
    raise SystemExit(0)

frame = OUT / 'sora_sprite_pilot_512.png'
scene.render.filepath = str(frame)
bpy.ops.render.render(write_still=True)

# 128px export and side-by-side comparison with the approved idle frame on white.
img = bpy.data.images.load(str(frame))
small = img.copy(); small.scale(128, 128)
small.filepath_raw = str(OUT / 'sora_sprite_pilot_128.png'); small.file_format = 'PNG'; small.save()


def on_white(image):
    px = np.empty(image.size[0]*image.size[1]*4, dtype=np.float32); image.pixels.foreach_get(px)
    px = px.reshape(image.size[1], image.size[0], 4); a = px[..., 3:4]
    return np.concatenate([px[..., :3]*a + (1-a), np.ones_like(a)], axis=2)


idle = bpy.data.images.load(str(IDLE))
board = np.concatenate([on_white(idle), np.ones((512, 16, 4), np.float32), on_white(img)], axis=1)
cmp_img = bpy.data.images.new('comparison', board.shape[1], 512, alpha=True)
cmp_img.pixels.foreach_set(board.ravel())
cmp_img.filepath_raw = str(OUT / 'Approved_Idle_vs_Pilot.png'); cmp_img.file_format = 'PNG'; cmp_img.save()

alpha = np.empty(512*512*4, dtype=np.float32); img.pixels.foreach_get(alpha)
rows = np.where(alpha.reshape(512, 512, 4)[..., 3].max(1) > .5)[0]
blend = OUT / 'sora_sprite_pilot.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
report = {
    'version': version, 'blender': bpy.app.version_string, 'source': 'downloads/p_ex150.fbx + downloads/Kingdom Key/Kingdom Key.obj',
    'height_m': HEIGHT, 'key_grip_to_tip_m': KEY_REACH, 'camera_yaw_deg': CAM_YAW, 'ortho_scale': round(cam_data.ortho_scale, 4),
    'light_dir': [round(v, 3) for v in LIGHT], 'pose': POSE,
    'figure_rows_px': [int(511 - rows.max()), int(511 - rows.min())] if len(rows) else None,
    'outputs': ['sora_sprite_pilot_512.png', 'sora_sprite_pilot_128.png', 'Approved_Idle_vs_Pilot.png', blend.name],
}
(OUT / 'Pilot_Report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('PILOT_OK', json.dumps(report))
