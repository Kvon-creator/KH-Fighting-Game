"""Limit Form Sora's body on the pipeline's KH2 Sora skeleton (Kvon, October 29: player 2 / the CPU / the training
dummy are Sora in his Limit Form, with every current animation).

Blender 5.2 has no Collada (.dae) importer any more, and Kvon's Limit Form model
(design/sprite_backups/sora_limit_form/Sora (Limit Form).dae, KH2 game skeleton: 284 numbered bones) doesn't share
bone names with the pipeline's KH2 Sora rip (p_ex150.fbx: 49 named bones). Both are KH2 Sora with the same
proportions, so instead of re-rigging every pose, this reads the .dae itself (plain XML) and puts the Limit Form
mesh on the KH2 Sora armature that build_sprite_pilot.py already poses:
1. Mesh: positions x bind-shape matrix (the skinned rest shape), triangles, UVs, one material per texture.
2. Fit: a uniform scale + rotation + move (no mirroring) that best lays the Limit Form skeleton's main joints (hips,
   chest, neck, head, both legs and arms) onto the KH2 armature's matching bones - left/right chosen by the fit.
3. Skin: every Limit Form bone hands its weights to the KH2 bone whose segment (head -> tail) is nearest the centre
   of the vertices it moves (after the fit), so vertex groups get the KH2 names the pipeline relies on (L_te, L_yubiA, R_momo...).
Used by build_sprite_pilot.py when the environment variable SORA_CHARACTER=limit_form is set (outputs then go to
design/models/sora_limit_form/). Plain Python + bpy + numpy.
"""
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

NS = {'c': 'http://www.collada.org/2005/11/COLLADASchema'}
# Limit Form joints (by sid) for the fit, read from its skeleton (rest T-pose, Z up, face toward -Y):
# hips / chest / neck / head, then each side's hip, knee, ankle, toe, upper arm, elbow, wrist.
LF_CENTRE = {'hara': 'bone065', 'mune': 'bone067', 'kubi': 'bone068', 'atama': 'bone140'}
LF_SIDE_A = {'momo': 'bone011', 'sune': 'bone012', 'ashi1': 'bone015', 'ashi2': 'bone018',
             'ude1': 'bone078', 'ude2': 'bone079', 'te': 'bone082'}      # the +X side
LF_SIDE_B_X = -1.0                                                       # its mirror twins sit at -X


def _floats(node):
    return np.array([float(x) for x in node.text.split()])


def _joint_rest(root):
    # Each joint's world matrix in the skeleton's rest pose (the visual scene's node matrices, chained).
    out = {}

    def walk(node, pm):
        m = node.find('c:matrix', NS)
        wm = pm @ (np.array([float(x) for x in m.text.split()]).reshape(4, 4) if m is not None else np.eye(4))
        if node.attrib.get('type') == 'JOINT':
            out[node.attrib.get('sid') or node.attrib['id']] = wm
        for ch in node.findall('c:node', NS):
            walk(ch, wm)
    for n in root.find('c:library_visual_scenes', NS)[0].findall('c:node', NS):
        walk(n, np.eye(4))
    return out


