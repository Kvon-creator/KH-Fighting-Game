"""Keyblade swing smears from Kvon's weapon-smear guide (November 18): "elongated multiples" on each swing's hit drawing
and a "crescent / anticipation" smear on the drawing before it for the heavies. Added on top of the existing smear
layers (make_smears.py's solid crescents) in the game's 384-px smear frames.

- Elongated multiples: the Keyblade's own pixels, cut from the game drawing (its silver / gold pixels in a corridor
  around the projected blade), copied back along the swing at 3 points between the previous drawing's blade and this
  one; each copy is itself 5 thin sub-copies spread across its slice of the arc (= stretched along the motion),
  tinted toward the smear blue and fading the further back it is. Drawn UNDER the existing crescent.
- Crescent anticipation: on the drawing before the hit (heavies), a thin, sharp crescent along the first part of the
  coming arc, from the tip forward - a "snap" just before the swing.
The blade's position per drawing comes from the 3D version's report (`key_track`, camera), projected like
make_boxes.py does, so the game drawing's pixels and the projection line up. The first run saves the original game
smear frames to <2d version>/frames_smear_384_base/; every run starts from those (safe to re-run).
Run: python make_key_multiples.py [--debug]   (--debug writes overlays of the projected blade to design/.../combat/)
"""
import json
import math
import shutil
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sora_paths import SORA, ROOT  # noqa: E402

ASSETS = ROOT / 'KingdomArena/assets/sora'
SCALE = 384 / 512
LINE_TONE = np.array((122, 178, 255), float)
# anim, 3D version, 2D version, hit drawing, grip slide (as make_boxes.py), crescent before the hit
SWINGS = [
    ('attack_medium', 'atk_smed_v15', 'atk_smed2d_v15', 5, 0.0, False),
    ('attack_heavy', 'atk_sheavy_v7', 'atk_sheavy2d_v7', 4, 0.0, True),
    ('attack_clight', 'atk_clight_v31', 'atk_clight2d_v31', 2, .10, False),
    ('attack_cmedium', 'atk_cmed_v24', 'atk_cmed2d_v24', 4, .10, False),
    ('attack_cheavy', 'atk_cheavy_v17', 'atk_cheavy2d_v17', 2, .10, True),
    ('attack_jlight', 'atk_jlight_v8', 'atk_jlight2d_v8', 2, .10, False),
    ('attack_jmedium', 'atk_jmed_v7', 'atk_jmed2d_v7', 3, .10, False),
    ('attack_jheavy', 'atk_jheavy_v2', 'atk_jheavy2d_v2', 3, 0.0, True),
]
MULTIPLES = [(.40, .26), (.66, .40), (.88, .58)]   # (point along the swing's last part, opacity): older = fainter
SUB = 11
MAX_SPAN = 70.0   # the copies trail the blade by at most this many degrees (a big swing doesn't fan out)
DEBUG = '--debug' in sys.argv


def projector(rep):
    w_, h_ = rep.get('canvas_size', [512, 512])
    px = max(w_, h_) / rep['ortho_scale']
    t = math.radians(rep['camera_yaw_deg'])
    right = np.array([math.cos(t), math.sin(t), 0.0])
    cam = np.array(rep['camera_location'])

    def screen(p):
        d = np.array(p) - cam
        return np.array([(w_/2 + d.dot(right)*px)*SCALE, (h_/2 - d[2]*px)*SCALE])
    return screen, px, right


def blade(rep, i, frame_of, slide):
    """Grip and tip of drawing i's blade, in drawing frame_of's pixels (the drawings can be shifted in render)."""
    screen, px, right = projector(rep)
    tr, ref = rep['key_track'][i], rep['key_track'][frame_of]
    shift = (ref.get('offset_px', [0, 0])[0] - tr.get('offset_px', [0, 0])[0]) / px
    g = np.array(tr['grip_world']) + right*shift
    reach = rep['key_reach_m'] - slide
    return screen(g), screen(g + np.array(tr['dir_world'])*reach)


def key_cutout(img, grip, tip):
    """The Keyblade's pixels in a game drawing: silver / gold pixels in a corridor around the projected blade."""
    a = np.asarray(img.convert('RGBA')).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    silver = (mx > 90) & (mx - mn < 30)
    gold = (r > 150) & (g > 90) & (b < 110) & (r > g + 20)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = tip - grip
    L2 = max(d.dot(d), 1.0)
    t = ((xx - grip[0])*d[0] + (yy - grip[1])*d[1]) / L2
    px_ = grip[0] + np.clip(t, 0, 1)*d[0]; py_ = grip[1] + np.clip(t, 0, 1)*d[1]
    near = np.hypot(xx - px_, yy - py_) < 15
    keep = (al > 60) & near & (t > -0.12) & (t < 1.12) & (silver | gold)
    out = a.copy(); out[..., 3] = np.where(keep, al, 0)
    return Image.fromarray(out.astype(np.uint8), 'RGBA'), int(keep.sum())


def ang(p, q):
    return math.atan2(q[1] - p[1], q[0] - p[0])


