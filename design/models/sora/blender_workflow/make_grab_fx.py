"""Grab effects, drawn as their own transparent layers like the Keyblade smears. The same three for the ground grab
and the air grab (Kvon, November 13), all on `frames_fx_back_512` - drawn BEHIND both bodies:
- Rings on the level swing (ground: the spin, drawings 2-9; air: spin and whip, 2-6): three flat arcs round Sora's
  pivot (fitted to the build report's `grab_hand_L`), outside the bodies, trailing the opponent by about a quarter turn.
- Arcs where the opponent is swung out of it (ground: heave and toss, 10-11; air: the release, 7): three wide arcs
  round Sora ending at the opponent's far end and trailing back the way it came.
- Speed lines on the drawing after the release (ground 12, air 8): from the opponent back toward Sora.
Ground only: the impact burst on the strike (drawing 14) - a two-tone star burst with a few streaks where the Key
meets the opponent (from `key_track`), on `frames_fx_front_512`, drawn on top of everything; and the layers are cut
at the floor line (in the air grab the opponent is thrown below Sora's feet line).
The opponent's position per drawing is measured from its rendered layer (third argument), so live pose edits count.
Tones match the smears (pale blue band, near-white core). Plain Python + Pillow + numpy.
Run: python make_grab_fx.py atk_grab_v7 atk_grab2d_v7 hurt_grab2d_v7
     python make_grab_fx.py atk_agrab_v10 atk_agrab2d_v10 hurt_agrab2d_v10
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
AIR = src.startswith('atk_agrab')
# Drawings with rings (the level swing), with arcs (the opponent swung out of it: air = thrown down, ground = heaved
# and tossed up), with speed lines (just released), and with the impact burst (ground only: the Keyblade strike).
SPIN, SWEEP, RELEASED, STRIKE = (range(2, 7), (7,), 8, None) if AIR else (range(2, 10), (10, 11), 12, 14)
SQUASH = .38                                   # how flat a level circle looks from the sprite camera


def screen(p):
    d = np.asarray(p) - CAM
    return np.array(((W_/2 + d.dot(RIGHT)*PX)*SS, (H_/2 - d[2]*PX)*SS))


hands = [np.array(h) for h in rep['grab_hand_L']]
spin_pts = hands[2:7] if AIR else hands[2:10]
# Least-squares circle through the spin's fist positions (top view) -> its centre (his pivot). v7's steps are uneven
# (the spin accelerates), so a plain average no longer lands on the centre.
_xy = np.array([h[:2] for h in spin_pts])
_A = np.column_stack((2*_xy, np.ones(len(_xy))))
_sol = np.linalg.lstsq(_A, (_xy**2).sum(axis=1), rcond=None)[0]
center = _sol[:2]


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


def centre(folder, i):
    # middle of a rendered layer's drawing (supersampled px)
    a = np.asarray(Image.open(SORA / folder / 'frames_512' / f'sora_idle3d_{i:02d}.png').getchannel('A')) > 40
    ys, xs = np.nonzero(a)
    return np.array((xs.mean(), ys.mean()))*SS


def far_end(i, me):
    # the opponent's point furthest from Sora's middle on drawing i, relative to it (supersampled px)
    a = np.asarray(Image.open(SORA / sys.argv[3] / 'frames_512' / f'sora_idle3d_{i:02d}.png').getchannel('A')) > 40
    ys, xs = np.nonzero(a)
    far = np.column_stack((xs, ys))*SS - me
    return far[np.argmax((far**2).sum(axis=1))]


for sub in ('frames_fx_back_512', 'frames_fx_front_512'):
    (SORA / dst / sub).mkdir(parents=True, exist_ok=True)
log = []
for i in range(len(hands)):
    back = Image.new('RGBA', (W_*SS, H_*SS), (0, 0, 0, 0))
    front = Image.new('RGBA', (W_*SS, H_*SS), (0, 0, 0, 0))
    if i in SPIN:
        # Rings round his pivot. The sprite camera is level, so the fist's circle is really a flat line on screen;
        # it is drawn as a shallow ellipse (far side up) so the turn reads. Three arcs outside the bodies, trailing
        # the opponent by about a quarter turn.
        ctr = screen(np.array((center[0], center[1], hands[i][2])))
        def theta(h_):
            # where the fist is on its circle, seen from above, measured from the camera's right (far side = up)
            return math.atan2(h_[1] - center[1], h_[0] - center[0]) - t
        turn = (theta(hands[i]) - theta(hands[i - 1]) + math.pi) % (2*math.pi) - math.pi
        sgn = 1.0 if turn >= 0 else -1.0
        reach_px = max(np.linalg.norm(centre(sys.argv[3], i) - ctr), 150*SS)
        d = ImageDraw.Draw(back, 'RGBA')
        for extra, w_px, alpha in ((70, 15, 240), (125, 12, 225), (180, 9, 205)):
            R = reach_px + extra*SS
            angs = np.linspace(theta(hands[i]) - sgn*math.radians(115), theta(hands[i]) - sgn*math.radians(20), 28)
            pts = [ctr + np.array((R*math.cos(a), -R*SQUASH*math.sin(a))) for a in angs]
            tapered(d, pts, w_px, LINE_TONE, alpha)
            tapered(d, pts, w_px*.4, CORE_TONE, alpha)
        log.append({'drawing': i, 'rings': 3, 'turn_deg': round(math.degrees(turn), 1)})
    if i in SWEEP:
        # The release: the opponent is swung over and down in front of him (clockwise on screen). Three
        # wide arcs round Sora, ending at the opponent's far end and trailing back up the way it came.
        me = centre(dst, i)
        tip, was = far_end(i, me), far_end(i - 1, centre(dst, i - 1))
        t_tip, R0 = math.atan2(-tip[1], tip[0]), float(np.linalg.norm(tip))
        t_was = math.atan2(-was[1], was[0])
        way = 1.0 if (t_tip - t_was + math.pi) % (2*math.pi) - math.pi >= 0 else -1.0
        d = ImageDraw.Draw(back, 'RGBA')
        for scale, w_px, alpha in ((.95, 26, 240), (.75, 19, 225), (.55, 13, 210)):
            angs = np.linspace(t_tip - way*math.radians(85), t_tip - way*math.radians(10), 28)
            pts = [me + np.array((R0*scale*math.cos(a_), -R0*scale*math.sin(a_))) for a_ in angs]
            tapered(d, pts, w_px, LINE_TONE, alpha)
            tapered(d, pts, w_px*.4, CORE_TONE, alpha)
        log.append({'drawing': i, 'sweep_radius_px': round(R0/SS)})
    if i == RELEASED:
        # Thrown: straight speed lines from the opponent back toward the hand that threw it.
        c, me = centre(sys.argv[3], i), centre(dst, i)
        along = (c - me)/max(np.linalg.norm(c - me), 1.0)
        side = np.array((-along[1], along[0]))
        d = ImageDraw.Draw(back, 'RGBA')
        for k, off in enumerate((-64, -32, 0, 32, 64)):
            near = c - along*40*SS + side*off*SS          # starts inside the body's silhouette (hidden behind it)
            far_ = near - along*(190 + 50*(k % 2))*SS
            pts = [far_ + (near - far_)*u for u in np.linspace(0.0, 1.0, 12)]
            tapered(d, pts, 13, LINE_TONE, 235)
            tapered(d, pts, 5.2, CORE_TONE, 235)
        log.append({'drawing': i, 'speed_lines': 5})
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
        if not AIR:
            floor_y = int(rep['ground_baseline_y']*SS)
            ImageDraw.Draw(img).rectangle([0, floor_y, W_*SS, H_*SS], fill=(0, 0, 0, 0))
        img.resize((W_, H_), Image.LANCZOS).save(SORA / dst / sub / f'sora_fx_{i:02d}.png')
(SORA / dst / 'FX_Report.json').write_text(json.dumps({'source': src, 'fx': log}, indent=2) + '\n', encoding='utf-8')
print('FX_OK', log)
