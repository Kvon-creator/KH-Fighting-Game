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
from mathutils import Euler, Matrix, Vector

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'sprite_pilot_v1'
LOOP = version.startswith('idle_loop_v')  # refined pose + 10-frame breathing loop; sprite_pilot_v* = single frame
KEY_FACES_CAMERA = LOOP and version not in ('idle_loop_v2', 'idle_loop_v3')  # user grip correction
CURL_FINGERS = KEY_FACES_CAMERA and version != 'idle_loop_v4'  # close the rip's open hands on the handle
# v6+ (user request): twist each wrist so the palm faces the handle, and turn the teeth up.
WRIST_TWIST = CURL_FINGERS and version != 'idle_loop_v5'
KEY_TEETH_UP = WRIST_TWIST
# v7+: pose from Kvon's Smash idle reference image instead of the approved 2D idle.
REF_POSE = LOOP and version not in {f'idle_loop_v{n}' for n in range(1, 7)}
SORA = ROOT / 'design/models/sora'
OUT = SORA / version
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
bpy.ops.import_scene.fbx(filepath=str(SORA / 'downloads/p_ex150.fbx'))
arm = next(o for o in scene.objects if o.type == 'ARMATURE')
body = [o for o in scene.objects if o.type == 'MESH']
# The rip stores faces as separate strips; weld coincident vertices (UVs and weights are kept).
for o in body:
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
if REF_POSE and version == 'idle_loop_v7':
    # v7: Kvon's Smash idle reference (design/references/sora_smash_idle_pose_reference.png).
    # Wide stance with mild knee bend and toes out, upright torso, both hands low in front of the
    # waist, blade sweeping up and out past his right shoulder at a flat angle.
    POSE = {
        'drop': .10, 'lean_deg': 4,
        'R_hand': (-.05, -.24, .74), 'L_hand_along_handle': -.075,
        'R_foot': (-.40, .02, None), 'L_foot': (.40, .02, None),
        'blade_dir': (-.80, .30, .52), 'toe_out_deg': 25, 'head_tilt_deg': 5,
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
    wrist = Vector(grip)
    for _ in range(3 if LOOP else 1):
        two_bone(f'{side}_ude1', f'{side}_ude2', f'{side}_te', wrist, bend_hint)
        if not LOOP:
            break
        wrist += Vector(grip) - hand_point(side)


def hand_point(side):
    socket = pose_world(f'{side}_buki').translation
    return (pose_world(f'{side}_te').translation + socket) / 2 if KEY_FACES_CAMERA else socket


ankle_z = pose_world('L_ashi1').translation.z
blade = Vector(POSE['blade_dir']).normalized()


def solve_pose(breath=0.0, lag=None):
    # `lag` is the breath phase for hands/Key/head follow-through (trails the body slightly).
    lag = breath if lag is None else lag
    reset_pose()
    b = BREATH if LOOP else {'drop': 0, 'lean_deg': 0, 'hands_z': 0, 'head_counter_deg': 0}
    set_pose_world('center', Matrix.Translation((0, 0, -POSE['drop'] - b['drop']*breath)) @ pose_world('center'))
    rotate_world('mune', 'X', POSE['lean_deg'] + b['lean_deg']*breath)
    if b['head_counter_deg']:
        rotate_world('kubi', 'X', b['head_counter_deg']*lag)
    r_hand = Vector(POSE['R_hand']) + Vector((0, 0, b['hands_z']*lag))
    l_hand = r_hand + blade*POSE['L_hand_along_handle']
    toe_out = POSE.get('toe_out_deg', 0)
    for s, foot in (('R', POSE['R_foot']), ('L', POSE['L_foot'])):
        sign = -1 if s == 'R' else 1
        # Knees track over turned-out toes.
        knee = (sign*(.3 + toe_out/50), -1, 0)
        two_bone(f'{s}_momo', f'{s}_sune', f'{s}_ashi1', (foot[0], foot[1], ankle_z), knee)
        if toe_out:
            rotate_world(f'{s}_ashi1', 'Z', sign*toe_out)
    if POSE.get('head_tilt_deg'):
        rotate_world('atama', 'Y', POSE['head_tilt_deg'])  # top of head toward his left, as referenced
    hand_on('R', r_hand, (-1, .4, -.3))
    hand_on('L', l_hand, (1, .4, -.3))
    for side, degrees in TWIST.items():
        forearm = (pose_world(f'{side}_te').translation - pose_world(f'{side}_ude2').translation).normalized()
        rotate_world(f'{side}_te', forearm, degrees)
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


solve_pose(0.0)
if WRIST_TWIST:
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
        grip_world = (pose_world('R_te').translation + pose_world('R_buki').translation) / 2
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
    for i in range(n):
        breath = (1 - math.cos(2*math.pi*i/n)) / 2
        # v3+: follow-through lag; a symmetric breath alone made frames 1-4 repeat as 9-6.
        lag = (1 - math.cos(2*math.pi*(i/n - BREATH_LAG))) / 2
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
                                                - (Vector(POSE['R_hand']) + Vector((0, 0, BREATH['hands_z']*lag))
                                                   + blade*POSE['L_hand_along_handle'])).length, 4)})
    scene.frame_start, scene.frame_end = 1, n
    if REF_POSE:
        # Pose check from roughly the reference screenshot's near-front angle (not a sprite view).
        scene.frame_set(1)
        ref_data = bpy.data.cameras.new('reference_angle_camera'); ref_data.type = 'ORTHO'
        ref_data.ortho_scale = cam_data.ortho_scale
        ref_cam = bpy.data.objects.new('reference_angle_camera', ref_data); scene.collection.objects.link(ref_cam)
        ref_t = math.radians(-10)
        ref_cam.location = Vector((0, 0, center_z)) + Vector((math.sin(ref_t), -math.cos(ref_t), 0))*6
        ref_cam.rotation_euler = (math.radians(90), 0, ref_t)
        scene.camera = ref_cam
        scene.render.filepath = str(OUT / 'reference_angle_frame00.png')
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