def _read_dae(path):
    root = ET.parse(path).getroot()
    rest = _joint_rest(root)
    top_m = root.find('c:library_visual_scenes', NS)[0].find('c:node/c:matrix', NS)
    top = np.array([float(x) for x in top_m.text.split()]).reshape(4, 4) if top_m is not None else np.eye(4)
    sources = {}
    for s in root.iter('{%s}source' % NS['c']):
        if 'id' in s.attrib:  # (sampler <source> elements are plain text, without an id)
            sources[s.attrib['id']] = s
    images = {im.attrib['id']: im.find('c:init_from', NS).text for im in root.find('c:library_images', NS)}
    effect_img = {}
    for eff in root.find('c:library_effects', NS):
        samp = {}
        for np_ in eff.iter('{%s}newparam' % NS['c']):
            surf = np_.find('c:surface/c:init_from', NS)
            if surf is not None:
                samp[np_.attrib['sid']] = surf.text
            s2 = np_.find('c:sampler2D/c:source', NS)
            if s2 is not None:
                samp[np_.attrib['sid']] = samp.get(s2.text, s2.text)
        tex = next(iter(eff.iter('{%s}texture' % NS['c'])), None)
        if tex is not None:
            img = samp.get(tex.attrib['texture'], tex.attrib['texture'])
            effect_img[eff.attrib['id']] = images.get(img, img)
    mat_img = {}
    for m in root.find('c:library_materials', NS):
        eid = m.find('c:instance_effect', NS).attrib['url'][1:]
        mat_img[m.attrib['id']] = effect_img.get(eid)
    meshes = []
    for ctrl in root.find('c:library_controllers', NS):
        skin = ctrl.find('c:skin', NS)
        geom = root.find(f"c:library_geometries/c:geometry[@id='{skin.attrib['source'][1:]}']", NS)
        bsm = np.array([float(x) for x in skin.find('c:bind_shape_matrix', NS).text.split()]).reshape(4, 4)
        jn = skin.find('c:joints', NS)
        jsrc = next(i.attrib['source'][1:] for i in jn if i.attrib['semantic'] == 'JOINT')
        isrc = next(i.attrib['source'][1:] for i in jn if i.attrib['semantic'] == 'INV_BIND_MATRIX')
        names = sources[jsrc].find('c:Name_array', NS).text.split()
        inv = _floats(sources[isrc].find('c:float_array', NS)).reshape(-1, 4, 4)
        vw = skin.find('c:vertex_weights', NS)
        wsrc = next(i.attrib['source'][1:] for i in vw.findall('c:input', NS) if i.attrib['semantic'] == 'WEIGHT')
        wts = _floats(sources[wsrc].find('c:float_array', NS))
        vc = [int(x) for x in vw.find('c:vcount', NS).text.split()]
        v = [int(x) for x in vw.find('c:v', NS).text.split()]
        infl, k = [], 0
        for n_ in vc:
            infl.append([(names[v[k + 2*j]], wts[v[k + 2*j + 1]]) for j in range(n_)])
            k += 2*n_
        mesh = geom.find('c:mesh', NS)
        vsrc = mesh.find('c:vertices/c:input', NS).attrib['source'][1:]
        pos = _floats(sources[vsrc].find('c:float_array', NS)).reshape(-1, 3)
        # The mesh is stored before the scene's top node transform (centimetres, Y up); the skeleton is already in
        # its space (the bind matrices give it unposed), so only the vertices take that transform.
        pos = (np.c_[pos, np.ones(len(pos))] @ (top @ bsm).T)[:, :3]
        tris = mesh.find('c:triangles', NS)
        ins = {i.attrib['semantic']: (int(i.attrib['offset']), i.attrib['source'][1:]) for i in tris.findall('c:input', NS)}
        stride = max(o for o, _ in ins.values()) + 1
        p = np.array([int(x) for x in tris.find('c:p', NS).text.split()]).reshape(-1, stride)
        uv = None
        if 'TEXCOORD' in ins:
            uv_all = _floats(sources[ins['TEXCOORD'][1]].find('c:float_array', NS)).reshape(-1, 2)
            uv = uv_all[p[:, ins['TEXCOORD'][0]]]
        meshes.append({'name': geom.attrib.get('name', geom.attrib['id']), 'pos': pos,
                       'faces': p[:, ins['VERTEX'][0]].reshape(-1, 3), 'uv': uv, 'infl': infl,
                       'image': mat_img.get(tris.attrib.get('material'))})
    return meshes, {n: m[:3, 3] for n, m in rest.items()}


def _similarity(src, dst):
    # Umeyama: scale s, rotation R (no reflection), translation t with dst ~ s R src + t.
    mu_s, mu_d = src.mean(0), dst.mean(0)
    a, b = src - mu_s, dst - mu_d
    u, d, vt = np.linalg.svd(b.T @ a)
    e = np.eye(3)
    if np.linalg.det(u @ vt) < 0:
        e[2, 2] = -1
    r = u @ e @ vt
    s = np.trace(np.diag(d) @ e)/(a**2).sum()
    return s, r, mu_d - s*r @ mu_s


