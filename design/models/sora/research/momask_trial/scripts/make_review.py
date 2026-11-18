"""Review images for an attack: each 2D version's drawings with the smear layer on top, on white.
Writes <out>/<name>_compare.png (one row per version) and <out>/<name>_slow.gif per version (holds x3).
Plain Python + Pillow; reads only. Run: python make_review.py <out_dir> <name> atk_clight2d_v8 atk_clight2d_v9
"""
import json
import sys
from pathlib import Path
from PIL import Image

SORA = Path(__file__).resolve().parents[2]
out_dir, name, versions = Path(sys.argv[1]), sys.argv[2], sys.argv[3:]
out_dir.mkdir(parents=True, exist_ok=True)
CELL, SLOW = 320, 3


def drawings(version):
    d = SORA / version
    rep = json.loads((d / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))
    imgs = []
    for i, f in enumerate(rep['frames']):
        im = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
        im.alpha_composite(Image.open(d / 'frames_512' / f['filename']).convert('RGBA'))
        smear = d / 'frames_smear_512' / f'sora_smear_{i:02d}.png'
        if smear.exists():
            im.alpha_composite(Image.open(smear).convert('RGBA'))
        imgs.append(im)
    return imgs, rep['game_frames_60fps']


rows = [drawings(v) for v in versions]
cols = max(len(r[0]) for r in rows)
sheet = Image.new('RGB', (CELL*cols, CELL*len(rows)), 'white')
for r, (imgs, _) in enumerate(rows):
    for c, im in enumerate(imgs):
        sheet.paste(im.convert('RGB').resize((CELL, CELL), Image.LANCZOS), (c*CELL, r*CELL))
sheet.save(out_dir / f'{name}_compare.png')
for v, (imgs, holds) in zip(versions, rows):
    frames = [im.convert('RGB') for im in imgs]
    frames[0].save(out_dir / f'{name}_{v}_slow.gif', save_all=True, append_images=frames[1:],
                   duration=[round(h*1000/60*SLOW) for h in holds], loop=0)
print('REVIEW_OK', out_dir, [len(r[0]) for r in rows])
