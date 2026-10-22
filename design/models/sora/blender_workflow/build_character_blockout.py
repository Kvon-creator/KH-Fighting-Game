"""Procedural Sora character blockout in a neutral A-pose for later rigging.

Approximate KH2-outfit construction from the approved idle reference; not an
extracted game asset or approved production model. No engine or artwork edits.
Run: blender --background --factory-startup --python build_character_blockout.py -- character_blockout_v1
"""
import json
import math
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'character_blockout_v1'
assert version.startswith('character_blockout_v'), version
V1 = version == 'character_blockout_v1'  # earlier versions stay reproducible
VN = int(version.rsplit('_v', 1)[1])
OUT = ROOT / 'design/models/sora/experiments' / version
if OUT.exists():
    raise RuntimeError('Preserve existing blockout; choose a new version')
assert bpy.app.version[:2] == (5, 2), bpy.app.version_string
OUT.mkdir(parents=True)
scene = bpy.context.scene
for obj in tuple(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.render.resolution_x, scene.render.resolution_y = 600, 800
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.world.color = (.5, .5, .5)
# Thin dark contour lines approximate the sprite line art.
scene.render.use_freestyle = True
scene.render.line_thickness_mode = 'ABSOLUTE'
scene.render.line_thickness = 1.3
lineset = bpy.context.view_layer.freestyle_settings.linesets[0]
lineset.select_crease = False
lineset.linestyle.color = (.03, .02, .03)
preview_property = bpy.context.preferences.filepaths.bl_rna.properties.get('file_preview_type')
if preview_property and 'NONE' in {item.identifier for item in preview_property.enum_items}:
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'


def toon(name, color):
    # Same constant-ramp emission cel shader as the weapon pilot.
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    normal = nodes.new('ShaderNodeNewGeometry')
    dot = nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = Vector((-.5, -.8, .65)).normalized()
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    base = ramp.color_ramp.elements[0]; base.position = 0
    base.color = (*(x*.45 for x in color), 1)
    for position, scale in [(.15, .72), (.5, 1.0), (.85, 1.12)]:
        item = ramp.color_ramp.elements.new(position)
        item.color = (*(min(1, x*scale) for x in color), 1)
    links = mat.node_tree.links
    links.new(normal.outputs['Normal'], dot.inputs[0])
    links.new(dot.outputs['Value'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], emission.inputs['Color'])
    links.new(emission.outputs[0], output.inputs['Surface'])
    return mat


# Linear values converted from sRGB colors sampled by eye from the approved idle.
M = {
    'skin': toon('skin_cel', (.955, .672, .456)),
    'hair': toon('hair_brown_cel', (.305, .085, .020)),
    'jacket': toon('jacket_black_cel', (.030, .030, .042)),
    'trim': toon('trim_white_cel', (.72, .72, .76)),
    'red': toon('accent_red_cel', (.58, .015, .02)),
    'yellow': toon('shoe_yellow_cel', (.955, .578, .013)),
    'sole': toon('sole_black_cel', (.02, .02, .025)),
    'eye_white': toon('eye_white_cel', (.92, .92, .92)),
    'iris': toon('iris_blue_cel', (.021, .155, .716)),
    'pupil': toon('pupil_cel', (.005, .01, .04)),
    'silver': toon('silver_cel', (.66, .73, .81)),
    'mouth': toon('mouth_cel', (.25, .03, .03)),
    'pocket': toon('pocket_grey_cel', (.07, .07, .085)),
}
root = bpy.data.objects.new('Sora_Blockout_Root', None)
scene.collection.objects.link(root)
root['role'] = 'Procedural approximate KH2 Sora blockout; not extracted game data or approved model'
root['pose'] = 'Neutral A-pose, facing -Y, ground at Z=0, units in meters'


def finish(obj, mat, subdiv=2):
    obj.parent = root
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if subdiv:
        mod = obj.modifiers.new('smooth_subdivision', 'SUBSURF')
        mod.levels = mod.render_levels = subdiv
    return obj


def loft(name, sections, mat, segments=16, subdiv=2):
    """Tube through (center, rx, ry) rings; ry follows the front (-Y) axis where possible."""
    centers = [Vector(c) for c, _, _ in sections]
    verts, faces = [], []
    for i, (center, rx, ry) in enumerate(sections):
        a = centers[max(i-1, 0)]; b = centers[min(i+1, len(centers)-1)]
        t = (b-a).normalized()
        ref = Vector((0, -1, 0)) if abs(t.y) < .9 else Vector((0, 0, 1))
        front = (ref - t*ref.dot(t)).normalized()
        side = t.cross(front)
        for k in range(segments):
            angle = 2*math.pi*k/segments
            verts.append(centers[i] + side*rx*math.cos(angle) + front*ry*math.sin(angle))
    for i in range(len(sections)-1):
        for k in range(segments):
            j = (k+1) % segments
            faces.append((i*segments+k, i*segments+j, (i+1)*segments+j, (i+1)*segments+k))
    # Rounded end caps: pole slightly beyond each end ring.
    for end, ring, sign in ((0, 0, -1), (len(sections)-1, len(sections)-1, 1)):
        nb = centers[end-sign] if 0 <= end-sign < len(centers) else centers[end]
        t = (centers[end]-nb).normalized() if (centers[end]-nb).length else Vector((0, 0, sign))
        r = min(sections[end][1], sections[end][2])
        verts.append(centers[end] + t*r*.6)
        pole = len(verts)-1
        for k in range(segments):
            j = (k+1) % segments
            a, b = ring*segments+k, ring*segments+j
            faces.append((a, b, pole) if sign > 0 else (b, a, pole))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    return finish(obj, mat, subdiv)


def blob(name, location, scale, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name; obj.scale = scale
    return finish(obj, mat, 1)


def ring(name, location, major, minor, scale, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=32,
                                     minor_segments=10, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name; obj.scale = scale
    return finish(obj, mat, 1)


def box(name, location, scale, mat, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name; obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    finish(obj, mat, 0)
    mod = obj.modifiers.new('rounded_edges', 'BEVEL'); mod.width = bevel; mod.segments = 3
    return obj


# Proportions: about 1.55 m to the hair top, large head and shoes per the sprite style.
HEAD = Vector((0, 0, 1.33))
if VN < 3:
    jaw = [((0, -.045, 1.165), .03, .025), ((0, -.03, 1.20), .075, .07), ((0, -.01, 1.25), .118, .115)]
else:
    # v3: rounder chin and fuller cheeks.
    jaw = [((0, -.05, 1.172), .04, .03), ((0, -.035, 1.205), .085, .075), ((0, -.012, 1.255), .125, .118)]
head = loft('head', jaw + [((0, 0, 1.31), .138, .132), ((0, .005, 1.37), .135, .13), ((0, .01, 1.43), .10, .10),
              ((0, .01, 1.465), .04, .04)], M['skin'], segments=20)
for s in (-1, 1):
    blob(f'ear_{"L" if s > 0 else "R"}', (s*.135, .02, 1.30), (.018, .03, .038), M['skin'])
    # Eyes follow the face curve, rotated outward.
    yaw = s*math.radians(22)
    if VN < 5:
        if VN < 4:
            eye = [(-.117, (.032, .012, .036)), (-.126, (.019, .008, .026)), (-.131, (.008, .005, .013))]
        else:
            # v4: eyes set into the face surface, with a larger iris.
            eye = [(-.115, (.031, .011, .037)), (-.122, (.022, .006, .029)), (-.126, (.009, .004, .015))]
        blob(f'eye_white_{"L" if s > 0 else "R"}', (s*.055, eye[0][0], 1.305), eye[0][1], M['eye_white'], (0, 0, yaw))
        blob(f'iris_{"L" if s > 0 else "R"}', (s*.053, eye[1][0], 1.302), eye[1][1], M['iris'], (0, 0, yaw))
        blob(f'pupil_{"L" if s > 0 else "R"}', (s*.052, eye[2][0], 1.302), eye[2][1], M['pupil'], (0, 0, yaw))
        blob(f'brow_{"L" if s > 0 else "R"}', (s*.058, -.123, 1.352), (.035, .008, .007), M['hair'], (0, math.radians(s*-8), yaw))
    if 3 <= VN < 5:
        loft(f'eyelash_{"L" if s > 0 else "R"}', [((s*.024, -.128, 1.332), .005, .004), ((s*.055, -.127, 1.343), .006, .004),
                                                   ((s*.086, -.113, 1.334), .005, .004)], M['pupil'], segments=8, subdiv=1)
    if VN >= 3:
        blob(f'hair_side_{"L" if s > 0 else "R"}', (s*.12, .05, 1.30), (.04, .075, .075), M['hair'])
if VN >= 3:
    if VN < 4:
        blob('nose', (0, -.133, 1.268), (.011, .012, .016), M['skin'])
    else:
        # v4: small soft nose tip mostly sunk into the face.
        blob('nose', (0, -.126, 1.27), (.007, .008, .011), M['skin'])
    loft('mouth', [((-.022, -.113, 1.217), .004, .003), ((0, -.118, 1.213), .004, .003),
                   ((.022, -.113, 1.217), .004, .003)], M['mouth'], segments=8, subdiv=1)
if VN >= 5:
    # v5: almond eyes per the supplied KH2 render (arched upper lid, nearly flat lower edge),
    # built as thin layers projected onto the evaluated head surface so nothing protrudes.
    tree = BVHTree.FromObject(head, bpy.context.evaluated_depsgraph_get())

    def on_face(x, z, offset):
        hit, normal, _, _ = tree.ray_cast(Vector((x, -1, z)), Vector((0, 1, 0)))
        assert hit is not None, (x, z)
        if normal.y > 0:  # loft winding gives inward normals; offsets must point out of the face
            normal = -normal
        return hit + normal*offset

    def face_decal(name, outline, offset, mat):
        area = sum(x0*z1 - x1*z0 for (x0, z0), (x1, z1) in zip(outline, outline[1:] + outline[:1]))
        if area < 0:  # counter-clockwise as seen from the front gives a -Y facing normal
            outline = outline[::-1]
        n = len(outline)
        verts = [on_face(x, z, offset) for x, z in outline] + [on_face(x, z, offset - .003) for x, z in outline]
        faces = [tuple(range(n)), tuple(range(2*n-1, n-1, -1))]
        faces += [(i, i+n, (i+1) % n + n, (i+1) % n) for i in range(n)]
        mesh = bpy.data.meshes.new(name); mesh.from_pydata([tuple(v) for v in verts], [], faces); mesh.update()
        obj = bpy.data.objects.new(name, mesh); scene.collection.objects.link(obj)
        obj.parent = root; obj.data.materials.append(mat)
        return obj

    W, Z0, Z1 = .054, 1.298, 1.307  # eye width, inner and outer corner heights
    def top(u): return Z0 + (Z1-Z0)*u/W + .025*math.sin(math.pi*u/W)**.7
    def bot(u): return Z0 + (Z1-Z0)*u/W - .008*math.sin(math.pi*u/W)
    def clipped(uc, zc, ru, rz, count=28):
        pts = []
        for k in range(count):
            a = 2*math.pi*k/count
            u = min(max(uc + ru*math.cos(a), .001), W - .001)
            pts.append((u, min(max(zc + rz*math.sin(a), bot(u)), top(u))))
        return pts
    for s in (-1, 1):
        side = 'L' if s > 0 else 'R'
        def X(pts): return [(s*(.028 + u), z) for u, z in pts]
        outline = [(W*k/14, top(W*k/14)) for k in range(15)] + [(W*k/14, bot(W*k/14)) for k in range(13, 0, -1)]
        face_decal(f'eye_white_{side}', X(outline), .0015, M['eye_white'])
        face_decal(f'iris_{side}', X(clipped(.024, Z0 + .009, .0155, .021)), .0028, M['iris'])
        face_decal(f'pupil_{side}', X(clipped(.024, Z0 + .010, .0065, .010)), .0040, M['pupil'])
        face_decal(f'eye_highlight_{side}', X(clipped(.029, Z0 + .018, .0035, .0045, 16)), .0052, M['eye_white'])
        lash = [(-.003, top(0) + .001)] + [(W*k/6, top(W*k/6) + .002) for k in range(1, 6)] + [(W + .007, Z1 + .001)]
        loft(f'eyelash_{side}', [(on_face(s*(.028 + u), z, .005), .0045, .003) for u, z in lash],
             M['pupil'], segments=8, subdiv=1)
        brow = [(.0, 1.346), (.025, 1.354), (.052, 1.356)]
        loft(f'brow_{side}', [(on_face(s*(.028 + u), z, .004), .003, .0025) for u, z in brow],
             M['hair'], segments=6, subdiv=1)
loft('neck', [((0, .0, 1.09), .05, .045), ((0, .005, 1.20), .045, .042)], M['skin'])

# Hair: cap plus flattened tapered spikes (azimuth 0 = front, elevation, length, radius, droop).
if V1:
    blob('hair_cap', (0, .02, 1.375), (.15, .148, .112), M['hair'])
else:
    # v2: cap reaches lower at the back and sides; nape mass covers the bald skull seen in v1.
    blob('hair_cap', (0, .035, 1.36), (.152, .158, .13), M['hair'])
    blob('hair_nape', (0, .08, 1.27), (.12, .08, .09), M['hair'])
SPIKES = [(-28, 12, .10, .036, .75), (0, 16, .11, .036, .8), (28, 12, .10, .036, .75),
          (-55, 6, .10, .038, .6), (55, 6, .10, .038, .6),
          (-80, 4, .14, .045, .35), (80, 4, .14, .045, .35), (-100, 20, .16, .05, .15), (100, 20, .16, .05, .15),
          (-118, -8, .13, .045, .4), (118, -8, .13, .045, .4), (0, 62, .12, .05, -.1),
          (-40, 48, .14, .05, 0), (40, 48, .14, .05, 0), (-142, 35, .17, .05, .1), (142, 35, .17, .05, .1),
          (180, 32, .16, .05, .15), (-162, 6, .13, .045, .3), (162, 6, .13, .045, .3), (180, -14, .12, .04, .4)]
if VN >= 3:
    SPIKES += [(-88, -20, .08, .03, .6), (88, -20, .08, .03, .6)]  # sideburns in front of the ears
hair_center = Vector((0, .02, 1.36))
if VN < 5:
    for n, (az, el, length, radius, droop) in enumerate(SPIKES):
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a)*math.cos(e), -math.cos(a)*math.cos(e), math.sin(e)))
        pts = []
        for f, r in ((0, 1), (.35, .8), (.7, .45), (1, .1)):
            p = hair_center + d*(.105 + length*f) + Vector((0, 0, -droop*length*f*f))
            pts.append((p, radius*r, radius*r*.55))
        loft(f'hair_spike_{n:02d}', pts, M['hair'], segments=10)
else:
    # v5: flatter, sharper blade locks in two layers, after the supplied KH2 render.
    # (azimuth, elevation, length, width, droop, pull toward the face, lighter tone)
    LOCKS = [(-42, 10, .10, .032, .55, .03, 0), (-24, 14, .11, .033, .6, .04, 1), (-6, 4, .115, .026, .62, .05, 0),
             (12, 12, .11, .032, .6, .04, 1), (30, 10, .10, .032, .55, .03, 0), (46, 6, .09, .03, .5, .02, 1),
             (0, 60, .12, .05, -.12, 0, 1), (-88, -20, .08, .03, .6, 0, 0), (88, -20, .08, .03, .6, 0, 0),
             (180, 40, .16, .05, .1, 0, 0), (180, -12, .12, .042, .4, 0, 0)]
    for s in (-1, 1):
        LOCKS += [(s*az, el, length, width, droop, 0, tone) for az, el, length, width, droop, tone in
                  [(64, 10, .12, .04, .45, 1), (80, 2, .15, .045, .30, 0), (96, 22, .17, .05, .12, 1),
                   (112, -6, .14, .045, .38, 0), (126, 14, .15, .045, .2, 1), (30, 50, .14, .05, -.02, 0),
                   (60, 40, .15, .05, .05, 1), (145, 38, .17, .05, .08, 1), (160, 15, .15, .047, .25, 0),
                   (140, 0, .13, .045, .35, 1), (165, -20, .10, .04, .45, 0),
                   (50, 28, .09, .035, .1, 1), (105, 28, .09, .035, .1, 0), (150, 28, .09, .035, .1, 1)]]
    hair_light = toon('hair_light_cel', (.42, .14, .035))
    for n, (az, el, length, width, droop, pull, tone) in enumerate(LOCKS):
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a)*math.cos(e), -math.cos(a)*math.cos(e), math.sin(e)))
        pts = []
        for f, r in ((0, 1), (.2, .95), (.45, .75), (.7, .45), (.88, .2), (1, .04)):
            p = hair_center + d*(.105 + length*f) + Vector((0, pull*f*f, -droop*length*f*f))
            pts.append((p, width*r, width*r*.38))
        loft(f'hair_lock_{n:02d}', pts, hair_light if tone else M['hair'], segments=8)

