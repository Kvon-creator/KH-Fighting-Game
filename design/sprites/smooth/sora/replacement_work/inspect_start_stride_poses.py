"""Coordinate boards for the final three genuine run-start source poses."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
OUT = ROOT/'ready/run_start/refinement_v4'
OUT.mkdir(parents=True, exist_ok=True)
source = Image.open(OUT.parent/'run_start_source.png').convert('RGBA')
# Final pose extends left of its old grid cell. Include original shoe pixels.
boxes = [(445, 450, 889, 887), (889, 450, 1333, 887), (1306, 450, 1774, 887)]
for i, box in enumerate(boxes, 5):
    im = source.crop(box)
    im.save(OUT/f'frame_{i:02d}_original_crop.png')
    crop = im.crop((100, 20, 480, 280)).resize((1140, 780))
    bg = Image.new('RGB', crop.size, '#646970')
    bg.paste(crop, (0, 0), crop)
    d = ImageDraw.Draw(bg)
    for x in range(0, 380, 20):
        d.line((x*3, 0, x*3, 780), fill='#55a0aa')
        d.text((x*3+2, 3), str(100+x), fill='white')
    for y in range(0, 260, 20):
        d.line((0, y*3, 1140, y*3), fill='#55a0aa')
        d.text((2, y*3+2), str(20+y), fill='white')
    bg.save(OUT/f'Frame_{i:02d}_Coordinate_Inspection.png')
print('Saved source inspection boards for frames 05-07.')
