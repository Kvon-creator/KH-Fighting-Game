# Blender script: import a BVH and draw a stick-figure contact sheet (front row + side row) as PNG.
# usage: blender -b --factory-startup --python bvh_contact_sheet.py -- <in.bvh> <out.png> [samples]
import sys, bpy, numpy as np

args = sys.argv[sys.argv.index('--') + 1:]
src, out = args[0], args[1]
samples = int(args[2]) if len(args) > 2 else 10

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_anim.bvh(filepath=src, update_scene_fps=True)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
scn = bpy.context.scene
f0, f1 = (int(x) for x in arm.animation_data.action.frame_range)
frames = np.linspace(f0, f1, samples).round().astype(int)

bones = arm.pose.bones
pts = []  # per frame: list of (head, tail, name)
for f in frames:
    scn.frame_set(int(f))
    pts.append([((arm.matrix_world @ b.head)[:], (arm.matrix_world @ b.tail)[:], b.name) for b in bones])
allp = np.array([p for fr in pts for h, t, _ in fr for p in (h, t)])
lo, hi = allp.min(0), allp.max(0)
print('BOUNDS', lo.round(2), hi.round(2), 'frames', f0, f1)

cell, pad = 220, 14
W, H = cell * samples, cell * 2
img = np.ones((H, W, 4), np.float32)
span = max(hi - lo) * 1.05

def line(a, b, col, w=2):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for s in np.linspace(0, 1, n):
        x, y = int(a[0] + (b[0] - a[0]) * s), int(a[1] + (b[1] - a[1]) * s)
        img[max(0, y - w):y + w, max(0, x - w):x + w, :3] = col

def colour(name):
    if name.startswith('Right'): return (0.85, 0.15, 0.1)   # right side red (sword arm)
    if name.startswith('Left'): return (0.1, 0.3, 0.85)
    return (0.1, 0.1, 0.1)

for i, fr in enumerate(pts):
    for row, (ax, flip) in enumerate(((0, 1), (1, -1))):  # front: X across; side: Y across
        ox, oy = i * cell, (1 - row) * cell  # image rows grow downward from the bottom in Blender pixels
        def proj(p):
            u = (p[ax] - (lo[ax] + hi[ax]) / 2) * flip / span
            v = (p[2] - lo[2]) / span
            return (ox + cell / 2 + u * (cell - 2 * pad), oy + pad + v * (cell - 2 * pad))
        line((ox, oy + pad - 2), (ox + cell, oy + pad - 2), (0.7, 0.7, 0.7), 1)  # floor
        for h, t, name in fr:
            line(proj(h), proj(t), colour(name))

im = bpy.data.images.new('sheet', W, H, alpha=True)
im.pixels = img.ravel()
im.filepath_raw = out
im.file_format = 'PNG'
im.save()
print('SAVED', out, 'sampled frames', list(frames))
