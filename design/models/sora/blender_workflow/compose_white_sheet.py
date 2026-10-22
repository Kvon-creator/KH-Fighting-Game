"""Compose a version's 512 px frames into a white-background sprite sheet.

Frames go left to right, top to bottom; unused cells stay blank white. No text or grid lines.
Plain Python + Pillow; reads only the frames.
Run: python compose_white_sheet.py walk_fwd2d_v12 4 3
"""
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
assert str(ROOT).lower() == r'D:\KH Fighting Game'.lower()
version, cols, rows = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
OUT = ROOT / 'design/models/sora' / version
frames = [f['filename'] for f in json.loads((OUT / 'Idle_Loop_Report.json').read_text(encoding='utf-8'))['frames']]
assert len(frames) <= cols*rows, (len(frames), cols, rows)
sheet = Image.new('RGBA', (512*cols, 512*rows), (255, 255, 255, 255))
for i, name in enumerate(frames):
    im = Image.open(OUT / 'frames_512' / name).convert('RGBA')
    assert im.size == (512, 512), im.size
    sheet.alpha_composite(im, ((i % cols)*512, (i // cols)*512))
path = OUT / f'{version}_sheet_white_{cols}x{rows}.png'
sheet.convert('RGB').save(path)
print('SHEET_OK', path.name, sheet.size, 'frames', len(frames), 'blank cells', cols*rows - len(frames))
