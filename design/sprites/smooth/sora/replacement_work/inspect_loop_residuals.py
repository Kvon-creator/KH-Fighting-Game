"""Inspect attached old-weapon remnants on the two affected body plates."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
for index in (3, 4):
    folder = ROOT/'ready/run_loop/layers'/f'frame_{index:02d}_review_v2'
    im = Image.open(folder/'body_rebuilt.png').convert('RGBA')
    crop = im.crop((170, 80, 320, 185)).resize((900, 630))
    bg = Image.new('RGB', crop.size, '#646970')
    bg.paste(crop, (0, 0), crop)
    d = ImageDraw.Draw(bg)
    for x in range(0, 150, 10):
        d.line((x*6, 0, x*6, 630), fill='#55a0aa')
        d.text((x*6+2, 3), str(170+x), fill='white')
    for y in range(0, 105, 10):
        d.line((0, y*6, 900, y*6), fill='#55a0aa')
        d.text((2, y*6+2), str(80+y), fill='white')
    bg.save(folder/'Residual_Coordinate_Inspection.png')
print('Saved body-plate residual inspections.')
