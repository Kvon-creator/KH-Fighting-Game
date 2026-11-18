"""Living background for Dark Depths (Kvon, November 18: "Living background" - drifting clouds, a soft pulse on the
Heartless emblem, a few drifting embers / dark particles).

Splits the background layer (assets/stages/dark_depths/bg.png) into:
- sky.png: the sky dome alone (rendered from bg_cam with the pillars hidden: raw_bg_sky_2x.png), made to wrap
  sideways (the last FADE columns are blended into the first ones) so Parallax2D can scroll it forever.
- pillars.png: bg.png with the sky cut out (alpha from raw_bg_pillars_2x.png = pillars / terrain rendered alone).
  The far horizon (mountain line, from HORIZON down) stays in this layer so it doesn't drift with the clouds.
- emblem_glow.png: a soft red glow made from the Heartless emblem's red pixels on the middle pillar, pulsed in game.
Re-render the two raw images with the scratch render_bg_split.py approach (bg_cam, 3200 x 2160, film transparent:
once with only the skybox, once with only L_bg). Run: python stages/build_living_bg.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'stages/dark_depths_render'
OUT = ROOT / 'KingdomArena/assets/stages/dark_depths'
W, H = 1600, 1080
HORIZON = (800, 840)          # game px rows: the pillars layer fades from transparent to solid sky over these rows
FADE = 240                    # game px blended across the sky's wrap seam
EMBLEM = (720, 465, 880, 585)  # game px box around the emblem on the middle pillar

bg = np.asarray(Image.open(OUT / 'bg.png').convert('RGBA')).astype(float)
pil_a = np.asarray(Image.open(RAW / 'raw_bg_pillars_2x.png').resize((W, H), Image.LANCZOS))[..., 3].astype(float)
y = np.arange(H)[:, None].astype(float)
ground = np.clip((y - HORIZON[0]) / (HORIZON[1] - HORIZON[0]), 0, 1) * 255
pillars = bg.copy()
pillars[..., 3] = np.maximum(pil_a, ground)
Image.fromarray(pillars.clip(0, 255).astype(np.uint8), 'RGBA').save(OUT / 'pillars.png')

sky = np.asarray(Image.open(RAW / 'raw_bg_sky_2x.png').resize((W, H), Image.LANCZOS)).astype(float)
sky = sky[:HORIZON[1] + 8]    # nothing below the horizon is ever seen through the pillars layer
t = (np.arange(FADE) / (FADE - 1))[None, :, None]
tile = sky[:, :W - FADE].copy()
tile[:, :FADE] = sky[:, W - FADE:] * (1 - t) + sky[:, :FADE] * t   # left edge continues from the right edge
tile[..., 3] = 255
Image.fromarray(tile.clip(0, 255).astype(np.uint8), 'RGBA').save(OUT / 'sky.png')

x0, y0, x1, y1 = EMBLEM
box = bg[y0:y1, x0:x1]
r, g, b = box[..., 0], box[..., 1], box[..., 2]
red = ((r > 140) & (g < 70) & (b < 80)).astype(float) * 255
pad = 24
mask = Image.fromarray(np.pad(red, pad).astype(np.uint8), 'L')
glow = np.maximum(np.asarray(mask.filter(ImageFilter.GaussianBlur(9))).astype(float) * 1.6,
                  np.asarray(mask.filter(ImageFilter.GaussianBlur(2))).astype(float))
out = np.zeros(glow.shape + (4,))
out[..., 0], out[..., 1], out[..., 2] = 255, 70, 90
out[..., 3] = glow.clip(0, 255)
Image.fromarray(out.astype(np.uint8), 'RGBA').save(OUT / 'emblem_glow.png')
print('LIVING_BG_OK sky', tile.shape[1], 'x', tile.shape[0], 'emblem px', int((red > 0).sum()),
      'glow at', (x0 - pad, y0 - pad))