def swap_in(scene, arm, folder):
    """Delete the KH2 meshes, add the Limit Form meshes skinned to arm with KH2 bone names; returns them."""
    dae = Path(folder) / 'Sora (Limit Form).dae'
    meshes, joints = _read_dae(dae)
    head = {b.name: np.array(arm.matrix_world @ b.head_local) for b in arm.data.bones}
    tail = {b.name: np.array(arm.matrix_world @ b.tail_local) for b in arm.data.bones}
    best = None
    for a_side, b_side in (('L', 'R'), ('R', 'L')):
        src, dst = [], []
        for kh, lf in LF_CENTRE.items():
            src.append(joints[lf]); dst.append(head[kh])
        for kh, lf in LF_SIDE_A.items():
            twin = min(joints, key=lambda j: np.linalg.norm(joints[j] - joints[lf]*np.array([LF_SIDE_B_X, 1, 1])))
            src += [joints[lf], joints[twin]]
            dst += [head[f'{a_side}_{kh}'], head[f'{b_side}_{kh}']]
        src, dst = np.array(src), np.array(dst)
        s, r, t = _similarity(src, dst)
        err = np.linalg.norm((s*(r @ src.T)).T + t - dst, axis=1).mean()
        if best is None or err < best[0]:
            best = (err, s, r, t, a_side)
    err, s, r, t, a_side = best
    print('LIMIT_FORM fit', 'side+X=', a_side, 'mean joint error (m) =', round(float(err), 4), 'scale =', round(float(s), 4))
    fit = lambda pts: (s*(r @ np.asarray(pts).T)).T + t

    # KH2 limb segments: each bone from its joint to each child's joint (imported FBX bone tails are arbitrary);
    # a bone without children is its joint point. The Root bone (floor -> hips) is left out.
    segs = []
    for b in arm.data.bones:
        if b.name == 'Root':
            continue
        kids = [c for c in b.children]
        for c in kids or [None]:
            segs.append((b.name, head[b.name], head[c.name] if c is not None else head[b.name]))

    def nearest_bone(p):
        best_b, best_d = None, 1e9
        for n, a_, b_ in segs:
            ab = b_ - a_
            u = np.clip((p - a_) @ ab/max(ab @ ab, 1e-18), 0, 1)
            d = np.linalg.norm(p - (a_ + u*ab))
            if d < best_d:
                best_b, best_d = n, d
        return best_b
    # Each Limit Form bone goes to the KH2 bone nearest the centre of the vertices it moves (its joint point alone
    # is ambiguous: a knee joint touches both the thigh and the shin).
    acc = {}
    for m in meshes:
        world = fit(m['pos'])
        for vi, infl in enumerate(m['infl']):
            for jn, w in infl:
                if w > 0:
                    a_ = acc.setdefault(jn, [np.zeros(3), 0.0])
                    a_[0] += world[vi]*w
                    a_[1] += w
    bone_map = {j: nearest_bone(a_[0]/a_[1]) for j, a_ in acc.items() if a_[1] > 0}
    for o in [o for o in scene.objects if o.type == 'MESH']:
        bpy.data.objects.remove(o, do_unlink=True)
    mats = {}
    out = []
    for m in meshes:
        me = bpy.data.meshes.new('LF_' + m['name'])
        me.from_pydata([tuple(v) for v in fit(m['pos'])], [], [tuple(f) for f in m['faces']])
        if m['uv'] is not None:
            layer = me.uv_layers.new(name='UVMap')
            for i, loop in enumerate(me.loops):
                layer.data[i].uv = tuple(m['uv'][i])
        img = m['image']
        if img not in mats:
            mat = bpy.data.materials.new('LF_' + str(img))
            mat.use_nodes = True
            if img:
                tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
                tex.image = bpy.data.images.load(str(Path(folder) / img), check_existing=True)
            mats[img] = mat
        me.materials.append(mats[img])
        me.update()
        o = bpy.data.objects.new('LF_' + m['name'], me)
        scene.collection.objects.link(o)
        groups = {}
        for vi, infl in enumerate(m['infl']):
            acc = {}
            for jn, w in infl:
                kb = bone_map.get(jn)
                if kb and w > 0:
                    acc[kb] = acc.get(kb, 0.0) + w
            for kb, w in acc.items():
                if kb not in groups:
                    groups[kb] = o.vertex_groups.new(name=kb)
                groups[kb].add([vi], w, 'REPLACE')
        mod = o.modifiers.new('Armature', 'ARMATURE')
        mod.object = arm
        o.parent = arm
        o.matrix_parent_inverse = arm.matrix_world.inverted()
        out.append(o)
    print('LIMIT_FORM meshes', len(out), 'faces', sum(len(o.data.polygons) for o in out),
          'groups', sorted({g.name for o in out for g in o.vertex_groups}))
    return out
