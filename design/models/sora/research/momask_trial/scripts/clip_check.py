# Blender script: clipping check for an attack build. Opens <version>/sora_idle_loop.blend read-only and, for each
# keyed drawing, renders a quick top-down and a front (along the travel axis) view, plus counts right-arm vertices
# that sit inside the torso (closer to the spine bones than the torso's own surface). Writes <out>.png and prints counts.
# usage: blender -b --factory-startup --python clip_check.py -- <path/to/sora_idle_loop.blend> <out.png>
import sys, math
import bpy, numpy as np
from mathutils import Vector

blend, out = sys.argv[sys.argv.index('--') + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=blend)
scn = bpy.context.scene
scn.render.engine = 'BLENDER_WORKBENCH'
scn.render.use_freestyle = False
scn.render.film_transparent = False
scn.render.resolution_x = scn.render.resolution_y = 256
scn.display.shading.light = 'STUDIO'
scn.display.shading.color_type = 'MATERIAL'
cam_old = scn.camera
arm = next(o for o in scn.objects if o.type == 'ARMATURE')
body = max((o for o in scn.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' for m in o.modifiers)),
           key=lambda o: len(o.data.vertices))

cam = bpy.data.objects.new('chk', bpy.data.cameras.new('chk'))
scn.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.4
scn.camera = cam
frames = list(range(scn.frame_start, scn.frame_end + 1))  # one scene frame per drawing
grp = {g.name: g.index for g in body.vertex_groups}
arm_groups = [grp[n] for n in ('R_ude2', 'R_te') if n in grp]
torso_groups = [grp[n] for n in ('mune', 'hara', 'center') if n in grp]
vg = np.zeros((len(body.data.vertices), 2), bool)
for v in body.data.vertices:
    for g in v.groups:
        if g.weight > .5:
            if g.group in arm_groups: vg[v.index, 0] = True
            if g.group in torso_groups: vg[v.index, 1] = True
tiles = []
for f in frames:
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    me = body.evaluated_get(dg).to_mesh()
    co = np.array([body.matrix_world @ v.co for v in me.vertices])
    body.evaluated_get(dg).to_mesh_clear()
    hips = co[vg[:, 1]].mean(0)
    # inside test: arm vertices within the torso's horizontal radius around the spine at their height
    t = co[vg[:, 1]]; a = co[vg[:, 0]]
    inside = 0
    for p in a:
        near = t[np.abs(t[:, 2] - p[2]) < .04]
        if len(near) < 8: continue
        c = near.mean(0); r = np.percentile(np.linalg.norm((near - c)[:, :2], axis=1), 80)
        inside += np.linalg.norm((p - c)[:2]) < r * .85
    print(f'CLIP frame {f}: right forearm/hand vertices inside torso = {inside} of {len(a)}')
    for name, loc, rot in (('top', hips + np.array([0, 0, 3]), (0, 0, 0)),
                           ('front', hips + np.array([0, -3, 0]), (math.pi / 2, 0, 0))):
        cam.location = Vector(loc); cam.rotation_euler = rot
        path = f'{out}_{f}_{name}.png'
        scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        tiles.append((f, name, path))
# contact sheet: top row = top views, bottom row = front views
imgs = {(f, n): bpy.data.images.load(p) for f, n, p in tiles}
W, H = 256 * len(frames), 512
px = np.ones((H, W, 4), np.float32)
for i, f in enumerate(frames):
    for r, n in enumerate(('front', 'top')):
        im = imgs[(f, n)]
        a = np.array(im.pixels[:], np.float32).reshape(256, 256, 4)
        px[r * 256:(r + 1) * 256, i * 256:(i + 1) * 256] = a
sheet = bpy.data.images.new('clip_sheet', W, H)
sheet.pixels = px.ravel(); sheet.filepath_raw = out + '.png'; sheet.file_format = 'PNG'; sheet.save()
print('CLIP_SHEET', out + '.png', frames)
