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
assert (ROOT / 'KingdomArena/project.godot').is_file(), ROOT  # project root (any clone)
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
# crouch_down_v* / crouch_hold_v*: from the approved battle idle, Sora sinks into a deep crouch with the
# Keyblade in the right hand only (Kvon: "One hand"): the left hand lets go of the handle and comes up
# as a guard fist, and the Key swings round behind him to point low toward screen left, away from the
# opponent. crouch_down eases idle -> crouch; crouch_hold is the crouched bounce loop. Standing up is
# crouch_down played backwards.
CROUCH = version if version.startswith(('crouch_down_v', 'crouch_hold_v')) else None
if CROUCH:
    version = 'battle_v12'
# run_start_v* / run_loop_v* / run_stop_v*: from Gemini's round-05 spec (Kvon asked for Gemini's support).
# Keyblade in the right hand, low behind the hip pointing back (screen left); left arm swings free.
# The body turns from the idle's -25 deg (facing the camera) to +30 deg (three-quarter toward screen right).
RUN = version if version.startswith(('run_start_v', 'run_loop_v', 'run_stop_v')) else None
# glide_start_v* / glide_loop_v* / glide_stop_v*: Kvon replaced the run with a low ground glide (October 23),
# from Gemini's concept art: push-off and skid landing from gemini_walk_review/round_18, the relaxed glide
# pose from round_19 for the loop. Built on the run machinery (as the v18 run), with its own poses.
GLIDE = version if version.startswith(('glide_start_v', 'glide_loop_v', 'glide_stop_v')) else None
if GLIDE:
    RUN = GLIDE.replace('glide_', 'run_').rsplit('_v', 1)[0] + '_v18'
# jump_<part>_v*: Sora's first (KH1-style) jump, October 26 - from Gemini's round-31 sheet (which Kvon judged a
# jump rather than a back-dash) and his air-pose references: takeoff, rising (ref_01), apex tuck (ref_02),
# falling with the Keyblade raised high (ref_03, Kvon's rule) and landing. Built on the run machinery; the
# drawings stay in place (the game moves him up and down).
JUMP = version if version.startswith(('jump_start_v', 'jump_rise_v', 'jump_apex_v', 'jump_fall_v', 'jump_land_v',
                                      'jump_spin_v', 'jump_dash_v', 'jump_bdash_v',
                                      'hurt_ground_v', 'hurt_air_v', 'hurt_fall_v', 'hurt_down_v',
                                      'hurt_getup_v', 'atk_slight_v', 'atk_smed_v', 'atk_sheavy_v',
                                      'atk_clight_v', 'atk_cmed_v')) else None
# Hurt set and the attacks share the whole-body machinery (spin/roll/ground) of the hurt recipes.
HURT = JUMP if JUMP and JUMP.startswith(('hurt_', 'atk_')) else None
if JUMP:
    RUN = 'run_loop_v18'
if RUN:
    version = 'battle_v12'
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
if RUN:
    # Holds per drawing (60 fps game frames), Gemini round 05.
    GAME_FRAMES = {'run_start': [2, 2, 3, 3], 'run_loop': [2, 3, 2, 3]*2,
                   'run_stop': [2, 3, 3, 3, 3]}[RUN.rsplit('_v', 1)[0]]
    if GLIDE and RUN.startswith('run_loop'):
        GAME_FRAMES = [3]*6  # smooth hover loop: 6 drawings x 3 game frames
    if JUMP:
        GAME_FRAMES = {'jump_start': [2, 2, 2], 'jump_rise': [4, 4], 'jump_apex': [6], 'jump_fall': [4, 4],
                       'jump_spin': [2]*11, 'jump_dash': [3, 4, 4, 3], 'jump_bdash': [2, 4, 4, 3, 4],
                       'jump_land': [3, 3, 4], 'hurt_ground': [2, 6, 5, 4], 'hurt_air': [4, 8],
                       'hurt_fall': [4, 4, 4], 'hurt_down': [3, 4, 6],
                       'hurt_getup': [5, 4, 4, 4, 4], 'atk_slight': [2, 4, 3, 3],
                       'atk_smed': [2, 2, 3, 3, 2, 3, 4, 4, 4],
                       # Standing Heavy: Ekko's heavy timing - startup 13 (7 drawings), active 3, recovery 21.
                       'atk_sheavy': [1, 2, 3, 2, 2, 1, 2, 3, 6, 9, 6],
                       'atk_clight': [2, 3, 3, 4, 4, 4], 'atk_cmed': [6, 6, 6]}[JUMP.rsplit('_v', 1)[0]]
        if JUMP.startswith('hurt_fall') and not JUMP.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
            GAME_FRAMES = [3, 4, 4, 4]  # v6: horizontal in-between first
        if JUMP.startswith('jump_fall') and not JUMP.endswith(('_v1', '_v2', '_v3')):
            GAME_FRAMES = [3, 3, 4]  # v4: in-between + the two falling drawings
    DURATIONS_MS = [round(f*1000/60, 3) for f in GAME_FRAMES]