def multiples(size, key_img, grip_prev, tip_prev, grip_now, tip_now):
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    a0, a1 = ang(grip_prev, tip_prev), ang(grip_now, tip_now)
    da = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
    tinted = np.asarray(key_img).astype(float)
    tinted[..., :3] = tinted[..., :3]*.45 + LINE_TONE*.55
    base = Image.fromarray(tinted.clip(0, 255).astype(np.uint8), 'RGBA')
    span = min(1.0, math.radians(MAX_SPAN) / max(abs(da), 1e-6))
    step = 0.16
    for u, alpha in MULTIPLES:
        for k in range(SUB):   # spread across the slice of arc = an elongated copy
            uu = 1 - span*(1 - (u + step*(k/(SUB - 1) - .5)))
            rot = math.degrees(-(da*(uu - 1)))   # PIL turns counter-clockwise on screen; screen angles go clockwise
            g = grip_prev + (grip_now - grip_prev)*uu
            c = base.rotate(rot, resample=Image.BICUBIC, center=tuple(grip_now), translate=tuple(g - grip_now))
            arr = np.asarray(c).astype(float); arr[..., 3] *= alpha / SUB * 1.8
            layer.alpha_composite(Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA'))
    return layer


def crescent(size, grip, tip, tip_next_angle):
    """A thin, sharp crescent along the first part of the coming arc, from the tip forward."""
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    a0 = ang(grip, tip)
    da = (tip_next_angle - a0 + math.pi) % (2*math.pi) - math.pi
    R = float(np.linalg.norm(tip - grip))
    outer, inner = [], []
    for k in range(25):
        u = k / 24
        a = a0 + da*.5*u
        w = math.sin(math.pi*u)   # sharp at both ends, thickest in the middle
        outer.append((grip[0] + math.cos(a)*(R + 6*w), grip[1] + math.sin(a)*(R + 6*w)))
        inner.append((grip[0] + math.cos(a)*(R - 7*w), grip[1] + math.sin(a)*(R - 7*w)))
    d = ImageDraw.Draw(layer, 'RGBA')
    d.polygon(outer + inner[::-1], fill=(122, 178, 255, 210))
    core = [(grip[0] + math.cos(a0 + da*.5*k/24)*(R + 1.5*math.sin(math.pi*k/24)),
             grip[1] + math.sin(a0 + da*.5*k/24)*(R + 1.5*math.sin(math.pi*k/24))) for k in range(25)]
    d.line(core, fill=(240, 247, 255, 235), width=2)
    return layer


log = []
for anim, v3d, v2d, hit, slide, cres in SWINGS:
    rep = json.loads((SORA / v3d / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
    smear_dir = ASSETS / f'{anim}_smear_384'
    base_dir = SORA / v2d / 'frames_smear_384_base'
    if not base_dir.exists():
        shutil.copytree(smear_dir, base_dir, ignore=shutil.ignore_patterns('*.import'))
    name = lambda i: f'sora_{anim}_smear_{i:02d}.png'
    body = lambda i: Image.open(ASSETS / f'{anim}_384' / f'sora_{anim}_{i:02d}.png').convert('RGBA')
    out = {}
    gp, tp = blade(rep, hit - 1, hit, slide)
    gn, tn = blade(rep, hit, hit, slide)
    key_img, npx = key_cutout(body(hit), gn, tn)
    smear = Image.open(base_dir / name(hit)).convert('RGBA')
    m = multiples(smear.size, key_img, gp, tp, gn, tn)
    m.alpha_composite(smear)                       # the existing crescent stays on top
    out[hit] = m
    entry = {'anim': anim, 'hit': hit, 'key_px': npx, 'swing_deg': round(math.degrees(
        (ang(gn, tn) - ang(gp, tp) + math.pi) % (2*math.pi) - math.pi), 1)}
    if cres:
        g0, t0 = blade(rep, hit - 1, hit - 1, slide)
        g1, t1 = blade(rep, hit, hit - 1, slide)
        before = Image.open(base_dir / name(hit - 1)).convert('RGBA')
        c = crescent(before.size, g0, t0, ang(g1, t1))
        c.alpha_composite(before)
        out[hit - 1] = c
        entry['crescent_on'] = hit - 1
    for i, im in out.items():
        im.save(smear_dir / name(i))
    if DEBUG:
        dbg = body(hit).copy(); dbg.alpha_composite(m)
        dd = ImageDraw.Draw(dbg)
        dd.line([tuple(gn), tuple(tn)], fill=(255, 0, 0, 255), width=2); dd.line([tuple(gp), tuple(tp)], fill=(0, 200, 0, 255), width=2)
        (SORA / 'boxes_preview').mkdir(exist_ok=True)
        bg = Image.new('RGBA', dbg.size, (255, 255, 255, 255)); bg.alpha_composite(dbg)
        bg.convert('RGB').save(SORA / 'boxes_preview' / f'keymult_{anim}.png')
    log.append(entry)
print('KEY_MULTIPLES_OK', json.dumps(log))
