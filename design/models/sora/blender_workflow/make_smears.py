"""Draw Keyblade smear frames for an attack as their own transparent layer (effects stay separate from the body).

Reads the 3D version's Idle_Loop_Report.json (camera, Key reach and the per-drawing `key_track`: grip point, blade
direction and `smear` = how many drawings back the smear starts, 0 = none). For a smeared drawing the blade is swept
from that earlier drawing through the ones between to this one (direction slerped, grip lerped per segment) and
projected through the sprite camera. The layer is meant to sit ON TOP of the body sprite (as in the reference).
Style follows Kvon's reference (Ekko's standing heavy in 2XKO): a SOLID crescent
along the tip's path, widest at the blade and tapering to a point where the swing began, two flat tones (a deeper
outer band and a pale core) like cel shading. It stops a little short of the blade so the Key itself stays readable.
Writes <2d version>/frames_smear_512/sora_smear_NN.png (one per drawing, empty where there is no smear).
Plain Python + Pillow + numpy; reads only the report.
Run: python make_smears.py atk_smed_v4 atk_smed2d_v4
"""
import json
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
src, dst = sys.argv[1:3]
SORA = ROOT / 'design/models/sora'
rep = json.loads((SORA / src / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
track = rep['key_track']
assert track, 'no key_track in the report (built before smear support?)'
OUT = SORA / dst / 'frames_smear_512'
OUT.mkdir(parents=True, exist_ok=True)

SS = 4                                    # supersampling
PX = 512 / rep['ortho_scale']             # pixels per metre
t = math.radians(rep['camera_yaw_deg'])
RIGHT = np.array([math.cos(t), math.sin(t), 0.0])
CAM = np.array(rep['camera_location'])
REACH = rep['key_reach_m']
STEPS = 18                                # per drawing-to-drawing segment
INNER = .30                               # the band's inner edge at its widest (share of the blade from the grip)
STOP = .94                                # stop this far along the last segment, short of the blade
OUTER_TONE = (122, 178, 255, 235)         # deeper outer band
CORE_TONE = (232, 243, 255, 240)          # pale core
# Guard-bash streak (Standing Light; Kvon: match the guard's colour): sampled from the guard in the approved drawing
# (mid 234,156,0 / highlight 255,190,0), with a lighter gold core for the same two-tone look.
GUARD_TONE = (234, 156, 0, 235)
GUARD_CORE = (255, 214, 96, 240)


def screen(p):
    d = p - CAM
    return ((256 + d.dot(RIGHT)*PX)*SS, (256 - d[2]*PX)*SS)


def slerp(a, b, u):
    a, b = a/np.linalg.norm(a), b/np.linalg.norm(b)
    om = math.acos(max(-1.0, min(1.0, float(a.dot(b)))))
    if om < 1e-4:
        return a
    return (math.sin((1 - u)*om)*a + math.sin(u*om)*b)/math.sin(om)


def sag_offsets(path):
    # A level swing seen from this eye-level camera projects to a nearly straight line. Like 2D fighting-game smears,
    # bow it into a crescent: when the tip's screen path bends less than 20% of its length, push its middle down so it
    # does (0 at both ends, most in the middle).
    outer = np.array([screen(g + d*REACH) for g, d in path])
    a, b = outer[0], outer[-1]
    chord = b - a
    length = float(np.linalg.norm(chord))
    if length < 1e-6:
        return [0.0]*len(path)
    nrm = np.array([-chord[1], chord[0]])/length
    dev = max(abs(float((p_ - a).dot(nrm))) for p_ in outer)
    need = max(0.0, .20*length - dev)
    n = len(path) - 1
    return [need*math.sin(math.pi*k/n) for k in range(n + 1)]


def crescent(draw, path, inner_frac, tone, sag, min_px):
    # path: list of (grip, dir); the band tapers from zero width at the start to full width at the end. A blade
    # pointing toward the camera looks short on screen, so the band is at least min_px wide (x taper) toward the grip.
    n = len(path) - 1
    outer = [screen(g + d*REACH) for g, d in path]
    inner = []
    for k, (g, d) in enumerate(path):
        w = (k/n)**.75                                  # 0 at the start -> 1 at the blade
        o_ = np.array(outer[k]); i_ = np.array(screen(g + d*REACH*(1 - (1 - inner_frac)*w)))
        v_ = i_ - o_; want = min_px*SS*w
        if np.linalg.norm(v_) < want:
            to_grip = np.array(screen(g)) - o_
            dir_ = to_grip/np.linalg.norm(to_grip) if np.linalg.norm(to_grip) > 1e-6 else np.array([0.0, 1.0])
            v_ = dir_*want
        inner.append(tuple(o_ + v_))
    outer = [(x, y + sag[k]) for k, (x, y) in enumerate(outer)]
    inner = [(x, y + sag[k]) for k, (x, y) in enumerate(inner)]
    draw.polygon(outer + inner[::-1], fill=tone)


def thrust(draw, a, b, width_px, tone):
    # Straight streak for a push (the Standing Light's guard bash): from where the guard was (a point) to just behind
    # where it is now (full width), tapering to a point behind it, with a rounded leading end.
    a, b = np.array(a), np.array(b)
    d = b - a
    ln = float(np.linalg.norm(d))
    if ln < 1e-6:
        return
    u = d/ln; nrm = np.array([-u[1], u[0]])
    end = a + d*.85                                   # stop short of the guard so it stays readable
    w = width_px*SS/2
    pts = [tuple(a), tuple(end + nrm*w), tuple(end - nrm*w)]
    draw.polygon(pts, fill=tone)
    draw.ellipse([end[0] - w, end[1] - w, end[0] + w, end[1] + w], fill=tone)


def dash_lines(draw, a, b):
    a, b = np.array(a), np.array(b)
    d = b - a
    ln = float(np.linalg.norm(d))
    if ln < 1e-6:
        return
    u = d/ln; nrm = np.array([-u[1], u[0]])
    head = a + d*.80                                   # lines end a little behind the guard
    for off_px, len_k, w_px in ((-14, .70, 3), (0, 1.0, 3), (13, .55, 2)):
        front = head + nrm*off_px*SS
        back = front - u*ln*len_k
        steps = 6
        for k in range(steps):                         # thin toward the back end, fully opaque only at the front
            p0 = back + (front - back)*k/steps; p1 = back + (front - back)*(k + 1)/steps
            t_ = (k + 1)/steps
            draw.line([tuple(p0), tuple(p1)], fill=GUARD_TONE[:3] + (int(200*t_),),
                      width=max(1, round(w_px*SS*(.4 + .6*t_))))


report = []
for i, fr in enumerate(track):
    img = Image.new('RGBA', (512*SS, 512*SS), (0, 0, 0, 0))
    back = int(fr.get('smear') or 0)
    if back and i - back >= 0 and fr.get('smear_style') == 'thrust':
        # Guard point = the leading (left) fist for the Light; earlier drawing moved into this drawing's frame.
        a_ = track[i - back]
        shift = (fr.get('offset_px', (0, 0))[0] - a_.get('offset_px', (0, 0))[0])/PX
        pa = np.array(a_['lgrip_world']) + RIGHT*shift
        pb = np.array(fr['lgrip_world'])
        draw = ImageDraw.Draw(img, 'RGBA')
        # Kvon: subtle dash lines instead of a smear - three thin gold lines trailing behind the guard along the
        # push, offset across it, different lengths, thinning toward their back ends.
        dash_lines(draw, screen(pa), screen(pb))
        report.append({'drawing': i, 'from_drawing': i - back, 'style': 'thrust',
                       'length_px': round(float(np.linalg.norm(np.array(screen(pb)) - np.array(screen(pa))))/SS, 1)})
    elif back and i - back >= 0:
        path, sweep = [], 0.0
        for s_ in range(i - back, i):
            a, b = track[s_], track[s_ + 1]
            # Drawings shifted inside the frame (offset_px) are drawn where they appear in THIS drawing's frame.
            sh_ = lambda f_: (np.array(fr.get('offset_px', (0, 0)))[0] - np.array(f_.get('offset_px', (0, 0)))[0])/PX
            ga = np.array(a['grip_world']) + RIGHT*sh_(a)
            gb = np.array(b['grip_world']) + RIGHT*sh_(b)
            da, db = np.array(a['dir_world']), np.array(b['dir_world'])
            sweep += math.degrees(math.acos(max(-1.0, min(1.0, float(da.dot(db)/np.linalg.norm(da)/np.linalg.norm(db))))))
            last = s_ == i - 1
            for j in range(STEPS + 1):
                if j == 0 and path:
                    continue
                u = (STOP if last else 1.0)*j/STEPS
                path.append((ga + (gb - ga)*u, slerp(da, db, u)))
        draw = ImageDraw.Draw(img, 'RGBA')
        sag = sag_offsets(path)
        crescent(draw, path, INNER, OUTER_TONE, sag, 64)
        crescent(draw, path, .62, CORE_TONE, sag, 30)  # narrower pale core along the tip side
        report.append({'drawing': i, 'from_drawing': i - back, 'sweep_deg': round(sweep, 1)})
    img.resize((512, 512), Image.LANCZOS).save(OUT / f'sora_smear_{i:02d}.png')
(SORA / dst / 'Smear_Report.json').write_text(json.dumps({'source': src, 'smears': report}, indent=2) + '\n',
                                             encoding='utf-8')
print('SMEARS_OK', report)