# Jacket torso, hood rim, front trim, shoulders and short sleeves.
loft('jacket_torso', [((0, .0, .76), .15, .11), ((0, .0, .84), .142, .10), ((0, .0, .94), .155, .105),
                      ((0, .005, 1.02), .17, .11), ((0, .01, 1.07), .15, .09), ((0, .01, 1.11), .07, .06)],
     M['jacket'], segments=20)
ring('hood_rim', (0, .025, 1.10), .095, .03, (1.05, 1.0, .8), M['trim'], (math.radians(-12), 0, 0))
if not V1:
    blob('hood_back', (0, .10, 1.12), (.12, .06, .07), M['jacket'])
if VN >= 3:
    ring('jacket_hem_trim', (0, 0, .80), .14, .01, (1.02, .76, 1), M['trim'])
for s in (-1, 1):
    side = 'L' if s > 0 else 'R'
    loft(f'jacket_front_trim_{side}', [((s*.05, -.108, 1.08), .012, .006), ((s*.06, -.112, .98), .012, .006),
                                         ((s*.065, -.112, .86), .012, .006), ((s*.07, -.115, .78), .012, .006)],
         M['trim'], segments=8, subdiv=1)
    shoulder = Vector((s*.165, .0, 1.06))
    d = Vector((s*math.sin(math.radians(50)), 0, -math.cos(math.radians(50))))
    elbow = shoulder + d*.23
    wrist = elbow + d*.21
    blob(f'shoulder_pad_{side}', tuple(shoulder + Vector((s*.01, 0, .015))), (.07, .07, .05), M['trim'])
    loft(f'sleeve_{side}', [(shoulder - d*.02, .068, .068), (shoulder + d*.07, .066, .064), (shoulder + d*.13, .058, .056)],
         M['jacket'])
    ring(f'sleeve_cuff_{side}', tuple(shoulder + d*.13), .055, .012, (1, 1, 1), M['trim'],
         (0, math.atan2(d.x, d.z), 0))
    loft(f'upper_arm_{side}', [(shoulder, .042, .042), (shoulder + d*.15, .038, .038), (elbow, .033, .033)], M['skin'])
    loft(f'forearm_{side}', [(elbow, .034, .034), (elbow + d*.08, .036, .035), (wrist, .028, .028)], M['skin'])
    loft(f'glove_cuff_{side}', [(wrist - d*.045, .034, .034), (wrist + d*.012, .033, .033)], M['jacket'])
    # Hand thin across the palm plane so palms face the body.
    if V1:
        loft(f'hand_{side}', [(wrist, .02, .032), (wrist + d*.045, .022, .042), (wrist + d*.085, .018, .037),
                              (wrist + d*.105, .012, .022)], M['jacket'])
    else:
        # v2: fingerless glove over the palm, bare skin fingers beyond it.
        loft(f'hand_{side}', [(wrist, .02, .032), (wrist + d*.045, .022, .042), (wrist + d*.07, .02, .04)],
             M['jacket'])
        loft(f'fingers_{side}', [(wrist + d*.06, .017, .037), (wrist + d*.09, .016, .034),
                                 (wrist + d*.115, .011, .022)], M['skin'])
    loft(f'thumb_{side}', [(wrist + d*.025 + Vector((0, -.03, 0)), .011, .011),
                           (wrist + d*.06 + Vector((0, -.05, 0)), .009, .009)], M['skin'], segments=8)

