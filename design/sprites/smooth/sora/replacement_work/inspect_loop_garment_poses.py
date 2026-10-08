"""Coordinate boards for individual loop jacket repairs; sources stay intact."""
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
assert ROOT.parents[4].name == 'KH Fighting Game'
LAYERS = ROOT/'ready/run_loop/layers'
for index, box in [(3, (150, 110, 390, 285)), (4, (170, 80, 410, 255))]:
    prior = LAYERS/f'frame_{index:02d}_review_v1'
    current = LAYERS/f'frame_{index:02d}_review_v2'
    board = Image.new('RGB', (1440, 575), '#555e68')
    for column, (path, label) in enumerate([
        (prior/'original_crop.png', 'Original body coordinates'),
        (prior/'head_occlusion.png', 'Retained head layer')]):
        im = Image.open(path).convert('RGBA').crop(box).resize((720, 525))
        board.paste(im, (column*720, 40), im)
        d = ImageDraw.Draw(board)
        d.text((column*720+8, 12), label, fill='white')
        for x in range(box[0], box[2], 20):
            px = column*720+(x-box[0])*3
            d.line((px, 40, px, 565), fill='#74909a')
            d.text((px+2, 42), str(x), fill='white')
        for y in range(box[1], box[3], 20):
            py = 40+(y-box[1])*3
            d.line((column*720, py, column*720+719, py), fill='#74909a')
            d.text((column*720+2, py+2), str(y), fill='white')
    board.save(current/'Garment_Source_Inspection.png')
print('Saved garment/head coordinate boards for loop03 and04.')
