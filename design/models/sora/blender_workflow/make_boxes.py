"""Hurtboxes and hitboxes for every Sora drawing in the game, written as a GDScript data file.

Hurtboxes (where he can be hit): for every drawing in KingdomArena/assets/sora/*_384 (not the smear layers), the
silhouette with its thin parts removed (a morphological opening wider than the Keyblade's shaft, so the Key, hair
spikes and the thinnest limb ends drop out), split into three horizontal bands (head/chest, waist, legs); each band's
bounding box, grown a little.
Hitboxes (where an attack hits): on each attack's active drawing, the Keyblade's own pixels - the silhouette pixels
inside a corridor around the Key's projected line (grip -> tip, from the 3D version's key_track) - boxed; for the
Standing Light's guard bash, the pixels around the guard/left fist.
All boxes are in the drawing's own 384-scale frame pixels (x right, y down), before the in-game DRAW_SHIFT - the game
places them exactly like the sprite (same offset, mirrored for a fighter facing left).
Writes KingdomArena/scripts/sora_boxes.gd and design/models/sora/boxes_preview/ (overlays to check by eye).
Plain Python + Pillow + numpy. Run: python make_boxes.py
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[4]
assert (ROOT / 'KingdomArena/project.godot').is_file(), ROOT
ASSETS = ROOT / 'KingdomArena/assets/sora'
SORA = ROOT / 'design/models/sora'
OUT_GD = ROOT / 'KingdomArena/scripts/sora_boxes.gd'
PREVIEW = SORA / 'boxes_preview'
SCALE = 384 / 512          # 3D render pixels -> game frame pixels
OPEN_PX = 9                # opening size: wider than the Key's shaft (~6-7 px), narrower than his limbs
BANDS = 3
GROW = 3

# Each attack in the game: animation, the 3D version its drawings came from, its active drawing(s), and how the
# hitbox is found ('key' = along the Keyblade, 'guard' = around the guard / left fist).
# The last value is how far the Key sits slid down in the fist on the active drawing (grip_slide, metres) - the
# mid-handle grip rule shortens the reach past the fist by that much.
ATTACKS = [
    ('attack_light', 'atk_slight_v12', [1], 'guard', 0.0),
    ('attack_medium', 'atk_smed_v15', [5], 'key', 0.0),
    ('attack_heavy', 'atk_sheavy_v7', [4], 'key', 0.0),
    ('attack_clight', 'atk_clight_v31', [2], 'key', .10),
    ('attack_cmedium', 'atk_cmed_v24', [4], 'key', .10),
    ('attack_cheavy', 'atk_cheavy_v9', [2], 'key', .10),
    ('attack_jlight', 'atk_jlight_v8', [2], 'key', .10),
    ('attack_jmedium', 'atk_jmed_v7', [3], 'key', .10),
    ('attack_jheavy', 'atk_jheavy_v2', [3], 'key', 0.0),
]
SWEEP_FROM = .5            # a 'key' hitbox covers the Key's path over the last half of the swing into the hit
# ... except: the Crouching Medium's last half swings round behind him (its hit is the whole low sweep from the
# front), and the Jumping Medium's spin brings the Key down from high over his head (only the end of it strikes).
SWEEP_FROM_BY = {'attack_cmedium': 0.0, 'attack_jmedium': .8, 'attack_cheavy': 0.0}
# Extra forward reach (px, 384 scale) on top of the drawing: the launcher's Key points straight up, so on its own it
# could never touch an opponent pushed up against Sora (the middle hurtboxes keep them ~178 px apart); its hitbox
# covers the whole upward swing from chest height and reaches this far further forward.
FORWARD_PX = {'attack_cheavy': 110}


def alpha_mask(path):
    return np.asarray(Image.open(path).convert('RGBA').getchannel('A')) > 127


def body_mask(path):
    # The silhouette without the Keyblade's silver shaft/teeth (light, unsaturated grey) - its gold guard is thin
    # bars that the opening below removes once the shaft is gone.
    a = np.asarray(Image.open(path).convert('RGBA')).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    silver = (mx > 95) & (mx - mn < 28)
    # Its gold guard too, but only above his shoes (also gold): the bottom 35% of the figure keeps its gold. The
    # guard is held out in front, so leaving it in widened the middle (push) box past his body.
    gold = (r > 170) & (g > 95) & (g < 215) & (b < 100) & (r > g + 25)
    ys = np.nonzero((al > 127).any(1))[0]
    if len(ys):
        cut = int(ys[0] + (ys[-1] - ys[0])*.65)
        gold[cut:] = False
    return (al > 127) & ~silver & ~gold


def hurtboxes(mask):
    img = Image.fromarray((mask*255).astype(np.uint8))
    body = np.asarray(img.filter(ImageFilter.MinFilter(OPEN_PX)).filter(ImageFilter.MaxFilter(OPEN_PX))) > 127
    if not body.any():
        body = mask
    ys = np.nonzero(body.any(1))[0]
    top, bot = int(ys[0]), int(ys[-1]) + 1
    boxes = []
    for k in range(BANDS):
        y0 = top + (bot - top)*k//BANDS
        y1 = top + (bot - top)*(k + 1)//BANDS
        band = body[y0:y1]
        if not band.any():
            continue
        cols = np.nonzero(band.any(0))[0]
        rows = np.nonzero(band.any(1))[0]
        boxes.append((int(cols[0]) - GROW, y0 + int(rows[0]) - GROW,
                      int(cols[-1] - cols[0]) + 1 + 2*GROW, int(rows[-1] - rows[0]) + 1 + 2*GROW))
    return boxes


def projector(rep):
    w_, h_ = rep.get('canvas_size', [512, 512])
    px = max(w_, h_)/rep['ortho_scale']
    t = math.radians(rep['camera_yaw_deg'])
    right = np.array([math.cos(t), math.sin(t), 0.0])
    cam = np.array(rep['camera_location'])

    def screen(p):
        d = np.array(p) - cam
        return np.array([(w_/2 + d.dot(right)*px)*SCALE, (h_/2 - d[2]*px)*SCALE])
    return screen


def box_of(mask, near):
    ys, xs = np.nonzero(mask & near)
    if not len(xs):
        return None
    return (int(xs.min()) - GROW, int(ys.min()) - GROW, int(xs.max() - xs.min()) + 1 + 2*GROW,
            int(ys.max() - ys.min()) + 1 + 2*GROW)


def slerp(a, b, u):
    a, b = a/np.linalg.norm(a), b/np.linalg.norm(b)
    om = math.acos(max(-1.0, min(1.0, float(a.dot(b)))))
    return a if om < 1e-4 else (math.sin((1 - u)*om)*a + math.sin(u*om)*b)/math.sin(om)


def hitbox(mask, rep, i, style, slide, sweep_from=SWEEP_FROM):
    screen = projector(rep)
    track = rep['key_track']
    tr = track[i]
    if style == 'guard':
        yy, xx = np.mgrid[0:mask.shape[0], 0:mask.shape[1]]
        pts = np.stack([xx, yy], -1).astype(float)
        near = np.linalg.norm(pts - screen(tr['lgrip_world']), axis=-1) < 26
        return box_of(mask, near)
    # The Key's line (guard -> tip) from SWEEP_FROM of the way through the previous drawing -> this one, the previous
    # drawing moved into this drawing's frame (offset_px) like make_smears.py, through any smear_via directions.
    px = max(rep.get('canvas_size', [512, 512]))/rep['ortho_scale']
    t = math.radians(rep['camera_yaw_deg']); right = np.array([math.cos(t), math.sin(t), 0.0])
    pv = track[i - 1]
    shift = (tr.get('offset_px', [0, 0])[0] - pv.get('offset_px', [0, 0])[0])/px
    ga, gb = np.array(pv['grip_world']) + right*shift, np.array(tr['grip_world'])
    dirs = [np.array(pv['dir_world'])] + [np.array(v) for v in tr.get('smear_via') or []] + [np.array(tr['dir_world'])]
    reach = rep['key_reach_m'] - slide
    pts = []
    for k in range(25):
        u = sweep_from + (1 - sweep_from)*k/24
        leg = min(int(u*(len(dirs) - 1)), len(dirs) - 2)
        d = slerp(dirs[leg], dirs[leg + 1], u*(len(dirs) - 1) - leg)
        g = ga + (gb - ga)*u
        for f in (.15, .5, 1.0):
            pts.append(screen(g + d*reach*f))
    pts = np.array(pts)
    x0, y0 = pts.min(0) - 6; x1, y1 = pts.max(0) + 6
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(mask.shape[1], x1), min(mask.shape[0], y1)
    return (int(x0), int(y0), int(x1 - x0), int(y1 - y0))


def main():
    hurt, hit = {}, {}
    for folder in sorted(p for p in ASSETS.iterdir() if p.is_dir() and p.name.endswith('_384')
                         and '_smear_' not in p.name):
        for png in sorted(folder.glob('*.png')):
            hurt[f'{folder.name}/{png.name}'] = hurtboxes(body_mask(png))
    PREVIEW.mkdir(exist_ok=True)
    for anim, src, active, style, slide in ATTACKS:
        rep = json.loads((SORA / src / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
        for i in active:
            name = f'{anim}_384/sora_{anim}_{i:02d}.png'
            mask = alpha_mask(ASSETS / name)
            box = hitbox(mask, rep, i, style, slide, SWEEP_FROM_BY.get(anim, SWEEP_FROM))
            if anim in FORWARD_PX:
                box = (box[0], box[1], min(mask.shape[1] - box[0], box[2] + FORWARD_PX[anim]), box[3])
            assert box, (anim, i)
            hit[name] = [box]
            # preview: drawing + hurt (blue) + hit (red)
            im = Image.open(ASSETS / name).convert('RGBA')
            bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
            dr = ImageDraw.Draw(bg)
            for x, y, w, h in hurt[name]:
                dr.rectangle([x, y, x + w, y + h], outline=(40, 110, 255, 255), width=2)
            for x, y, w, h in hit[name]:
                dr.rectangle([x, y, x + w, y + h], outline=(230, 30, 30, 255), width=3)
            bg.convert('RGB').save(PREVIEW / f'{anim}_{i:02d}.png')
    lines = ['## Generated by design/models/sora/blender_workflow/make_boxes.py - do not edit by hand (re-run it).',
             '## Boxes per drawing, keyed by "<asset folder>/<file>", in the drawing\'s own frame pixels (x right, y down).',
             '## HURT: where Sora can be hit. HIT: where an attack hits (its active drawings only).',
             '', 'const HURT := {']
    for k, v in hurt.items():
        lines.append(f'\t"{k}": [' + ', '.join(f'Rect2({x}, {y}, {w}, {h})' for x, y, w, h in v) + '],')
    lines += ['}', '', 'const HIT := {']
    for k, v in hit.items():
        lines.append(f'\t"{k}": [' + ', '.join(f'Rect2({x}, {y}, {w}, {h})' for x, y, w, h in v) + '],')
    lines += ['}', '']
    OUT_GD.write_text('\n'.join(lines), encoding='utf-8')
    print('BOXES_OK', len(hurt), 'drawings with hurtboxes,', len(hit), 'hitboxes')


main()