# Belt, red side flaps, crown pendant.
ring('belt', (0, 0, .775), .14, .022, (1.08, .82, 1), M['jacket'])
for s in (-1, 1):
    blob(f'belt_red_flap_{"L" if s > 0 else "R"}', (s*.145, -.02, .745), (.035, .06, .055), M['red'],
         (0, math.radians(s*15), 0))
crown = [(-.02, 0), (-.026, .028), (-.012, .016), (0, .032), (.012, .016), (.026, .028), (.02, 0)]
cv = [(x, y, z+1.0) for y in (-.122, -.114) for x, z in crown]
cf = [tuple(range(len(crown)))[::-1], tuple(range(len(crown), 2*len(crown)))]
cf += [(i, i+1, i+1+len(crown), i+len(crown)) for i in range(len(crown)-1)]
cf.append((len(crown)-1, 0, len(crown), 2*len(crown)-1))
cmesh = bpy.data.meshes.new('crown_pendant'); cmesh.from_pydata(cv, [], cf); cmesh.update()
cobj = bpy.data.objects.new('crown_pendant', cmesh); scene.collection.objects.link(cobj); finish(cobj, M['silver'], 0)
loft('necklace_cord', [((-.04, -.085, 1.10), .005, .005), ((0, -.118, 1.035), .005, .005),
                       ((.04, -.085, 1.10), .005, .005)], M['sole'], segments=6, subdiv=1)

