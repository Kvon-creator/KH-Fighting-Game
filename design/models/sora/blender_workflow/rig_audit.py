"""Read-only rig + weight audit (the checks from the three rigging / weight painting tutorials).
Checks Auto Normalize (weights add up to 100%), unweighted vertices, vertex groups with no bone, weights reaching
bones far away in the skeleton ("stray", e.g. hair following a hand), perfectly straight sided joints (IK cannot tell
the bend direction) and left/right bones without a partner. See memory/Rig_Weight_Checklist.md.
Run: blender --background --factory-startup --python rig_audit.py -- <model .fbx or .blend> <label> <out.json>
Never saves anything.
"""
import json
import math
import re
import sys
from collections import Counter, deque
import bpy

src, label, out = sys.argv[sys.argv.index('--') + 1:][:3]
if src.lower().endswith('.blend'):
    bpy.ops.wm.open_mainfile(filepath=src)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=src)

SIDE = re.compile(r'(^|[._ \-])(L|R|Left|Right|l|r)([._ \-]|$)')


def mirror(n):
    def sw(m):
        t = {'L': 'R', 'R': 'L', 'l': 'r', 'r': 'l', 'Left': 'Right', 'Right': 'Left'}[m.group(2)]
        return m.group(1) + t + m.group(3)
    return SIDE.sub(sw, n, count=1)


report = {'label': label, 'source': src, 'meshes': []}
for o in bpy.data.objects:
    mod = next((m for m in o.modifiers if m.type == 'ARMATURE' and m.object), None) if o.type == 'MESH' else None
    if not mod:
        continue
    arm = mod.object.data
    bones = {b.name: b for b in arm.bones}
    deform = {n for n, b in bones.items() if b.use_deform}
    # tree distance between bones (hops through parents / children)
    adj = {n: set() for n in bones}
    for n, b in bones.items():
        if b.parent:
            adj[n].add(b.parent.name); adj[b.parent.name].add(n)

    def hops(a, b, cap=6):
        seen, q = {a: 0}, deque([a])
        while q:
            x = q.popleft()
            if x == b:
                return seen[x]
            if seen[x] >= cap:
                continue
            for y in adj[x]:
                if y not in seen:
                    seen[y] = seen[x] + 1; q.append(y)
        return cap + 1

    gname = {g.index: g.name for g in o.vertex_groups}
    orphan = sorted(n for n in gname.values() if n not in bones)
    n_v = len(o.data.vertices)
    unweighted = over = under = 0
    max_sum = 0.0
    per_vert = Counter()
    stray_pairs = Counter()
    stray_verts = 0
    for v in o.data.vertices:
        ws = [(gname[g.group], g.weight) for g in v.groups if gname.get(g.group) in deform and g.weight > 1e-4]
        tot = sum(w for _, w in ws)
        per_vert[len(ws)] += 1
        if not ws:
            unweighted += 1; continue
        max_sum = max(max_sum, tot)
        if tot > 1.01:
            over += 1
        elif tot < .99:
            under += 1
        dom = max(ws, key=lambda x: x[1])[0]
        bad = [n for n, w in ws if w > .05 and n != dom and hops(dom, n) > 3]
        if bad:
            stray_verts += 1
            for n in bad:
                stray_pairs[(dom, n)] += 1
    # rest pose: sided parent -> child joints that are perfectly straight (IK can't tell the bend direction)
    straight = []
    for n, b in bones.items():
        p = b.parent
        if p and SIDE.search(n) and b.children and p.length > 1e-6 and b.length > 1e-6:
            a = math.degrees(p.vector.angle(b.vector)) if p.vector.length and b.vector.length else 0
            if a < 2.0 and len(b.children) == 1 and n in deform:
                straight.append(f'{p.name}>{n} {a:.1f}deg')
    missing_mirror = sorted(n for n in bones if SIDE.search(n) and mirror(n) != n and mirror(n) not in bones)
    report['meshes'].append({
        'mesh': o.name, 'armature': mod.object.name, 'bones': len(bones), 'deform_bones': len(deform),
        'vertices': n_v, 'unweighted': unweighted, 'sum_over_100pct': over, 'sum_under_100pct': under,
        'max_weight_sum': round(max_sum, 3), 'bones_per_vertex': dict(sorted(per_vert.items())),
        'stray_vertices': stray_verts,
        'stray_top': [f'{a} -> {b}: {c}' for (a, b), c in stray_pairs.most_common(8)],
        'orphan_groups': orphan[:10], 'orphan_group_count': len(orphan),
        'straight_sided_joints': straight[:12], 'straight_count': len(straight),
        'missing_mirror': missing_mirror[:10], 'missing_mirror_count': len(missing_mirror),
        'preserve_volume': mod.use_deform_preserve_volume,
    })
json.dump(report, open(out, 'w'), indent=1)
print('AUDIT_OK', label, len(report['meshes']), 'meshes')
