"""Post-process the illustration-style renders into flat 2D sprites matched to the pose sheet.

Per frame: smooth PS2 texture noise, snap colors to a palette sampled from the pose sheet's
top-right figure, and add a crisp outer ink line. Writes frames_512 / frames_128 plus an
Idle_Loop_Report.json (timing copied from the source loop) so package_idle_loop.py can run.
Plain Python + Pillow + numpy; reads only.
Run: python stylize_2d_frames.py battle_v12 sprite2d_v1
"""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[4]
assert (ROOT / 'KingdomArena/project.godot').is_file(), ROOT  # project root (any clone)
source, version = sys.argv[1:3]
SORA = ROOT / 'design/models/sora'
OUT = SORA / version
SHEET = ROOT / 'design/references/sora_kh2_pose_sheet.png'
INK = np.array([26, 22, 38], np.float32)
PALETTE_SIZE = 28

# Palette from the reference figure, excluding the sheet's flat navy background.
ref = np.asarray(Image.open(SHEET).convert('RGB').crop((520, 40, 1024, 500)), np.float32).reshape(-1, 3)
bg = np.array([46, 53, 63], np.float32)
figure = ref[np.linalg.norm(ref - bg, axis=1) > 28]
strip = Image.fromarray(figure.astype(np.uint8).reshape(1, -1, 3))
palette = np.array(strip.quantize(PALETTE_SIZE, method=Image.Quantize.MEDIANCUT).getpalette()[:PALETTE_SIZE*3],
                   np.float32).reshape(-1, 3)
palette = np.vstack([palette, INK])  # ink is always available for line pixels

(OUT / 'frames_512').mkdir(exist_ok=True); (OUT / 'frames_128').mkdir(exist_ok=True)
src_report = json.loads((SORA / source / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
# *_ink versions (Kvon, option 1): separate the front forearm from the dark jacket with a firm ink
# line on the jacket side and a 1 px light rim on the skin side, only around that forearm.
LIMB = SORA / source / 'Limb_Screen.json'
FOREARM = json.loads(LIMB.read_text(encoding='utf-8'))['frames'] if version.endswith('_ink') and LIMB.exists() else None
INK_LOG = []


def capsule(shape, a_, b_, radius):
    yy, xx = np.mgrid[:shape[0], :shape[1]]
    a_, b_ = np.array(a_, float), np.array(b_, float)
    d_ = b_ - a_
    t_ = np.clip(((xx - a_[0])*d_[0] + (yy - a_[1])*d_[1]) / (d_ @ d_), 0, 1)
    return np.hypot(xx - (a_[0] + t_*d_[0]), yy - (a_[1] + t_*d_[1])) <= radius


def dilate(mask, px):
    return np.asarray(Image.fromarray((mask*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2*px + 1))) > 127


def ink_forearm(rgb, alpha, joints):
    region = capsule(alpha.shape, joints['elbow'], joints['wrist'], 26) & (alpha > 200)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = rgb @ np.array([.299, .587, .114])
    skin = region & (r > 120) & (r > g + 15) & (g > b) & (lum > 90)
    dark = region & (lum < 70)
    edge_dark = dark & dilate(skin, 2)          # 2 px ink band on the jacket side of the boundary
    edge_skin = skin & dilate(dark, 1)          # 1 px light rim on the skin side
    out = rgb.copy()
    out[edge_dark] = INK
    out[edge_skin] = np.clip(out[edge_skin]*1.18 + 12, 0, 255)
    # Readability: mean luminance step across the skin/jacket boundary inside the region.
    step = float(lum[edge_skin].mean() - (out[edge_dark] @ np.array([.299, .587, .114])).mean()) if edge_skin.any() and edge_dark.any() else 0.0
    return out, {'ink_px': int(edge_dark.sum()), 'rim_px': int(edge_skin.sum()), 'boundary_luma_step': round(step, 1)}


frames = []
for entry in src_report['frames']:
    raw = Image.open(OUT / 'frames_512_raw' / entry['filename']).convert('RGBA')
    alpha = np.asarray(raw.getchannel('A'), np.float32)
    if version == 'sprite2d_v1':
        smooth = np.asarray(raw.convert('RGB').filter(ImageFilter.MedianFilter(5)), np.float32)
        flat = smooth.reshape(-1, 3)
        nearest = np.argmin(((flat[:, None, :] - palette[None, :, :])**2).sum(2), axis=1)
        rgb = palette[nearest].reshape(smooth.shape)
    else:
        # v2+: v1's palette snap and median washed colours out and muddied the face; keep the
        # rendered colours and only lift saturation/contrast slightly toward the sheet's look.
        rgb = np.asarray(raw.convert('RGB'), np.float32)
        grey = rgb.mean(2, keepdims=True)
        rgb = np.clip((grey + (rgb - grey)*1.18 - 128)*1.06 + 128, 0, 255)
    # Outer ink: grow the silhouette ~2px and fill the new rim with ink, softly anti-aliased.
    solid = Image.fromarray(((alpha > 127)*255).astype(np.uint8))
    grow = 5 if version in ('sprite2d_v1', 'sprite2d_v2') else 3  # v3+: 1px crisp rim
    grown = np.asarray(solid.filter(ImageFilter.MaxFilter(grow)).filter(ImageFilter.GaussianBlur(.6)), np.float32)
    rim = np.clip(grown - alpha, 0, 255) / 255
    a = np.clip(alpha + rim*255, 0, 255)
    rgb = rgb*(1 - rim[..., None]) + INK*rim[..., None]
    if FOREARM is not None:
        rgb, stats = ink_forearm(rgb, alpha, FOREARM[len(frames)])
        INK_LOG.append(stats)
    out = Image.fromarray(np.dstack([rgb, a]).astype(np.uint8), 'RGBA')
    out.save(OUT / 'frames_512' / entry['filename'])
    out.resize((128, 128), Image.LANCZOS).save(OUT / 'frames_128' / entry['filename'])
    frames.append({**entry})
report = {**src_report, 'version': version, 'frames': frames,
          'style_2d': {'source_loop': source, 'palette_from': 'design/references/sora_kh2_pose_sheet.png top-right',
                       'palette_size': PALETTE_SIZE + 1, 'median_filter': 5, 'outer_ink_px': 2,
                       'forearm_ink': INK_LOG or None}}
(OUT / 'Idle_Loop_Report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('STYLIZE_OK', len(frames))