if CROUCH:
    # Full-crouch targets; drawings blend toward them by CR_T (0 = battle idle, 1 = crouched).
    CR = {'crouch_extra': .22, 'hunch_extra': 6, 'pitch_extra': 8, 'neck_extra': -8, 'knee_splay': .4,
          'R_hand': (-.26, .06, .62), 'L_guard': (.10, -.30, .98), 'blade_down_tip_m': .10}
    if not CROUCH.endswith('_v1'):
        # v2+: v1's head dropped only ~30 render px; sink much lower and hunch more.
        CR.update({'crouch_extra': .32, 'hunch_extra': 9, 'pitch_extra': 10, 'neck_extra': -12, 'knee_splay': .6})
    CR_BEHIND = .45
    if not CROUCH.endswith(('_v1', '_v2')):
        # v3+: v2's fist sat at knee height behind the right thigh and the tip nearly left the frame:
        # fist higher and outside the hip, blade angled further behind him (foreshortened).
        CR.update({'R_hand': (-.36, .10, .82), 'blade_down_tip_m': .14})
        CR_BEHIND = .85
    if not CROUCH.endswith(('_v1', '_v2', '_v3')):
        # v4+: in the v3 hold loop the tip reached the frame's left edge; turn it further behind him.
        CR_BEHIND = 1.4
    if CROUCH.startswith('crouch_down'):
        # 7 drawings (Kvon's 7-12 drawing transitions), 12 game frames: quick out of the idle, settling in.
        CR_T = [u_*u_*(3 - 2*u_) for u_ in [(i_ + 1)/8 for i_ in range(7)]]
        GAME_FRAMES = [2, 1, 1, 1, 2, 2, 3]
    else:
        CR_T = [1.0]*8
        GAME_FRAMES = [6, 5, 5, 7, 6, 5, 5, 7]
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
    if POSE.get('screen_lean_deg'):
        # Hurt v2+: knock the upper body back toward screen left in the screen plane (a lean about his own side axis
        # mostly goes into the screen from this three-quarter camera and barely showed in v1).
        rotate_world('hara', to_cam, POSE['screen_lean_deg'])
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
    if POSE.get('screen_head_deg'):
        rotate_world('kubi', to_cam, POSE['screen_head_deg'])  # hurt v2+: head thrown back on screen
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
        if POSE.get('knee_hint_world', {}).get(s) is not None:
            # Kneeling crouch (v6+): this knee points where given in world terms (down and forward to the floor).
            knee = knee.lerp(Vector(POSE['knee_hint_world'][s]), POSE.get('knee_hint_w', 1.0))
        lift = foot[2] or 0  # walk gait raises the swinging foot
        foot_t = turn_m @ Vector((foot[0], foot[1], ankle_z + lift))
        if POSE.get('leg_reach'):
            # Hurt (Kvon: legs mostly straight in the air hit and the fall): the foot goes to this fraction of the full
            # leg length along its direction from the hip, so the knee keeps only a slight bend.
            hip_l = pose_world(f'{s}_momo').translation
            len_l = ((pose_world(f'{s}_sune').translation - hip_l).length
                     + (pose_world(f'{s}_ashi1').translation - pose_world(f'{s}_sune').translation).length)
            foot_t = hip_l + (foot_t - hip_l).normalized()*len_l*POSE['leg_reach']
        two_bone(f'{s}_momo', f'{s}_sune', f'{s}_ashi1', foot_t, knee)
        if toe or turn:
            rotate_world(f'{s}_ashi1', 'Z', sign*toe + turn)  # feet don't inherit the body turn
    if POSE.get('hip_back_deg'):
        # Hurt (Kvon): swing both legs backward at the hip joints about his side-to-side axis.
        for s_h in ('L', 'R'):
            rotate_world(f'{s_h}_momo', (turn_m @ Vector((1, 0, 0))).normalized(), POSE['hip_back_deg'])
    for side, deg in POSE.get('foot_pitch', {}).items():
        if deg:
            # Heel up about the ankle, toes down (the ankle target was raised to keep toes on the floor).
            ankle = pose_world(f'{side}_ashi1').translation
            fwd = pose_world(f'{side}_ashi2').translation - ankle; fwd.z = 0; fwd.normalize()
            rotate_world(f'{side}_ashi1', fwd.cross(Vector((0, 0, 1))).normalized(), -deg)
    if POSE.get('ankle_deg') is not None:
        # Hurt (Kvon: straighten the ankles): turn each foot in the shin/foot plane so the foot leaves the shin's line
        # at this angle (0 = fully pointed in line with the shin, 90 = a neutral right-angle ankle).
        # A dict gives a per-side angle (Crouching Medium: only the back foot).
        ad_ = POSE['ankle_deg'] if isinstance(POSE['ankle_deg'], dict) else {'L': POSE['ankle_deg'], 'R': POSE['ankle_deg']}
        for s_a, deg_a in ad_.items():
            ank_ = pose_world(f'{s_a}_ashi1').translation
            shin_ = (ank_ - pose_world(f'{s_a}_sune').translation).normalized()
            foot_ = (pose_world(f'{s_a}_ashi2').translation - ank_).normalized()
            ax_a = shin_.cross(foot_)
            if ax_a.length > 1e-4:
                rotate_world(f'{s_a}_ashi1', ax_a.normalized(), deg_a - math.degrees(shin_.angle(foot_)))
    for s_t, deg_t in (POSE.get('toe_bend') or {}).items():
        # Crouching Medium (Kvon: a bend in the front foot's toes): the toe bone turns back flat onto the floor after
        # the heel was lifted by foot_pitch, so the foot bends at the ball.
        ank_ = pose_world(f'{s_t}_ashi1').translation
        fwd_ = pose_world(f'{s_t}_ashi2').translation - ank_; fwd_.z = 0; fwd_.normalize()
        rotate_world(f'{s_t}_ashi2', fwd_.cross(Vector((0, 0, 1))).normalized(), deg_t)
    if POSE.get('head_yaw_cancel') and POSE.get('chest_twist_deg'):
        rotate_world('kubi', 'Z', -POSE['chest_twist_deg'])  # v19+: face stays on the opponent
    if POSE.get('L_shrug_deg'):
        # Glide v28+: raise only the left shoulder (collarbone up) before the arm is solved.
        kh_ = pose_world('L_kata').translation
        kd_ = pose_world('L_ude1').translation - kh_
        rotate_world('L_kata', kd_.cross(Vector((0, 0, 1))).normalized(), POSE['L_shrug_deg'])
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
    hand_on('R', r_hand, POSE.get('R_elbow_hint_world') or (-1, .4, -.3))  # jump land v3+: elbow can point out
    if ONE_HAND:
        guard_hint = turn_m @ Vector(POSE.get('L_elbow_hint', (1, .6, -.2)))
        two_bone('L_ude1', 'L_ude2', 'L_te', turn_m @ Vector(POSE['L_relaxed_wrist']), guard_hint)
    elif POSE.get('L_arm'):
        # Crouching Light v30+: the free arm set directly by shape, not by a hand target - the shoulder -> wrist
        # direction and elbow side from a reference drawing, turned with the shoulder line, and an exact elbow fold
        # (0 = straight). No shoulder reach, so the fold is what's asked for.
        la_ = POSE['L_arm']
        sh_l, sh_r = pose_world('L_ude1').translation, pose_world('R_ude1').translation
        yaw_ = math.degrees(math.atan2((sh_l - sh_r).y, (sh_l - sh_r).x))
        rot_ = Matrix.Rotation(math.radians(yaw_ - la_['ref_yaw']), 3, 'Z')
        h_ = sh_l.copy()
        l1_ = (pose_world('L_ude2').translation - h_).length
        l2_ = (pose_world('L_te').translation - pose_world('L_ude2').translation).length
        inner_ = math.radians(180 - la_['fold'])
        dist_ = math.sqrt(l1_*l1_ + l2_*l2_ - 2*l1_*l2_*math.cos(inner_))
        two_bone('L_ude1', 'L_ude2', 'L_te', h_ + (rot_ @ Vector(la_['dir'])).normalized()*dist_,
                 rot_ @ Vector(la_['elbow']))
    elif POSE.get('L_free'):
        # Crouch: the left hand slides off the handle toward its free guard spot.
        l_target, l_w = POSE['L_free']
        hand_on('L', l_hand.lerp(Vector(l_target) - Vector((0, 0, POSE.get('crouch_extra', 0))), l_w),
                POSE.get('L_elbow_hint_world', (1, .4, -.3)))  # glide v22+: elbow hint can point lower
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
        for side in [s for s in GRIP_SIDES if not (s == 'L' and POSE.get('L_palm_to_camera'))
                     and not (s == 'R' and POSE.get('wrist_roll') is not None)]:
            m = pose_world(f'{side}_te'); head = m.translation.copy()
            f = (pose_world(f'{side}_yubiB').translation - head).normalized()
            across = f - blade*f.dot(blade)
            if across.length > 1e-3:
                turn = f.rotation_difference(across.normalized())
                set_pose_world(f'{side}_te', Matrix.Translation(head) @ turn.to_matrix().to_4x4()
                               @ Matrix.Translation(-head) @ m)
    if POSE.get('wrist_roll') is not None:
        # Glide v16+: a straight wrist - the hand keeps the forearm's direction and only rolls about it; the Key
        # then sits wherever that straight grip puts it.
        fore_w = (pose_world('R_te').translation - pose_world('R_ude2').translation).normalized()
        rotate_world('R_te', fore_w, POSE['wrist_roll'])
    if POSE.get('r_hand_rot'):
        # Crouch: the right fist keeps the idle grip on the Key and turns with it as one piece; the
        # forearm takes half of the roll so the wrist doesn't candy-wrap.
        rot = Matrix(POSE['r_hand_rot'])
        for pass_ in range(4):
            if pass_ == 0:
                elbow = pose_world('R_ude2').translation; wrist = pose_world('R_te').translation
                fore = (wrist - elbow).normalized()
                delta = (rot @ pose_world('R_te').to_3x3().inverted()).to_quaternion()
                twist = math.degrees(2*math.atan2(Vector(delta[1:]).dot(fore), delta[0]))
                rotate_world('R_ude2', fore, ((twist + 180) % 360 - 180)/2)
            set_pose_world('R_te', Matrix.Translation(pose_world('R_te').translation) @ rot.to_4x4())
            # Turning the fist moves its centre off the grip point: move the wrist back onto it.
            miss = r_hand - hand_point('R')
            if miss.length < .003:
                break
            two_bone('R_ude1', 'R_ude2', 'R_te', pose_world('R_te').translation + miss, (-1, .4, -.3))
        set_pose_world('R_te', Matrix.Translation(pose_world('R_te').translation) @ rot.to_4x4())
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
    if RUN:
        LAG0 = (1 - math.cos(2*math.pi*(0 - .12))) / 2  # idle frame 1, as the shuffle/crouch start
        solve_pose(0.0, LAG0)
        place_key()
        CR_TE0 = pose_world('R_te').to_3x3()
        CR_KEY_IN_TE = pose_world('R_te').inverted() @ key.matrix_world
        CR_BLADE0 = blade.copy()
        U_ = Vector((math.cos(t), math.sin(t), 0))  # travel direction (screen right)
        V_ = to_cam.copy(); V_.z = 0; V_.normalize()  # across the track, toward the camera

        def to_w(turn_deg, xy):
            # body-frame floor point -> (along travel, across) relative to the hips
            w = Matrix.Rotation(math.radians(turn_deg), 3, 'Z') @ Vector((xy[0], xy[1], 0))
            return (w.dot(U_), w.dot(V_))

        def to_body(turn_deg, sl):
            w = U_*sl[0] + V_*sl[1]
            b_ = Matrix.Rotation(math.radians(turn_deg), 3, 'Z').inverted() @ w
            return (b_.x, b_.y)

        TOE_D = 1.5*(pose_world('L_ashi2').translation - pose_world('L_ashi1').translation).length
        IDLE_R = dict(turn=POSE['body_turn_deg'], ce=0.0, hunch=0.0, pitch=0.0, neck=0.0,
                      look=POSE.get('look_deg', 0), tilt=POSE.get('head_tilt_deg', 0), toe=35.0, twist=0.0,
                      feet={'L': (*to_w(POSE['body_turn_deg'], POSE['L_foot']), 0.0, 0.0),
                            'R': (*to_w(POSE['body_turn_deg'], POSE['R_foot']), 0.0, 0.0)},
                      hand=Matrix.Rotation(math.radians(POSE['body_turn_deg']), 3, 'Z') @ Vector(POSE['R_hand']),
                      release=0.0, arm=0.0, blade_s=0.0, hz=0.0)
        if JUMP:
            # Jump (Kvon: the Key elbow bent too far inward on landing): the real idle's fist ends up a little off its
            # aim point after the wrist is squared, and this machinery aims at the unsettled point - the rebuilt idle
            # grip sat further across his body. Use the real idle's measured fist position instead.
            solve_pose(0.0, LAG0)
            IDLE_R['hand'] = hand_point('R') - Vector((0, 0, BREATH['hands_z']*LAG0))
        RUN_TURN = 30.0
        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 11))):
            # v11+ (Gemini round 14, after Kvon said v8 didn't match its poses at all): turn him nearly side-on
            # (+50 deg is exact profile on this camera) so the legs' silhouette and stride show.
            RUN_TURN = 48.0
        # Run blade: back toward screen left, angled out toward the camera so it breaks his silhouette, -10 deg.
        hb = (-U_*.9 + V_*.35).normalized()
        RUN_BLADE = (hb*math.cos(math.radians(-10)) + Vector((0, 0, math.sin(math.radians(-10))))).normalized()
        CR_YAW0 = math.atan2(CR_BLADE0.y, CR_BLADE0.x)
        CR_EL0 = math.asin(max(-1, min(1, CR_BLADE0.z)))
        yaw1 = math.atan2(RUN_BLADE.y, RUN_BLADE.x)
        cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
        cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
        CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(-V_))
        CR_EL1 = math.asin(RUN_BLADE.z)
        RUN_HAND = Matrix.Rotation(math.radians(RUN_TURN), 3, 'Z') @ Vector((-.24, .12, .70))
        ARM_BACK = Matrix.Rotation(math.radians(RUN_TURN), 3, 'Z') @ Vector((.20, .24, .86))
        ARM_FWD = Matrix.Rotation(math.radians(RUN_TURN), 3, 'Z') @ Vector((.10, -.30, 1.00))
        LAT = {'L': -.09, 'R': .09}  # left foot on the far side of the track
        # Loop half with the left foot planted: (planted s, lift, toe pitch), (swing s, lift, pitch),
        # total hip drop (m), chest-twist weight, free-arm back amount, root motion (m) as the drawing starts.
        HALF = [((.25, 0, 0), (-.25, 0, 30), .16, 1.0, 1.0, .15),    # contact
                ((.15, 0, 0), (-.35, .08, 20), .22, .6, .5, .10),    # down
                ((0.0, 0, 15), (0.0, .20, 0), .12, 0.0, -.3, .15),   # passing (high knee)
                ((-.10, .03, 30), (.20, .10, 0), .07, -.5, -.8, .10)]  # flight

        RUN_PITCH = 4.0
        if not RUN.endswith('_v1'):
            # v2+: v1's blade stuck straight out to screen left past the frame edge, the torso read upright
            # and the steps looked short: blade angled down and out toward the camera (foreshortened), more
            # forward lean, a longer reach on contact (roots re-balanced to keep the planted foot fixed).
            hb = (-U_*.7 + V_*.75).normalized()
            RUN_BLADE = (hb*math.cos(math.radians(-32)) + Vector((0, 0, math.sin(math.radians(-32))))).normalized()
            yaw1 = math.atan2(RUN_BLADE.y, RUN_BLADE.x)
            cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
            cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
            CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(-V_))
            CR_EL1 = math.asin(RUN_BLADE.z)
            RUN_PITCH = 12.0
            HALF = [((.30, 0, 0), (-.20, 0, 30), .17, 1.0, 1.0, .10),
                    ((.18, 0, 0), (-.32, .08, 20), .23, .6, .5, .12),
                    ((.03, 0, 15), (0.0, .20, 0), .13, 0.0, -.3, .15),
                    ((-.10, .03, 30), (.25, .10, 0), .08, -.5, -.8, .13)]

        RUN_HUNCH = -4.0
        if not RUN.endswith(('_v1', '_v2')):
            # v3+: v2 still read upright and its passing drawings stacked one foot on the other: lean from the
            # hips, and tuck the swinging foot up behind him (knee forward) before it reaches out.
            RUN_HUNCH, RUN_PITCH = 6.0, 16.0
            HALF[2] = ((.03, 0, 15), (-.14, .26, 0), .13, 0.0, -.3, .15)
            HALF[3] = ((-.10, .03, 30), (.22, .14, 0), .08, -.5, -.8, .13)

        if not RUN.endswith(('_v1', '_v2', '_v3')):
            # v4+ (Gemini round 06): less lean (v1's lean read upright on screen, so about halfway), a smaller
            # hip bounce, the passing foot nearer under the hips, a longer reach, a flatter blade that still
            # fits the frame. Roots re-balanced so the planted foot stays still.
            RUN_HUNCH, RUN_PITCH = 0.0, 8.0
            HALF = [((.35, 0, 0), (-.15, 0, 30), .12, 1.0, 1.0, .09),
                    ((.23, 0, 0), (-.28, .08, 20), .16, .6, .5, .12),
                    ((.07, 0, 15), (-.06, .20, 0), .08, 0.0, -.3, .16),
                    ((-.06, .03, 30), (.25, .12, 0), .04, -.5, -.8, .13)]
            hb = (-U_*.85 + V_*.5).normalized()
            RUN_BLADE = (hb*math.cos(math.radians(-24)) + Vector((0, 0, math.sin(math.radians(-24))))).normalized()
            yaw1 = math.atan2(RUN_BLADE.y, RUN_BLADE.x)
            cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
            cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
            CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(-V_))
            CR_EL1 = math.asin(RUN_BLADE.z)

        if not RUN.endswith(('_v1', '_v2', '_v3', '_v4')):
            # v5+: v4's contact leg was nearly locked (0.687 of 0.693 m) and the tip touched the frame edge.
            HALF[0] = (HALF[0][0], HALF[0][1], .14, *HALF[0][3:])
            hb = (-U_*.8 + V_*.6).normalized()
            RUN_BLADE = (hb*math.cos(math.radians(-27)) + Vector((0, 0, math.sin(math.radians(-27))))).normalized()
            yaw1 = math.atan2(RUN_BLADE.y, RUN_BLADE.x)
            cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
            cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
            CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(-V_))
            CR_EL1 = math.asin(RUN_BLADE.z)

        RUN_NECK, ARM_STATIC, TWIST_AMP = -10.0, None, 8.0
        if not RUN.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
            # v6+ (Kvon: match the running poses Gemini generated, round 09/10): steeper aerodynamic lean,
            # static arms (left fist forward as a chest guard, right fist behind the hip) with the blade
            # pointing BACK AND UP, the swing heel kicked up behind on passing, a smaller hip bounce.
            RUN_HUNCH, RUN_PITCH, RUN_NECK, TWIST_AMP = 6.0, 14.0, -25.0, 0.0
            ARM_STATIC = -1.0  # -1 = the forward guard position for the whole loop
            HALF = [((.35, 0, 0), (-.15, 0, 30), .14, 1.0, 1.0, .09),
                    ((.23, 0, 0), (-.30, .10, 30), .16, .6, .5, .12),
                    ((.07, 0, 15), (-.15, .25, 0), .12, 0.0, -.3, .16),
                    ((-.06, .03, 30), (.22, .12, 0), .10, -.5, -.8, .13)]
            RUN_HAND = U_*-.20 + V_*.22 + Vector((0, 0, .80))
            hb = (-U_*.62 + V_*.78).normalized()
            RUN_BLADE = (hb*math.cos(math.radians(12)) + Vector((0, 0, math.sin(math.radians(12))))).normalized()
            yaw1 = math.atan2(RUN_BLADE.y, RUN_BLADE.x)
            cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
            cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
            CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(-V_))
            CR_EL1 = math.asin(RUN_BLADE.z)

        if not RUN.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6')):
            # v7+: v6 still ran tall and upright next to Gemini's poses: much deeper lean and lower hips, a
            # longer reach, and the push-off leg leaves the ground at flight and stays kicked up and back
            # until it swings through (no planted trailing toe). ~594 px/s (0.55 m per step).
            RUN_HUNCH, RUN_PITCH, RUN_NECK = 20.0, 20.0, -30.0
            HALF = [((.40, 0, 0), (-.30, .15, 0), .20, 1.0, 1.0, .13),
                    ((.27, 0, 0), (-.32, .22, 0), .24, .6, .5, .13),
                    ((.10, 0, 15), (-.12, .25, 0), .16, 0.0, -.3, .17),
                    ((-.22, .08, 20), (.25, .12, 0), .14, -.5, -.8, .12)]

        if not RUN.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7')):
            # v8+ (v9 changes only the start/stop blade timing) (Gemini round 11: v7 overshot): lean about 56 deg total, hips higher, a longer recovery arc
            # with the passing foot nearer under the hips, the blade nearly level (still a touch up, like
            # Gemini's picture) and the guard fist lower, at the ribs.
            RUN_HUNCH, RUN_PITCH, RUN_NECK = 14.0, 14.0, -30.0
            HALF = [((.38, 0, 0), (-.30, .14, 0), .16, 1.0, 1.0, .13),
                    ((.25, 0, 0), (-.30, .20, 0), .20, .6, .5, .13),
                    ((.08, 0, 15), (-.06, .20, 0), .12, 0.0, -.3, .17),
                    ((-.20, .08, 20), (.25, .10, 0), .10, -.5, -.8, .12)]
            ARM_FWD = Matrix.Rotation(math.radians(RUN_TURN), 3, 'Z') @ Vector((.10, -.30, .90))
            RUN_BLADE = (hb*math.cos(math.radians(6)) + Vector((0, 0, math.sin(math.radians(6))))).normalized()
            yaw1 = math.atan2(RUN_BLADE.y, RUN_BLADE.x)
            cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
            cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
            CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(-V_))
            CR_EL1 = math.asin(RUN_BLADE.z)

        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 11))):
            # v11+: a sprint, not a crouched sneak. Hips high (lowest 0.12 m on the down drawing), legs nearly
            # straight on contact, the swing knee drives high and FORWARD on passing (foot ahead of the hips,
            # toes down), the push-off leg kicks up behind through flight. Lean ~42 deg, guard fist loose at
            # the waist. Planted foot fixed: roots .12/.18 while planted, .13/.12 through flight (594 px/s).
            RUN_HUNCH, RUN_PITCH, RUN_NECK = 6.0, 8.0, -20.0
            HALF = [((.30, 0, 0), (-.32, .12, 20), .09, 1.0, 1.0, .12),
                    ((.18, 0, 0), (-.36, .22, 30), .12, .6, .5, .12),
                    ((0.0, 0, 10), (.12, .25, 25), .04, 0.0, -.3, .18),
                    ((-.26, .14, 30), (.28, .08, 0), .02, -.5, -.8, .13)]
            ARM_FWD = Matrix.Rotation(math.radians(RUN_TURN), 3, 'Z') @ Vector((.12, -.24, .82))
            RUN_HAND = U_*-.18 + V_*.22 + Vector((0, 0, .82))

        RUN_LOOK = 0.0
        RUN_LOOK_DEG = float(ARGS[2]) if len(ARGS) > 2 else -20.0  # head turn toward the camera (sign checked by render)
        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 12))):
            # v12+: v11 tipped the head down and away (top of the hair showed, not the face): lift the head
            # to look ahead and turn it a little toward the camera, as in Gemini's poses.
            RUN_NECK, RUN_LOOK = -34.0, RUN_LOOK_DEG

        PITCH_J, HZ_J = [0, 0, 0, 0], [0, 0, 0, 0]
        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 13))):
            # v13+ (Gemini round 15): passing foot under the hips (no marching kick-out), flight foot
            # reaches the full stride, head faces the run direction, the torso compresses on landing and
            # stretches in the air, the Key lags the body's bounce. Contact refit to the longer reach.
            RUN_LOOK = 0.0
            HALF = [((.28, 0, 0), (-.32, .12, 20), .09, 1.0, 1.0, .12),
                    ((.16, 0, 0), (-.36, .22, 30), .12, .6, .5, .12),
                    ((-.02, 0, 10), (-.03, .25, 25), .04, 0.0, -.3, .18),
                    ((-.26, .14, 30), (.40, .08, 0), .02, -.5, -.8, .13)]
            PITCH_J, HZ_J = [0, 3, 0, -3], [0, .05, 0, -.05]

        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 14))):
            # v14+: in v13 the collar and hair hid the face (Gemini's poses show the face in profile, chin up)
            # and the reaching flight leg locked straight (0.692 of 0.693 m): chin up, a slight turn toward
            # the camera (half v12's), hips a little lower in flight.
            RUN_NECK, RUN_LOOK = -44.0, RUN_LOOK_DEG/2
            HALF[3] = (HALF[3][0], HALF[3][1], .05, *HALF[3][3:])

        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 15))):
            # v15+: the +0.40 flight reach was beyond the leg (IK clamped it straight); +0.36, contact refit.
            HALF[0] = ((.26, 0, 0), *HALF[0][1:])
            HALF[1] = ((.14, 0, 0), *HALF[1][1:])
            HALF[2] = ((-.04, 0, 10), *HALF[2][1:])
            HALF[3] = (HALF[3][0], (.36, .08, 0), *HALF[3][2:])

        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 16))):
            # v16+ (Gemini round 16): the jacket and shorts swallow the lean and the knee, so over-rotate.
            # Spine pitched until the measured on-screen back angle reaches Gemini's 45-50 deg; the passing
            # knee cheated forward through the shorts; wider scissor at contact and flight; blade tip up.
            RUN_HUNCH, RUN_PITCH, RUN_NECK = 16.0, 19.0, -48.0
            HALF = [((.26, 0, 0), (-.35, .12, 20), .12, 1.0, 1.0, .12),
                    ((.14, 0, 0), (-.38, .22, 30), .14, .6, .5, .12),
                    ((-.04, 0, 10), (.10, .28, 45), .06, 0.0, -.3, .18),
                    ((-.38, .21, 30), (.36, .08, 0), .05, -.5, -.8, .13)]
            ARM_FWD = Matrix.Rotation(math.radians(RUN_TURN), 3, 'Z') @ Vector((.12, -.34, .84))
            RUN_BLADE = (hb*math.cos(math.radians(18)) + Vector((0, 0, math.sin(math.radians(18))))).normalized()
            yaw1 = math.atan2(RUN_BLADE.y, RUN_BLADE.x)
            cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
            cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
            CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(-V_))
            CR_EL1 = math.asin(RUN_BLADE.z)

        if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 17))):
            # v17+: v16 measured 39-43 deg on screen; a few more degrees to reach Gemini's 45-50.
            RUN_HUNCH, RUN_PITCH, RUN_NECK = 19.0, 23.0, -54.0

        def loop_key(j):
            plant, swing = ('L', 'R') if j < 4 else ('R', 'L')
            sign = 1 if j < 4 else -1
            pl, sw, drop_, tw, armb, root = HALF[j % 4]
            feet = {plant: (pl[0], LAT[plant], pl[1], pl[2]), swing: (sw[0], LAT[swing], sw[1], sw[2])}
            return dict(turn=RUN_TURN, ce=drop_ - POSE['drop'], hunch=RUN_HUNCH, pitch=RUN_PITCH + PITCH_J[j % 4], neck=RUN_NECK, look=RUN_LOOK,
                        tilt=0.0, toe=8.0, twist=TWIST_AMP*tw*sign, feet=feet, hand=RUN_HAND.copy(), release=1.0,
                        arm=armb*sign if ARM_STATIC is None else ARM_STATIC, blade_s=1.0, hz=0.0, root=root)

        def mix(a, b, w):
            out = {k_: a[k_] + (b[k_] - a[k_])*w for k_ in ('turn', 'ce', 'hunch', 'pitch', 'neck', 'look', 'tilt',
                                                          'toe', 'twist', 'release', 'arm', 'blade_s', 'hz')}
            out['hand'] = a['hand'].lerp(b['hand'], w)
            out['feet'] = {sd: tuple(a['feet'][sd][c_] + (b['feet'][sd][c_] - a['feet'][sd][c_])*w for c_ in range(4))
                           for sd in ('L', 'R')}
            return out

        if GLIDE:
            # Relaxed glide (round 19): body tilted forward at an easy diagonal, hovering low; knees soft, one
            # leg trailing low behind, the other tucked; left arm loose out behind; Keyblade in the right hand
            # low in front, blade angled down toward screen right (as drawn); constant ~600 px/s.
            G_SPEED = 600/180.5/60*3  # metres per 3-frame drawing
            G_HAND = U_*.06 + V_*.24 + Vector((0, 0, .72))
            G_ARM = Matrix.Rotation(math.radians(RUN_TURN), 3, 'Z') @ Vector((.32, .24, .88))
            hb_g = (U_*.8 + V_*.6).normalized()
            G_BLADE = (hb_g*math.cos(math.radians(-30)) + Vector((0, 0, math.sin(math.radians(-30))))).normalized()
            yaw_g = math.atan2(G_BLADE.y, G_BLADE.x)
            CR_DYAW = min([yaw_g - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)], key=abs)  # shortest turn
            CR_EL1 = math.asin(G_BLADE.z)
            ARM_BACK = G_ARM

            # v2+: v1's legs bunched under him (read as a crouched hop): lean further and stretch the trailing
            # leg back and low, the other knee softly tucked, as in the drawing.
            G_LEGS = ((-.30, .09, 20.0), (-.10, .22, 35.0), .14, 12.0, 14.0) if GLIDE.endswith('_v1') else                 ((-.42, .07, 25.0), (-.20, .20, 40.0), .10, 16.0, 20.0)
            G_TURN = RUN_TURN
            if not GLIDE.endswith(('_v1', '_v2')):
                # v3+: the drawing is three-quarter (chest toward the camera) with the legs split wide: trailing
                # leg far back and low, the other knee tucked forward under the hips; hips a little lower so the
                # long trailing leg still reaches.
                G_TURN = 20.0
                G_LEGS = ((-.46, .06, 20.0), (.02, .18, 35.0), .18, 16.0, 20.0)
            if not GLIDE.endswith(('_v1', '_v2', '_v3')):
                # v4+: in the drawing the NEAR leg (his right, toward the camera) trails far back and low and the far
                # knee is tucked; the Key hand sits low at the hip instead of covering the chest.
                G_LEGS = ((.02, .18, 35.0), (-.46, .06, 20.0), .18, 16.0, 20.0)
                G_HAND = U_*.14 + V_*.26 + Vector((0, 0, .58))
            G_NECK = -40.0
            if not GLIDE.endswith(('_v1', '_v2', '_v3', '_v4')):
                # v5+ (Gemini round 20, the parts that agree with its drawing): softer trailing knee (-0.30 m), the
                # tucked knee under/behind the hips (-0.12 m) instead of leading, ~45 deg on-screen lean, face ahead.
                # Not taken: its "left hand forward" and "blade backward" contradict its own relaxed-glide drawing.
                G_LEGS = ((-.12, .18, 35.0), (-.30, .06, 20.0), .16, 19.0, 24.0)
                G_NECK = -48.0
            if not GLIDE.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                # v6+: v5 looked compact next to the drawing's wide spread. The -0.46 m trail was not locked
                # (0.56 of the 0.69 m leg, measured), so the long trailing leg comes back; tucked knee under the hips.
                G_LEGS = ((-.08, .20, 35.0), (-.44, .05, 20.0), .17, 19.0, 24.0)
            G_V7 = not GLIDE.endswith(tuple(f'_v{n_}' for n_ in range(1, 7)))
            if G_V7:
                # v7+ (Gemini round 21, all six applied at Kvon's request; he chose a pure side profile):
                # full side profile; legs staggered and skimming lower (near -0.35 m / 3 cm up, far -0.15 m /
                # 12 cm up); blade -30 deg tucked flat to his side (5 deg flare); left elbow softly bent.
                # The landing leans back and the push-off ends in a full stretch (below).
                G_TURN = 55.0
                G_LEGS = ((-.15, .12, 30.0), (-.35, .03, 20.0), .17, 19.0, 24.0)
                G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.22, .14, .88))
                ARM_BACK = G_ARM
                hb_g = (U_*math.cos(math.radians(5)) + V_*math.sin(math.radians(5))).normalized()
                G_BLADE = (hb_g*math.cos(math.radians(-30)) + Vector((0, 0, math.sin(math.radians(-30))))).normalized()
                yaw_g = math.atan2(G_BLADE.y, G_BLADE.x)
                CR_DYAW = min([yaw_g - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)], key=abs)
                CR_EL1 = math.asin(G_BLADE.z)

            if not GLIDE.endswith(tuple(f'_v{n_}' for n_ in range(1, 8))):
                # v8+: +55 turned past profile (his back and the back of his head showed) - +50 is exact profile on
                # this camera; the in-plane blade ran to the frame's right edge: hand a little back, blade -36 deg.
                G_TURN = 50.0
                G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.22, .14, .88))
                ARM_BACK = G_ARM
                G_HAND = U_*.02 + V_*.26 + Vector((0, 0, .60))
                G_BLADE = (hb_g*math.cos(math.radians(-36)) + Vector((0, 0, math.sin(math.radians(-36))))).normalized()
                yaw_g = math.atan2(G_BLADE.y, G_BLADE.x)
                CR_DYAW = min([yaw_g - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)], key=abs)
                CR_EL1 = math.asin(G_BLADE.z)

            if not GLIDE.endswith(tuple(f'_v{n_}' for n_ in range(1, 9))):
                G_HAND = U_*.02 + V_*.26 + Vector((0, 0, .67))  # v9+: v8's blade tip dipped below the floor line
            G_V10 = not GLIDE.endswith(tuple(f'_v{n_}' for n_ in range(1, 10)))
            if G_V10:
                # v10+ (instructions agreed with Gemini, rounds 23-24, built at Kvon's "Yes"): loop three-quarter
                # with the chest toward the viewer (+20), Key low at the right hip with the blade forward-down,
                # left arm trailing behind with the elbow almost straight, soft knees with the feet behind/below a
                # few cm up, back 40-45 deg, face toward screen right. (Loop = v6's pose with a straighter left arm.)
                G_TURN = 20.0
                G_LEGS = ((-.08, .20, 35.0), (-.44, .05, 20.0), .17, 19.0, 24.0)
                G_HAND = U_*.14 + V_*.26 + Vector((0, 0, .58))
                G_NECK = -48.0
                G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.30, .42, .84))
                ARM_BACK = G_ARM
                hb_g = (U_*.8 + V_*.6).normalized()
                G_BLADE = (hb_g*math.cos(math.radians(-30)) + Vector((0, 0, math.sin(math.radians(-30))))).normalized()
                yaw_g = math.atan2(G_BLADE.y, G_BLADE.x)
                CR_DYAW = min([yaw_g - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)], key=abs)
                CR_EL1 = math.asin(G_BLADE.z)
            # v11+ (Kvon: "changes nothing but the angle at which Sora is facing the screen by small amounts"):
            # the same v10 glide with only the loop's body turn changed; each version is one small step.
            G_TURN_STEPS = {'_v11': 10.0, '_v12': 0.0, '_v13': -10.0, '_v14': -10.0, '_v15': -10.0, '_v16': -10.0, '_v17': -10.0, '_v18': -10.0, '_v19': -10.0, '_v20': -10.0, '_v21': -10.0, '_v22': -10.0, '_v23': -10.0, '_v24': -10.0, '_v25': -10.0, '_v26': -10.0, '_v27': -10.0, '_v28': -10.0, '_v29': -10.0, '_v30': -10.0, '_v31': -10.0, '_v32': -10.0, '_v33': -10.0, '_v34': -10.0, '_v35': -10.0}
            G_SPIN = Matrix.Identity(3)  # turns the whole v10 figure (feet, hand, blade, arm) with the body
            # v14 (Kvon: keep attempt 3's body but turn the head back to attempt 2's angle): body -10, head +10
            # relative to it, so the head faces the same way as in v12 (body 0, head 0).
            G_LOOK = 10.0 if GLIDE.endswith(('_v14', '_v15', '_v16', '_v17', '_v18', '_v19', '_v20', '_v21', '_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')) else 0.0
            for suf_, turn_ in G_TURN_STEPS.items():
                if GLIDE.endswith(suf_):
                    G_SPIN = Matrix.Rotation(math.radians(turn_ - G_TURN), 3, 'Z')
                    G_TURN = turn_
                    G_HAND, G_ARM = G_SPIN @ G_HAND, G_SPIN @ G_ARM
                    ARM_BACK = G_ARM
                    G_BLADE = (G_SPIN @ G_BLADE).normalized()
                    yaw_g = math.atan2(G_BLADE.y, G_BLADE.x)
                    CR_DYAW = min([yaw_g - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)], key=abs)
                    CR_EL1 = math.asin(G_BLADE.z)

            G_BACK_DIR = None
            G_L_HINT = (1, .4, -.3)
            if GLIDE.endswith(('_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                # v30 (Kvon: orient the shoulder so the elbow points out forward a little more): same fist position,
                # the elbow direction swings toward his front.
                G_L_HINT = tuple((Vector((1, .4, -.3)).normalized() + Matrix.Rotation(math.radians(-10.0), 3, 'Z') @ Vector((0, -1, 0))*.8).normalized())
            if GLIDE.endswith(('_v26', '_v27', '_v28')):
                # v26 (Kvon: reorient the shoulder to bring the elbow closer to the torso): same fist position,
                # the arm turns about the shoulder so the elbow points back toward his side instead of outward.
                G_L_HINT = tuple(Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.15, .9, -.4)))
            if GLIDE.endswith(('_v15', '_v16', '_v17', '_v18', '_v19', '_v20', '_v21', '_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                # v15 (Kvon: v14 with only the Keyblade arm changed - "extends the keyblade behind himself"): the right
                # arm reaches back past the hip and the blade trails out behind him, angled toward the camera
                # (so the tip stays in the frame) and a little down.
                G_HAND = G_SPIN @ (U_*-.30 + V_*.24 + Vector((0, 0, .74)))
                if GLIDE.endswith(('_v16', '_v17', '_v18', '_v19', '_v20', '_v21', '_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v16: with a straight wrist the nearly locked arm let the hover bob swing the forearm (and the
                    # Key) between drawings; a slightly shorter reach keeps the elbow stable.
                    G_HAND = G_SPIN @ (U_*-.24 + V_*.24 + Vector((0, 0, .76)))
                if GLIDE.endswith('_v19'):
                    # v19 (Kvon: "bring the other arm forward into view"): the left hand comes forward in front of
                    # his chest, slightly out to his left, elbow softly bent, so the camera sees the whole arm.
                    G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.20, -.36, .92))
                    ARM_BACK = G_ARM
                if GLIDE.endswith('_v20'):
                    # v20 (Kvon: lower the fist a little by bending the elbow): fist ~8 cm lower and pulled 6 cm in.
                    G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.18, -.30, .84))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v21', '_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v21 (Kvon: "Lower it more"): fist another ~8 cm lower with the elbow bent a bit more.
                    G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.17, -.26, .76))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v22 (Kvon: rotate the arm from its shoulder to lower the elbow): the whole arm swings down about
                    # the shoulder (~20 deg), so the elbow drops and the forearm and fist come down with it.
                    # (Swinging only the elbow round the shoulder-fist line flipped it out sideways - not used.)
                    G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.16, -.20, .66))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v23 (Kvon: "Lower a little more"): the arm swings down a little further at the shoulder.
                    G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.16, -.15, .60))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v24 (Kvon: bring the hand out in front of the raised leg): keep the low arm, the hand comes
                    # forward (screen right) and toward the camera so it sits in front of the tucked knee.
                    G_ARM = G_ARM + U_*.08 + V_*.14 + Vector((0, 0, .03))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v27', '_v28', '_v29')):
                    # v27 (Kvon: straighten the elbow more and put the arm behind the raised leg): from v23's low arm,
                    # the hand reaches further down and forward (straighter elbow) on the FAR side of the tucked knee
                    # (away from the camera), so the leg covers the forearm.
                    G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((.16, -.15, .60))                         + U_*.10 - V_*.08 + Vector((0, 0, -.12))
                    ARM_BACK = G_ARM
                if GLIDE.endswith('_v28'):
                    # v28 (Kvon: raise the shoulder; the arm looked a little too long): left collarbone shrugged up and
                    # the hand raised ~5 cm, so the straight arm behind the raised leg reads shorter.
                    G_ARM = G_ARM + Vector((0, 0, .05))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v29 (Kvon: hold the forearm in front of the torso): the left hand comes across in front of his
                    # belly toward his right side, elbow out to his left - the forearm lies across the body.
                    G_ARM = Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((-.06, -.30, .86))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v31 (Kvon: now lower the forearm): elbow still forward, the fist ~8 cm lower.
                    G_ARM = G_ARM + Vector((0, 0, -.08))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v32', '_v33', '_v34', '_v35')):
                    # v32 (Kvon: move the hand away from the torso): the fist moves ~10 cm out in front of his body.
                    G_ARM = G_ARM + Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((0, -.10, 0))
                    ARM_BACK = G_ARM
                if GLIDE.endswith('_v35'):
                    # v35 (Kvon: extend the forearm by straightening the elbow a little): the fist moves ~6 cm further
                    # out along the forearm's line (forward and across), so the elbow opens up.
                    G_ARM = G_ARM + Matrix.Rotation(math.radians(G_TURN), 3, 'Z') @ Vector((-.04, -.04, -.01))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v25', '_v26')):
                    # v25 (Kvon: straighten the elbow out some): the hand reaches ~7 cm further along the arm's line.
                    G_ARM = G_ARM + U_*.03 + V_*.04 + Vector((0, 0, -.05))
                    ARM_BACK = G_ARM
                if GLIDE.endswith(('_v18', '_v19', '_v20', '_v21', '_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')):
                    # v18 (Kvon: straighten the elbow a little, the wrist following): the hand reaches 4 cm further back,
                    # the wrist stays straight with v17's roll, so the hand and Key follow the forearm.
                    G_HAND = G_SPIN @ (U_*-.28 + V_*.24 + Vector((0, 0, .76)))
                hb_b = (-U_*.38 + V_*.92).normalized()
                G_BACK_DIR = (hb_b*math.cos(math.radians(-18)) + Vector((0, 0, math.sin(math.radians(-18))))).normalized()  # set against the camera (not spun) so it stays in the frame

            def loop_key(j):
                ph = 2*math.pi*j/6
                bob = .015*math.sin(ph)
                (ls, ll, lp), (rs, rl, rp), g_drop, g_hunch, g_pitch = G_LEGS
                feet = {'L': (ls + .02*math.sin(ph), LAT['L'], ll + bob, lp),
                        'R': (rs - .02*math.sin(ph), LAT['R'], rl + bob, rp)}
                if globals().get('G_SPIN') is not None and G_SPIN != Matrix.Identity(3):
                    for sd_, (fs_, fl_, *rest_) in list(feet.items()):
                        wv_ = G_SPIN @ (U_*fs_ + V_*fl_)
                        feet[sd_] = (wv_.dot(U_), wv_.dot(V_), *rest_)
                return dict(turn=G_TURN, ce=g_drop - bob - POSE['drop'], hunch=g_hunch, pitch=g_pitch + 2*math.sin(ph),
                            neck=G_NECK, look=G_LOOK, tilt=0.0, toe=8.0, twist=0.0, feet=feet, hand=G_HAND.copy(),
                            release=1.0, arm=1.0, blade_s=1.0,
                            hz=0.0 if GLIDE.endswith(('_v16', '_v17', '_v18', '_v19', '_v20', '_v21', '_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')) else .02*math.sin(ph - 1.0), root=G_SPEED,
                            l_elbow_hint=G_L_HINT, l_shrug=-4.0 if GLIDE.endswith(('_v34', '_v35')) else 4.0 if GLIDE.endswith('_v33') else (12.0 if GLIDE.endswith(('_v28', '_v29', '_v30', '_v31', '_v32')) else 0.0),
                            blade_dir=G_BACK_DIR, wrist_roll=20.0 if GLIDE.endswith(('_v18', '_v19', '_v20', '_v21', '_v22', '_v23', '_v24', '_v25', '_v26', '_v27', '_v28', '_v29', '_v30', '_v31', '_v32', '_v33', '_v34', '_v35')) else (0.0 if GLIDE.endswith(('_v16', '_v17')) else None))

        part = RUN.rsplit('_v', 1)[0]
        RUN_KEYS = []
        if JUMP:
            J_TURN = -10.0  # the approved glide's camera angle
            T_ = lambda v_: Matrix.Rotation(math.radians(J_TURN), 3, 'Z') @ Vector(v_)
            CHEST = T_((.12, -.22, 1.02))  # left fist up at the chest (sheet poses 2-3)

            def jk(feet, ce=0.0, hunch=0.0, pitch=0.0, neck=-6.0, hand=None, blade=None, release=1.0, arm=1.0):
                return dict(turn=J_TURN, ce=ce, hunch=hunch, pitch=pitch, neck=neck, look=8.0, tilt=0.0, toe=15.0,
                            twist=0.0, feet=feet, hand=hand if hand is not None else U_*-.16 + V_*.22 + Vector((0, 0, .80)),
                            release=release, arm=arm, blade_s=1.0, hz=0.0, root=0.0,
                            blade_dir=tuple(blade) if blade is not None else None, l_elbow_hint=(1, .4, -.3), l_shrug=0.0)
            L0, R0 = IDLE_R['feet']['L'], IDLE_R['feet']['R']
            back_low = (-U_*.62 + V_*.55 + Vector((0, 0, -.45))).normalized()   # Key low behind him, one hand
            up_high = (-U_*.35 + V_*.25 + Vector((0, 0, .90))).normalized()     # Key raised high (falling)
            J_V2 = not JUMP.endswith('_v1')
            if J_V2:
                # v2: v1's raised Key ran off the top of the frame - angled back over his shoulder instead.
                up_high = (-U_*.75 + V_*.45 + Vector((0, 0, .50))).normalized()
            if not JUMP.endswith(('_v1', '_v2')):
                # v3: v2 still clipped the frame corner - raised but angled toward the camera (shorter on screen).
                up_high = (-U_*.45 + V_*.85 + Vector((0, 0, .45))).normalized()
            ARM_BACK = CHEST
            jpart = JUMP.rsplit('_v', 1)[0]

            def toward_cam(b_, deg_):
                # Kvon: rotate the wrist so the Keyblade points toward the player (the camera) by deg_.
                b_ = Vector(b_).normalized(); c_ = to_cam - b_*to_cam.dot(b_)
                return tuple((b_*math.cos(math.radians(deg_)) + c_.normalized()*math.sin(math.radians(deg_))).normalized())
            if jpart == 'jump_start':
                # Takeoff (sheet pose 1): crouch, push through the toes, leave the floor; the left hand lets go.
                crouch = mix(IDLE_R, IDLE_R, 0.0); crouch.update(ce=.10, root=0.0)
                crouch.update(hunch=4.0, pitch=4.0)
                push = jk({'L': (L0[0]*.8, L0[1], .02, 25.0), 'R': (R0[0]*.8, R0[1], .03, 35.0)}, ce=.02, pitch=-2.0)
                push.update(release=.5, blade_dir=tuple(CR_BLADE0.lerp(back_low, .5).normalized()))
                leave = jk({'L': (L0[0]*.5, L0[1], .14, 40.0), 'R': (R0[0]*.5, R0[1], .10, 45.0)}, ce=-.04, pitch=-4.0,
                           blade=back_low)
                RUN_KEYS = [crouch, push, leave]
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4')):
                    # v5 (Kvon: straighten the Keyblade elbow a bit in takeoff 3): the fist reaches ~6 cm further down and
                    # back along the arm.
                    leave['hand'] = U_*-.20 + V_*.23 + Vector((0, 0, .76))
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                    # v6 (Kvon: add a few more degrees to the Keyblade elbow bend in takeoff 1 and 2): the grip comes ~5 cm
                    # up toward the shoulders, so both elbows bend a little more.
                    crouch['hz'] = crouch.get('hz', 0.0) + .05
                    push['hz'] = push.get('hz', 0.0) + .05
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6')):
                    # v7 (Kvon: keep takeoff 1's extra bend; he meant LESS bend for 2 and 3): the grip drops ~5 cm in
                    # takeoff 2 (below its v5 height) and ~4 cm more in takeoff 3, so those elbows straighten a little.
                    push['hz'] = -.05
                    leave['hz'] = leave.get('hz', 0.0) - .04
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7')):
                    # v8: takeoff 3's Keyblade turned 20 deg toward the player (rising continues at 40 and 60).
                    leave['blade_dir'] = toward_cam(back_low, 20.0)
            elif jpart == 'jump_rise':
                # Rising (sheet pose 2 / ref_01): front knee driven up, the other leg trailing down, body upright.
                RUN_KEYS = [jk({'L': (.10, LAT['L'], .34, 10.0), 'R': (-.08, LAT['R'], .10, 45.0)}, ce=-.02, pitch=-4.0,
                               blade=back_low),
                            jk({'L': (.10, LAT['L'], .38, 10.0), 'R': (-.06, LAT['R'], .14, 45.0)}, ce=-.02, pitch=-5.0,
                               blade=back_low)]
                if J_V2:
                    # v2: v1 still read as a standing stance - hips up and the front knee driven high, back leg hanging.
                    RUN_KEYS = [jk({'L': (.16, LAT['L'], .50, 0.0), 'R': (-.10, LAT['R'], .08, 50.0)}, ce=-.12, pitch=-4.0,
                                   blade=back_low),
                                jk({'L': (.16, LAT['L'], .54, 0.0), 'R': (-.08, LAT['R'], .12, 50.0)}, ce=-.12, pitch=-5.0,
                                   blade=back_low)]
                if not JUMP.endswith(('_v1', '_v2')):
                    # v3 (Kvon: rotate the wrist so the Keyblade points toward the player, more in each image): 40, 60 deg.
                    RUN_KEYS[0]['blade_dir'] = toward_cam(back_low, 40.0)
                    RUN_KEYS[1]['blade_dir'] = toward_cam(back_low, 60.0)
                if not JUMP.endswith(('_v1', '_v2', '_v3')):
                    # v4 (Kvon: rising 1's Keyblade elbow straighter than takeoff 3, rising 2 straighter still): the hips
                    # (and shoulders) ride 12 cm higher in the rising drawings, so the fist goes further down and back
                    # relative to the shoulder - takeoff 3 sits ~0.72 m below... ~0.66 and ~0.60 here.
                    for k_, (back_, hz_) in zip(RUN_KEYS, ((-.22, -.14), (-.26, -.20))):
                        k_['hand'] = U_*back_ + V_*.23 + Vector((0, 0, .80))
                        k_['hz'] = hz_
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4')):
                    # v5 (Kvon: rising 2 slightly more bend, still less than rising 1): rising 2's fist comes back halfway.
                    RUN_KEYS[1]['hand'] = U_*-.24 + V_*.23 + Vector((0, 0, .80))
                    RUN_KEYS[1]['hz'] = -.17
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                    # v6 (Kvon: increase the wrist rotation in rising 2): the Keyblade turns 75 deg toward the player (was 60).
                    RUN_KEYS[1]['blade_dir'] = toward_cam(back_low, 75.0)
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6')):
                    # v7 (Kvon: straighten the wrist some, then angle the Keyblade down toward his feet somewhat): ease the
                    # turn back to 65 deg (a less cocked wrist) and tip the blade downward toward his feet.
                    b7 = Vector(toward_cam(back_low, 65.0))*.75 + Vector((0, 0, -.55))
                    RUN_KEYS[1]['blade_dir'] = tuple(b7.normalized())
                if not JUMP.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7')):
                    # v8+ (Kvon: v7 reverted; "straighten the wrist" = the Keyblade's handle/guard lined up with the forearm):
                    # rising 2 uses a straight wrist (hand only rolls about the forearm, as in the glide). The roll is
                    # chosen below so the blade angles somewhat down toward his feet.
                    RUN_KEYS[1]['blade_dir'] = toward_cam(back_low, 75.0)
                    RUN_KEYS[1]['wrist_roll'] = 0.0
                if not JUMP.endswith(tuple(f'_v{n_}' for n_ in range(1, 10))):
                    # v10 (Kvon reverted v7-v9 to v6, then: angle the Keyblade down slightly more): v6's 75 deg turn toward
                    # the player with the bent wrist, tipped a little further down.
                    RUN_KEYS[1]['wrist_roll'] = None
                    RUN_KEYS[1]['blade_dir'] = tuple((Vector(toward_cam(back_low, 75.0)) + Vector((0, 0, -.3))).normalized())
                if not JUMP.endswith(tuple(f'_v{n_}' for n_ in range(1, 11))):
                    # v11 (Kvon: twist the Keyblade while keeping it in the same position): rising 2's Key rolls about its
                    # own shaft; the hand turns with it.
                    import re as re_t
                    m_t = re_t.search(r'_t(-?\d+)', OUT_NAME.rsplit('_v', 1)[-1])
                    RUN_KEYS[1]['blade_twist'] = float(m_t.group(1)) if m_t else 45.0
                if not JUMP.endswith(tuple(f'_v{n_}' for n_ in range(1, 12))):
                    # v12 (Kvon: rising 2's raised upper leg is pressed too far into his torso): the knee comes down and
                    # forward a little, so the thigh clears the jacket.
                    lf_ = RUN_KEYS[1]['feet']['L']
                    RUN_KEYS[1]['feet']['L'] = (lf_[0] + .06, lf_[1], lf_[2] - .12, lf_[3])
                if not JUMP.endswith(tuple(f'_v{n_}' for n_ in range(1, 13))):
                    # v13 (Kvon: straighten both legs some; the higher leg's toes point down some): the raised foot reaches
                    # further forward and a bit lower, the hanging foot drops lower, and the raised foot pitches toes-down.
                    lf_ = RUN_KEYS[1]['feet']['L']; rf_ = RUN_KEYS[1]['feet']['R']
                    RUN_KEYS[1]['feet']['L'] = (lf_[0] + .08, lf_[1], lf_[2] - .04, 35.0)
                    RUN_KEYS[1]['feet']['R'] = (rf_[0] - .02, rf_[1], rf_[2] - .08, rf_[3])
                if not JUMP.endswith(tuple(f'_v{n_}' for n_ in range(1, 14))):
                    # v14: v13's raised leg barely straightened (the toes-down pitch lifts the ankle target); reach it
                    # clearly further forward and down so hip-to-ankle opens up.
                    lf_ = RUN_KEYS[1]['feet']['L']
                    RUN_KEYS[1]['feet']['L'] = (lf_[0] + .12, lf_[1], lf_[2] - .12, 35.0)
                if not JUMP.endswith(tuple(f'_v{n_}' for n_ in range(1, 15))):
                    # v15 (Kvon: rotate the joint so the upper leg's toes point down): the raised foot's ankle pitches
                    # 70 deg toes-down; the ankle target is lowered by the same toe offset so the leg itself doesn't move.
                    lf_ = RUN_KEYS[1]['feet']['L']
                    if JUMP.endswith('_v15'):
                        RUN_KEYS[1]['feet']['L'] = (lf_[0], lf_[1], lf_[2] - TOE_D*(math.sin(math.radians(70)) - math.sin(math.radians(35))), 70.0)
                if JUMP.endswith('_v16'):
                    # v16 = v14 (Kvon reverted the v15 toe change) + leg-position review options from the output name:
                    # ..._x<cm>_z<cm> moves the raised foot forward(+)/back(-) and up(+)/down(-).
                    import re as re_
                    m_r = re_.search(r'_rz(-?\d+)$', OUT_NAME)
                    if m_r:
                        # ..._rz<cm>: the hanging (lower) leg's foot moves up(+)/down(-) - down straightens that leg.
                        rf_ = RUN_KEYS[1]['feet']['R']
                        RUN_KEYS[1]['feet']['R'] = (rf_[0], rf_[1], rf_[2] + int(m_r.group(1))/100, rf_[3])
                    m_ = re_.search(r'_x(-?\d+)_z(-?\d+)(?:_rz-?\d+)?$', OUT_NAME)
                    if m_:
                        lf_ = RUN_KEYS[1]['feet']['L']
                        RUN_KEYS[1]['feet']['L'] = (lf_[0] + int(m_.group(1))/100, lf_[1], lf_[2] + int(m_.group(2))/100, lf_[3])
            elif jpart == 'jump_apex':
                # Apex tuck (sheet pose 3 / ref_02): both knees pulled up, slight curl forward.
                RUN_KEYS = [jk({'L': (.06, LAT['L'], .42, 20.0), 'R': (-.02, LAT['R'], .34, 30.0)}, ce=-.02, hunch=8.0,
                               pitch=6.0, blade=back_low)]
                if J_V2:
                    RUN_KEYS = [jk({'L': (.10, LAT['L'], .54, 20.0), 'R': (.00, LAT['R'], .46, 30.0)}, ce=-.12, hunch=10.0,
                                   pitch=8.0, blade=back_low)]
                if not JUMP.endswith(('_v1', '_v2', '_v3')):
                    # v4 (Kvon: the apex continues on from the approved rising 2): same Keyblade hand, direction and
                    # -30 deg twist as rising 2; the raised knee lifts a little higher and the hanging leg tucks up under
                    # him; a slight curl forward at the top.
                    k_ = jk({'L': (.16, LAT['L'], .30, 35.0), 'R': (-.04, LAT['R'], .10, 45.0)}, ce=-.12, hunch=5.0,
                            pitch=2.0, blade=(Vector(toward_cam(back_low, 75.0)) + Vector((0, 0, -.3))).normalized())
                    k_['hand'] = U_*-.24 + V_*.23 + Vector((0, 0, .80)); k_['hz'] = -.17; k_['blade_twist'] = -30.0
                    RUN_KEYS = [k_]
            elif jpart == 'jump_bdash':
                # Back-dash (Kvon: Gemini round 36, a quick LOW backstep, corrected so he leans BACK): push off from the
                # idle, a low hop with the body upright and tipped back, knees bent, feet a little in front, Keyblade low
                # behind in the right hand, left arm out for balance; feet reach down, touch down and settle in the idle.
                hop_k = jk({'L': (.18, LAT['L'], .12, 15.0), 'R': (.02, LAT['R'], .08, 10.0)}, ce=-.02, hunch=-3.0,
                           pitch=-9.0, neck=8.0, blade=back_low)
                hop_k['hand'] = U_*-.24 + V_*.22 + Vector((0, 0, .72))
                ARM_BACK = T_((.30, -.10, .92))   # left arm out to his left side for balance
                push_k = mix(IDLE_R, hop_k, .35); push_k['ce'] += .07
                push_k['feet'] = {sd: (f_[0], f_[1], .02, 20.0) for sd, f_ in push_k['feet'].items()}
                push_k['blade_dir'] = tuple(CR_BLADE0.lerp(Vector(back_low), .5).normalized())
                hop2_k = dict(hop_k); hop2_k['feet'] = {'L': (.16, LAT['L'], .04, 10.0), 'R': (.0, LAT['R'], .02, 8.0)}
                hop2_k['pitch'] = -6.0
                touch_k = mix(hop2_k, IDLE_R, .55); touch_k['ce'] += .05
                touch_k['feet'] = {sd: (f_[0], f_[1], 0.0, 0.0) for sd, f_ in touch_k['feet'].items()}
                touch_k['blade_dir'] = tuple(Vector(back_low).lerp(CR_BLADE0, .55).normalized())
                settle_k = mix(hop2_k, IDLE_R, .9); settle_k['release'] = 0.0
                settle_k['feet'] = {sd: (f_[0], f_[1], 0.0, 0.0) for sd, f_ in settle_k['feet'].items()}
                settle_k['blade_dir'] = tuple(Vector(back_low).lerp(CR_BLADE0, .92).normalized())
                if not JUMP.endswith('_v1'):
                    # v2: v1's hop barely left the floor and the lean back didn't show: feet out in front and lifted,
                    # knees bent, torso tipped back more (the drawings are in place; the game lifts him a little too).
                    for k_, (lf_, rf_, pt_, hn_) in ((hop_k, ((.28, .24), (.12, .16), -17.0, -7.0)),
                                                     (hop2_k, ((.24, .12), (.08, .08), -12.0, -5.0))):
                        k_['feet'] = {'L': (lf_[0], LAT['L'], lf_[1], 5.0), 'R': (rf_[0], LAT['R'], rf_[1], 5.0)}
                        k_['pitch'], k_['hunch'] = pt_, hn_
                    hop_k['ce'] = -.06
                    touch_k = mix(hop2_k, IDLE_R, .55); touch_k['ce'] += .05
                    touch_k['feet'] = {sd: (f_[0], f_[1], 0.0, 0.0) for sd, f_ in touch_k['feet'].items()}
                    touch_k['blade_dir'] = tuple(Vector(back_low).lerp(CR_BLADE0, .55).normalized())
                RUN_KEYS = [push_k, hop_k, hop2_k, touch_k, settle_k]
            elif jpart == 'jump_dash':
                # Forward air-dash (Kvon: Gemini round-34 sheet, bottom-left pose as the main reference, transitions
                # built around it): burst out of the apex tuck -> the dash pose (leaning forward and crouched, front
                # knee tucked under, back leg trailing, Keyblade held straight back behind him in the right hand,
                # left fist forward at the chest) held for two drawings -> brake upright, handing over to falling.
                apex_k = jk({'L': (.16, LAT['L'], .30, 35.0), 'R': (-.04, LAT['R'], .10, 45.0)}, ce=-.12, hunch=5.0,
                            pitch=2.0, blade=(Vector(toward_cam(back_low, 75.0)) + Vector((0, 0, -.3))).normalized())
                apex_k['hand'] = U_*-.24 + V_*.23 + Vector((0, 0, .80)); apex_k['hz'] = -.17
                dash_blade = (-U_*.75 + V_*.6 + Vector((0, 0, .05))).normalized()
                dash_k = jk({'L': (.12, LAT['L'], .26, 25.0), 'R': (-.42, LAT['R'], .12, 40.0)}, ce=-.10, hunch=12.0,
                            pitch=16.0, neck=-20.0, blade=dash_blade)
                dash_k['hand'] = U_*-.34 + V_*.24 + Vector((0, 0, .98))
                ARM_BACK = CHEST + U_*.14
                burst_k = mix(apex_k, dash_k, .5)
                burst_k['blade_dir'] = tuple((Vector(apex_k['blade_dir']) + dash_blade).normalized())
                dash2_k = dict(dash_k); dash2_k['feet'] = {'L': (.10, LAT['L'], .24, 25.0), 'R': (-.38, LAT['R'], .14, 40.0)}
                dash2_k['pitch'] = 14.0
                brake_k = jk({'L': (.10, LAT['L'], .18, 20.0), 'R': (-.16, LAT['R'], .12, 35.0)}, ce=-.04, hunch=2.0,
                             pitch=-4.0, neck=-6.0, blade=(-U_*.5 + V_*.4 + Vector((0, 0, .75))).normalized())
                brake_k['hand'] = U_*-.18 + V_*.22 + Vector((0, 0, 1.12))
                if not JUMP.endswith('_v1'):
                    # v2: v1 stood too upright facing the camera with the legs under him and the Key off the frame.
                    # Turn more side-on (like the sheet), lean well forward, both legs bent with the feet trailing
                    # behind, the Key arm reaching back with the blade angled toward the camera so it fits.
                    dash_blade = (-U_*.55 + V_*.82 + Vector((0, 0, .08))).normalized()
                    dash_k = jk({'L': (-.06, LAT['L'], .32, 45.0), 'R': (-.38, LAT['R'], .22, 55.0)}, ce=-.10, hunch=16.0,
                                pitch=26.0, neck=-34.0, blade=dash_blade)
                    dash_k['turn'] = 25.0
                    dash_k['hand'] = U_*-.40 + V_*.24 + Vector((0, 0, .98))
                    burst_k = mix(apex_k, dash_k, .5)
                    burst_k['blade_dir'] = tuple((Vector(apex_k['blade_dir']) + dash_blade).normalized())
                    dash2_k = dict(dash_k)
                    dash2_k['feet'] = {'L': (-.04, LAT['L'], .30, 45.0), 'R': (-.34, LAT['R'], .22, 55.0)}
                    dash2_k['pitch'] = 22.0
                    brake_k = jk({'L': (.10, LAT['L'], .18, 20.0), 'R': (-.16, LAT['R'], .12, 35.0)}, ce=-.04, hunch=2.0,
                                 pitch=-4.0, neck=-6.0, blade=(-U_*.35 + V_*.7 + Vector((0, 0, .6))).normalized())
                    brake_k['turn'] = 8.0
                    brake_k['hand'] = U_*-.18 + V_*.22 + Vector((0, 0, 1.05))
                RUN_KEYS = [burst_k, dash_k, dash2_k, brake_k]
            elif jpart == 'jump_spin':
                # Second jump (Kvon: KH2 Aerial Dodge - an upright spin on his vertical axis like a top, from Gemini's
                # round-33 sheet, with more angles than the sheet): the approved apex pose turned through a full circle
                # in 30 deg steps (11 drawings; the 0/360 pose is the apex drawing itself). Feet, hands, blade, left
                # arm and elbow directions all turn with the body about his vertical axis.
                SPIN_DIR = -1.0 if 'ccw' in OUT_NAME else 1.0
                for a_ in range(30, 360, 30):
                    k_ = jk({'L': (.16, LAT['L'], .30, 35.0), 'R': (-.04, LAT['R'], .10, 45.0)}, ce=-.12, hunch=5.0,
                            pitch=2.0, blade=(Vector(toward_cam(back_low, 75.0)) + Vector((0, 0, -.3))).normalized())
                    k_['hand'] = U_*-.24 + V_*.23 + Vector((0, 0, .80)); k_['hz'] = -.17; k_['blade_twist'] = -30.0
                    k_['spin_deg'] = SPIN_DIR*a_
                    if not JUMP.endswith('_v1'):
                        # v2: v1's blade stuck straight out sideways at the side-on angles and hit the frame edge; it now
                        # hangs down close along his leg (as in Gemini's sheet) so it stays near his body all the way round.
                        k_['blade_dir'] = tuple((Vector(toward_cam(back_low, 75.0))*.45 + Vector((0, 0, -1.0))).normalized())
                        if not JUMP.endswith(('_v1', '_v2')):
                            # v3: v2 ran off the frame's bottom and changed too much from the apex; between the two.
                            k_['blade_dir'] = tuple((Vector(toward_cam(back_low, 75.0)) + Vector((0, 0, -.75))).normalized())
                            k_['hand'] = U_*-.24 + V_*.23 + Vector((0, 0, .86))
                        if not JUMP.endswith(('_v1', '_v2', '_v3')):
                            # v4: v3 still hit the side edges (a level Key is too long side-on). Hang it down (v2, fits)
                            # through the middle of the spin and ease from/back to the apex angle over the first/last 60 deg.
                            apex_b = (Vector(toward_cam(back_low, 75.0)) + Vector((0, 0, -.3))).normalized()
                            down_b = (Vector(toward_cam(back_low, 75.0))*.45 + Vector((0, 0, -1.0))).normalized()
                            e_ = min(1.0, min(a_, 360 - a_)/60.0)
                            k_['blade_dir'] = tuple(apex_b.lerp(down_b, e_).normalized())
                            k_['hand'] = U_*-.24 + V_*.23 + Vector((0, 0, .80))
                    RUN_KEYS.append(k_)
            elif HURT:
                # Hurt set (Kvon, October 26; Gemini round-37 sheet): ground hit, air hit, head-first fall with his back
                # to the screen, landing flat on his back (face up). Each drawing is solved upright first, so the knees
                # and elbows bend the normal way, then the finished pose is turned as one piece: 'spin_deg' about his
                # vertical axis, 'roll' in the screen plane about the hips (+ = head toward screen left), 'ground' drops
                # the lowest point of the body onto the floor (+ 'lift' for a bounce). Kvon: Gemini's head-first poses
                # had the legs facing the wrong way - turning the solved pose keeps the legs' anatomy at any angle.
                B_ = lambda x_, y_, z_: T_((x_, y_, z_))   # body frame: +x his left, -y his front
                hit_blade = (-U_*.70 + V_*.45 + Vector((0, 0, -.40))).normalized()
                H_V2 = not HURT.endswith('_v1')
                if H_V2:
                    hit_blade = (-U_*.40 + V_*.80 + Vector((0, 0, -.45))).normalized()  # v1 ran off the left edge

                def hurt(feet, ce, hunch, pitch, neck, hand, blade, l_hand, roll=0.0, spin=0.0, ground=False, lift=0.0):
                    k_ = jk(feet, ce=ce, hunch=hunch, pitch=pitch, neck=neck, blade=blade)
                    k_.update(hand=hand, l_hand=tuple(l_hand), roll=roll, ground=ground, lift=lift, look=0.0, toe=10.0)
                    if spin:
                        k_['spin_deg'] = spin
                    return k_

                def ease(a_, b_, w_, release):
                    # In-between toward the idle: mix() keeps only the common numbers; carry the extras across.
                    k_ = mix(a_, b_, w_)
                    k_.update(blade_dir=tuple(Vector(a_['blade_dir']).lerp(CR_BLADE0, w_).normalized()),
                              l_hand=a_['l_hand'], release=release, root=0.0, l_elbow_hint=(1, .4, -.3), l_shrug=0.0,
                              lean_cam=a_.get('lean_cam', 0.0)*(1 - w_), head_cam=a_.get('head_cam', 0.0)*(1 - w_))
                    return k_
                stand = {'L': (L0[0], L0[1], 0.0, 0.0), 'R': (R0[0], R0[1], 0.0, 0.0)}
                if jpart == 'hurt_ground':
                    # Snap back (chest out, head thrown back, arms flung), deepest lean, then recover into the idle.
                    hit_k = hurt(stand, .05, -8.0, -14.0, -16.0, U_*-.34 + V_*.26 + Vector((0, 0, 1.00)), hit_blade,
                                 B_(.30, -.28, 1.15))
                    peak_k = hurt(stand, .07, -11.0, -20.0, -22.0, U_*-.40 + V_*.26 + Vector((0, 0, 1.05)), hit_blade,
                                  B_(.32, -.20, 1.22))
                    if H_V2:
                        hit_k.update(lean_cam=20.0, head_cam=14.0, pitch=-8.0, hunch=-4.0, neck=-6.0)
                        peak_k.update(lean_cam=27.0, head_cam=20.0, pitch=-10.0, hunch=-5.0, neck=-8.0)
                    if not HURT.endswith(('_v1', '_v2')):
                        # v3 (Kvon picked Gemini round 38 #1): a violent snap - the spine bent back another ~17 deg into a
                        # sharp C, chest pushed out, head thrown back so the face aims at the ceiling.
                        hit_k.update(lean_cam=36.0, head_cam=28.0, pitch=-16.0, hunch=-8.0, neck=-14.0)
                        peak_k.update(lean_cam=44.0, head_cam=34.0, pitch=-18.0, hunch=-9.0, neck=-16.0)
                    if not HURT.endswith(('_v1', '_v2', '_v3')):
                        # v4 (Kvon: leans too far back): halfway between v2 and v3.
                        hit_k.update(lean_cam=28.0, head_cam=21.0, pitch=-12.0, hunch=-6.0, neck=-10.0)
                        peak_k.update(lean_cam=35.0, head_cam=27.0, pitch=-14.0, hunch=-7.0, neck=-12.0)
                    RUN_KEYS = [hit_k, peak_k, ease(peak_k, IDLE_R, .5, .5), ease(peak_k, IDLE_R, .85, .15)]
                elif jpart == 'hurt_air':
                    # The same snap back in the air, legs dangling in front; then drifting back and starting to tip over.
                    RUN_KEYS = [hurt({'L': (.20, LAT['L'], .10, 20.0), 'R': (.04, LAT['R'], .05, 25.0)}, -.04, -8.0, -16.0,
                                     -16.0, U_*-.36 + V_*.26 + Vector((0, 0, 1.02)), hit_blade, B_(.30, -.28, 1.18),
                                     roll=10.0),
                                hurt({'L': (.30, LAT['L'], .22, 15.0), 'R': (.18, LAT['R'], .14, 20.0)}, -.06, -10.0, -18.0,
                                     -12.0, U_*-.40 + V_*.24 + Vector((0, 0, 1.08)), hit_blade, B_(.32, -.18, 1.25),
                                     roll=35.0)]
                    if H_V2:
                        for k_, ln_ in zip(RUN_KEYS, (16.0, 10.0)):
                            k_.update(lean_cam=ln_, head_cam=12.0)
                            if not HURT.endswith('_v2'):
                                k_['leg_reach'] = .975  # v3 (Kvon): legs mostly straight
                        if not HURT.endswith(('_v2', '_v3')):
                            RUN_KEYS[0]['offset_px'] = (0, 36)    # v4: v3's feet touched the bottom edge
                            RUN_KEYS[1]['offset_px'] = (-44, 0)   # v4: and the right edge
                        if not HURT.endswith(('_v2', '_v3', '_v4')):
                            for k_ in RUN_KEYS:
                                k_['leg_reach'] = .94   # v5 (Kvon): slightly more knee bend
                            RUN_KEYS[1]['ankle_deg'] = 30.0  # v5 (Kvon): straighten the ankles on the drift drawing
                        if not HURT.endswith(('_v2', '_v3', '_v4', '_v5')):
                            RUN_KEYS[0]['ankle_deg'] = 30.0  # v6 (Gemini round 38 #3): the impact drawing too
                elif jpart == 'hurt_fall':
                    # Head first with his back to the screen and his feet in the air: tipping over while turning away,
                    # upside down, then the shoulders heading for the floor. Arms loose around his head.
                    over_blade = (-U_*.80 + V_*.40 + Vector((0, 0, .20))).normalized()
                    RUN_KEYS = [hurt({'L': (.24, LAT['L'], .20, 15.0), 'R': (.10, LAT['R'], .12, 20.0)}, -.06, -6.0, -12.0,
                                     -10.0, U_*-.30 + V_*.22 + Vector((0, 0, 1.25)), over_blade, B_(.30, -.12, 1.30),
                                     roll=90.0, spin=70.0),
                                hurt({'L': (.06, LAT['L'], .12, 30.0), 'R': (-.10, LAT['R'], .20, 30.0)}, -.06, 4.0, 0.0,
                                     -6.0, U_*-.20 + V_*.20 + Vector((0, 0, 1.45)), over_blade, B_(.25, -.05, 1.45),
                                     roll=175.0, spin=150.0),
                                hurt({'L': (.10, LAT['L'], .16, 30.0), 'R': (-.06, LAT['R'], .24, 30.0)}, -.06, 6.0, 2.0,
                                     -4.0, U_*-.18 + V_*.20 + Vector((0, 0, 1.40)), over_blade, B_(.25, -.08, 1.40),
                                     roll=160.0, spin=150.0)]
                    if not HURT.endswith(('_v1', '_v2', '_v3')):
                        for k_ in RUN_KEYS:
                            k_['leg_reach'] = .975 if HURT.endswith('_v4') else .94  # v4 (Kvon): mostly straight; v5: bit more bend
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                        # v6 (Gemini round 38 #2): an in-between from the air drift (roll 35) - body horizontal in the air,
                        # back parallel to the floor, just starting to turn away; legs mostly straight, feet pointed.
                        flat_k = hurt({'L': (.30, LAT['L'], .22, 15.0), 'R': (.18, LAT['R'], .14, 20.0)}, -.06, -10.0,
                                      -16.0, -12.0, U_*-.36 + V_*.24 + Vector((0, 0, 1.15)),
                                      (-U_*.40 + V_*.80 + Vector((0, 0, .20))).normalized(), B_(.32, -.16, 1.28),
                                      roll=80.0, spin=25.0)
                        flat_k.update(lean_cam=6.0, head_cam=10.0, leg_reach=.94, ankle_deg=30.0, offset_px=(-30, 0))
                    if H_V2:
                        # v1's first drawing (on its side, half turned) read as a jumble: further over and further round.
                        RUN_KEYS[0].update(roll=130.0, spin_deg=110.0)
                        for k_ in RUN_KEYS:
                            k_['blade_dir'] = tuple((-U_*.40 + V_*.80 + Vector((0, 0, .20))).normalized())
                            if not HURT.endswith('_v2'):
                                # v3: the spin turned v2's blade away from the camera (off the left edge): aim it so it
                                # points at the camera AFTER the spin.
                                k_['blade_dir'] = tuple(Matrix.Rotation(math.radians(-k_['spin_deg']), 3, 'Z')
                                                        @ (V_*.85 - U_*.25 + Vector((0, 0, .20))).normalized())
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                        RUN_KEYS.insert(0, flat_k)
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6')):
                        # v7 (Kvon): drawings 3-4 keep drawing 2's tilt and turn (head first on the diagonal) instead of
                        # going straight upside down; all four swing the legs back slightly at the hips.
                        for k_ in RUN_KEYS[2:]:
                            k_.update(roll=RUN_KEYS[1]['roll'], spin_deg=RUN_KEYS[1]['spin_deg'])
                            if not HURT.endswith('_v7'):
                                # v8: v7 kept the Key aimed for the old turn and it ran off the bottom: aim as drawing 2.
                                k_['blade_dir'] = RUN_KEYS[1]['blade_dir']
                        for k_ in RUN_KEYS:
                            k_['hip_back_deg'] = 12.0
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7', '_v8')):
                        # v9 (Kvon): the final falling drawing straight upside down with the arms down at his sides
                        # (body frame before the turn; the Key hangs along his right side).
                        RUN_KEYS[3].update(roll=180.0, hand=B_(-.30, .04, .80), l_hand=tuple(B_(.30, .04, .80)),
                                           release=1.0, blade_dir=tuple(T_((-.12, .05, -1.0)).normalized()))
                        if not HURT.endswith('_v9'):
                            # v10: v9's hands sat at the waist with bent elbows; lower so the arms hang straight at his sides.
                            RUN_KEYS[3].update(hand=B_(-.30, .04, .64), l_hand=tuple(B_(.30, .04, .64)))
                        if not HURT.endswith(('_v9', '_v10')):
                            RUN_KEYS[3]['offset_px'] = (0, -24)  # v11: v10's Key tip touched the top edge
                elif jpart == 'atk_slight':
                    # Standing Light (Kvon, October 27): a guard bash like a bunt - the Key level at chest height, guard
                    # in front toward the opponent and blade pointing back, right fist (inside the guard) on the handle,
                    # left hand steadying the shaft behind it; a short shove forward so the guard hits, then back.
                    lvl_blade = (-U_*.92 + V_*.30 + Vector((0, 0, .04))).normalized()
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                        # v6 (Kvon): the blade tip points slightly toward the player (~35 deg toward the camera).
                        lvl_blade = (-U_*.80 + V_*.55 + Vector((0, 0, .03))).normalized()
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6')):
                        lvl_blade = (-U_*.72 + V_*.70 + Vector((0, 0, .03))).normalized()  # v7: ~45 deg (Kvon: more)

                    def bunt(hand, ce, pitch, feet):
                        # v2: v1's left hand (.22 m back) sat almost on the guard; further back along the shaft.
                        back_ = .22 if HURT.endswith('_v1') else (.32 if HURT.endswith(('_v2', '_v3')) else
                                                                  (.24 if HURT.endswith('_v4') else
                                                                   (.36 if HURT.endswith(('_v5', '_v6', '_v7', '_v8'))
                                                                    else .44)))  # v9 (Kvon): further up the shaft
                        k_ = hurt(feet, ce, 0.0, pitch, -6.0, hand, lvl_blade, hand + lvl_blade*back_, ground=True)
                        k_.update(no_center=True, look=8.0)
                        if not HURT.endswith(('_v1', '_v2')):
                            # v3 (Kvon: swap the hands for this attack): the LEFT fist holds the handle inside the guard at
                            # `hand`, the right hand steadies the shaft behind it; the Key is slid onto the left fist after
                            # the solve ('key_in_left').
                            k_.update(hand=hand + lvl_blade*back_, l_hand=tuple(hand), key_in_left=True)
                        return k_
                    step_in = {'L': (L0[0] + .06, L0[1], 0.0, 0.0), 'R': (R0[0] + .02, R0[1], 0.0, 0.0)}
                    set_k = bunt(U_*.14 + V_*.22 + Vector((0, 0, .96)), .05, 2.0, stand)
                    bash_k = bunt(U_*.34 + V_*.22 + Vector((0, 0, .96)), .08, 8.0, step_in)
                    recoil_k = bunt(U_*.18 + V_*.22 + Vector((0, 0, .94)), .06, 4.0, step_in)
                    if not HURT.endswith(('_v1', '_v2', '_v3')):
                        # v4 (Kvon: extend the Keyblade out in front for the hit): guard at arm's length on the bash,
                        # bigger step in and lean; the hands closer together on the Key so both arms can reach.
                        step_in = {'L': (L0[0] + .12, L0[1], 0.0, 0.0), 'R': (R0[0] + .04, R0[1], 0.0, 0.0)}
                        set_k = bunt(U_*.20 + V_*.20 + Vector((0, 0, .98)), .05, 3.0, stand)
                        bash_k = bunt(U_*.52 + V_*.16 + Vector((0, 0, 1.00)), .09, 12.0, step_in)
                        recoil_k = bunt(U_*.30 + V_*.18 + Vector((0, 0, .98)), .07, 6.0, step_in)
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4')):
                        # v5: v4's Key crossed his face - chest height; hands further apart (right hand past the guard,
                        # on the shaft) and the Key slid forward so the handle's middle sits in the left fist.
                        set_k = bunt(U_*.20 + V_*.20 + Vector((0, 0, .90)), .05, 3.0, stand)
                        bash_k = bunt(U_*.52 + V_*.16 + Vector((0, 0, .92)), .09, 12.0, step_in)
                        recoil_k = bunt(U_*.30 + V_*.18 + Vector((0, 0, .90)), .07, 6.0, step_in)
                        if not HURT.endswith(('_v5', '_v6', '_v7', '_v8', '_v9')):
                            # v10 (Kvon): front foot a little closer to his torso through the attack.
                            near_ = {'L': (L0[0] - .05, L0[1], 0.0, 0.0), 'R': (R0[0] + .04, R0[1], 0.0, 0.0)}
                            set_k = bunt(U_*.20 + V_*.20 + Vector((0, 0, .90)), .05, 3.0,
                                         {'L': (L0[0] - .03, L0[1], 0.0, 0.0), 'R': (R0[0], R0[1], 0.0, 0.0)})
                            bash_k = bunt(U_*.52 + V_*.16 + Vector((0, 0, .92)), .09, 12.0, near_)
                            recoil_k = bunt(U_*.30 + V_*.18 + Vector((0, 0, .90)), .07, 6.0, near_)
                        if not HURT.endswith(('_v5', '_v6', '_v7', '_v8', '_v9', '_v10')):
                            # v11 (Kvon: a little further in).
                            near_ = {'L': (L0[0] - .10, L0[1], 0.0, 0.0), 'R': (R0[0] + .04, R0[1], 0.0, 0.0)}
                            set_k = bunt(U_*.20 + V_*.20 + Vector((0, 0, .90)), .05, 3.0,
                                         {'L': (L0[0] - .07, L0[1], 0.0, 0.0), 'R': (R0[0], R0[1], 0.0, 0.0)})
                            bash_k = bunt(U_*.52 + V_*.16 + Vector((0, 0, .92)), .09, 12.0, near_)
                            recoil_k = bunt(U_*.30 + V_*.18 + Vector((0, 0, .90)), .07, 6.0, near_)
                        for k_ in (set_k, bash_k, recoil_k):
                            k_['key_slide'] = .12
                            if not HURT.endswith('_v5') and not HURT.endswith('_v6'):
                                k_['shaft_grip'] = tuple(lvl_blade)  # v7: straight wrist on the shaft hand
                    if not HURT.endswith(tuple(f'_v{n_}' for n_ in range(1, 12))):
                        # v12 (Kvon: a small smear on the Light too): same poses as the approved v11; the bash drawing
                        # gets a short straight streak behind the guard (make_smears.py 'thrust' style).
                        bash_k.update(smear=1, smear_style='thrust')
                    back_k = ease(recoil_k, IDLE_R, .6, .4)
                    back_k.update(ground=True, no_center=True)
                    RUN_KEYS = [set_k, bash_k, recoil_k, back_k]
                elif jpart in ('atk_clight', 'atk_cmed'):
                    # The Crouching Medium (atk_cmed) reuses this section's kneel, crouch guard and cl() keys: build the
                    # approved Crouching Light (v30) first, then replace its drawings below.
                    CM_HURT = HURT if jpart == 'atk_cmed' else None
                    if CM_HURT:
                        HURT = 'atk_clight_v30'
                    # Crouching Light (Kvon, October 27; posture after Ky's 2S in Guilty Gear Strive): from the approved
                    # crouch (crouch_hold_v4: sunk .32, hunch 9, pitch 10, neck -12, knees splayed .6, right fist low behind
                    # him with the blade trailing back, left fist up at the chest) a small draw-back, a quick one-handed
                    # forehand slash that sweeps the Key forward low, ending at shin height in front of him, then back.
                    tc_ = Matrix.Rotation(math.radians(IDLE_R['turn']), 3, 'Z')
                    cr_hand = tc_ @ Vector((-.36, .10, .82))
                    cr_guard = tc_ @ Vector((.10, -.30, .98))
                    cr_blade = (-U_*.55 + -to_cam*.75 + Vector((0, 0, -.38))).normalized()   # trailing back, behind him
                    KNEEL_CL = not HURT.endswith(tuple(f'_v{n_}' for n_ in range(1, 7)))
                    if KNEEL_CL:
                        # v7+ (Kvon approved the kneeling crouch, crouch_*_v15): hips .08 higher than the old crouch, the
                        # back (right) knee straight down to the floor, the shin turned .50 m toward the background, the
                        # foot on its toes (pitch 25, ankle .11 up).
                        kneel_R = (R0[0], R0[1] - .50, .11 - TOE_D*math.sin(math.radians(25.0)), 25.0)
                        kneel_L = stand['L']
                        if not HURT.endswith('_v7'):
                            # v8 (final crouch v18): back foot .24 toward his centre and .57 into the background, front
                            # foot .14 in under his torso.
                            kneel_R = (R0[0] + .24, R0[1] - .57, .11 - TOE_D*math.sin(math.radians(25.0)), 25.0)
                            kneel_L = (L0[0] - .14, L0[1], 0.0, 0.0)

                    def cl(hand, blade, ce=.32, hunch=9.0, pitch=10.0, turn=None, l_hand=None, feet=None):
                        if KNEEL_CL:
                            ce -= .08
                            feet = feet or {'L': kneel_L, 'R': kneel_R}
                        k_ = hurt(feet or stand, ce, hunch, pitch, -12.0, hand, Vector(blade).normalized(),
                                  l_hand if l_hand is not None else cr_guard, ground=True)
                        k_.update(no_center=True, look=8.0, knee_splay=.6, release=1.0)
                        if KNEEL_CL:
                            k_.update(toe=IDLE_R['toe'], knee_hint_world={'R': tuple(U_*.15 + Vector((0, 0, -1.0)))})
                        if turn is not None:
                            k_['turn'] = turn
                        return k_
                    draw_k = cl(cr_hand + U_*-.08 + Vector((0, 0, .06)), -U_*.70 + -to_cam*.55 + Vector((0, 0, -.20)),
                                turn=IDLE_R['turn'] + 12.0)
                    sweep_k = cl(U_*.02 + V_*.24 + Vector((0, 0, .66)), V_*.95 + U_*.10 + Vector((0, 0, -.30)),
                                 ce=.36, pitch=14.0, turn=IDLE_R['turn'] - 6.0)
                    hit_k = cl(U_*.30 + V_*.18 + Vector((0, 0, .58)), U_*.80 + V_*.45 + Vector((0, 0, -.40)),
                               ce=.38, pitch=18.0, hunch=12.0, turn=IDLE_R['turn'] - 18.0)
                    follow_k = cl(U_*.26 + V_*.08 + Vector((0, 0, .60)), U_*.55 - to_cam*.20 + Vector((0, 0, -.45)),
                                  ce=.37, pitch=16.0, hunch=11.0, turn=IDLE_R['turn'] - 22.0)
                    back1 = cl(cr_hand.lerp(follow_k['hand'], .5), (Vector(follow_k['blade_dir']) + cr_blade).normalized(),
                               ce=.34, pitch=12.0, turn=IDLE_R['turn'] - 8.0)
                    back2 = cl(cr_hand.lerp(follow_k['hand'], .15), (Vector(follow_k['blade_dir'])*.15 + cr_blade).normalized(),
                               ce=.32, turn=IDLE_R['turn'])
                    if not HURT.endswith('_v1'):
                        # v2: v1's draw-back blade left the frame, the sweep pointed end-on at the camera and the hit /
                        # follow-through tips went through the floor - a low but nearly level forehand arc.
                        draw_k['blade_dir'] = tuple((-U_*.40 - to_cam*.85 + Vector((0, 0, -.12))).normalized())
                        sweep_k.update(hand=U_*.04 + V_*.24 + Vector((0, 0, .70)),
                                       blade_dir=tuple((V_*.80 + U_*.45 + Vector((0, 0, -.08))).normalized()))
                        hit_k.update(hand=U_*.30 + V_*.18 + Vector((0, 0, .66)),
                                     blade_dir=tuple((U_*.85 + V_*.42 + Vector((0, 0, -.14))).normalized()))
                        follow_k.update(hand=U_*.24 + V_*.06 + Vector((0, 0, .68)),
                                        blade_dir=tuple((U_*.55 - to_cam*.55 + Vector((0, 0, -.14))).normalized()))
                        back1['hand'] = cr_hand.lerp(follow_k['hand'], .5)
                        back1['blade_dir'] = tuple((Vector(follow_k['blade_dir']) + cr_blade).normalized())
                        back2['blade_dir'] = tuple((Vector(follow_k['blade_dir'])*.15 + cr_blade).normalized())
                    if not HURT.endswith(('_v1', '_v2')):
                        hit_k['offset_px'] = (-40, 0)  # v3: v2's tip touched the right edge (Godot shifts back)
                        follow_k['blade_dir'] = tuple((U_*.72 - to_cam*.35 + Vector((0, 0, -.12))).normalized())  # v2 end-on
                        back1['blade_dir'] = tuple((Vector(follow_k['blade_dir']) + cr_blade).normalized())
                        back2['blade_dir'] = tuple((Vector(follow_k['blade_dir'])*.15 + cr_blade).normalized())
                    if not HURT.endswith(('_v1', '_v2', '_v3')):
                        follow_k['offset_px'] = (-30, 0)   # v4: v3's follow-through tip touched the right edge
                        back1['blade_dir'] = tuple((-U_*.20 + V_*.40 + Vector((0, 0, -.30))).normalized())  # v3 end-on
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4')):
                        back1['blade_dir'] = tuple((-U_*.30 + V_*.40 + Vector((0, 0, -.08))).normalized())  # v5: v4 dipped through the floor
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                        # v6: smears traced from the draw-back ran along the floor (the blade starts pointing back): smear
                        # only the visible part of the swing - sweep -> hit, and hit -> follow-through.
                        sweep_k['smear'] = 0; hit_k['smear'] = 1; follow_k['smear'] = 1
                        CL_SMEAR_SET = True
                    if not globals().get('CL_SMEAR_SET'):
                        sweep_k['smear'] = 1; hit_k['smear'] = 2
                    if not HURT.endswith(tuple(f'_v{n_}' for n_ in range(1, 9))):
                        # v9 (Kvon: refine with MoMask): body mechanics from MoMask clip a3 (momask_trial/a3/
                        # swing_analysis.json), scaled to the kneel and to a Light. Wind-up: hand up and back past the
                        # shoulder (a3 f15-16), blade angled toward the camera so it stays in frame; swipe down and
                        # forward while the hips drop (a3 f17-21, hips -.25 m -> .06 here); the torso pitches forward
                        # and the right shoulder leads through the hit and follow-through (a3 pitch 13 -> 54, shoulder
                        # twist +16 -> +25; halved for the kneel). Same drawings, timing and kneeling legs as v8.
                        draw_k = cl(U_*-.12 + V_*.30 + Vector((0, 0, 1.08)), -U_*.45 + V_*.75 + Vector((0, 0, .50)),
                                    hunch=6.0, pitch=6.0, turn=IDLE_R['turn'] + 12.0)
                        sweep_k = cl(U_*.06 + V_*.28 + Vector((0, 0, .86)), U_*.70 + V_*.45 + Vector((0, 0, .25)),
                                     ce=.35, pitch=4.0, turn=IDLE_R['turn'] - 6.0)
                        hit_k = cl(U_*.36 + V_*.20 + Vector((0, 0, .62)), U_*.85 + V_*.42 + Vector((0, 0, -.14)),
                                   ce=.38, pitch=24.0, hunch=13.0, turn=IDLE_R['turn'] - 18.0)
                        follow_k = cl(U_*.34 + V_*.10 + Vector((0, 0, .60)), U_*.72 - to_cam*.35 + Vector((0, 0, -.12)),
                                      ce=.39, pitch=32.0, hunch=14.0, turn=IDLE_R['turn'] - 22.0)
                        back1 = cl(cr_hand.lerp(follow_k['hand'], .5), (-U_*.30 + V_*.40 + Vector((0, 0, -.08))),
                                   ce=.35, pitch=18.0, hunch=11.0, turn=IDLE_R['turn'] - 8.0)
                        back2 = cl(cr_hand.lerp(follow_k['hand'], .15), (Vector(follow_k['blade_dir'])*.15 + cr_blade),
                                   ce=.32, turn=IDLE_R['turn'])
                        for k_, tw_ in ((draw_k, -6.0), (sweep_k, 6.0), (hit_k, 12.0), (follow_k, 16.0), (back1, 6.0)):
                            k_['twist'] = tw_
                        hit_k['offset_px'] = (-40, 0)
                        follow_k['offset_px'] = (-30, 0)
                        # the draw-back is now high, so the draw -> sweep arc no longer runs along the floor: smear it too
                        sweep_k['smear'] = 1; hit_k['smear'] = 1; follow_k['smear'] = 1
                        if not HURT.endswith('_v9'):
                            # v10: v9's draw -> sweep smear covered his face and the steep sweep blade turned the hit
                            # smear into an upright fin; no smear on the sweep, its blade nearly level.
                            sweep_k['blade_dir'] = tuple((U_*.80 + V_*.45 + Vector((0, 0, .08))).normalized())
                            sweep_k['smear'] = 0
                        if not HURT.endswith(('_v9', '_v10')):
                            # v11: the low-swing bow turned v10's sweep -> hit smear (a downward chop) into a dome; keep
                            # the tip's real path instead.
                            hit_k['smear_bow'] = False
                        if not HURT.endswith(('_v9', '_v10', '_v11')):
                            # v12 (Kvon: the arm clipped through him - turn his torso): v9-v11 turned him toward the
                            # camera through the swing, so the right arm reached across his chest and the guard sat on his
                            # front thigh. Hips stay at the crouch turn; the upper body twists toward the opponent so the
                            # right shoulder leads. Hands and blades unchanged (same range).
                            for k_, tw_ in ((sweep_k, 25.0), (hit_k, 40.0), (follow_k, 45.0), (back1, 20.0)):
                                k_.update(turn=IDLE_R['turn'], twist=tw_)
                        if not HURT.endswith(('_v9', '_v10', '_v11', '_v12')):
                            # v13: v12's sweep forearm still crossed his chest and the hit/follow guard sat in his front
                            # shin. Hands move straight toward the camera (V_ is the view axis of this orthographic
                            # camera, so the on-screen path and reach are unchanged) and the sweep twists further.
                            for k_, dv_ in ((sweep_k, .14), (hit_k, .14), (follow_k, .16)):
                                k_['hand'] = k_['hand'] + V_*dv_
                            sweep_k['twist'] = 35.0
                            back1['hand'] = cr_hand.lerp(follow_k['hand'], .5)
                            if not HURT.endswith('_v13'):
                                back1['hand'] = back1['hand'] + V_*.12  # v14: v13's return guard still sat on his thigh
                            if not HURT.endswith(('_v13', '_v14')):
                                # v15 (Kvon: he leans over too much - rotate the torso toward the attack, only a small
                                # lean): MoMask's forward pitch (hit 24 / follow 32) back near the crouch's own 10/9; the
                                # rotation toward the opponent carries the swing (twist +5 on hit and follow).
                                for k_, p_, h_, tw_ in ((sweep_k, 6.0, 9.0, 35.0), (hit_k, 13.0, 9.0, 45.0),
                                                        (follow_k, 14.0, 9.0, 50.0), (back1, 11.0, 9.0, 20.0)):
                                    k_.update(pitch=p_, hunch=h_, twist=tw_)
                    if not HURT.endswith(tuple(f'_v{n_}' for n_ in range(1, 16))):
                        # v16 (Kvon: make it a jab instead of a downward slash): chamber at the hip with the blade
                        # already aimed at the opponent, a straight low thrust out to about the slash's reach, retract,
                        # back to the crouch. Torso rotates toward the attack with a small lean (v15 rule); hands sit on
                        # the camera side (V_ .34) so the arm stays out of his body. Thrust dash lines behind the right
                        # fist on the hit instead of an arc smear.
                        jab_dir = U_*.96 + V_*.08 + Vector((0, 0, -.16))
                        draw_k = cl(U_*-.10 + V_*.34 + Vector((0, 0, .74)), jab_dir, pitch=9.0, turn=IDLE_R['turn'])
                        sweep_k = cl(U_*.12 + V_*.34 + Vector((0, 0, .70)), jab_dir, ce=.34, pitch=10.0,
                                     turn=IDLE_R['turn'])
                        hit_k = cl(U_*.30 + V_*.34 + Vector((0, 0, .66)), jab_dir, ce=.36, pitch=12.0,
                                   turn=IDLE_R['turn'])
                        follow_k = cl(U_*.24 + V_*.34 + Vector((0, 0, .67)), jab_dir, ce=.35, pitch=11.0,
                                      turn=IDLE_R['turn'])
                        back1 = cl(cr_hand.lerp(U_*.02 + V_*.34 + Vector((0, 0, .72)), .5) + V_*.12,
                                   (jab_dir + cr_blade).normalized(), ce=.33, pitch=10.0, turn=IDLE_R['turn'])
                        back2 = cl(cr_hand.lerp(follow_k['hand'], .15), (jab_dir*.15 + cr_blade), ce=.32,
                                   turn=IDLE_R['turn'])
                        for k_, tw_ in ((draw_k, -10.0), (sweep_k, 25.0), (hit_k, 45.0), (follow_k, 40.0),
                                        (back1, 15.0)):
                            k_['twist'] = tw_
                        hit_k['offset_px'] = (-40, 0)
                        follow_k['offset_px'] = (-30, 0)
                        hit_k.update(smear=1, smear_style='thrust', smear_grip='R')
                        if not HURT.endswith('_v16'):
                            # v17: v16's hit target (V_ .34) was out of arm's reach - the fist stopped where the sweep
                            # was, so the jab barely travelled; and the return blade dipped through the floor. Chamber
                            # further back, extended hands nearer his body line, return blade level behind (as v5).
                            draw_k['hand'] = U_*-.22 + V_*.30 + Vector((0, 0, .74))
                            sweep_k['hand'] = U_*.06 + V_*.24 + Vector((0, 0, .70))
                            hit_k['hand'] = U_*.30 + V_*.18 + Vector((0, 0, .66))
                            follow_k['hand'] = U_*.22 + V_*.20 + Vector((0, 0, .67))
                            back1['blade_dir'] = tuple((-U_*.30 + V_*.40 + Vector((0, 0, -.08))).normalized())
                        if not HURT.endswith(('_v16', '_v17')):
                            # v18 (Kvon: tuck the non-sword hand at his side, still bent): the left fist leaves the chest
                            # guard for his left side at the waist, a little behind the hip, elbow bent, through the jab;
                            # halfway back on the first return drawing, the crouch guard again on the last.
                            l_tuck = tc_ @ Vector((.22, .06, .80))
                            for k_ in (draw_k, sweep_k, hit_k, follow_k):
                                k_['l_hand'] = tuple(l_tuck)
                            back1['l_hand'] = tuple(l_tuck.lerp(cr_guard, .5))
                        if not HURT.endswith(('_v16', '_v17', '_v18')):
                            # v19 (Kvon chose the 68 deg C2 free hand for the chamber and asked to match the rest): the
                            # left fist in front of his lower chest toward the camera, elbow out to his side; through the
                            # drive / hit / hold it rotates about his spine with the torso twist so the arm keeps its shape;
                            # halfway to the guard on the first return drawing. The v18 hit/hold/drive Key teeth ran off
                            # the frame's right edge: shifted further left in-frame (Godot shifts back).
                            c2_ = tc_ @ Vector((.12, -.10, .82)) + V_*.32
                            for k_ in (draw_k, sweep_k, hit_k, follow_k):
                                rot_ = Matrix.Rotation(math.radians(k_['twist'] - draw_k['twist']), 3, 'Z')
                                k_['l_hand'] = tuple(rot_ @ Vector((c2_.x, c2_.y, 0)) + Vector((0, 0, c2_.z)))
                            back1['l_hand'] = tuple(Vector(follow_k['l_hand']).lerp(cr_guard, .5))
                            sweep_k['offset_px'] = (-60, 0)
                            hit_k['offset_px'] = (-110, 0)
                            follow_k['offset_px'] = (-100, 0)
                            if HURT.endswith(tuple(f'_v{n_}' for n_ in range(26, 100))):
                                # v26 (Kvon: the arm stays tucked at his side for poses 1-4; after pose 2 the elbow bends
                                # more and more until pose 4): the fist holds the chamber spot instead of swinging across
                                # his chest with the twist; poses 3 and 4 pull it toward the shoulder (v27+, measured).
                                for k_ in (draw_k, sweep_k, hit_k, follow_k):
                                    k_['l_hand'] = tuple(c2_)
                                if not HURT.endswith('_v26'):
                                    # v27: v26's fixed fist left the arm straight (35/29/31 deg) - the twist carries his
                                    # left shoulder ~.15 m back. Rebuild each fist from the measured shoulder (v26 world):
                                    # the chamber's shoulder -> fist offset turned with the shoulder line (+35 / +50 / +40
                                    # deg) and shortened for more bend in poses 3-4 (1 / .87 / .75). Target = chamber
                                    # target + (wanted fist - chamber fist); `l_fix` adds the measured residual (v28+).
                                    s1_, f1_ = Vector((.0521, -.161, .7572)), Vector((-.0458, -.3478, .5781))
                                    l_fix = {}
                                    if not HURT.endswith('_v27'):
                                        # v28: v27's fists landed off the wanted spots (bends 96 / 63 / 63) - each drawing's
                                        # measured residual (wanted - v27 fist) added to its target.
                                        l_fix = {id(sweep_k): (.1922, -.1496, .0484), id(hit_k): (.3447, -.2674, .0205),
                                                 id(follow_k): (.3122, -.2415, .016)}
                                    for k_, s_, yaw_, sc_ in ((sweep_k, (-.1538, .0766, .8234), 35.4, 1.0),
                                                              (hit_k, (-.3112, .2244, .7861), 50.1, .87),
                                                              (follow_k, (-.2743, .1942, .7956), 40.4, .75)):
                                        want_ = Vector(s_) + Matrix.Rotation(math.radians(yaw_), 3, 'Z') @ (f1_ - s1_)*sc_
                                        # v29: v28's full residual over-folded (100 / 140 / 144: the shoulder follows the
                                        # fist in). Interpolated per drawing from the measured bends for 70 / 85 / 100 deg:
                                        # drive .57 of v27's move (v26 35 -> v27 96), hit .29 and hold .46 of the residual.
                                        base_, fs_ = 1.0, 1.0
                                        if not HURT.endswith(('_v27', '_v28')):
                                            base_, fs_ = {id(sweep_k): (.57, 0.0), id(hit_k): (1.0, .29),
                                                          id(follow_k): (1.0, .46)}[id(k_)]
                                        k_['l_hand'] = tuple(c2_ + (want_ - f1_)*base_ +
                                                             Vector(l_fix.get(id(k_), (0, 0, 0)))*fs_)
                                back1['l_hand'] = tuple(Vector(follow_k['l_hand']).lerp(cr_guard, .5))
                                if HURT.endswith(tuple(f'_v{n_}' for n_ in range(30, 100))):
                                    # v30: v27-v29's hand targets were chased by the shoulder reach and the bend jumped
                                    # (96/63/63, 100/140/144, 92/10/40). Poses 2-4 now set the arm by shape (new 'l_arm'):
                                    # the chamber's measured shoulder -> wrist direction and elbow side (v25 drawing 1:
                                    # true elbow fold 96.5 deg, shoulder line yaw -33.4) turned with his shoulders, folded
                                    # 96.5 (same as the chamber) -> 111.5 -> 126.5 deg.
                                    arm_ref = dict(ref_yaw=-33.4, dir=(-.0979, -.1868, -.1791), elbow=(.0681, -.0935, -.1909))
                                    for k_, fold_ in ((sweep_k, 96.5), (hit_k, 111.5), (follow_k, 126.5)):
                                        k_['l_arm'] = dict(arm_ref, fold=fold_)
                                    back1['l_hand'] = tuple(c2_.lerp(cr_guard, .5))
                            elif HURT.endswith(tuple(f'_v{n_}' for n_ in range(21, 26))):
                                # v21: what sets the bend is the shoulder-to-fist distance (v19: chamber .277 m = 68 deg,
                                # hit / hold .356 m = 47 / 46 deg). Keep v19's directions; pull the hit and hold fists
                                # ~.08 m toward the measured shoulder (elbow_angles / shfist on v19).
                                # v22: v21's full .08 m overshot (96 deg; the shoulder also follows the fist) - .43 of it.
                                # v23: .43 gave 80 / 81 deg; measured 0 -> 47, .43 -> 80, 1 -> 96: 68 deg at ~.27.
                                # v24: .27 gave hit 51 / hold 77 (the solver is not smooth) - tuned separately from each
                                # drawing's own measurements: hit .36, hold .19.
                                pull_ = {'_v21': 1.0, '_v22': .43, '_v23': .27}.get(HURT[HURT.rindex('_v'):])
                                # v25: the solver jumps between ~50 and ~78 deg (hit .27 -> 51, .36 -> 78; hold .19 -> 52,
                                # .27 -> 77), so 68 itself isn't reachable; use the bent branch on both: hit .36, hold .27.
                                pull_h, pull_f = ((pull_, pull_) if pull_ is not None else
                                                  (.36, .19) if HURT.endswith('_v24') else (.36, .27))
                                hit_k['l_hand'] = tuple(Vector(hit_k['l_hand']) + Vector((-.047, .042, .046))*pull_h)
                                follow_k['l_hand'] = tuple(Vector(follow_k['l_hand']) + Vector((-.041, .044, .046))*pull_f)
                                back1['l_hand'] = tuple(Vector(follow_k['l_hand']).lerp(cr_guard, .5))
                            elif not HURT.endswith('_v19'):
                                # v20: v19's full-twist rotation swung the fist past where the chest turns (bends 68 / 73 /
                                # 47 / 46 deg); the chest takes ~60% of the twist, so the fist follows by that much.
                                for k_ in (sweep_k, hit_k, follow_k):
                                    rot_ = Matrix.Rotation(math.radians(.6*(k_['twist'] - draw_k['twist'])), 3, 'Z')
                                    k_['l_hand'] = tuple(rot_ @ Vector((c2_.x, c2_.y, 0)) + Vector((0, 0, c2_.z)))
                                back1['l_hand'] = tuple(Vector(follow_k['l_hand']).lerp(cr_guard, .5))
                    if OUT_NAME.endswith('_lhandcheck6'):
                        # review 6 (Kvon: take the new C2, pivot the shoulder so the elbow moves further toward his back):
                        # lhandcheck5's C2 fist unchanged; the left elbow hint swings from the default toward his back
                        # (tc_ (0, 1, 0): he faces -y in his body frame), a little down.
                        c2_hand = tuple(tc_ @ Vector((.12, -.10, .82)) + V_*.32)
                        back_dir = (tc_ @ Vector((0, 1, 0)) + Vector((0, 0, -.30))).normalized()
                        RUN_KEYS = []
                        for t_ in (0.0, .4, .7, 1.0):
                            k_ = dict(draw_k)
                            k_.update(l_hand=c2_hand, smear=0,
                                      l_elbow_hint=tuple(Vector((1, .4, -.3)).normalized().lerp(back_dir, t_)))
                            RUN_KEYS.append(k_)
                        GAME_FRAMES = [6]*len(RUN_KEYS); DURATIONS_MS = [100.0]*len(RUN_KEYS); n = len(RUN_KEYS)
                    elif OUT_NAME.endswith('_lhandcheck5'):
                        # review 5: lhandcheck4 opened C2 to 68 but C1 only to 135 (fist kept against the ribs folds the
                        # elbow); C1 fist lower and further toward the camera. Others as lhandcheck4.
                        RUN_KEYS = []
                        for p_, dv_, dir_, ext_ in (((.18, .12, .95), 0.0, (.67, .21, -.71), .10),
                                                    ((.20, .00, .70), .32, (0, 0, 1), 0.0),
                                                    ((.12, -.10, .82), .32, (0, 0, 1), 0.0),
                                                    ((.10, -.10, .95), .32, (-.46, -.83, -.33), .06)):
                            k_ = dict(draw_k)
                            k_.update(l_hand=tuple(tc_ @ Vector(p_) + V_*dv_ + Vector(dir_).normalized()*ext_), smear=0)
                            RUN_KEYS.append(k_)
                        GAME_FRAMES = [6]*len(RUN_KEYS); DURATIONS_MS = [100.0]*len(RUN_KEYS); n = len(RUN_KEYS)
                    elif OUT_NAME.endswith('_lhandcheck4'):
                        # review 4: lhandcheck3 opened C (84) and C3 (37) but C1 folded further (164) and C2 barely moved
                        # (91) - the shoulder slid forward after the fist. C1/C2 fists instead drop below the shoulder and
                        # come further toward the camera.
                        RUN_KEYS = []
                        for p_, dv_, dir_, ext_ in (((.18, .12, .95), 0.0, (.67, .21, -.71), .10),
                                                    ((.16, -.02, .80), .22, (0, 0, 1), 0.0),
                                                    ((.12, -.10, .82), .32, (0, 0, 1), 0.0),
                                                    ((.10, -.10, .95), .32, (-.46, -.83, -.33), .06)):
                            k_ = dict(draw_k)
                            k_.update(l_hand=tuple(tc_ @ Vector(p_) + V_*dv_ + Vector(dir_).normalized()*ext_), smear=0)
                            RUN_KEYS.append(k_)
                        GAME_FRAMES = [6]*len(RUN_KEYS); DURATIONS_MS = [100.0]*len(RUN_KEYS); n = len(RUN_KEYS)
                    elif OUT_NAME.endswith('_lhandcheck3'):
                        # review 3 (Kvon: less bend in the elbow for all of these poses): the lhandcheck2 fists moved
                        # further from the shoulder along the measured shoulder -> fist direction (elbow_angles.py on
                        # lhandcheck2: bends 133 / 149 / 95 / 62 deg).
                        RUN_KEYS = []
                        for p_, dv_, dir_, ext_ in (((.18, .12, .95), 0.0, (.67, .21, -.71), .10),
                                                    ((.14, -.04, .95), .12, (.86, -.12, -.49), .12),
                                                    ((.12, -.08, .95), .22, (.25, -.75, -.62), .10),
                                                    ((.10, -.10, .95), .32, (-.46, -.83, -.33), .06)):
                            k_ = dict(draw_k)
                            k_.update(l_hand=tuple(tc_ @ Vector(p_) + V_*dv_ + Vector(dir_).normalized()*ext_), smear=0)
                            RUN_KEYS.append(k_)
                        GAME_FRAMES = [6]*len(RUN_KEYS); DURATIONS_MS = [100.0]*len(RUN_KEYS); n = len(RUN_KEYS)
                    elif OUT_NAME.endswith('_lhandcheck2'):
                        # review 2 (Kvon: focus on C, rotate the shoulder so the fist is toward the player): C's rib-height
                        # fist, brought round toward the camera in steps (world V_ = toward the viewer).
                        RUN_KEYS = []
                        for p_, dv_ in (((.18, .12, .95), 0.0), ((.14, -.04, .95), .12), ((.12, -.08, .95), .22),
                                        ((.10, -.10, .95), .32)):
                            k_ = dict(draw_k); k_.update(l_hand=tuple(tc_ @ Vector(p_) + V_*dv_), smear=0)
                            RUN_KEYS.append(k_)
                        GAME_FRAMES = [6]*len(RUN_KEYS); DURATIONS_MS = [100.0]*len(RUN_KEYS); n = len(RUN_KEYS)
                    elif OUT_NAME.endswith('_lhandcheck'):
                        # review (Kvon: show possible orientations of the non-sword arm for the first pose): the chamber
                        # drawing with the left fist in different places (body frame: +x his left, -y forward, z up).
                        L_OPTIONS = [('A tucked at side', (.22, .06, .80)), ('B chest guard', (.10, -.30, .98)),
                                     ('C high chamber at ribs', (.18, .12, .95)), ('D forward guard', (.06, -.42, 1.02)),
                                     ('E on front knee', (.12, -.34, .58)), ('F back for balance', (.30, .32, .86))]
                        RUN_KEYS = []
                        for label_, p_ in L_OPTIONS:
                            k_ = dict(draw_k); k_.update(l_hand=tuple(tc_ @ Vector(p_)), smear=0)
                            RUN_KEYS.append(k_)
                        GAME_FRAMES = [6]*len(RUN_KEYS); DURATIONS_MS = [100.0]*len(RUN_KEYS); n = len(RUN_KEYS)
                    else:
                        RUN_KEYS = [draw_k, sweep_k, hit_k, follow_k, back1, back2]
                    if OUT_NAME.endswith('_crouchcheck'):
                        RUN_KEYS = [cl(cr_hand, cr_blade)]  # review: the rebuilt crouch next to the approved one
                        GAME_FRAMES = [6]; DURATIONS_MS = [100.0]; n = 1
                    if CM_HURT:
                        HURT = CM_HURT
                        # Crouching Medium v1 (Kvon, October 28: the active pose like Ky's GGST 2S, his reference
                        # design/references/ky_ggst_2s_active_kvon.png): review-only active-pose candidates on the approved
                        # kneel, free fist at the chest guard. A = Ky's pose: end of a wide low sweep, sword arm extended
                        # back and low on the camera side, blade trailing behind to the floor, chest opened toward the
                        # camera, forward lean. B = A with a small lean (Kvon's Crouching Light rule). C = the same body
                        # mid-sweep, blade low and out in front toward the opponent.
                        trail_ = -U_*.80 + V_*.55 + Vector((0, 0, -.30))
                        cm_a = cl(U_*-.28 + V_*.32 + Vector((0, 0, .50)), trail_, ce=.36, hunch=12.0, pitch=24.0,
                                  turn=IDLE_R['turn'])
                        cm_a.update(twist=-20.0, offset_px=(70, 0))
                        cm_b = cl(U_*-.28 + V_*.32 + Vector((0, 0, .54)), trail_, ce=.36, hunch=9.0, pitch=12.0,
                                  turn=IDLE_R['turn'])
                        cm_b.update(twist=-20.0, offset_px=(70, 0))
                        cm_c = cl(U_*.28 + V_*.34 + Vector((0, 0, .52)), U_*.60 + V_*.70 + Vector((0, 0, -.25)), ce=.36,
                                  hunch=9.0, pitch=14.0, turn=IDLE_R['turn'])
                        cm_c.update(twist=35.0, offset_px=(-60, 0))
                        if not HURT.endswith('_v1'):
                            # v2: in v1's A/B the sword hand sat in front of his knee (arm across his body; Ky's reaches
                            # back past his hip) and the tip dipped under the floor: hand back behind the hip and higher,
                            # blade raised so the tip just touches the floor, drawn further right in the frame.
                            trail_ = -U_*.85 + V_*.55 + Vector((0, 0, -.22))
                            for k_, z_ in ((cm_a, .66), (cm_b, .70)):
                                k_.update(hand=U_*-.50 + V_*.30 + Vector((0, 0, z_)),
                                          blade_dir=tuple(trail_.normalized()), offset_px=(100, 0))
                        RUN_KEYS = [cm_a, cm_b, cm_c]
                        GAME_FRAMES = [6]*3; DURATIONS_MS = [100.0]*3; n = 3
                        if not HURT.endswith(('_v1', '_v2')):
                            # v3 (Kvon, October 29: "Use these poses for now" - Gemini round 51, active pose A): from the
                            # kneel, the Key rises up and back over his rear shoulder (wind-up), sweeps forward low near
                            # the floor in front of him, swings round toward the camera (in-between Gemini skips), reaches
                            # pose A (arm back, Key trailing low behind), then comes back low in front and into the kneel.
                            # Startup 9 (in, wind-up, sweep, round), active 3, recovery 17 - like the Standing Medium.
                            crouch_k = cl(cr_hand, cr_blade)
                            CM_LOOK_SIGN = -1.0 if OUT_NAME.endswith('_lookneg') else 1.0
                            windup_k = cl(U_*-.30 + V_*.18 + Vector((0, 0, 1.10)), -U_*.55 + V_*.35 + Vector((0, 0, .75)),
                                          ce=.30, hunch=4.0, pitch=4.0, turn=IDLE_R['turn'] + 10.0)
                            windup_k['twist'] = -15.0
                            in_k = cl(cr_hand.lerp(windup_k['hand'], .5),
                                      (cr_blade + Vector(windup_k['blade_dir'])).normalized(), ce=.31, turn=IDLE_R['turn'] + 5.0)
                            sweep_k = cl(U_*.26 + V_*.30 + Vector((0, 0, .56)), U_*.80 + V_*.40 + Vector((0, 0, -.18)),
                                         ce=.36, hunch=10.0, pitch=16.0, turn=IDLE_R['turn'])
                            sweep_k.update(twist=30.0, offset_px=(-60, 0))
                            round_k = cl(U_*-.02 + V_*.36 + Vector((0, 0, .56)), V_*.85 - U_*.20 + Vector((0, 0, -.20)),
                                         ce=.36, hunch=11.0, pitch=20.0, turn=IDLE_R['turn'])
                            round_k['twist'] = 5.0
                            act_k = dict(cm_a)
                            recover_k = cl(U_*.10 + V_*.30 + Vector((0, 0, .62)), U_*.45 + V_*.55 + Vector((0, 0, -.45)),
                                           ce=.34, hunch=8.0, pitch=10.0, turn=IDLE_R['turn'])
                            if not HURT.endswith('_v3'):
                                # v4: v3's in-between blade ran off the left edge and the recovery tip went through the floor.
                                in_k['blade_dir'] = tuple((-U_*.30 + V_*.75 + Vector((0, 0, .45))).normalized())
                                recover_k['blade_dir'] = tuple((U_*.55 + V_*.70 + Vector((0, 0, -.22))).normalized())
                            if not HURT.endswith(('_v3', '_v4')):
                                # v5 (Kvon): a lunge from the wind-up to the hit - front knee fully bent over the front foot,
                                # back leg stretched straight behind on its toes; wind-up with the right forearm across the
                                # chest under the chin and the Key over his FRONT shoulder; then a backhand sweep into pose A.
                                lunge_f = {'L': (L0[0] + .16, L0[1], 0.0, 0.0), 'R': (R0[0] - .42, R0[1], .02, 45.0)}
                                half_f = {'L': (L0[0] + .08, L0[1], 0.0, 0.0), 'R': (R0[0] - .20, R0[1], .02, 30.0)}
                                back_hint = {'R': tuple(-U_*.6 + Vector((0, 0, -.8)))}
                                windup_k = cl(tc_ @ Vector((.14, -.24, 1.06)), U_*.50 - to_cam*.45 + Vector((0, 0, .70)),
                                              ce=.40, hunch=10.0, pitch=18.0, turn=IDLE_R['turn'] + 10.0,
                                              l_hand=tc_ @ Vector((.24, -.30, .86)), feet=lunge_f)
                                windup_k['twist'] = -10.0
                                in_k = cl(cr_hand.lerp(windup_k['hand'], .5),
                                          (cr_blade + Vector(windup_k['blade_dir'])).normalized(), ce=.34, hunch=9.0,
                                          pitch=12.0, turn=IDLE_R['turn'] + 5.0, feet=half_f)
                                for k_, (ce_, pt_) in ((sweep_k, (.42, 22.0)), (round_k, (.42, 24.0)), (act_k, (.42, 26.0))):
                                    k_['feet'] = lunge_f
                                    k_['ce'] = ce_ - .08 + .08  # same sink as the wind-up
                                    k_['pitch'] = pt_
                                recover_k['feet'] = half_f
                                for k_ in (in_k, windup_k, sweep_k, round_k, act_k, recover_k):
                                    k_['knee_hint_world'] = back_hint
                                if not HURT.endswith('_v5'):
                                    # v6: v5 sank into a split (hips centred between the feet and far too low, legs through
                                    # the floor) so the front knee could not bend: hips forward over the front foot (front
                                    # foot under him, back foot far behind), less sink, front knee pointing forward.
                                    lunge_f = {'L': (L0[0] - .04, L0[1], 0.0, 0.0), 'R': (R0[0] - .55, R0[1], .02, 50.0)}
                                    half_f = {'L': (L0[0] - .02, L0[1], 0.0, 0.0), 'R': (R0[0] - .28, R0[1], .02, 35.0)}
                                    hints_ = {'R': tuple(-U_*.6 + Vector((0, 0, -.8))), 'L': tuple(U_*.9 + Vector((0, 0, .1)))}
                                    for k_, ce_, ft_ in ((in_k, .34, half_f), (windup_k, .36, lunge_f), (sweep_k, .37, lunge_f),
                                                         (round_k, .37, lunge_f), (act_k, .37, lunge_f), (recover_k, .34, half_f)):
                                        k_.update(feet=ft_, ce=ce_, knee_hint_world=hints_)
                                    sweep_k['offset_px'] = (0, 0)
                                if not HURT.endswith(('_v5', '_v6')):
                                    # v7: v6's back foot sat 1.0 m behind the hips - longer than the leg (.69 m) - forcing
                                    # a split. Back foot ~.55 m behind, front foot ~.20 m ahead under the bent knee, and the
                                    # hips at the height that leaves the back leg almost straight.
                                    lunge_f = {'L': (.20, L0[1], 0.0, 0.0), 'R': (-.55, R0[1], .02, 50.0)}
                                    half_f = {'L': (.30, L0[1], 0.0, 0.0), 'R': (-.50, R0[1], .02, 35.0)}
                                    for k_, ce_, ft_ in ((in_k, .30, half_f), (windup_k, .32, lunge_f), (sweep_k, .33, lunge_f),
                                                         (round_k, .33, lunge_f), (act_k, .33, lunge_f), (recover_k, .30, half_f)):
                                        k_.update(feet=ft_, ce=ce_)
                                if not HURT.endswith(('_v5', '_v6', '_v7')):
                                    # v8: back leg straighter (foot further behind), sweep drawn left so its tip stays inside.
                                    lunge_f = {'L': (.20, L0[1], 0.0, 0.0), 'R': (-.66, R0[1], .02, 55.0)}
                                    for k_ in (windup_k, sweep_k, round_k, act_k):
                                        k_['feet'] = lunge_f
                                    sweep_k['offset_px'] = (-50, 0)
                                if not HURT.endswith(('_v5', '_v6', '_v7', '_v8')):
                                    # v9 (Kvon: straighten the back knee on the wind-up, sweep, round and active poses).
                                    lunge_f = {'L': (.20, L0[1], 0.0, 0.0), 'R': (-.78, R0[1], .02, 60.0)}
                                    for k_ in (windup_k, sweep_k, round_k, act_k):
                                        k_['feet'] = lunge_f
                                    if not HURT.endswith('_v9'):
                                        sweep_k['offset_px'] = (-30, 0)  # v10: v9's back foot touched the left edge
                                if not HURT.endswith(('_v5', '_v6', '_v7', '_v8', '_v9', '_v10')):
                                    # v11 (Kvon: straighten the ankle too, bend the front foot's toes, lean the torso
                                    # forward): back foot pointed in line with the straight leg; front heel lifted with the
                                    # toes bent flat on the floor; more forward lean (pitch +14, hunch +6).
                                    lunge_f = {'L': (.20, L0[1], 0.0, 25.0), 'R': (-.78, R0[1], .02, 60.0)}
                                    for k_ in (windup_k, sweep_k, round_k, act_k):
                                        k_.update(feet=lunge_f, ankle_deg={'R': 15.0}, toe_bend={'L': 25.0},
                                                  pitch=k_['pitch'] + (14.0 if HURT.endswith('_v11') else 10.0),
                                                  hunch=k_['hunch'] + (6.0 if HURT.endswith('_v11') else 4.0))
                                    if not HURT.endswith(('_v11', '_v12', '_v13')):
                                        # v14 (Kvon: orient the straight leg so the foot touches the ground): v13's back leg
                                        # rose to hip height (ankle target lifted by the toe pitch). Ankle aimed low at the
                                        # floor so the straight leg slopes down and the pointed foot reaches the ground.
                                        for k_ in (windup_k, sweep_k, round_k, act_k):
                                            k_['feet'] = {'L': lunge_f['L'], 'R': (-.70, R0[1], 0.0, 0.0)}
                                    if not HURT.endswith(tuple(f'_v{n_}' for n_ in range(11, 15))):
                                        # v15 (Kvon: step 1 - lock the active pose toward Ky's 2S, with Ky's lower bent back
                                        # leg): back knee low near the floor (kneel-style, shin back), front knee deeply bent
                                        # over the front foot, chest up and opened to the camera, head lifted toward the
                                        # opponent, sword arm reaching back at shoulder height, blade sloping down to the
                                        # floor behind him, free fist at the chest.
                                        act_k.update(feet={'L': (.22, L0[1], 0.0, 25.0),
                                                           'R': (R0[0] + .10, R0[1] - .40, .11 - TOE_D*math.sin(math.radians(25.0)), 25.0)},
                                                     ce=.36, pitch=10.0, hunch=-2.0, neck=-26.0, twist=-28.0,
                                                     hand=U_*-.48 + V_*.30 + Vector((0, 0, 1.00)),
                                                     blade_dir=tuple((-U_*.70 + V_*.40 + Vector((0, 0, -.60))).normalized()),
                                                     knee_hint_world={'R': tuple(U_*.15 + Vector((0, 0, -1.0))),
                                                                      'L': tuple(U_*.9 + Vector((0, 0, .1)))},
                                                     ankle_deg=None, toe_bend={'L': 25.0}, offset_px=(110, 0))
                                        if not HURT.endswith('_v15'):
                                            # v16: lean forward from the hips like Ky; neck tilted back so the head stays up.
                                            act_k.update(pitch=22.0, neck=-38.0)
                                        if not HURT.endswith(('_v15', '_v16')):
                                            # v17: v16's pitch went mostly into the screen from this camera; lean the upper
                                            # body toward the opponent in the screen plane (as the hurt poses do), head
                                            # turned back up.
                                            act_k.update(pitch=12.0, neck=-28.0, lean_cam=-24.0, head_cam=16.0)
                                        if not HURT.endswith(('_v15', '_v16', '_v17')):
                                            # v18 (Kvon): front foot further forward (v17's thigh pressed into his torso).
                                            act_k['feet'] = {'L': (.36, L0[1], 0.0, 25.0), 'R': act_k['feet']['R']}
                                    if not HURT.endswith(tuple(f'_v{n_}' for n_ in range(11, 18))):
                                        # v18 (Kvon: he looks forward for the whole animation): the head turns back against
                                        # the chest twist so the face stays on the opponent at screen right.
                                        for k_ in (in_k, windup_k, sweep_k, round_k, act_k, recover_k):
                                            k_['look'] = 8.0 + CM_LOOK_SIGN*k_.get('twist', 0.0)
                                        for k_ in (windup_k, sweep_k, round_k):
                                            # the lunge's forward lean tipped the face down: neck back and head up on screen
                                            k_.update(neck=-30.0, head_cam=-18.0 if OUT_NAME.endswith('_hcneg') else 18.0)
                                    if not HURT.endswith('_v11'):
                                        # v12: v11 hid his face and pushed the pointed back foot / low blades past the left
                                        # edge and the floor: a little less lean, frames drawn right, blades raised.
                                        windup_k['offset_px'] = (30, 0); sweep_k['offset_px'] = (10, 0)
                                        round_k['offset_px'] = (30, 0)
                                        sweep_k['blade_dir'] = tuple(((U_*.80 + V_*.45) if HURT.endswith('_v12') else
                                                                      (U_*.55 + V_*.80) + Vector((0, 0, -.04))).normalized())
                                        round_k['blade_dir'] = tuple((V_*.85 - U_*.20 + Vector((0, 0, -.06))).normalized())
                            sweep_k['smear'] = 1; round_k['smear'] = 1; act_k['smear'] = 1
                            RUN_KEYS = [in_k, windup_k, sweep_k, round_k, act_k, recover_k, crouch_k]
                            GAME_FRAMES = [2, 3, 2, 2, 3, 5, 12]
                            DURATIONS_MS = [round(f_*1000/60, 3) for f_ in GAME_FRAMES]; n = len(DURATIONS_MS)
                elif jpart == 'atk_sheavy':
                    # Standing Heavy (Kvon, October 27; matched to Gemini round-45 poses 2-9 with spin in-betweens): a wide
                    # spinning two-handed slash. Raised over the rear shoulder -> coiled low wind-up -> a full turn on the
                    # spot (turning away first: back to the viewer, round to chest-to-camera) with the Key trailing out
                    # level -> deep-lunge impact with the Key level out front -> follow-through over the shoulder -> heavy
                    # settle with the Key pointing down -> idle. Hands/blades in his body frame where they turn with him;
                    # through the spin the feet pivot with the body so the legs never twist.
                    bfh = lambda turn_, x_, y_, z_: Matrix.Rotation(math.radians(turn_), 3, 'Z') @ Vector((x_, y_, z_))

                    def hv(turn, twist, hand, blade, ce=.06, pitch=0.0, hunch=0.0, feet=None):
                        k_ = hurt(feet or stand, ce, hunch, pitch, -6.0, hand, Vector(blade).normalized(), hand, ground=True)
                        k_.update(no_center=True, look=8.0, turn=turn, twist=twist, release=0.0,
                                  l_elbow_hint=tuple(V_*.75 + U_*.10 + Vector((0, 0, -.65))))
                        return k_

                    def pivot_feet(turn, half=.11):
                        # feet side by side under him in his body frame, turned with him
                        out = {}
                        for sd_, x_ in (('L', half), ('R', -half)):
                            w_ = bfh(turn, x_, 0.0, 0.0)
                            out[sd_] = (w_.dot(U_), w_.dot(V_), 0.0, 10.0)
                        return out
                    lunge = {'L': (L0[0] + .22, L0[1], 0.0, 0.0), 'R': (R0[0] - .14, R0[1], 0.0, 35.0)}
                    raised = hv(25.0, -10.0, bfh(25.0, -.14, -.06, 1.06), U_*.75 + V_*.18 + Vector((0, 0, .55)), ce=.06)
                    windup = hv(60.0, -16.0, bfh(60.0, -.18, .04, .90), -U_*.60 + V_*.75 + Vector((0, 0, -.15)), ce=.14,
                                hunch=6.0, feet={'L': (L0[0] + .08, L0[1], 0.0, 0.0), 'R': (R0[0], R0[1], 0.0, 0.0)})
                    spin0 = hv(100.0, -12.0, bfh(100.0, -.10, -.20, 1.05), bfh(100.0, -.50, .50, .70), ce=.08,
                               feet=pivot_feet(100.0, .16))
                    spin1 = hv(150.0, -8.0, bfh(150.0, -.20, -.15, .95), bfh(150.0, -.60, .75, .05), ce=.04,
                               feet=pivot_feet(150.0))
                    spin2 = hv(230.0, -8.0, bfh(230.0, -.20, -.15, .95), bfh(230.0, -.60, .75, .05), ce=.04,
                               feet=pivot_feet(230.0))
                    around = hv(310.0, -6.0, bfh(310.0, -.10, -.25, 1.00), bfh(310.0, -.55, .60, .55), ce=.05,
                                feet=pivot_feet(310.0))
                    impact = hv(375.0, 10.0, U_*.44 + V_*.12 + Vector((0, 0, .86)), U_*.50 + V_*.80 + Vector((0, 0, .22)),
                                ce=.17, pitch=16.0, hunch=6.0, feet=lunge)
                    follow = hv(410.0, 16.0, bfh(410.0, .12, -.12, 1.10), -U_*.70 - V_*.25 + Vector((0, 0, .55)), ce=.14,
                                pitch=8.0, feet=lunge)
                    settle = hv(20.0, 4.0, bfh(20.0, 0.0, -.30, .70), U_*.35 + V_*.35 + Vector((0, 0, -.90)), ce=.16,
                                hunch=14.0, pitch=10.0, feet={'L': (L0[0] + .08, L0[1], 0.0, 0.0), 'R': (R0[0], R0[1], 0.0, 0.0)})
                    if not HURT.endswith('_v1'):
                        # v2 (closer to Gemini's sheet): the turn goes the other way - out of the wind-up his chest swings
                        # toward the camera with the Key up and back over his left shoulder (pose 4), then his back comes
                        # round (pose 5), round again to the front (pose 6) and into the impact; one continuous turn
                        # (decreasing angle). The level trailing Key keeps the same place relative to his body.
                        rb_ = lambda turn_, w_: tuple(Matrix.Rotation(math.radians(-turn_), 3, 'Z') @ Vector(w_))
                        trail_b = rb_(-150.0, (-U_*.85 + V_*.30 + Vector((0, 0, .02))).normalized())
                        spin0 = hv(-30.0, -10.0, bfh(-30.0, .12, -.10, 1.10), bfh(-30.0, .40, .40, .80), ce=.08,
                                   feet=pivot_feet(-30.0, .16))
                        spin1 = hv(-150.0, -8.0, bfh(-150.0, .05, -.28, .95), bfh(-150.0, *trail_b), ce=.04,
                                   feet=pivot_feet(-150.0))
                        spin2 = hv(-240.0, -8.0, bfh(-240.0, .05, -.28, .95), bfh(-240.0, *trail_b), ce=.04,
                                   feet=pivot_feet(-240.0))
                        around = hv(-330.0, -6.0, bfh(-330.0, .12, -.10, 1.08), bfh(-330.0, .40, .40, .80), ce=.05,
                                    feet=pivot_feet(-330.0))
                        impact['turn'] = -345.0
                        follow['turn'] = -385.0; follow['hand'] = bfh(-385.0, .12, -.12, 1.10)
                        settle['hand'] = bfh(20.0, 0.0, -.30, .80)
                        settle['blade_dir'] = tuple((U_*.45 + V_*.45 + Vector((0, 0, -.75))).normalized())
                    if not HURT.endswith(('_v1', '_v2')):
                        # v3: v2's raised blades stood straight up off the frame top, the back-view trailing Key ran off
                        # the left edge and the settle tip went through the floor: tilt them back / toward the camera.
                        for k_, tn_ in ((spin0, -30.0), (around, -330.0)):
                            k_['blade_dir'] = tuple(bfh(tn_, .30, .75, .55).normalized())
                        trail2 = rb_(-150.0, (-U_*.55 + V_*.80 + Vector((0, 0, .02))).normalized())
                        spin1['blade_dir'] = tuple(bfh(-150.0, *trail2).normalized())
                        spin2['blade_dir'] = tuple(bfh(-240.0, *trail2).normalized())
                        settle['blade_dir'] = tuple((U_*.55 + V_*.55 + Vector((0, 0, -.62))).normalized())
                    for k_ in (spin1, spin2, around):
                        k_['smear'] = 1
                    impact['smear'] = 2
                    follow['smear'] = 1
                    pre = ease(raised, IDLE_R, .5, 0.0)
                    pre.update(ground=True, no_center=True)
                    back_k = ease(settle, IDLE_R, .7, 0.0)
                    back_k.update(ground=True, no_center=True, turn=IDLE_R['turn'] + (settle['turn'] - IDLE_R['turn'])*.3)
                    RUN_KEYS = [pre, raised, windup, spin0, spin1, spin2, around, impact, follow, settle, back_k]
                    if not HURT.endswith(('_v1', '_v2', '_v3')):
                        # v4 (Kvon: instead an ADVANCING DOWNWARD SLASH, stepping forward with the back foot for range;
                        # reference Sol's 6H in Guilty Gear Strive): Key lifts -> overhead -> the back foot steps up to the
                        # front foot -> the front foot strides out into a deep lunge as the Key comes down -> impact
                        # (torso leaning hard forward, both hands driving the blade down-forward in front) -> follow-
                        # through low -> recover -> the back foot steps up into the idle, one step further on. Feet are
                        # planned in world terms (x0/r0 = idle front/back foot) and the body position b each drawing; the
                        # drawing's feet are world - b and its root motion is the change in b, so planted feet stay put.
                        x0, r0 = L0[0], R0[0]
                        Rp = x0 - .08                       # where the back foot plants after stepping up
                        b4 = Rp + .38                       # body over the lunge
                        Lp = b4 + .26                       # front foot of the lunge
                        b_end = Lp - x0                     # idle again with the left foot still planted at Lp
                        # (drawing, body b, L world (s, lift, pitch), R world (s, lift, pitch))
                        plan = [(0.0, (x0, 0, 0), (r0, 0, 0)),
                                (-.02, (x0, 0, 0), (r0, 0, 10.0)),
                                (.10, (x0, 0, 0), ((r0 + x0)/2, .10, 20.0)),
                                (.22, (x0 + .22, .07, 10.0), (Rp, 0, 0)),
                                (b4, (Lp, 0, 0), (Rp, 0, 30.0)),
                                (b4 + .02, (Lp, 0, 0), (Rp, 0, 30.0)),
                                (b4 - .08, (Lp, 0, 0), (Rp, 0, 15.0)),
                                ((b4 + b_end)/2, (Lp, 0, 0), ((Rp + b_end + r0)/2, .08, 15.0)),
                                (b_end, (Lp, 0, 0), (b_end + r0, 0, 0))]
                        bfz = lambda tn_, x_, y_, z_: bfh(tn_, x_, y_, z_)
                        poses = [  # turn, twist, hand, blade, ce, pitch, hunch
                            (15.0, -4.0, bfz(15.0, -.04, -.10, 1.10), U_*.20 + V_*.25 + Vector((0, 0, 1.0)), .07, 0.0, 0.0),
                            (20.0, -6.0, bfz(20.0, -.08, .04, 1.32), -U_*.55 + V_*.35 + Vector((0, 0, .75)), .05, -6.0, -4.0),
                            (15.0, -4.0, bfz(15.0, -.06, .02, 1.30), -U_*.50 + V_*.35 + Vector((0, 0, .80)), .03, -4.0, -2.0),
                            (5.0, 4.0, bfz(5.0, 0.0, -.20, 1.28), U_*.30 + V_*.40 + Vector((0, 0, .85)), .08, 6.0, 4.0),
                            (0.0, 10.0, U_*.40 + V_*.16 + Vector((0, 0, .78)), U_*.55 + V_*.50 + Vector((0, 0, -.62)),
                             .18, 22.0, 12.0),
                            (0.0, 10.0, U_*.34 + V_*.18 + Vector((0, 0, .62)), U_*.40 + V_*.55 + Vector((0, 0, -.72)),
                             .19, 26.0, 14.0),
                            (5.0, 6.0, U_*.26 + V_*.20 + Vector((0, 0, .70)), U_*.60 + V_*.55 + Vector((0, 0, -.40)),
                             .14, 14.0, 8.0)]
                        keys_ = []
                        for j_, (b_, (lx_, ll_, lp_), (rx_, rl_, rp_)) in enumerate(plan[:7]):
                            tn_, tw_, hd_, bl_, ce_, pt_, hn_ = poses[j_]
                            ft_ = {'L': (lx_ - b_, L0[1], ll_, lp_), 'R': (rx_ - b_, R0[1], rl_, rp_)}
                            k_ = hv(tn_, tw_, hd_, bl_, ce=ce_, pitch=pt_, hunch=hn_, feet=ft_)
                            keys_.append(k_)
                        for j_ in (7, 8):  # back foot steps up, then the idle
                            b_, (lx_, ll_, lp_), (rx_, rl_, rp_) = plan[j_]
                            k_ = ease(keys_[6], IDLE_R, .55 if j_ == 7 else .9, 0.0)
                            k_.update(ground=True, no_center=True,
                                      feet={'L': (lx_ - b_, L0[1], ll_, lp_), 'R': (rx_ - b_, R0[1], rl_, rp_)})
                            keys_.append(k_)
                        prev_ = 0.0
                        for k_, (b_, *_) in zip(keys_, plan):
                            k_['root'] = b_ - prev_; prev_ = b_
                        if not HURT.endswith('_v4'):
                            # v5: v4's raised blades left the frame top and the impact/follow-through tips went through the
                            # floor - angle them toward the camera / less steeply; a wider lunge like Sol's.
                            fix_ = {0: (None, U_*.45 + V_*.40 + Vector((0, 0, .60))),
                                    1: (bfz(20.0, -.08, .04, 1.22), -U_*.70 + V_*.50 + Vector((0, 0, .45))),
                                    2: (bfz(15.0, -.06, .02, 1.20), -U_*.65 + V_*.50 + Vector((0, 0, .50))),
                                    3: (bfz(5.0, 0.0, -.20, 1.16), U_*.50 + V_*.55 + Vector((0, 0, .50))),
                                    4: (U_*.40 + V_*.16 + Vector((0, 0, .82)), U_*.62 + V_*.60 + Vector((0, 0, -.36))),
                                    5: (U_*.36 + V_*.18 + Vector((0, 0, .72)), U_*.50 + V_*.65 + Vector((0, 0, -.48))),
                                    6: (None, U_*.62 + V_*.60 + Vector((0, 0, -.25)))}
                            for j_, (hd_, bl_) in fix_.items():
                                if hd_ is not None:
                                    keys_[j_]['hand'] = hd_
                                keys_[j_]['blade_dir'] = tuple(bl_.normalized())
                            for j_ in (4, 5, 6):  # wider lunge: front foot further ahead, back leg further behind
                                f_ = keys_[j_]['feet']
                                keys_[j_]['feet'] = {'L': (f_['L'][0] + .06, *f_['L'][1:]), 'R': (f_['R'][0] - .06, *f_['R'][1:])}
                                keys_[j_]['ce'] = min(keys_[j_]['ce'], .14)
                        if not HURT.endswith(('_v4', '_v5')):
                            keys_[4]['offset_px'] = (-48, 0)  # v6: v5's impact tip touched the right edge (Godot shifts back)
                        if not HURT.endswith(('_v4', '_v5', '_v6')):
                            # v7 (Kvon: extend the Keyblade forward slightly more): hands further toward the opponent, blade
                            # a little less steep; bigger in-frame shift so the tip stays inside.
                            keys_[4]['hand'] = U_*.50 + V_*.14 + Vector((0, 0, .84))
                            keys_[4]['blade_dir'] = tuple((U_*.72 + V_*.55 + Vector((0, 0, -.28))).normalized())
                            keys_[5]['hand'] = U_*.44 + V_*.16 + Vector((0, 0, .74))
                            keys_[5]['blade_dir'] = tuple((U_*.60 + V_*.62 + Vector((0, 0, -.42))).normalized())
                            keys_[4]['offset_px'] = (-96, 0)
                            keys_[5]['offset_px'] = (-40, 0)
                        keys_[3]['smear'] = 2; keys_[4]['smear'] = 2; keys_[5]['smear'] = 1
                        RUN_KEYS = keys_
                        GAME_FRAMES = [2, 4, 3, 4, 3, 5, 6, 5, 5]   # startup 13, active 3, recovery 21 (Ekko's heavy)
                        DURATIONS_MS = [round(f_*1000/60, 3) for f_ in GAME_FRAMES]
                        n = len(DURATIONS_MS)
                elif jpart == 'atk_smed':
                    # Standing Medium (Kvon, October 27; Gemini round 44 + his notes): a horizontal two-handed slash. Out of
                    # the idle the Key rises over his right shoulder (two in-betweens), winds back level behind him with the
                    # torso turned well away, then he throws his weight into it: hips and shoulders turn through square
                    # to past square, front knee bends, back heel lifts, the Key sweeps level in front of him to full
                    # extension, follows through up over his other shoulder, comes down and settles into the idle.
                    # 'turn' = body facing (+50 = side-on toward the opponent), 'twist' = shoulders past the hips
                    # (+ = right shoulder forward). release 0 = both hands on the handle.
                    def slash(turn, twist, hand, blade, ce=.06, pitch=0.0, hunch=0.0, neck=-6.0, feet=None):
                        k_ = hurt(feet or stand, ce, hunch, pitch, neck, hand, Vector(blade).normalized(),
                                  hand, ground=True)
                        k_.update(no_center=True, look=8.0, turn=turn, twist=twist, release=0.0)
                        return k_
                    heel = {'L': (L0[0] + .04, L0[1], 0.0, 0.0), 'R': (R0[0] + .03, R0[1], 0.0, 25.0)}
                    raised = slash(5.0, -6.0, U_*-.06 + V_*.14 + Vector((0, 0, 1.28)),
                                   -U_*.45 + V_*.25 + Vector((0, 0, .85)), ce=.04)
                    windup = slash(95.0, -18.0, U_*-.28 + V_*.18 + Vector((0, 0, .95)),
                                   -U_*.75 + V_*.60 + Vector((0, 0, .06)), ce=.10, hunch=4.0)
                    begin = slash(55.0, -4.0, U_*.04 + V_*.26 + Vector((0, 0, .95)),
                                  U_*.10 + V_*.98 + Vector((0, 0, .04)), ce=.10, pitch=4.0, feet=heel)
                    impact = slash(15.0, 14.0, U_*.34 + V_*.12 + Vector((0, 0, .95)),
                                   U_*.80 + V_*.58 + Vector((0, 0, .04)), ce=.12, pitch=10.0, feet=heel)
                    follow = slash(-25.0, 18.0, U_*.12 + V_*-.08 + Vector((0, 0, 1.18)),
                                   -U_*.45 - V_*.30 + Vector((0, 0, .85)), ce=.10, pitch=6.0, feet=heel)
                    recover = slash(-15.0, 6.0, U_*.10 + V_*.18 + Vector((0, 0, .80)),
                                    U_*.80 + V_*.30 + Vector((0, 0, -.20)), ce=.08)
                    if not HURT.endswith('_v1'):
                        # v2: v1's raised and follow-through Keys stood straight up off the frame top, the wind-up showed
                        # his whole back with the Key off the left edge, the slash start hid the blade end-on and the
                        # impact ran off the right edge: tilt the over-shoulder blades back, ease the wind-up turn, and
                        # angle the slash/impact blades a little toward the camera so they fit.
                        raised = slash(10.0, -8.0, U_*-.08 + V_*.14 + Vector((0, 0, 1.20)),
                                       -U_*.80 + V_*.25 + Vector((0, 0, .50)), ce=.04)
                        windup = slash(75.0, -16.0, U_*-.24 + V_*.20 + Vector((0, 0, .95)),
                                       -U_*.55 + V_*.80 + Vector((0, 0, .06)), ce=.10, hunch=4.0)
                        begin = slash(45.0, -2.0, U_*.06 + V_*.26 + Vector((0, 0, .95)),
                                      U_*.40 + V_*.90 + Vector((0, 0, .04)), ce=.10, pitch=4.0, feet=heel)
                        impact = slash(15.0, 14.0, U_*.28 + V_*.14 + Vector((0, 0, .95)),
                                       U_*.62 + V_*.76 + Vector((0, 0, .04)), ce=.12, pitch=10.0, feet=heel)
                        follow = slash(-25.0, 18.0, U_*.10 + V_*-.06 + Vector((0, 0, 1.08)),
                                       -U_*.70 - V_*.25 + Vector((0, 0, .55)), ce=.10, pitch=6.0, feet=heel)
                    if not HURT.endswith(('_v1', '_v2')):
                        # v3 (Kvon: match Gemini's raised poses): both hands up by his REAR shoulder beside his head, the
                        # blade angled up and FORWARD over his head like a batter's stance (v2 pointed it up and back).
                        raised = slash(25.0, -10.0, U_*-.20 + V_*.10 + Vector((0, 0, 1.28)),
                                       U_*.45 + V_*.15 + Vector((0, 0, .88)), ce=.05)
                        for k_ in (begin, impact, follow):
                            k_['smear'] = True  # the fast part of the swing gets a smear (make_smears.py)
                    if not HURT.endswith(('_v1', '_v2', '_v3')):
                        # v4 (Kvon's reference: Ekko's standing heavy in 2XKO): a deep lunge on the impact - front foot
                        # far forward with the knee bent, back leg stretched behind with the heel up, a hard lean into
                        # the swing, both arms extended with the Key level and slightly up; raised poses lowered (v3's
                        # tip left the frame top). Impact smear spans windup -> begin -> impact (smear = drawings back).
                        lunge = {'L': (L0[0] + .22, L0[1], 0.0, 0.0), 'R': (R0[0] - .14, R0[1], 0.0, 35.0)}
                        mid_l = {'L': (L0[0] + .12, L0[1], 0.0, 0.0), 'R': (R0[0] - .06, R0[1], 0.0, 20.0)}
                        raised = slash(25.0, -10.0, U_*-.20 + V_*.10 + Vector((0, 0, 1.12)),
                                       U_*.62 + V_*.18 + Vector((0, 0, .70)), ce=.05)
                        begin = slash(45.0, -2.0, U_*.08 + V_*.26 + Vector((0, 0, .95)),
                                      U_*.40 + V_*.90 + Vector((0, 0, .04)), ce=.12, pitch=8.0, feet=mid_l)
                        impact = slash(10.0, 18.0, U_*.36 + V_*.12 + Vector((0, 0, 1.00)),
                                       U_*.60 + V_*.72 + Vector((0, 0, .22)), ce=.17, pitch=18.0, hunch=6.0, feet=lunge)
                        follow = slash(-25.0, 18.0, U_*.14 + V_*-.06 + Vector((0, 0, 1.08)),
                                       -U_*.70 - V_*.25 + Vector((0, 0, .55)), ce=.14, pitch=10.0, feet=lunge)
                        begin['smear'], impact['smear'], follow['smear'] = 1, 2, 1
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4')):
                        # v5: the swing rises into the hit - the wind-up blade starts a little low behind him.
                        windup = slash(75.0, -16.0, U_*-.24 + V_*.20 + Vector((0, 0, .90)),
                                       -U_*.55 + V_*.80 + Vector((0, 0, -.22)), ce=.10, hunch=4.0)
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5')):
                        # v6 (Kvon: where is the arm not holding the Keyblade?): v5's hands sat out toward his right
                        # (camera) side, so once he turned the left hand could not reach the handle (up to .28 m short)
                        # and that arm hid behind him. Hands are now placed in his own body frame where both arms reach:
                        # (x = his left, y = behind, z = up) - rear shoulder, rear hip, chest, arm's length, other shoulder.
                        bf = lambda turn_, x_, y_, z_: Matrix.Rotation(math.radians(turn_), 3, 'Z') @ Vector((x_, y_, z_))
                        for k_, (x_, y_, z_) in ((raised, (-.14, -.06, 1.18)), (windup, (-.18, .02, .95)),
                                                 (begin, (-.04, -.30, .96)), (impact, (0.0, -.42, 1.00)),
                                                 (follow, (.12, -.12, 1.10)), (recover, (0.0, -.28, .82))):
                            k_['hand'] = bf(k_['turn'], x_, y_, z_)
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6')):
                        # v7: the left hand was on the handle all along (beside the right one) but the arm stayed on the
                        # far side, hidden behind his torso and right arm. Point the left elbow down and toward the
                        # camera so that arm comes round the near side and its forearm shows reaching to the handle.
                        for k_ in (raised, windup, begin, impact, follow, recover):
                            k_['l_elbow_hint'] = tuple(V_*.75 + U_*.10 + Vector((0, 0, -.65)))
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7')):
                        # v8: v7's raised tip left the frame top - hands a little lower, blade tilted further forward.
                        raised['hand'] = bf(raised['turn'], -.14, -.06, 1.06)
                        raised['blade_dir'] = tuple((U_*.75 + V_*.18 + Vector((0, 0, .55))).normalized())
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7', '_v8')):
                        recover['blade_dir'] = tuple((U_*.62 + V_*.62 + Vector((0, 0, -.20))).normalized())  # v9: v8's tip touched the right edge
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7', '_v8', '_v9')):
                        # v10 (Kvon: on the slash start and impact the arms were completely behind his body): his chest
                        # faced away from the camera there, so the arms reached forward on the far side. Turn the chest
                        # toward the camera through the swing (like Ekko's frame and his idle) so the arms are in front
                        # of the body; the feet keep the lunge, so hips and shoulders twist into it.
                        for k_, (tn_, tw_, (x_, y_, z_)) in ((begin, (20.0, 0.0, (-.04, -.32, .96))),
                                                             (impact, (-20.0, 10.0, (0.0, -.42, 1.00))),
                                                             (follow, (-40.0, 12.0, (.12, -.14, 1.10))),
                                                             (recover, (-20.0, 4.0, (0.0, -.28, .82)))):
                            k_.update(turn=tn_, twist=tw_, hand=bf(tn_, x_, y_, z_))
                    if not HURT.endswith(('_v1', '_v2', '_v3', '_v4', '_v5', '_v6', '_v7', '_v8', '_v9', '_v10')):
                        # v11: v10's hands bunched at his chest with the guard over his face - reach out toward the
                        # opponent (screen right) at chest-to-waist height so the arms extend, like Ekko's.
                        begin['hand'] = U_*.14 + V_*.22 + Vector((0, 0, .90))
                        impact['hand'] = U_*.44 + V_*.12 + Vector((0, 0, .86))
                        if not HURT.endswith('_v11'):
                            impact['blade_dir'] = tuple((U_*.50 + V_*.80 + Vector((0, 0, .22))).normalized())  # v12: v11 tip touched the edge
                    wrap = None
                    if not HURT.endswith(tuple(f'_v{n_}' for n_ in range(1, 13))):
                        # v13 (Kvon: the body follows the Keyblade like someone swinging a bat): a kinetic chain - the
                        # hips lead into the swing while the shoulders lag, the shoulders and arms whip through to the
                        # impact, then the body keeps turning with the Key: a new "wrap" drawing (Key sweeping on round
                        # in front of him), and the follow-through with hips and chest fully round, the back foot
                        # pivoting onto its toe with the knee turned in, the front leg straighter and the arms wrapped
                        # up over his front shoulder.
                        pivot = {'L': (L0[0] + .22, L0[1], 0.0, 0.0), 'R': (R0[0] - .06, R0[1], .02, 50.0)}
                        begin.update(turn=40.0, twist=-22.0, hand=bf(40.0, -.10, -.18, .92))
                        impact.update(turn=-15.0, twist=8.0)
                        wrap = slash(-45.0, 16.0, bf(-45.0, .06, -.40, .98), -U_*.30 + V_*.92 + Vector((0, 0, .12)),
                                     ce=.13, pitch=12.0, feet=lunge)
                        wrap['knee_in'] = {'R': .4}
                        follow.update(turn=-70.0, twist=20.0, ce=.07, pitch=4.0, feet=pivot,
                                      hand=bf(-70.0, .14, -.10, 1.12), knee_in={'R': .8})
                        recover.update(turn=-35.0, twist=6.0, feet=pivot, knee_in={'R': .5},
                                       hand=bf(-35.0, 0.0, -.28, .82))
                        wrap['smear'] = 1
                        follow['smear'] = 1
                    if wrap and not HURT.endswith('_v13'):
                        # v14 (Kvon: legs in to almost meet under his torso; the Key fully extended for max range): feet a
                        # hand's width apart under him from the wind-up on (raised halfway), less knee bend; on the impact
                        # the arms straighten at shoulder height and the blade points straight at the opponent. Drawings
                        # whose reach passes the frame edge are shifted left inside the frame (offset_px; Godot shifts
                        # the sprite back by the same amount).
                        close = lambda l_, r_, rl_=0.0, rp_=0.0: {'L': (l_, L0[1], 0.0, 0.0), 'R': (r_, R0[1], rl_, rp_)}
                        raised['feet'] = close(L0[0]*.6, R0[0]*.6)
                        windup.update(feet=close(.16, -.12), ce=.07)
                        begin.update(feet=close(.14, -.10, 0.0, 20.0), ce=.08)
                        impact.update(feet=close(.12, -.08, .02, 35.0), ce=.08, pitch=14.0,
                                      hand=U_*.52 + V_*.10 + Vector((0, 0, 1.02)),
                                      blade_dir=tuple((U_*.95 + V_*.22 + Vector((0, 0, .10))).normalized()),
                                      offset_px=(-120, 0))
                        wrap.update(feet=close(.12, -.08, .02, 35.0), ce=.08, offset_px=(-40, 0))
                        follow.update(feet=close(.12, -.06, .02, 50.0), ce=.05)
                        recover.update(feet=close(.14, -.10, .02, 30.0), ce=.06)
                        if not HURT.endswith('_v14'):
                            # v15: with the feet that close, v14's knee bend bowed the knees apart into a squat - straighter
                            # legs through the swing.
                            for k_, ce_ in ((windup, .04), (begin, .04), (impact, .03), (wrap, .03), (follow, .02),
                                            (recover, .03)):
                                k_['ce'] = ce_
                    ins = []
                    for w_ in (.66, .33):  # idle -> raised in-betweens (w_ = share of the idle left)
                        k_ = ease(raised, IDLE_R, w_, 0.0)
                        k_.update(ground=True, no_center=True)
                        ins.append(k_)
                    back_k = ease(recover, IDLE_R, .7, 0.0)
                    back_k.update(ground=True, no_center=True)
                    RUN_KEYS = ins + [raised, windup, begin, impact] + ([wrap] if wrap else []) + [follow, recover, back_k]
                    if wrap:
                        GAME_FRAMES = [2, 2, 3, 3, 2, 3, 2, 3, 4, 4]
                        DURATIONS_MS = [round(f_*1000/60, 3) for f_ in GAME_FRAMES]
                        n = len(DURATIONS_MS)
                elif jpart == 'hurt_getup':
                    # Get-up (Kvon: build it from other fighting games' get-ups - the common neutral stand-up, e.g.
                    # Smash's floor getup / Street Fighter's quick rise): from lying face up, sit up leaning back with
                    # the left hand pushing on the floor behind him, tuck the knees, rise over the feet into a crouch,
                    # come up, settle into the idle. Hips lowered toward the floor by 'ce', grounded, not centred (the
                    # standing drawings must line up with the idle's feet).
                    sit_blade = (U_*.90 + V_*.35 + Vector((0, 0, -.12))).normalized()
                    sit_k = hurt({'L': (.60, LAT['L'], 0.0, 0.0), 'R': (.55, LAT['R'], 0.0, 0.0)}, .36, 0.0, 0.0, -6.0,
                                 B_(-.30, .10, .18), sit_blade, B_(.22, .30, .14), spin=30.0, ground=True)
                    sit_k.update(lean_cam=50.0, head_cam=-22.0, leg_reach=.95)
                    tuck_k = hurt({'L': (.30, LAT['L'], 0.0, 0.0), 'R': (.22, LAT['R'], 0.0, 0.0)}, .34, 10.0, 4.0, -10.0,
                                  B_(-.32, -.05, .30), (U_*.70 + V_*.45 + Vector((0, 0, -.25))).normalized(),
                                  B_(.25, .25, .16), spin=20.0, ground=True)
                    tuck_k.update(lean_cam=20.0, head_cam=-10.0)
                    crouch_k = hurt({'L': (.12, LAT['L'], 0.0, 0.0), 'R': (-.06, LAT['R'], 0.0, 0.0)}, .25, 18.0, 14.0,
                                    -24.0, U_*-.25 + V_*.25 + Vector((0, 0, .45)), back_low, B_(.30, -.28, .12),
                                    spin=10.0, ground=True)
                    rise_k = hurt({'L': (.30, LAT['L'], 0.0, 0.0), 'R': (-.26, LAT['R'], 0.0, 0.0)}, .12, 8.0, 6.0, -10.0,
                                  U_*-.20 + V_*.24 + Vector((0, 0, .62)),
                                  tuple(Vector(back_low).lerp(CR_BLADE0, .5).normalized()), B_(.20, -.25, .80),
                                  ground=True)
                    rise_k['release'] = .5
                    if not HURT.endswith('_v1'):
                        # v2: v1's blade tips went through the floor on drawings 1-3: lay them level along the floor
                        # (toward his feet), then held out low behind him, angled toward the camera.
                        sit_k['blade_dir'] = tuple((U_*.90 + V_*.40 + Vector((0, 0, .04))).normalized())
                        tuck_k['blade_dir'] = tuple((U_*.75 + V_*.60 + Vector((0, 0, .02))).normalized())
                        crouch_k['blade_dir'] = tuple((-U_*.55 + V_*.80 + Vector((0, 0, -.05))).normalized())
                    RUN_KEYS = [sit_k, tuck_k, crouch_k, rise_k, ease(rise_k, IDLE_R, .7, .15)]
                    for k_ in RUN_KEYS:
                        k_.update(ground=True, no_center=True)
                else:
                    # Shoulders hit the floor and the legs come down (a small bounce), settle, then lie flat on his back,
                    # face up, head toward screen left, seen side-on, Key lying loosely along his right side.
                    lie_blade = (V_*.30 + Vector((0, 0, -1.0))).normalized()
                    straight = {'L': (.02, LAT['L'], 0.0, 0.0), 'R': (-.02, LAT['R'], 0.0, 0.0)}
                    RUN_KEYS = [hurt({'L': (.16, LAT['L'], .26, 20.0), 'R': (.05, LAT['R'], .16, 20.0)}, -.02, 6.0, 0.0,
                                     -6.0, U_*-.14 + V_*.28 + Vector((0, 0, 1.05)), lie_blade, B_(.28, -.05, 1.05),
                                     roll=115.0, spin=60.0, ground=True, lift=.06),
                                hurt({'L': (.06, LAT['L'], .08, 10.0), 'R': (-.01, LAT['R'], .05, 10.0)}, -.05, 2.0, 0.0,
                                     -8.0, U_*-.10 + V_*.30 + Vector((0, 0, .80)), lie_blade, B_(.26, .02, .80),
                                     roll=96.0, spin=60.0, ground=True, lift=.02),
                                hurt(straight, -.06, 0.0, 0.0, -8.0, U_*-.10 + V_*.30 + Vector((0, 0, .70)), lie_blade,
                                     B_(.25, .05, .75), roll=90.0, spin=60.0, ground=True)]
                    if H_V2:
                        # v1 lay tilted (legs raised) with the Key across his chest: set the hips->neck line to an exact
                        # screen angle (180 = flat, head toward screen left), hand down by his hip.
                        for k_, ang_ in zip(RUN_KEYS, (195.0, 183.0, 179.0) if HURT.endswith('_v2') else (205.0, 184.0, 180.0)):
                            k_['body_angle'] = ang_
                        for k_ in RUN_KEYS[1:]:
                            k_['hand'] = U_*-.06 + V_*.32 + Vector((0, 0, .60))
                            if not HURT.endswith(('_v2', '_v3', '_v4')):
                                # v5+ (Gemini round 38 #4): chest and face turned more toward the camera so face-up reads
                                # (v4 was exact profile), right hand resting on the floor beside his hip, out to his side
                                # and level with his back, Key along the floor toward his feet.
                                k_['spin_deg'] = 30.0
                                k_['hand'] = B_(-.36, .10, .66)  # body frame; the spin turns it with him
                                k_['blade_dir'] = tuple(T_((-.25, .15, -1.0)).normalized())
                                if not HURT.endswith('_v5'):
                                    # v6: v5's blade tipped toward his back, i.e. down through the floor once he lay down;
                                    # hand level with his back and the blade tilted a little toward his front (up).
                                    k_['hand'] = B_(-.36, .02, .66)
                                    k_['blade_dir'] = tuple(T_((-.25, -.12, -1.0)).normalized())
                                continue
                            if not HURT.endswith(('_v2', '_v3')):
                                # v4: v3's Key pointed down AND forward, so it rose off the floor once he lay down;
                                # down and slightly back (after the spin), so it lies along his side on the floor.
                                k_['blade_dir'] = tuple(Matrix.Rotation(math.radians(-k_['spin_deg']), 3, 'Z')
                                                        @ (-U_*.15 + V_*.30 + Vector((0, 0, -1.0))).normalized())
            elif jpart == 'jump_fall':
                # Falling (ref_03): legs open and reach down for the floor; the Keyblade is raised high (Kvon's rule).
                hi = U_*-.04 + V_*.18 + Vector((0, 0, 1.50))
                if J_V2:
                    hi = U_*-.10 + V_*.20 + Vector((0, 0, 1.32))
                if not JUMP.endswith(('_v1', '_v2')):
                    hi = U_*-.06 + V_*.24 + Vector((0, 0, 1.26))
                RUN_KEYS = [jk({'L': (.10, LAT['L'], .18, 20.0), 'R': (-.14, LAT['R'], .12, 35.0)}, pitch=-6.0, neck=-2.0,
                               hand=hi, blade=up_high),
                            jk({'L': (.14, LAT['L'], .10, 15.0), 'R': (-.18, LAT['R'], .06, 30.0)}, pitch=-6.0, neck=-2.0,
                               hand=hi, blade=up_high)]
                if not JUMP.endswith(('_v1', '_v2', '_v3')):
                    # v4 (Kvon chose to smooth apex -> falling 1): one in-between drawing first, halfway between the
                    # approved apex (Key beside his leg, turned toward the player, -30 twist) and falling 1 (Key raised).
                    apex_hand = U_*-.24 + V_*.23 + Vector((0, 0, .80))
                    apex_blade = (Vector(toward_cam(back_low, 75.0)) + Vector((0, 0, -.3))).normalized()
                    f1 = RUN_KEYS[0]
                    mid_ = jk({'L': (.13, LAT['L'], .24, 28.0), 'R': (-.09, LAT['R'], .11, 40.0)}, ce=-.06, hunch=2.0,
                              pitch=-2.0, neck=-4.0, hand=apex_hand.lerp(f1['hand'], .5),
                              blade=(apex_blade + Vector(f1['blade_dir'])).normalized())
                    mid_['hz'] = -.085; mid_['blade_twist'] = -15.0
                    RUN_KEYS = [mid_] + RUN_KEYS
                import re as re_k
                m_k = re_k.search(r'_k(\d+)$', OUT_NAME)
                if m_k:
                    # Falling-1 Keyblade position options (Kvon's review sheet): (hand in U/V/up, blade direction).
                    Z_ = Vector((0, 0, 1))
                    KOPT = {
                        1: (hi, Vector(up_high)),                                              # current
                        2: (U_*-.02 + V_*.20 + Z_*1.30, (Z_ + V_*.25).normalized()),           # straight up overhead
                        3: (U_*-.10 + V_*.22 + Z_*1.22, (-U_ + Z_*.15 + V_*.3).normalized()),  # high, blade straight back
                        4: (U_*.10 + V_*.26 + Z_*1.24, (U_*.5 + Z_ + V_*.3).normalized()),     # high in front, tip up-forward
                        5: (U_*-.12 + V_*.24 + Z_*1.08, (-U_*.7 + Z_*.6 + V_*.4).normalized()),# shoulder height, back and up
                        6: (U_*-.04 + V_*.20 + Z_*1.30, (U_*.8 + Z_*.25 + V_*.3).normalized()),# overhead, tip pointing forward
                        7: (U_*-.18 + V_*.24 + Z_*1.18, (-U_*.5 + V_*.4 - Z_*.75).normalized()),# behind the head, tip down the back
                        8: (U_*-.20 + V_*.28 + Z_*1.34, (-U_*.6 + Z_*.75 + V_*.3).normalized()),# arm up and back, diagonal
                        9: (U_*-.16 + V_*.22 + Z_*.80, Vector(back_low)),                       # low behind (as rising)
                        # Kvon: option 1's hand, the blade rotated so it lies above his head (pointing forward/up).
                        10: (hi, (U_*.65 + Z_*.40 + V_*.45).normalized()),
                        11: (hi, (U_*.45 + Z_*.65 + V_*.45).normalized()),
                        12: (hi, (U_*.75 + Z_*.20 + V_*.55).normalized()),
                        # 13-15: same blades, hand raised ~10 cm and a touch back so the guard clears his face.
                        13: (hi + Z_*.10 - U_*.04, (U_*.75 + Z_*.20 + V_*.55).normalized()),
                        14: (hi + Z_*.10 - U_*.04, (U_*.65 + Z_*.40 + V_*.45).normalized()),
                        15: (hi + Z_*.10 - U_*.04, (U_*.45 + Z_*.65 + V_*.55).normalized()),
                    }
                    h_k, b_k = KOPT[int(m_k.group(1))]
                    RUN_KEYS[0]['hand'] = h_k; RUN_KEYS[0]['blade_dir'] = tuple(b_k)
            else:
                # Landing (sheet pose 4): feet down wide, hips sink to absorb it, both hands back on the Key, rise.
                land = mix(IDLE_R, IDLE_R, 0.0); land.update(ce=.10, hunch=4.0, pitch=4.0, root=0.0)
                land['feet'] = {'L': (L0[0]*1.05, L0[1], 0.0, 0.0), 'R': (R0[0]*1.05, R0[1], 0.0, 0.0)}
                mid = mix(land, IDLE_R, .5); mid['root'] = 0.0
                end_ = mix(land, IDLE_R, .85); end_['root'] = 0.0
                RUN_KEYS = [land, mid, end_]
                if not JUMP.endswith(('_v1', '_v2')):
                    # v3 (Kvon: the Key-holding elbow bent too far inward on landing): the right elbow points out to his
                    # right side and a little down, as in the idle, instead of folding in across his stomach.
                    out_ = Matrix.Rotation(math.radians(IDLE_R['turn']), 3, 'Z') @ Vector((-1, .15, 0))
                    hint_ = tuple((out_.normalized() + Vector((0, 0, -.35))).normalized())
                    if not JUMP.endswith(('_v1', '_v2', '_v3')):
                        # v4: the hint barely moved the elbow. The real cause: the landing crouch sank and tipped the grip
                        # across his body. Keep the chest upright and the grip at the idle spot (only 3 cm lower), so the
                        # Keyblade arm keeps the idle's shape while the legs absorb the landing.
                        hint_ = None
                        for k_ in RUN_KEYS:
                            k_['hz'] = k_['ce'] - .03*(k_['ce'] / .10)
                            k_['hunch'], k_['pitch'] = 0.0, 0.0
                    J_VAR = OUT_NAME.rsplit('_', 1)[-1] if OUT_NAME.startswith('jump_land_v3_') else ''
                    if J_VAR == 'down':
                        hint_ = tuple((out_.normalized()*.4 + Vector((0, 0, -1))).normalized())
                    elif J_VAR == 'cam':
                        hint_ = tuple((out_.normalized() + to_cam*.8).normalized())
                    elif J_VAR == 'back':
                        hint_ = tuple((out_.normalized() - to_cam*.8).normalized())
                    for k_ in RUN_KEYS:
                        k_['r_elbow_hint'] = hint_
            if OUT_NAME.endswith('_idlecheck'):
                # Diagnostic: the battle idle rebuilt through the run machinery, to compare with the real idle frame.
                RUN_KEYS = [mix(IDLE_R, IDLE_R, 0.0)]
                RUN_KEYS[0]['root'] = 0.0
            for k_ in RUN_KEYS:
                k_.setdefault('root', 0.0)
        elif GLIDE and part == 'run_loop':
            RUN_KEYS = [loop_key(j) for j in range(6)]
        elif GLIDE and part == 'run_start':
            # Push-off (round 18, poses 1-2): dip, the back (right) foot pushes off on its toe while the front
            # knee comes up, then he tips forward into the glide. Root ramps up to glide speed.
            end = loop_key(0)
            roots = [.02, .06, .12, .16]
            if G_V10:
                roots = [.02, .08, .10, .16]
            body_s = 0.0
            for j, w in enumerate([.2, .45, .75, 1.0]):
                k_ = mix(IDLE_R, end, w)
                body_s += roots[j]
                if j < 2:
                    k_['feet']['R'] = (IDLE_R['feet']['R'][0] - body_s, k_['feet']['R'][1], 0.0, [10.0, 35.0][j])
                if j == 1:
                    k_['feet']['L'] = (k_['feet']['L'][0] + .08, k_['feet']['L'][1], .16, 0.0)
                k_['ce'] += [.06, .03, 0, 0][j]
                k_['release'] = min(1.0, max(0.0, (w - .1)/.4))
                k_['root'] = roots[j]
                if G_V10 and j in (1, 2):
                    # v10+ (P1/P2): a deep forward lunge like Gemini's pose 2 - front knee bent over the planted front
                    # foot, the back leg stretched far behind pushing off the floor on its toe - with the Keyblade
                    # raised up BEHIND the shoulder; it swings down to the glide's forward-down carry on drawing 4.
                    r_back = -.45 - (roots[2] if j == 2 else 0.0)  # the back foot stays planted while he moves
                    k_['feet'] = {'L': (.26 - (roots[2] if j == 2 else 0.0), LAT['L'], 0.0, 0.0),
                                  'R': (r_back, LAT['R'], 0.0, 35.0)}
                    k_.update(turn=8.0 + 8.0*j, ce=.30 - POSE['drop'], hunch=12.0 + 2*j, pitch=16.0 + 3*j, neck=-34.0,
                              look=0.0, release=1.0, arm=1.0)
                    k_['hand'] = U_*-.16 + V_*.18 + Vector((0, 0, 1.12 - .02*j))
                    k_['blade_dir'] = (-U_*.72 + V_*.38 + Vector((0, 0, .58))).normalized()
                if GLIDE.endswith('_v34') and OUT_NAME.endswith(('_v34b', '_v34c', '_v34d')) and j in (1, 2):
                    # v34b (Kvon: the transition flashed the Keyblade up in the air behind him): no raised Key on the
                    # lunge drawings - the hand and blade ease straight from the idle grip toward the glide's carry.
                    k_['hand'] = IDLE_R['hand'].lerp(end['hand'], w)
                    k_['blade_ease'] = w  # blade direction filled in once the loop's Key direction is measured
                if GLIDE.endswith('_v34') and j == 3:
                    # v34 (approved pose): the last push-off drawing hands over to the loop with the loop's own arm
                    # setup (straight Keyblade wrist, forward left elbow, lowered shoulder), not v10's blend.
                    for key_ in ('wrist_roll', 'blade_dir', 'l_elbow_hint', 'l_shrug'):
                        k_[key_] = end.get(key_)
                if G_V7 and not G_V10 and j == 3:
                    # v7+: launch stretch - the push-off foot stays planted far back and the torso drives forward,
                    # a straight line from heel to head, before he settles into the relaxed hover.
                    k_['feet']['R'] = (-.45, k_['feet']['R'][1], 0.0, 30.0)
                    k_['hunch'] += 4.0
                    k_['pitch'] += 6.0
                RUN_KEYS.append(k_)
        elif GLIDE:
            # Skid landing (round 18, poses 6-7): the feet touch down wide and low, he skids (feet slide with
            # him) and takes the Key in both hands again, then rises into the battle idle.
            last = loop_key(5)
            plant = dict(last, turn=20.0, ce=.30 - POSE['drop'], hunch=0.0, pitch=-6.0, neck=-8.0, look=6.0,
                         toe=20.0, hz=0.0, root=G_SPEED)
            plant['feet'] = {'L': (.40, LAT['L'], 0.0, 0.0), 'R': (-.42, LAT['R'], 0.0, 15.0)}
            if G_V10:
                # v10+ (S1/S2): wide low stance with the torso nearly upright (no lean-back), both hands on the
                # Keyblade from drawing 1, low in front, blade forward-down; he skids, then rises into the idle.
                land_dir = (U_*.82 + V_*.45 + Vector((0, 0, -.36))).normalized()
                plant.update(turn=0.0, ce=.30 - POSE['drop'], hunch=-6.0, pitch=-8.0, neck=-6.0, look=10.0,
                             release=0.0, blade_dir=land_dir, hand=IDLE_R['hand'] + U_*.04,
                             wrist_roll=None, l_elbow_hint=(1, .4, -.3), l_shrug=0.0)  # both hands regrip the Key
            elif G_V7:
                # v7+: a braced skid - the torso leans back against the momentum (hara + mune about -18 deg
                # total) and the hips sink to 0.16 m, on drawings 1 and 2.
                plant.update(turn=G_TURN, ce=.16 - POSE['drop'], hunch=-14.0, pitch=-32.0)
            RUN_KEYS.append(plant)
            for j, (w, root) in enumerate(zip([.25, .5, .8, .97], [.10, .05, .02, 0.0])):
                k_ = mix(plant, IDLE_R, w)
                if G_V10:
                    k_['release'] = 0.0
                    k_['blade_dir'] = land_dir.lerp(CR_BLADE0, w).normalized() if j else land_dir
                    if j == 0:
                        k_.update(hunch=plant['hunch'], pitch=plant['pitch'], ce=plant['ce'], turn=plant['turn'],
                                  hand=plant['hand'].copy())
                        k_['feet'] = {sd: tuple(f_) for sd, f_ in plant['feet'].items()}  # still skidding wide
                    k_['root'] = root
                    RUN_KEYS.append(k_)
                    continue
                if G_V7 and j == 0:
                    k_.update(hunch=plant['hunch'], pitch=plant['pitch'], ce=plant['ce'])  # still braced
                k_['release'] = 1 - min(1.0, max(0.0, (w - .1)/.35))
                k_['root'] = root
                RUN_KEYS.append(k_)
        elif part == 'run_loop':
            RUN_KEYS = [loop_key(j) for j in range(8)]
            ce_ = [k_['ce'] for k_ in RUN_KEYS]
            for j, k_ in enumerate(RUN_KEYS):
                k_['hz'] = .6*(ce_[j] - ce_[j - 1]) + HZ_J[j % 4]  # the Key lags the body's bounce
        elif part == 'run_start' and not RUN.endswith('_v1'):
            # v2+ (Gemini round 07): the left foot (the idle's front foot) stays planted while the body turns,
            # dips and accelerates; the right foot lifts and drives up. Drawing 4 is the loop's passing pose
            # (loop drawing 3), so the game continues with loop drawing 4. Root motion ramps up toward run speed.
            end = loop_key(2)
            roots = [.03, .07, .12]
            if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 18))):
                roots = [.06, .11, .15]  # v18+: v17's passing pose sits further back; spread the distance
            roots.append(IDLE_R['feet']['L'][0] - end['feet']['L'][0] - sum(roots))
            body_s = 0.0
            for j, w in enumerate([.25, .5, .75, 1.0]):
                k_ = mix(IDLE_R, end, w)
                body_s += roots[j]
                k_['feet']['L'] = (IDLE_R['feet']['L'][0] - body_s, k_['feet']['L'][1], 0.0, end['feet']['L'][3]*w)
                k_['feet']['R'] = (k_['feet']['R'][0], k_['feet']['R'][1], end['feet']['R'][2]*w**1.3, 0.0)
                k_['ce'] += [.05, .03, .01, 0][j]  # anticipation dip
                k_['release'] = min(1.0, max(0.0, (w - .1)/.5))
                k_['root'] = roots[j]
                if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 9))):
                    # v9+: v8's drawing 3 pointed the blade straight back past the frame edge mid-swing;
                    # the blade reaches its carry angle (turned toward the camera) sooner.
                    k_['blade_s'] = min(1.0, w*1.25)
                RUN_KEYS.append(k_)
        elif part == 'run_start':
            # Idle -> loop contact. The left foot stays planted (it is the idle's front foot); the right foot
            # steps up behind to the loop's toe-off spot. Feet sit .15 m further ahead because the first loop
            # drawing moves the body .15 m as it starts.
            end = loop_key(0)
            end['feet'] = {sd: (f_[0] + .15, *f_[1:]) for sd, f_ in end['feet'].items()}
            roots = [0.0, 0.0, .02, IDLE_R['feet']['L'][0] - end['feet']['L'][0] - .02]
            body_s = 0.0
            for j, w in enumerate([.25, .5, .75, 1.0]):
                k_ = mix(IDLE_R, end, w)
                body_s += roots[j]
                k_['feet']['L'] = (IDLE_R['feet']['L'][0] - body_s, *k_['feet']['L'][1:])
                k_['feet']['R'] = (k_['feet']['R'][0], k_['feet']['R'][1],
                                   .05*math.sin(math.pi*w) if w < 1 else 0.0, k_['feet']['R'][3])
                k_['ce'] += [.06, .05, .02, 0][j]  # anticipation dip
                k_['release'] = min(1.0, max(0.0, (w - .1)/.5))
                k_['root'] = roots[j]
                RUN_KEYS.append(k_)
        elif not RUN.endswith('_v1'):
            # v2+ (Gemini round 07): after loop drawing 8 (right foot planted, left foot reaching) the left foot
            # plants wide, the hips sink and the torso leans back; root motion [.15, .08, .04, .01, 0]. Sora's
            # idle stance is wider than Gemini assumed, so the left foot skids forward a little while braking and
            # ends exactly on the idle's front-foot spot; the right foot stays planted, then steps back into place.
            last = loop_key(7)
            roots = [.15, .08, .04, .01, 0.0]
            brake_drop = .26 if RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 10))) else .20  # v10+: Gemini round 13
            plant = dict(last, turn=15.0, ce=brake_drop - POSE['drop'], hunch=-8.0, pitch=-16.0, neck=-2.0, look=8.0,
                         toe=20.0, twist=0.0, arm=-.5, hz=.04, root=roots[0])
            l_end = IDLE_R['feet']['L'][0]
            r_plant = last['feet']['R'][0] - roots[0]
            if not RUN.endswith(tuple(f'_v{n_}' for n_ in range(1, 18))):
                r_plant = max(r_plant, -.36)  # v18+: the v17 flight kick sits far back; plant within reach
            plant['feet'] = {'L': (l_end + .01, LAT['L'], 0.0, 0.0), 'R': (r_plant, LAT['R'], 0.0, 20.0)}
            RUN_KEYS.append(plant)
            body_s = 0.0
            for j, w in enumerate([.3, .6, .85, .97]):
                k_ = mix(plant, IDLE_R, w)
                body_s += roots[j + 1]
                k_['feet']['L'] = (l_end + .01*(1 - w), k_['feet']['L'][1], 0.0, 0.0)  # skid onto the idle spot
                step = max(0.0, (w - .55)/.42)  # right foot: planted, then steps back from w=.55
                r_s = r_plant - body_s + (IDLE_R['feet']['R'][0] - (r_plant - body_s))*min(1.0, step*1.15)
                k_['feet']['R'] = (r_s, k_['feet']['R'][1], .04*math.sin(math.pi*min(1.0, step)) if 0 < step < 1 else 0.0,
                                   20.0*(1 - w))
                k_['release'] = 1 - min(1.0, max(0.0, (w - .2)/.45))
                k_['root'] = roots[j + 1]
                # (Tried in run_stop_v9: holding the blade toward the camera longer put the tip past the
                # frame edge on drawing 2, so the brake keeps v8's blade timing.)
                RUN_KEYS.append(k_)
        else:
            # Brake from the loop's last drawing (right foot planted, left foot reaching): the left foot plants
            # wide where the idle's front foot belongs, the body sinks and leans back, slides over it, the Key
            # sweeps forward and the left hand takes the handle again, the right foot steps back into the stance.
            last = loop_key(7)
            plant = dict(last, turn=15.0, ce=.34 - POSE['drop'], hunch=-2.0, pitch=-10.0, neck=-4.0, look=8.0,
                         toe=20.0, twist=0.0, arm=-.5, hz=.04)
            body_after = [.06, .03, 0, 0]  # root motion of drawings 2-5
            l_plant = IDLE_R['feet']['L'][0] + sum(body_after)
            plant['feet'] = {'L': (l_plant, LAT['L'], 0.0, 0.0), 'R': (-.25, LAT['R'], 0.0, 20.0)}
            plant['root'] = .15
            RUN_KEYS.append(plant)
            body_s = 0.0
            for j, w in enumerate([.3, .6, .85, .97]):
                k_ = mix(plant, IDLE_R, w)
                body_s += body_after[j]
                k_['feet']['L'] = (l_plant - body_s, k_['feet']['L'][1], 0.0, 0.0)
                r_s = -.25 - body_s if w < .6 else plant['feet']['R'][0] + (IDLE_R['feet']['R'][0] - plant['feet']['R'][0])*w
                k_['feet']['R'] = (r_s, k_['feet']['R'][1], .03*math.sin(math.pi*min(1, (w - .3)/.6)) if w >= .6 else 0.0,
                                   k_['feet']['R'][3])
                k_['release'] = 1 - min(1.0, max(0.0, (w - .2)/.45))
                k_['root'] = body_after[j]
                RUN_KEYS.append(k_)

        def apply_run(k_):
            global blade
            if k_.get('spin_deg'):
                # Jump spin: turn the whole pose (body, feet, hands, left-arm target, elbow hints) about the vertical
                # axis through the hips; the Key hand keeps its grip and turns with him.
                rz_ = Matrix.Rotation(math.radians(k_['spin_deg']), 3, 'Z')
                k_ = dict(k_); k_['spin_deg'] = 0.0
                k_['turn'] = k_['turn'] + math.degrees(math.atan2(rz_[1][0], rz_[0][0]))
                k_['hand'] = rz_ @ Vector(k_['hand'])
                feet_ = {}
                for sd_, (fs_, fl_, *rest_) in k_['feet'].items():
                    wv_ = rz_ @ (U_*fs_ + V_*fl_)
                    feet_[sd_] = (wv_.dot(U_), wv_.dot(V_), *rest_)
                k_['feet'] = feet_
                k_['l_elbow_hint'] = tuple(rz_ @ Vector(k_.get('l_elbow_hint') or (1, .4, -.3)))
                k_['r_elbow_hint'] = tuple(rz_ @ Vector(k_.get('r_elbow_hint') or (-1, .4, -.3)))
                apply_run(k_)
                POSE['L_free'] = (tuple(rz_ @ Vector(POSE['L_free'][0])), POSE['L_free'][1])
                if POSE.get('r_hand_rot'):
                    POSE['r_hand_rot'] = [list(r_) for r_ in (rz_ @ Matrix(POSE['r_hand_rot']))]
                blade = (rz_ @ blade).normalized()
                return
            POSE['wrist_roll'] = k_.get('wrist_roll')
            POSE['screen_lean_deg'] = k_.get('lean_cam', 0.0)
            POSE['leg_reach'] = k_.get('leg_reach')
            POSE['ankle_deg'] = k_.get('ankle_deg')
            POSE['toe_bend'] = k_.get('toe_bend')
            POSE['hip_back_deg'] = k_.get('hip_back_deg')
            if HURT:
                POSE['knee_in'] = dict(k_.get('knee_in') or {})
                POSE['knee_splay'] = k_.get('knee_splay')  # crouching attacks: knees wide like the crouch
                POSE['knee_hint_world'] = k_.get('knee_hint_world') or {}  # kneeling crouch: back knee down
                POSE['knee_hint_w'] = 1.0  # Standing Medium v13+: back knee turns in on the pivot
            POSE['screen_head_deg'] = k_.get('head_cam', 0.0)
            POSE['L_elbow_hint_world'] = k_.get('l_elbow_hint', (1, .4, -.3))
            POSE['L_shrug_deg'] = k_.get('l_shrug', 0.0)
            POSE['R_elbow_hint_world'] = k_.get('r_elbow_hint')
            POSE.update({'body_turn_deg': k_['turn'], 'crouch_extra': k_['ce'], 'hunch_extra': k_['hunch'],
                         'pitch_extra': k_['pitch'], 'neck_extra': k_['neck'], 'look_deg': k_['look'],
                         'head_tilt_deg': k_['tilt'], 'toe_deg': {'L': k_['toe'], 'R': k_['toe']},
                         'twist_axis': 'spine', 'chest_twist_deg': k_['twist']*TW_SIGN,
                         'hands_extra_z': k_['hz']})
            turn_inv = Matrix.Rotation(math.radians(k_['turn']), 3, 'Z').inverted()
            POSE['R_hand'] = tuple(turn_inv @ k_['hand'])
            POSE['foot_pitch'] = {}
            for sd, (s_, l_, lift_, pitch_) in k_['feet'].items():
                bx, by = to_body(k_['turn'], (s_, l_))
                POSE[f'{sd}_foot'] = (bx, by, lift_ + TOE_D*math.sin(math.radians(pitch_)))
                POSE['foot_pitch'][sd] = pitch_
            arm_w = (k_['arm'] + 1)/2
            POSE['L_free'] = (tuple(ARM_FWD.lerp(ARM_BACK, arm_w)), k_['release'])
            if k_.get('l_hand') is not None:
                POSE['L_free'] = (tuple(k_['l_hand']), k_['release'])  # hurt: left hand flung to its own spot
            POSE['L_arm'] = k_.get('l_arm')
            if k_.get('wrist_roll') is not None:
                POSE['r_hand_rot'] = None
                return
            if k_.get('blade_dir') is not None:
                blade = Vector(k_['blade_dir']).normalized()
                yaw_t = math.atan2(blade.y, blade.x)
                d_c = [yaw_t - CR_YAW0 + m_*2*math.pi for m_ in (-1, 0, 1)]
                d_ = min(d_c, key=abs)
                if abs(d_) > math.radians(120):  # big turns go round behind him, as in the run
                    d_ = max([c_ for c_ in d_c if abs(c_) < 2*math.pi],
                             key=lambda c_: Vector((math.cos(CR_YAW0 + c_/2), math.sin(CR_YAW0 + c_/2), 0)).dot(-V_))
                yawed = Matrix.Rotation(d_, 3, 'Z') @ CR_BLADE0
                q_ = yawed.rotation_difference(blade).to_matrix() @ Matrix.Rotation(d_, 3, 'Z')
                if k_.get('blade_twist'):
                    # Jump rising v11+: twist the Key about its own shaft (same direction, different face showing).
                    q_ = Matrix.Rotation(math.radians(k_['blade_twist']), 3, blade) @ q_
                POSE['r_hand_rot'] = [list(r_) for r_ in (q_ @ CR_TE0)]
                return
            b_s = k_['blade_s']
            yaw_ = CR_YAW0 + CR_DYAW*b_s
            el_ = CR_EL0 + (CR_EL1 - CR_EL0)*b_s
            blade = (Vector((math.cos(yaw_), math.sin(yaw_), 0))*math.cos(el_) + Vector((0, 0, math.sin(el_)))).normalized()
            yawed = Matrix.Rotation(CR_DYAW*b_s, 3, 'Z') @ CR_BLADE0
            q_ = yawed.rotation_difference(blade).to_matrix() @ Matrix.Rotation(CR_DYAW*b_s, 3, 'Z')
            POSE['r_hand_rot'] = [list(r_) for r_ in (q_ @ CR_TE0)]

        if GLIDE and GLIDE.endswith(('_v16', '_v17')) and part == 'run_loop':
            # v16 (Kvon: straighten the wrist holding the Keyblade in relation to his arm): keep v15's arm, leave the
            # wrist straight and pick the roll about the forearm whose Key points most like v15's backward blade
            # while the tip stays in the frame and above the floor.
            TW_SIGN = 1  # (set properly below; the glide has no chest twist)
            ground_w = world_bounds(body)[0].z
            best_roll = None
            for roll_ in range(0, 360, 10):
                ok_, bd0_ = True, None
                for kk_ in RUN_KEYS:  # every drawing must keep the whole Key in the frame and above the floor
                    apply_run(dict(kk_, wrist_roll=float(roll_))); solve_pose(0.0, LAG0)
                    km_ = pose_world('R_te') @ CR_KEY_IN_TE
                    bd_ = km_.to_3x3().normalized().col[2]
                    tip_ = km_.translation + bd_*(KEY_REACH + .08)
                    hip_ = pose_world('hara').translation
                    ok_ = ok_ and (tip_ - hip_).dot(U_) > -.92 and tip_.z > ground_w + .04  # backward blades reach far
                    bd0_ = bd0_ or bd_
                bd_ = bd0_
                score_ = bd_.dot(G_BACK_DIR) - (0 if ok_ else 10)
                if best_roll is None or score_ > best_roll[0]:
                    best_roll = (score_, roll_, tuple(round(c_, 3) for c_ in bd_))
            print('WRIST_ROLL', best_roll)
            roll_final = float(best_roll[1])
            if GLIDE.endswith('_v17'):
                # v17 (Kvon: rotate the wrist "only a little bit" so the Keyblade's teeth show): 20 deg more roll,
                # in whichever direction turns the Key's flat face (local Y) further toward the camera.
                faces_ = {}
                for d_ in (20.0, -20.0):
                    apply_run(dict(RUN_KEYS[0], wrist_roll=roll_final + d_)); solve_pose(0.0, LAG0)
                    km_ = pose_world('R_te') @ CR_KEY_IN_TE
                    faces_[d_] = abs(km_.to_3x3().normalized().col[1].dot(to_cam))
                apply_run(dict(RUN_KEYS[0], wrist_roll=roll_final)); solve_pose(0.0, LAG0)
                face0_ = abs((pose_world('R_te') @ CR_KEY_IN_TE).to_3x3().normalized().col[1].dot(to_cam))
                d_best = max(faces_, key=faces_.get)
                print('WRIST_TEETH', {'face_to_camera_before': round(face0_, 3), 'options': {k: round(v, 3) for k, v in faces_.items()}, 'chosen': d_best})
                roll_final += d_best
            for k_ in RUN_KEYS:
                k_['wrist_roll'] = roll_final
        if GLIDE and GLIDE.endswith('_v34') and part == 'run_start' and OUT_NAME.endswith(('_v34b', '_v34c', '_v34d')):
            # Measure the glide loop's actual Key direction (straight wrist), then ease the lunge drawings toward it.
            TW_SIGN = 1
            apply_run(dict(loop_key(0))); solve_pose(0.0, LAG0)
            loop_dir_ = (pose_world('R_te') @ CR_KEY_IN_TE).to_3x3().normalized().col[2]
            for k_ in RUN_KEYS:
                if k_.get('blade_ease') is not None:
                    k_['blade_dir'] = tuple(CR_BLADE0.lerp(loop_dir_, k_['blade_ease']).normalized())
        if JUMP and JUMP.startswith('jump_rise') and JUMP.endswith(('_v8', '_v9')):
            # Straight-wrist roll for rising 2: whole Key in the frame and above the floor, blade pointing as far down
            # (toward his feet) as the straight wrist allows, but not straight down - "somewhat".
            TW_SIGN = 1
            ground_j = world_bounds(body)[0].z
            best_j = None
            for roll_ in range(0, 360, 10):
                apply_run(dict(RUN_KEYS[1], wrist_roll=float(roll_))); solve_pose(0.0, LAG0)
                km_ = pose_world('R_te') @ CR_KEY_IN_TE
                bd_ = km_.to_3x3().normalized().col[2]
                tip_ = km_.translation + bd_*(KEY_REACH + .08)
                ok_ = tip_.z > ground_j + .04 and abs((tip_ - pose_world('hara').translation).dot(U_)) < .80
                score_ = -abs(bd_.z + .55) + .3*bd_.dot(to_cam) - (0 if ok_ else 10)
                if not JUMP.endswith('_v8'):
                    # v9: v8's pick swung the blade forward across his body toward the opponent; keep it on his own side
                    # (not forward), turned toward the player and tipped down.
                    score_ = -abs(bd_.z + .5) + .8*bd_.dot(to_cam) - 1.5*max(0.0, bd_.dot(U_)) - (0 if ok_ else 10)
                print('ROLL', roll_, ok_, tuple(round(c_, 2) for c_ in bd_), round(score_, 3))
                if best_j is None or score_ > best_j[0]:
                    best_j = (score_, roll_, tuple(round(c_, 3) for c_ in bd_))
            print('JUMP_WRIST_ROLL', best_j)
            RUN_KEYS[1]['wrist_roll'] = float(best_j[1])
            if OUT_NAME.startswith('jump_rise_v9_r'):
                RUN_KEYS[1]['wrist_roll'] = float(OUT_NAME.rsplit('_r', 1)[1])  # review variants
        # Twist sign: at the left-foot contact the right (opposite) shoulder should be forward.
        TW_SIGN = 1
        apply_run(dict(loop_key(0), twist=0.0)); solve_pose(0.0, LAG0)
        x0 = pose_world('R_kata').translation.dot(U_)
        apply_run(dict(loop_key(0), twist=10.0)); solve_pose(0.0, LAG0)
        TW_SIGN = 1 if pose_world('R_kata').translation.dot(U_) > x0 else -1
        RUN_LOG = []
        ROOT_MOTION = []
    if CROUCH:
        turn_c = Matrix.Rotation(math.radians(POSE.get('body_turn_deg', 0)), 3, 'Z')
        solve_pose(0.0, (1 - math.cos(2*math.pi*(0 - .12))) / 2)
        place_key()
        CR_TE0 = pose_world('R_te').to_3x3()
        CR_KEY_IN_TE = pose_world('R_te').inverted() @ key.matrix_world  # Key rigid in the fist
        CR_BLADE0 = blade.copy()
        CR_HAND0 = turn_c @ Vector(POSE['R_hand'])
        CR_HAND1 = turn_c @ Vector(CR['R_hand'])
        CR_GUARD = turn_c @ Vector(CR['L_guard'])
        CR_YAW0 = math.atan2(CR_BLADE0.y, CR_BLADE0.x)
        CR_EL0 = math.asin(max(-1, min(1, CR_BLADE0.z)))
        # Crouched blade: toward screen left and a little behind him; tilt so the tip stops just above the floor.
        behind = -to_cam
        h1 = (-Vector((math.cos(t), math.sin(t), 0))*.8 + behind*CR_BEHIND).normalized()
        yaw1 = math.atan2(h1.y, h1.x)
        # Turn the way that passes behind him (the swing's midpoint faces away from the camera).
        cands = [yaw1 - CR_YAW0 + k_*2*math.pi for k_ in (-1, 0, 1)]
        cands = [d_ for d_ in cands if abs(d_) < 2*math.pi]
        CR_DYAW = max(cands, key=lambda d_: Vector((math.cos(CR_YAW0 + d_/2), math.sin(CR_YAW0 + d_/2), 0)).dot(behind))
        POSE.update({k_: CR[k_] for k_ in ('crouch_extra', 'hunch_extra', 'pitch_extra', 'neck_extra', 'knee_splay')})
        POSE['grip_offset_world'] = tuple(CR_HAND1 - CR_HAND0)
        solve_pose(0.0)
        hz = hand_point('R').z
        ground_c = world_bounds(body)[0].z
        drop_ = min(.95, max(0.0, hz - ground_c - CR['blade_down_tip_m']) / KEY_REACH)
        CR_EL1 = -math.asin(drop_)
        for k_ in ('crouch_extra', 'hunch_extra', 'pitch_extra', 'neck_extra', 'knee_splay', 'grip_offset_world'):
            POSE.pop(k_, None)
        CR_LOG = []
        CR_RFOOT0 = tuple(POSE['R_foot'][:2]) + (0.0,)
        CR_LFOOT0 = tuple(POSE['L_foot'][:2])
        CR_TOE = 1.5*(pose_world('L_ashi2').translation - pose_world('L_ashi1').translation).length
        # (back-foot slide behind in body frame +y, ankle lift, toe pitch deg, extra hip sink)
        CR_KNEEL = None if CROUCH.endswith(('_v1', '_v2', '_v3', '_v4')) else (
            (.30, .06, 60.0, .06) if CROUCH.endswith('_v5') else
            ((.08, .08, 65.0, .12) if CROUCH.endswith('_v6') else (.24, .07, 70.0, .10)))
        if CROUCH.endswith(('_v8',)) or not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 8))):
            CR_KNEEL = (.24, .02, 70.0, .10)  # v8: ankle lifted only by the toe pitch
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 9))):
            CR_KNEEL = (.28, .03, 40.0, -.08)  # v9: (slide left, ankle lift, toe pitch, sink: negative = hips HIGHER)
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 10))):
            CR_KNEEL = (0.0, .03, 40.0, -.08)  # v10: v9's foot sat too far back (leg straight, knee off the floor)
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 11))):
            CR_KNEEL = (0.0, .11, 25.0, -.08)  # v11: v10's toe went ~10 cm through the floor - ankle up, less pitch
        # v12 (Kvon: turn the shin so the foot sits slightly behind him toward the background): metres away from the camera.
        CR_KNEEL_DEPTH = .14 if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 12))) else 0.0
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 13))):
            CR_KNEEL_DEPTH = .28  # v13 (Kvon: increase the turn)
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 14))):
            CR_KNEEL_DEPTH = .42  # v14 (Kvon: more turn than v13)
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 15))):
            CR_KNEEL_DEPTH = .50  # v15 (Kvon: a little more turn)
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 16))):
            # v16 (Kvon: turn until the foot is almost completely behind Sora): depth alone barely moves it on screen,
            # so the foot also slides toward his body centre (negative slide = toward screen right).
            CR_KNEEL = (-.30, .11, 25.0, -.08)
            CR_KNEEL_DEPTH = .60
        if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 17))):
            CR_KNEEL = (-.24, .11, 25.0, -.08)  # v17 (Kvon: a tiny bit back the opposite way)
            CR_KNEEL_DEPTH = .57
        CR_FRONT_IN = .14 if not CROUCH.endswith(tuple(f'_v{n_}' for n_ in range(1, 18))) else 0.0  # v18: front foot in (m)
        # v6: (slide left, lift, pitch, sink); v7: v6's shin/foot hid behind the guard and the knee dipped below the
        # floor - foot further left so the shin shows along the floor, a little less sink.
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
    KEY_TRACK = []
    if HURT:
        arm.rotation_mode = 'QUATERNION'
        ARM_M0 = arm.matrix_world.copy()
    for i in range(n):
        breath = (1 - math.cos(2*math.pi*i/n)) / 2
        # v3+: follow-through lag; a symmetric breath alone made frames 1-4 repeat as 9-6.
        lag = (1 - math.cos(2*math.pi*(i/n - BREATH_LAG))) / 2
        if RUN:
            apply_run(RUN_KEYS[i])
            breath, lag = 0.0, LAG0
            ROOT_MOTION.append(round(RUN_KEYS[i]['root'], 4))
        if CROUCH:
            w_ = CR_T[i]
            if CROUCH.startswith('crouch_down'):
                breath = 0.0
                lag = (1 - math.cos(2*math.pi*(0 - .12))) / 2  # idle frame 1, as the shuffle starts
            POSE.update({k_: CR[k_]*w_ for k_ in ('crouch_extra', 'hunch_extra', 'pitch_extra', 'neck_extra', 'knee_splay')})
            if CR_KNEEL and CROUCH.endswith('_v5'):
                # v5 (Kvon: the back leg kneels): back foot further behind him onto its toes - but "behind" in his body
                # frame points into the screen from this camera, so the leg hid behind him (replaced by v6).
                kb_, kl_, kp_, kc_ = CR_KNEEL
                fx_, fy_, _ = CR_RFOOT0
                POSE['R_foot'] = (fx_, fy_ + kb_*w_, kl_*w_ + CR_TOE*math.sin(math.radians(kp_*w_)))
                POSE['foot_pitch'] = {'R': kp_*w_}
                POSE['crouch_extra'] = POSE['crouch_extra'] + kc_*w_
            elif CR_KNEEL and not CROUCH.endswith(('_v6', '_v7', '_v8')):
                # v9+: a real kneel. v6-v8 kept the crouch's very low hips (~.23 m), so the back leg could not fold
                # under him and stretched out sideways with the ankle raised. Hips higher (less sink), the back knee
                # on the floor a little behind the hips, the shin back along the floor to the foot on its toes; ankle
                # target low and the knee pointing down and back.
                ks_, ka_, kp_, kc_ = CR_KNEEL
                tb_ = Matrix.Rotation(math.radians(POSE.get('body_turn_deg', 0)), 3, 'Z').inverted()
                right_ = Vector((math.cos(t), math.sin(t), 0))
                d_ = tb_ @ (right_*-ks_ - to_cam*CR_KNEEL_DEPTH)  # v12+: foot turned back toward the background
                fx_, fy_, _ = CR_RFOOT0
                POSE['R_foot'] = (fx_ + d_.x*w_, fy_ + d_.y*w_, ka_*w_)
                POSE['foot_pitch'] = {'R': kp_*w_}
                POSE['crouch_extra'] = POSE['crouch_extra'] + kc_*w_
                POSE['knee_hint_world'] = {'R': tuple(-right_*.45 + Vector((0, 0, -.90)))}
                if not CROUCH.endswith('_v9'):
                    POSE['knee_hint_world'] = {'R': tuple(right_*.15 + Vector((0, 0, -1.0)))}  # v10: knee straight down
                if CR_FRONT_IN:
                    # v18+ (Kvon: more bend in the front knee, foot toward the middle of his torso): the front (left) foot
                    # slides toward screen left, under his body; the hips stay, so the knee bends more.
                    d2_ = tb_ @ (right_*-CR_FRONT_IN)
                    lx_, ly_ = CR_LFOOT0
                    POSE['L_foot'] = (lx_ + d2_.x*w_, ly_ + d2_.y*w_, POSE['L_foot'][2] if len(POSE['L_foot']) > 2 else None)
                POSE['knee_hint_w'] = w_
            elif CR_KNEEL:
                # v6+: kneel seen side-on - the back foot slides toward screen left onto its toes (shin back along the
                # floor), the hips sink so the knee reaches the floor, and that knee points down and forward.
                ks_, kl_, kp_, kc_ = CR_KNEEL
                tb_ = Matrix.Rotation(math.radians(POSE.get('body_turn_deg', 0)), 3, 'Z').inverted()
                d_ = tb_ @ (Vector((math.cos(t), math.sin(t), 0))*-ks_)
                fx_, fy_, _ = CR_RFOOT0
                POSE['R_foot'] = (fx_ + d_.x*w_, fy_ + d_.y*w_, kl_*w_ + CR_TOE*math.sin(math.radians(kp_*w_)))
                # v8: v7's foot tipped toes-UP (the pitch sign comes out reversed for this crouch's turned back foot).
                POSE['foot_pitch'] = {'R': (kp_ if CROUCH.endswith(('_v6', '_v7')) else -kp_)*w_}
                POSE['crouch_extra'] = POSE['crouch_extra'] + kc_*w_
                POSE['knee_hint_world'] = {'R': tuple(Vector((math.cos(t), math.sin(t), 0))*.55 + to_cam*.15
                                                      + Vector((0, 0, -.82)))}
                POSE['knee_hint_w'] = w_
            # Blade: yaw round behind him (away from the camera) and tilt down, s = blade progress.
            s_ = w_
            yaw_ = CR_YAW0 + CR_DYAW*s_
            dir_ = Vector((math.cos(yaw_), math.sin(yaw_), 0))
            el_ = CR_EL0 + (CR_EL1 - CR_EL0)*s_
            blade = (dir_*math.cos(el_) + Vector((0, 0, math.sin(el_)))).normalized()
            yawed = Matrix.Rotation(CR_DYAW*s_, 3, 'Z') @ CR_BLADE0
            q_ = yawed.rotation_difference(blade).to_matrix() @ Matrix.Rotation(CR_DYAW*s_, 3, 'Z')
            POSE['r_hand_rot'] = [list(r_) for r_ in (q_ @ CR_TE0)]
            # Right fist slides from the idle grip to his right hip (body frame, before the crouch sink).
            POSE['grip_offset_world'] = tuple((CR_HAND1 - CR_HAND0)*w_)
            # Left hand: on the handle for the first part of the move, then off to the guard.
            l_w = min(1.0, max(0.0, (w_ - .1)/.6)); l_w = l_w*l_w*(3 - 2*l_w)
            POSE['L_free'] = (tuple(CR_GUARD), l_w)
            if OUT_NAME.endswith('_dbg'):
                solve_pose(0.0, lag)
                print('KNEEDBG', {b_: [round(c_, 3) for c_ in pose_world(b_).translation] for b_ in ('R_momo', 'R_sune', 'R_ashi1', 'R_ashi2', 'L_sune', 'hara')},
                      'floor', round(world_bounds(body)[0].z, 3), 'R_foot', POSE['R_foot'], 'cam_right', [round(math.cos(t), 3), round(math.sin(t), 3)])
            CR_LOG.append({'t': round(w_, 3), 'left_release': round(l_w, 3),
                           'blade_yaw_deg': round(math.degrees(yaw_), 1), 'blade_el_deg': round(math.degrees(el_), 1)})
        elif GAIT and IDLE_SHUFFLE:
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
        if HURT:
            arm.matrix_world = ARM_M0  # solve upright; the whole-body turn comes after
            update()
        if HURT and RUN_KEYS[i].get('shaft_grip'):
            # Standing Light v7+ (Kvon: the shaft hand's wrist was bent and didn't line up): a straight wrist that only
            # rolls about the forearm; pick the roll whose fist grip axis lines up best with the shaft.
            shaft_ = Vector(RUN_KEYS[i]['shaft_grip']).normalized()
            KEY_ROT_FACE = Matrix(POSE['r_hand_rot']) @ CR_KEY_IN_TE.to_3x3()  # the Key's own angle (guard to camera)
            best_g = None
            for roll_ in range(0, 360, 10):
                POSE['wrist_roll'] = float(roll_); POSE['r_hand_rot'] = None
                solve_pose(breath, lag)
                ax_g = (pose_world('R_te').to_3x3().normalized() @ CR_KEY_IN_TE.to_3x3().normalized()).col[2]
                if best_g is None or abs(ax_g.dot(shaft_)) > best_g[0]:
                    best_g = (abs(ax_g.dot(shaft_)), roll_)
            POSE['wrist_roll'] = float(best_g[1])
            print('SHAFT_GRIP', i, best_g)
        solve_pose(breath, lag)
        if HURT and OUT_NAME.endswith('_footdbg'):
            dg_ = bpy.context.evaluated_depsgraph_get()
            print('FOOTDBG', i, {b_: [round(c_, 3) for c_ in pose_world(b_).translation] for b_ in ('R_momo', 'R_sune', 'R_ashi1', 'R_ashi2', 'hara')},
                  'R_foot_target', POSE.get('R_foot'))
        if HURT and OUT_NAME.endswith('_dbg'):
            sh_ = pose_world('L_ude1').translation; el_ = pose_world('L_ude2').translation; wr_ = pose_world('L_te').translation
            print('DBG', i, 'R', [round(c_, 3) for c_ in hand_point('R')], 'L', [round(c_, 3) for c_ in hand_point('L')],
                  'Lsh', [round(c_, 3) for c_ in sh_], 'armlen', round((el_ - sh_).length + (wr_ - el_).length, 3),
                  'sh->R', round((hand_point('R') - sh_).length, 3), 'L_free', POSE.get('L_free'), 'blade',
                  [round(c_, 3) for c_ in blade])
        if RUN:
            reach = {sd: round((pose_world(f'{sd}_ashi1').translation - pose_world(f'{sd}_momo').translation).length, 3)
                     for sd in ('L', 'R')}
            # On-screen back angle (tailbone -> neck base, degrees off vertical; + = leaning toward screen right).
            cam_r = Vector((math.cos(t), math.sin(t), 0))
            hip_, neck_ = pose_world('hara').translation, pose_world('kubi').translation
            back_deg = math.degrees(math.atan2((neck_ - hip_).dot(cam_r), (neck_ - hip_).z))
            RUN_LOG.append({'screen_back_deg': round(back_deg, 1), 'feet_world_s_lat_lift_pitch': {sd: [round(v_, 3) for v_ in f_] for sd, f_ in RUN_KEYS[i]['feet'].items()},
                            'hip_to_ankle_m': reach, 'turn_deg': round(RUN_KEYS[i]['turn'], 1),
                            'left_release': round(RUN_KEYS[i]['release'], 2)})
        if HURT:
            # Turn the solved pose as one piece in the screen plane about the hips, then put it on the floor.
            hk_ = RUN_KEYS[i]
            piv_ = pose_world('hara').translation.copy()
            cam_r_ = Vector((math.cos(t), math.sin(t), 0))
            roll_ = hk_.get('roll', 0.0)
            if 'body_angle' in hk_:
                # v2+: roll so the hips->neck line sits at this screen angle (90 = upright, 180 = flat, head left).
                d_ = pose_world('kubi').translation - piv_
                if not HURT.endswith(('_v1', '_v2')):
                    # v3: measure the whole body (ankles -> neck); v2's hips->neck line left the legs raised off the floor.
                    d_ = pose_world('kubi').translation - (pose_world('L_ashi1').translation
                                                           + pose_world('R_ashi1').translation)/2
                roll_ = hk_['body_angle'] - math.degrees(math.atan2(d_.z, d_.dot(cam_r_)))
            if OUT_NAME.endswith('_upright'):
                roll_ = 0.0  # review: the solved pose before the whole-body turn
            arm.matrix_world = (Matrix.Translation(piv_) @ Matrix.Rotation(math.radians(roll_), 4, to_cam)
                                @ Matrix.Translation(-piv_) @ ARM_M0)
            update()
            if hk_.get('ground') and not OUT_NAME.endswith('_upright'):
                dg_ = bpy.context.evaluated_depsgraph_get()
                pts_ = [o.matrix_world @ v.co for o in body for v in o.evaluated_get(dg_).data.vertices]
                low_ = min(p_.z for p_ in pts_)
                xs_ = [p_.dot(cam_r_) for p_ in pts_]
                # v2+: centre the figure across the frame (lying, he is longer than half the frame).
                dx_ = (cam.location.dot(cam_r_) - (min(xs_) + max(xs_))/2
                       if not HURT.endswith('_v1') and not hk_.get('no_center') else 0.0)
                arm.matrix_world = (Matrix.Translation(cam_r_*dx_ + Vector((0, 0, ground + hk_.get('lift', 0.0) - low_)))
                                    @ arm.matrix_world)
                update()
            if hk_.get('offset_px'):
                # v4+: straight legs reach further - nudge an air drawing back inside the frame (screen px, x right/y up).
                px_m_ = cam_data.ortho_scale/512
                arm.matrix_world = (Matrix.Translation(cam_r_*hk_['offset_px'][0]*px_m_
                                                       + Vector((0, 0, hk_['offset_px'][1]*px_m_))) @ arm.matrix_world)
                update()
            RUN_LOG[-1].update(roll_deg=round(roll_, 1), spin_deg=hk_.get('spin_deg', 0.0),
                               grounded=bool(hk_.get('ground')))
            for path in ('location', 'rotation_quaternion', 'scale'):
                arm.keyframe_insert(path, frame=i + 1)
        if CROUCH or RUN:
            key.matrix_world = pose_world('R_te') @ CR_KEY_IN_TE
            if RUN and RUN_KEYS[i].get('key_in_left') and HURT.endswith('_v3'):
                # Standing Light v3: same Key angle, slid along its line so the handle sits in the left fist.
                key.matrix_world = Matrix.Translation(hand_point('L') - hand_point('R')) @ key.matrix_world
            elif RUN and RUN_KEYS[i].get('key_in_left'):
                if RUN_KEYS[i].get('shaft_grip') and not HURT.endswith('_v7'):
                    # v8: the straight-wrist hand roll turned the whole Key on its axis (guard edge-on in v7); keep the
                    # Key's own angle (guard face to the camera) and only take its grip point from the fist.
                    gk_ = key.matrix_world.inverted() @ hand_point('R')
                    key.matrix_world = (Matrix.Translation(hand_point('R') - KEY_ROT_FACE @ gk_)
                                        @ KEY_ROT_FACE.to_4x4())
                # v4+ (Kvon: the wrists must line up with the parts they hold): the Key's grip point (now in the right
                # fist) goes to the centre of the LEFT fist and the blade runs from there through the right fist's
                # centre, so the handle sits in the left fist and the shaft passes through the right one.
                g_w = hand_point('R'); l_w = hand_point('L')
                old_d = key.matrix_world.to_3x3().normalized().col[2]
                turn_k = old_d.rotation_difference((g_w - l_w).normalized()).to_matrix().to_4x4()
                key.matrix_world = Matrix.Translation(l_w) @ turn_k @ Matrix.Translation(-g_w) @ key.matrix_world
                # v5+: slide the Key forward along its line (toward the guard end) so the handle's middle is in the fist.
                key.matrix_world = (Matrix.Translation(-(g_w - l_w).normalized()*RUN_KEYS[i].get('key_slide', 0.0))
                                    @ key.matrix_world)
            update()
        else:
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
        if HURT:
            # Smear data (Standing Medium v3+): the Key's grip point and blade direction in this drawing, so
            # make_smears.py can sweep the blade between drawings and draw the smear as its own layer.
            KEY_TRACK.append({'grip_world': [round(c_, 5) for c_ in hand_point('R')],
                              'dir_world': [round(c_, 5) for c_ in key.matrix_world.to_3x3().normalized().col[2]],
                              'smear': int(RUN_KEYS[i].get('smear') or 0),
                              'offset_px': list(RUN_KEYS[i].get('offset_px') or (0, 0)),
                              'lgrip_world': [round(c_, 5) for c_ in hand_point('L')],
                              'smear_style': RUN_KEYS[i].get('smear_style', 'arc')})
            for opt_ in ('smear_bow', 'smear_grip'):
                if opt_ in RUN_KEYS[i]:
                    KEY_TRACK[-1][opt_] = RUN_KEYS[i][opt_]
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
        'camera_location': [round(c_, 5) for c_ in cam.location], 'key_reach_m': KEY_REACH,
        'key_track': globals().get('KEY_TRACK', []),
        'root_motion_m': ROOT_MOTION if GAIT or RUN else None,
        'game_frames_60fps': globals().get('GAME_FRAMES'),
        'crouch': {'recipe': CROUCH, 'targets': CR, 'per_frame': CR_LOG} if CROUCH else None,
        'run': {'recipe': RUN, 'leg_length_m': round((pose_world('L_sune').translation - pose_world('L_momo').translation).length
                                                     + (pose_world('L_ashi1').translation - pose_world('L_sune').translation).length, 3),
                'twist_sign': TW_SIGN, 'per_frame': RUN_LOG,
                'root_px_384': [round(m_*180.5, 2) for m_ in ROOT_MOTION]} if RUN else None,
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
