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
GAIT = version if version.startswith(('walk_fwd_v', 'walk_back_v')) else None
if GAIT:
    # v1: one-handed battle_v2 stance. v2+ (Kvon): keep both hands on the Keyblade, so the walk
    # starts from the approved two-handed battle idle (battle_v12) with no grip change.
    version = 'battle_v2' if GAIT.endswith('_v1') else 'battle_v12'
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
        STRIDE, LIFT, SWING = .12, .06, .4  # half step length (m), foot lift (m), swing share of cycle
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
    for _ in range(4 if POSE.get('shoulder_reach') else 0):
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
    set_pose_world('center', Matrix.Translation((0, 0, -POSE['drop'] - b['drop']*breath)) @ pose_world('center'))
    if POSE.get('hunch_deg'):
        rotate_world('hara', ax_x, POSE['hunch_deg'])
    rotate_world('mune', ax_x, POSE['lean_deg'] + b['lean_deg']*breath)
    if POSE.get('neck_counter_deg'):
        rotate_world('kubi', ax_x, POSE['neck_counter_deg'])
    if b['head_counter_deg']:
        rotate_world('kubi', ax_x, b['head_counter_deg']*lag)
    if POSE.get('look_deg'):
        rotate_world('kubi', 'Z', POSE['look_deg'])  # eyes on the opponent
    r_hand = turn_m @ Vector(POSE['R_hand']) + Vector((0, 0, b['hands_z']*lag))
    l_hand = r_hand + blade*POSE['L_hand_along_handle']
    toe_out = POSE.get('toe_out_deg', 0)
    for s, foot in (('R', POSE['R_foot']), ('L', POSE['L_foot'])):
        sign = -1 if s == 'R' else 1
        toe = POSE.get('toe_deg', {}).get(s, toe_out)
        # Knees track over turned-out toes.
        knee = turn_m @ Vector((sign*(.3 + toe/50), -1, 0))
        lift = foot[2] or 0  # walk gait raises the swinging foot
        two_bone(f'{s}_momo', f'{s}_sune', f'{s}_ashi1', turn_m @ Vector((foot[0], foot[1], ankle_z + lift)), knee)
        if toe or turn:
            rotate_world(f'{s}_ashi1', 'Z', sign*toe + turn)  # feet don't inherit the body turn
    if POSE.get('head_tilt_deg'):
        rotate_world('atama', ax_y, POSE['head_tilt_deg'])  # top of head toward his left, as referenced
    hand_on('R', r_hand, (-1, .4, -.3))
    if ONE_HAND:
        guard_hint = turn_m @ Vector(POSE.get('L_elbow_hint', (1, .6, -.2)))
        two_bone('L_ude1', 'L_ude2', 'L_te', turn_m @ Vector(POSE['L_relaxed_wrist']), guard_hint)
    else:
        hand_on('L', l_hand, (1, .4, -.3))
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
        walk_dir = (turn_m.inverted() @ screen_right) * (1 if GAIT.startswith('walk_fwd') else -1)
        STANCE = {s: Vector((POSE[f'{s}_foot'][0], POSE[f'{s}_foot'][1], 0)) for s in ('R', 'L')}
        # The foot nearer the travel direction steps first; the other follows half a cycle later.
        leader = max(('R', 'L'), key=lambda s: STANCE[s].dot(walk_dir))

        def foot_at(side, phase):
            phase = (phase + (0 if side == leader else .5)) % 1
            if phase < SWING:  # swing: travel forward with a lift
                u = phase / SWING; u = u*u*(3 - 2*u)
                return -STRIDE + 2*STRIDE*u, LIFT*math.sin(math.pi*phase/SWING)
            return STRIDE - 2*STRIDE*(phase - SWING)/(1 - SWING), 0.0  # stance: planted, slides back
    for i in range(n):
        breath = (1 - math.cos(2*math.pi*i/n)) / 2
        # v3+: follow-through lag; a symmetric breath alone made frames 1-4 repeat as 9-6.
        lag = (1 - math.cos(2*math.pi*(i/n - BREATH_LAG))) / 2
        if GAIT:
            breath = (1 - math.cos(4*math.pi*i/n)) / 2  # one dip per step
            lag = (1 - math.cos(4*math.pi*(i/n - BREATH_LAG/2))) / 2
            for side in ('R', 'L'):
                offset, lift = foot_at(side, i/n)
                pos = STANCE[side] + walk_dir*offset
                POSE[f'{side}_foot'] = (pos.x, pos.y, lift)
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
