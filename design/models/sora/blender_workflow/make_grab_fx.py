"""Ground grab effects (v6+), drawn as their own transparent layers like the Keyblade smears.

- Spin motion lines (drawings 3-10): curved speed lines trailing the swung opponent along the circle Sora's left fist
  travels (from the build report's `grab_hand_L`), three lines at the opponent's chest / hips / legs, tapering and
  fading toward the back. Layer `frames_fx_back_512` - drawn BEHIND both bodies.
- Impact burst (drawing 14, the strike): a two-tone star burst with a few streaks where the Key meets the opponent
  (on the Key 80% of the way to the tip, from `key_track`). Layer `frames_fx_front_512` - drawn on top of everything.
Tones match the smears (pale blue band, near-white core).
Plain Python + Pillow + numpy; reads only the report.
Run: python make_grab_fx.py atk_grab_v6 atk_grab2d_v6
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
assert (ROOT / 'KingdomArena/project.godot').is_file(), ROOT  # project root (any clone)
src, dst = sys.argv[1:3]
SORA = ROOT / 'design/models/sora'
rep = json.loads((SORA / src / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
SS = 4
W_, H_ = rep['canvas_size']
PX = max(W_, H_) / rep['ortho_scale']
t = math.radians(rep['camera_yaw_deg'])
RIGHT = np.array([math.cos(t), math.sin(t), 0.0])
CAM = np.array(rep['camera_location'])
REACH = rep['key_reach_m']
LINE_TONE = (122, 178, 255)
CORE_TONE = (232, 243, 255)
SPIN = range(3, 11)      # drawings that get trailing lines (the swing from the first spin step through the heave)
STRIKE = 14


def screen(p):
    d = np.asarray(p) - CAM
    return np.array(((W_/2 + d.dot(RIGHT)*PX)*SS, (H_/2 - d[2]*PX)*SS))


hands = [np.array(h) for h in rep['grab_hand_L']]
spin_pts = hands[2:10]
# Least-squares circle through the spin's fist positions (top view) -> its centre (his pivot). v7's steps are uneven
# (the spin accelerates), so a plain average no longer lands on the centre.
_xy = np.array([h[:2] for h in spin_pts])
_A = np.column_stack((2*_xy, np.ones(len(_xy))))
_sol = np.linalg.lstsq(_A, (_xy**2).sum(axis=1), rcond=None)[0]
center = _sol[:2]


def ang(p):
    return math.atan2(p[1] - center[1], p[0] - center[0])


def arc(a0, a1, r, z, n=24):
    # world points on the horizontal circle from angle a0 to a1 (shortest way)
    da = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
    return [np.array((center[0] + r*math.cos(a0 + da*k/n), center[1] + r*math.sin(a0 + da*k/n), z))
            for k in range(n + 1)]


def tapered(draw, pts, width_px, tone, alpha):
    n = len(pts) - 1
    for k in range(n):
        u = (k + 1)/n                                  # 0 = back end (thin, faint) -> 1 = front end
        draw.line([tuple(pts[k]), tuple(pts[k + 1])], fill=tone + (int(alpha*u**1.3),),
                  width=max(1, round(width_px*SS*(.25 + .75*u))))


def burst(draw, c, r_out, r_in, spikes, tone, rot):
    pts = []
    for k in range(spikes*2):
        a = rot + math.pi*k/spikes
        r = r_out if k % 2 == 0 else r_in
        pts.append((c[0] + r*math.cos(a), c[1] + r*math.sin(a)))
    draw.polygon(pts, fill=tone)


for sub in ('frames_fx_back_512', 'frames_fx_front_512'):
    (SORA / dst / sub).mkdir(parents=True, exist_ok=True)
log = []
for i in range(len(hands)):
    back = Image.new('RGBA', (W_*SS, H_*SS), (0, 0, 0, 0))
    front = Image.new('RGBA', (W_*SS, H_*SS), (0, 0, 0, 0))
    if i in SPIN:
        h = hands[i]
        r = float(np.linalg.norm(h[:2] - center))
        a_now, a_prev = ang(h), ang(hands[i - 1])
        da = (a_now - a_prev + math.pi) % (2*math.pi) - math.pi
        a_start = a_now - da*2.2                         # trail a good deal longer than one step (visible past the bodies)
        a_end = a_now - da*.25                           # stop short of the body so it stays readable
        d = ImageDraw.Draw(back, 'RGBA')
        # chest, hips and legs of the opponent (legs swing wider and a little lower)
        for dr, dz, w_px, alpha in ((0.0, .10, 16, 240), (.35, -.10, 13, 225), (.75, -.25, 11, 210)):
            pts = [screen(p) for p in arc(a_start, a_end, r + dr, h[2] + dz)]
            tapered(d, pts, w_px, LINE_TONE, alpha)
            tapered(d, pts, w_px*.4, CORE_TONE, alpha)
        log.append({'drawing': i, 'lines': 3, 'sweep_deg': round(abs(math.degrees(da))*1.35, 1)})
    if i == STRIKE:
        fr = rep['key_track'][i]
        c = screen(np.array(fr['grip_world']) + np.array(fr['dir_world'])*REACH*.80)
        d = ImageDraw.Draw(front, 'RGBA')
        burst(d, c, 120*SS, 34*SS, 8, LINE_TONE + (225,), .2)
        burst(d, c, 72*SS, 20*SS, 8, CORE_TONE + (245,), .2 + math.pi/8)
        for k in range(6):                               # short streaks flying out along the hit (screen right/up)
            a = -math.radians(10 + 14*k)
            p0 = c + np.array((math.cos(a), math.sin(a)))*130*SS
            p1 = c + np.array((math.cos(a), math.sin(a)))*(175 + 25*(k % 2))*SS
            d.line([tuple(p0), tuple(p1)], fill=LINE_TONE + (220,), width=4*SS)
        log.append({'drawing': i, 'impact_px': [round(c[0]/SS), round(c[1]/SS)]})
    for img, sub in ((back, 'frames_fx_back_512'), (front, 'frames_fx_front_512')):
        floor_y = int(rep['ground_baseline_y']*SS)
        ImageDraw.Draw(img).rectangle([0, floor_y, W_*SS, H_*SS], fill=(0, 0, 0, 0))
        img.resize((W_, H_), Image.LANCZOS).save(SORA / dst / sub / f'sora_fx_{i:02d}.png')
(SORA / dst / 'FX_Report.json').write_text(json.dumps({'source': src, 'fx': log}, indent=2) + '\n', encoding='utf-8')
print('FX_OK', log)