# Baggy shorts with snug cuffs, calves and large KH2 shoes.
loft('shorts_pelvis', [((0, 0, .62), .14, .10), ((0, 0, .70), .16, .115), ((0, 0, .78), .152, .112)], M['jacket'])
for s in (-1, 1):
    side = 'L' if s > 0 else 'R'
    x = s*.09
    loft(f'shorts_leg_{side}', [((x, 0, .70), .10, .10), ((s*.10, -.005, .60), .112, .11),
                                ((s*.105, -.01, .48), .115, .11), ((s*.10, -.01, .40), .095, .09),
                                ((s*.10, -.005, .365), .07, .068)], M['jacket'])
    ring(f'shorts_cuff_{side}', (s*.10, -.005, .37), .066, .012, (1, 1, 1), M['trim'])
    loft(f'calf_{side}', [((s*.10, 0, .39), .05, .05), ((s*.10, .005, .30), .053, .052),
                          ((s*.10, 0, .20), .04, .04), ((s*.10, 0, .135), .034, .034)], M['skin'])
    if V1:
        loft(f'shoe_{side}', [((s*.10, .075, .085), .058, .065), ((s*.10, .03, .105), .072, .085),
                              ((s*.10, -.06, .08), .078, .062), ((s*.10, -.15, .065), .072, .05),
                              ((s*.10, -.215, .055), .05, .036)], M['yellow'], segments=18)
        box(f'sole_{side}', (s*.10, -.07, .014), (.155, .33, .028), M['sole'], .012)
    else:
        # v2: chunkier, rounder KH2 shoes with a raised toe.
        loft(f'shoe_{side}', [((s*.10, .08, .095), .065, .07), ((s*.10, .03, .12), .08, .095),
                              ((s*.10, -.07, .09), .092, .078), ((s*.10, -.16, .082), .09, .068),
                              ((s*.10, -.235, .075), .066, .05)], M['yellow'], segments=18)
        box(f'sole_{side}', (s*.10, -.075, .016), (.185, .37, .032), M['sole'], .014)
    ring(f'shoe_collar_{side}', (s*.10, .02, .155), .045, .018, (1.05, 1.1, 1), M['sole'])
    blob(f'shoe_heel_red_{side}', (s*.10, .085, .09), (.05, .025, .045), M['red'])
    if VN < 3:
        straps = [(-.03, .135, .075, .04), (-.085, .12, .075, .04)]
    else:
        # v3: raised to sit on the chunkier v2 shoe surface.
        straps = [(-.04, .185, .092, .07), (-.10, .15, .097, .065)]
    if VN < 4:
        for k, (y, z, half, drop) in enumerate(straps):
            loft(f'shoe_strap_{side}_{k}', [((s*.10 - half, y, z - drop), .014, .009), ((s*.10, y, z + .01), .014, .009),
                                             ((s*.10 + half, y, z - drop), .014, .009)], M['sole'], segments=8, subdiv=1)
    else:
        # v4: straps follow an arc just outside the shoe's interpolated cross-section.
        shoe = [(.08, .095, .065, .07), (.03, .12, .08, .095), (-.07, .09, .092, .078),
                (-.16, .082, .09, .068), (-.235, .075, .066, .05)]
        for k, y in enumerate((-.03, -.10)):
            for (y0, z0, rx0, ry0), (y1, z1, rx1, ry1) in zip(shoe, shoe[1:]):
                if y1 <= y <= y0:
                    f = (y0-y)/(y0-y1)
                    zc, rx, ry = z0+(z1-z0)*f, rx0+(rx1-rx0)*f, ry0+(ry1-ry0)*f
            arc = [((s*.10 + (rx+.004)*math.cos(math.radians(a)), y, zc + (ry+.004)*math.sin(math.radians(a))), .013, .008)
                   for a in range(15, 170, 25)]
            loft(f'shoe_strap_{side}_{k}', arc, M['sole'], segments=8, subdiv=1)
    if VN >= 3:
        blob(f'shorts_pocket_{side}', (s*.205, -.01, .56), (.022, .075, .065), M['pocket'])
        blob(f'pocket_flap_{side}', (s*.21, -.01, .615), (.02, .078, .02), M['trim'])

# Review renders from fixed orthographic cameras.
VIEWS = [('front', 0, 1.75, .80), ('sprite_three_quarter', -40, 1.75, .80), ('side', 90, 1.75, .80), ('back', 180, 1.75, .80)]
if VN >= 3:
    VIEWS += [('face_front', 0, .5, 1.32), ('face_three_quarter', -40, .5, 1.32)]
renders = []
for view, yaw, ortho, cam_z in VIEWS:
    cam_data = bpy.data.cameras.new(f'cam_{view}')
    cam_data.type = 'ORTHO'; cam_data.ortho_scale = ortho
    cam = bpy.data.objects.new(f'cam_{view}', cam_data)
    scene.collection.objects.link(cam)
    t = math.radians(yaw)
    cam.location = (5*math.sin(t), -5*math.cos(t), cam_z)
    cam.rotation_euler = (math.radians(90), 0, t)
    scene.camera = cam
    path = OUT / f'{view}.png'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    renders.append(path)
scene.camera = bpy.data.objects['cam_sprite_three_quarter']
face_renders = renders[4:]
renders = renders[:4]

# Turnaround board on white for quick review.
w, h = scene.render.resolution_x, scene.render.resolution_y
board = np.ones((h, w*len(renders), 4), dtype=np.float32)
for i, path in enumerate(renders):
    img = bpy.data.images.load(str(path))
    px = np.empty(w*h*4, dtype=np.float32); img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    a = px[..., 3:4]
    board[:, i*w:(i+1)*w, :3] = px[..., :3]*a + (1-a)
    bpy.data.images.remove(img)
out_img = bpy.data.images.new('turnaround', w*len(renders), h, alpha=True)
out_img.pixels.foreach_set(board.ravel())
out_img.filepath_raw = str(OUT / 'Turnaround.png'); out_img.file_format = 'PNG'; out_img.save()

blend = OUT / 'sora_character_blockout.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
meshes = [o for o in scene.objects if o.type == 'MESH']
dg = bpy.context.evaluated_depsgraph_get()
zs = [(o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box]
report = {
    'version': version, 'blender': bpy.app.version_string,
    'role': root['role'], 'pose': root['pose'],
    'mesh_objects': len(meshes),
    'evaluated_vertices': sum(len(o.evaluated_get(dg).data.vertices) for o in meshes),
    'height_m': round(max(zs) - min(zs), 4), 'min_z': round(min(zs), 4),
    'materials': sorted(m.name for m in bpy.data.materials if m.users),
    'renders': [p.name for p in renders + face_renders] + ['Turnaround.png'], 'blend': blend.name,
    'not_included': ['rig', 'weights', 'animation', 'Keyblade attachment', 'GLB export', 'user approval'],
}
(OUT / 'Blockout_Report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('BLOCKOUT_OK', json.dumps(report))
